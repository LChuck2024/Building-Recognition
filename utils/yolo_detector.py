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
        """预处理图像"""
        if isinstance(image, str):
            image = Image.open(image)
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        elif not isinstance(image, Image.Image):
            raise TypeError("Unsupported image type")
        
        return image
    
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
        for r in results[0]:
            boxes = r.boxes
            for box in boxes:
                # 获取边界框坐标
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                # 获取置信度
                conf = float(box.conf)
                # 获取类别ID
                cls_id = int(box.cls)
                
                # 获取建筑物类别标签
                label = self.building_classes[cls_id % len(self.building_classes)]
                
                detections.append({
                    'label': label,
                    'confidence': conf,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)]
                })
        
        return detections
    
    def draw_detections(self, image, detections, show_label=True):
        """在图像上绘制检测结果
        
        Args:
            image: PIL Image对象或numpy数组
            detections: 检测结果列表
            show_label: 是否显示标签
            
        Returns:
            numpy.ndarray: 绘制了检测框的图像
        """
        if isinstance(image, Image.Image):
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        viz_img = image.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            label = det['label']
            conf = det['confidence']
            
            # 绘制绿色边框
            cv2.rectangle(viz_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            if show_label:
                # 添加标签文本
                label_text = f"{label} {conf:.2f}"
                # 计算文本大小
                (text_width, text_height), _ = cv2.getTextSize(
                    label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
                # 绘制标签背景
                cv2.rectangle(viz_img, (x1, y1 - text_height - 4),
                            (x1 + text_width, y1), (0, 255, 0), -1)
                # 绘制白色文本
                cv2.putText(viz_img, label_text, (x1, y1 - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        return viz_img