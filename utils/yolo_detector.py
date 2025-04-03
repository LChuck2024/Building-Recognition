import torch
import numpy as np
from PIL import Image
import cv2
from pathlib import Path
from ultralytics import YOLO

class YOLODetector:
    def __init__(self, model_path=None, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        # 如果没有指定模型路径，使用预训练的YOLOv5模型
        if model_path is None:
            self.model = YOLO("yolo11n.pt")  # 使用YOLO11预训练模型
        else:
            self.model = YOLO(model_path)  # 加载自定义模型
        self.model.to(device)
        
        # 建筑物类别
        self.building_classes = [
            '住宅楼', '办公楼', '商业建筑', '工业建筑',
            '文教建筑', '医疗建筑', '酒店建筑', '其他建筑'
        ]
    
    def preprocess_image(self, image):
        """预处理图像
        
        Args:
            image: PIL Image对象、图像路径、numpy数组或文件对象
            
        Returns:
            PIL.Image: 预处理后的图像
            
        Raises:
            ValueError: 当图像格式不支持或图像损坏时
            TypeError: 当输入类型不支持时
        """
        try:
            if isinstance(image, (str, Path)):
                # 检查文件是否存在
                if not Path(image).exists():
                    raise FileNotFoundError(f"Image file not found: {image}")
                image = Image.open(image)
            elif isinstance(image, np.ndarray):
                image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            elif hasattr(image, 'read'):
                # 处理文件对象（如Streamlit的UploadedFile）
                try:
                    image = Image.open(image)
                except Exception as e:
                    raise ValueError(f"Failed to open image from file object: {str(e)}")
            elif not isinstance(image, Image.Image):
                raise TypeError(f"Unsupported image type: {type(image)}")
            
            # 验证图像格式
            if image.format not in ['JPEG', 'PNG', 'JPG']:
                raise ValueError(f"Unsupported image format: {image.format or 'Unknown'}")
            
            # 确保图像模式正确
            if image.mode not in ['RGB', 'RGBA']:
                image = image.convert('RGB')
                
            return image
            
        except (Image.UnidentifiedImageError, OSError) as e:
            raise ValueError(f"Invalid or corrupted image: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error processing image: {str(e)}")

    
    def detect(self, image, conf_thres=0.5, preview_size=None):
        """执行建筑物检测
        
        Args:
            image: PIL Image对象、图像路径或numpy数组
            conf_thres: 置信度阈值
            preview_size: 预览图像大小，格式为(width, height)。如果提供，将调整输出图像大小
            
        Returns:
            tuple: (检测结果列表, 绘制了检测框的图像)
        """
        # 预处理图像
        image = self.preprocess_image(image)
        
        # 执行检测
        results = self.model(image, conf=conf_thres, imgsz=image.size)
        
        # 处理检测结果
        detections = []
        for result in results:
            boxes = result.boxes
            for idx, (box, cls, conf) in enumerate(zip(boxes.xyxy, boxes.cls, boxes.conf)):
                if conf >= conf_thres:
                    label = result.names[int(cls.item())]
                    bbox = box.cpu().numpy().tolist()
                    detections.append({
                        'label': label,
                        'class': label,  # 添加class键
                        'confidence': float(conf.item()),
                        'bbox': bbox,
                        'width': int(image.width),
                        'height': int(image.height)
                    })
        
        # 使用YOLO的plot方法绘制检测结果
        plotted_image = results[0].plot()
        
        # 如果指定了预览大小，调整图像尺寸
        if preview_size is not None:
            plotted_image = cv2.resize(plotted_image, preview_size, interpolation=cv2.INTER_AREA)
        
        return detections, plotted_image