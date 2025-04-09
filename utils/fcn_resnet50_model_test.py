import os
import sys
import torch
from PIL import Image
from model_detector import ModelDetector
import matplotlib.pyplot as plt

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_fcn_model():
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(__file__))
    # 初始化模型检测器，使用相对于项目根目录的路径
    os.chdir(root_dir)
    detector = ModelDetector('fcn_resnet50_model_best.pth')
    
    # 加载测试图像
    test_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'detection_results', '1744116966_811F0309886A7EEA124B65641056E35830100218_w1920_h1280.jpg')
    image = Image.open(test_image_path)
    
    # 进行预测
    detections, plotted_image = detector.detect(image)
    
    # 显示结果
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 2, 1)
    plt.title('Original Image')
    plt.imshow(image)
    plt.axis('off')
    
    plt.subplot(1, 2, 2)
    plt.title('Segmentation Result')
    plt.imshow(plotted_image)
    plt.axis('off')
    
    plt.show()
    
    print('Detections:', detections)

if __name__ == '__main__':
    test_fcn_model()