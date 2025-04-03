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
    
    def preprocess_image(self, image, target_size=(640, 640)):
        """预处理图像
        
        Args:
            image: PIL Image对象、图像路径或numpy数组
            target_size: 目标图像大小 (width, height)
            
        Returns:
            PIL.Image: 预处理后的图像
        """
        if isinstance(image, str):
            image = Image.open(image)
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        elif not isinstance(image, Image.Image):
            raise TypeError("Unsupported image type")
        
        # 调整图像大小，保持宽高比
        w, h = image.size
        scale = min(target_size[0] / w, target_size[1] / h)
        new_w, new_h = int(w * scale), int(h * scale)
        
        # 调整大小并填充到目标尺寸
        image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        new_image = Image.new('RGB', target_size, (128, 128, 128))
        new_image.paste(image, ((target_size[0] - new_w) // 2,
                               (target_size[1] - new_h) // 2))
        
        return new_image
    
    def detect(self, image, conf_thres=0.5):
        """执行建筑物检测
        
        Args:
            image: PIL Image对象、图像路径或numpy数组
            conf_thres: 置信度阈值
            
        Returns:
            list: 检测结果列表，每个元素包含 [label, confidence, bbox]
        """
        # 预处理图像
        image = self.preprocess_image(image)
        
        # 执行检测
        results = self.model(image, conf=conf_thres)
        
        # 处理检测结果
        detections = []
        for result in results:
            boxes = result.boxes
            for idx, (box, cls, conf) in enumerate(zip(boxes.xyxy, boxes.cls, boxes.conf)):
                if conf >= conf_thres:
                    label = result.names[int(cls.item())]
                    bbox = box.cpu().numpy()
                    detections.append({
                        'label': label,
                        'confidence': conf.item(),
                        'bbox': bbox
                    })
        
        return detections

    def draw_detections(self, image, detections, show_conf=True):
        """在图像上绘制检测结果
        
        Args:
            image: PIL Image对象或numpy数组
            detections: detect方法返回的检测结果
            show_conf: 是否显示置信度
        
        Returns:
            numpy.ndarray: 绘制了检测框的图像
        """
        if isinstance(image, Image.Image):
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        elif isinstance(image, str):
            image = cv2.imread(image)
        
        img_draw = image.copy()
        
        for det in detections:
            bbox = det['bbox'].astype(int)
            label = det['label']
            conf = det['confidence']
            
            # 绘制边界框
            cv2.rectangle(img_draw, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
            
            # 准备标签文本
            label_text = f'{label} {conf:.2f}' if show_conf else label
            
            # 绘制标签背景
            (text_width, text_height), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(img_draw, (bbox[0], bbox[1] - text_height - 4),
                         (bbox[0] + text_width, bbox[1]), (0, 255, 0), -1)
            
            # 绘制标签文本
            cv2.putText(img_draw, label_text, (bbox[0], bbox[1] - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        return img_draw