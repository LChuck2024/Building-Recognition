import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import cv2

class BuildingDetector:
    def __init__(self):
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
        ])
        
        # 建筑物类别
        self.building_classes = [
            '住宅楼', '办公楼', '商业建筑', '工业建筑',
            '文教建筑', '医疗建筑', '酒店建筑', '其他'
        ]
    
    def preprocess_image(self, image):
        """预处理图像"""
        if isinstance(image, np.ndarray):
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        return self.transform(image)
    
    def detect_building(self, image):
        """检测建筑物类型"""
        # 预处理图像
        processed_image = self.preprocess_image(image)
        
        # TODO: 这里后续会添加实际的模型推理代码
        # 目前返回示例结果
        return {
            'class': '办公楼',
            'confidence': 0.95,
            'bbox': [100, 100, 300, 300]  # [x1, y1, x2, y2]
        }
    
    def draw_result(self, image, result):
        """在图像上绘制检测结果"""
        img = np.array(image)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # 绘制边界框
        x1, y1, x2, y2 = result['bbox']
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # 添加标签
        label = f"{result['class']} {result['confidence']:.2%}"
        cv2.putText(img, label, (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)