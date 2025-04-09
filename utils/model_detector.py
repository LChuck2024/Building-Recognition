import torch
import numpy as np
from PIL import Image
import cv2
from pathlib import Path
from ultralytics import YOLO
from torchvision import transforms

class ModelDetector:
    def __init__(self, model_name, device=None):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu')
        self.model_name = model_name
        
        model_path = Path(f"model/{self.model_name}")
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        print(f"Loading model: {model_path}")

        # 从文件名判断模型类型
        model_name_lower = self.model_name.lower()
        if 'yolo' in model_name_lower or 'v8n' in model_name_lower or '12s' in model_name_lower:
            self.model_type = 'yolo'
        elif 'unet' in model_name_lower:
            self.model_type = 'unet'
        elif 'fcn' in model_name_lower:
            self.model_type = 'fcn'
        else:
            raise ValueError(f"无法从文件名 {self.model_name} 中识别模型类型，文件名必须包含 'yolo'、'unet' 或 'fcn' 关键字")
        
        self._load_model(model_path)
        print(f"Successfully loaded {self.model_type} model: {self.model_name}")
    
    def _load_model(self, model_path):
        if self.model_type == 'yolo':
            self.model = YOLO(str(model_path), task='detect')
            self.model.to(self.device)
            self.model.eval()
        elif self.model_type in ['unet', 'fcn']:
            try:
                if self.model_type == 'fcn':
                    from torchvision.models.segmentation import fcn_resnet50
                    self.model = fcn_resnet50(pretrained=False, num_classes=1, aux_loss=True)
                    # 加载状态字典
                    state_dict = torch.load(model_path, map_location=self.device)
                    if isinstance(state_dict, dict) and 'state_dict' in state_dict:
                        state_dict = state_dict['state_dict']
                    # 过滤掉辅助分类器的参数
                    filtered_state_dict = {k: v for k, v in state_dict.items() if not k.startswith('aux_classifier')}
                    self.model.load_state_dict(filtered_state_dict, strict=False)
                elif self.model_type == 'unet':
                    # 加载UNet模型
                    import segmentation_models_pytorch as smp
                    self.model = smp.Unet(
                        encoder_name="efficientnet-b4",
                        encoder_weights=None,
                        in_channels=3,
                        classes=1,
                        encoder_depth=5,
                        decoder_channels=(256, 128, 64, 32, 16),
                        decoder_use_batchnorm=True
                    )
                    # 加载状态字典
                    state_dict = torch.load(model_path, map_location=self.device)
                    if isinstance(state_dict, dict):
                        if 'state_dict' in state_dict:
                            state_dict = state_dict['state_dict']
                        elif 'model_state_dict' in state_dict:
                            state_dict = state_dict['model_state_dict']
                    self.model.load_state_dict(state_dict)
                self.model = self.model.to(self.device)
                self.model.eval()
            except Exception as e:
                raise ValueError(f"Error loading model from {model_path}: {str(e)}")
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
    
    def preprocess_image(self, image):
        try:
            if isinstance(image, (str, Path)):
                if not Path(image).exists():
                    raise FileNotFoundError(f"Image file not found: {image}")
                image = Image.open(image)
            elif isinstance(image, np.ndarray):
                image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            elif hasattr(image, 'read'):
                image = Image.open(image)
            elif not isinstance(image, Image.Image):
                raise TypeError(f"Unsupported image type: {type(image)}")
            
            if image.format not in ['JPEG', 'PNG', 'JPG', None]:
                raise ValueError(f"Unsupported image format: {image.format}")
            
            return image.convert('RGB')
        except Exception as e:
            raise ValueError(f"Error processing image: {str(e)}")
    
    def detect(self, image, conf_thres=0.5, preview_size=None):
        image = self.preprocess_image(image)
        
        if self.model_type == 'yolo':
            results = self.model(image, conf=conf_thres, imgsz=image.size)
            detections = [{
                'label': 'building',
                'class': 'building',
                'confidence': float(conf.item()),
                'bbox': box.cpu().numpy().tolist(),
                'width': image.width,
                'height': image.height
            } for result in results[0] for box, cls, conf in zip(result.boxes.xyxy, result.boxes.cls, result.boxes.conf)
              if conf >= conf_thres]
            plotted_image = results[0].plot()
        
        else:
            transform = transforms.Compose([
                transforms.Resize((512, 512)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
            input_tensor = transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                output = self.model(input_tensor)
                if self.model_type == 'fcn':
                    output = output['out']
                pred = torch.argmax(output, dim=1).squeeze().cpu().numpy()
            
            detections = [{
                'label': 'building',
                'class': 'building',
                'confidence': 1.0,
                'segmentation': pred.tolist(),
                'width': image.width,
                'height': image.height
            }]
            
            plotted_image = np.zeros((pred.shape[0], pred.shape[1], 3), dtype=np.uint8)
            plotted_image[pred > 0] = [0, 255, 0]
            plotted_image = cv2.resize(plotted_image, (image.width, image.height))
            original_image = np.array(image)
            plotted_image = cv2.addWeighted(original_image, 0.7, plotted_image, 0.3, 0)
        
        if preview_size:
            plotted_image = cv2.resize(plotted_image, preview_size, interpolation=cv2.INTER_AREA)
        
        return detections, plotted_image