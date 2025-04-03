import numpy as np
import cv2
from PIL import Image
import torch
import os
from pathlib import Path


def preprocess_drone_image(image, resize=None, enhance_contrast=True):
    """
    预处理无人机影像，包括调整大小、增强对比度等
    
    参数:
        image: PIL.Image 或 numpy 数组，输入图像
        resize: tuple, 可选，调整图像大小的目标尺寸 (width, height)
        enhance_contrast: bool, 是否增强对比度
        
    返回:
        处理后的图像 (numpy 数组)
    """
    # 确保图像是 numpy 数组
    if isinstance(image, Image.Image):
        img = np.array(image)
    else:
        img = image.copy()
    
    # 调整图像大小
    if resize is not None:
        img = cv2.resize(img, resize)
    
    # 增强对比度
    if enhance_contrast:
        # 转换为 LAB 颜色空间
        lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
        # 分离通道
        l, a, b = cv2.split(lab)
        # 对亮度通道应用 CLAHE (对比度受限的自适应直方图均衡化)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        # 合并通道
        limg = cv2.merge((cl, a, b))
        # 转换回 RGB
        img = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    
    return img


def segment_buildings(image, method="instance", confidence_threshold=0.5):
    """
    对无人机影像进行建筑物分割
    
    参数:
        image: numpy 数组，输入图像
        method: str, 分割方法，可选 "semantic"、"instance" 或 "panoptic"
        confidence_threshold: float, 置信度阈值
        
    返回:
        segmentation_mask: numpy 数组，分割掩码
        num_buildings: int, 检测到的建筑物数量
        building_areas: list, 每个建筑物的面积 (像素数)
    """
    # 这里应该是实际的分割模型代码
    # 以下是模拟实现，实际应用中应替换为真实的模型
    
    # 创建模拟的分割掩码
    segmentation_mask = np.zeros(image.shape[:2], dtype=np.uint8)
    
    # 模拟一些建筑物区域
    height, width = segmentation_mask.shape
    building_areas = []
    num_buildings = np.random.randint(2, 6)  # 随机生成2-5个建筑物
    
    for _ in range(num_buildings):
        x1, y1 = np.random.randint(0, width - 100), np.random.randint(0, height - 100)
        w, h = np.random.randint(50, 150), np.random.randint(50, 150)
        x2, y2 = min(x1 + w, width), min(y1 + h, height)
        
        # 为每个建筑物分配一个唯一的ID（对于实例分割）
        if method == "instance" or method == "panoptic":
            building_id = _ + 1  # 从1开始的ID
            segmentation_mask[y1:y2, x1:x2] = building_id
        else:  # 语义分割只有前景/背景
            segmentation_mask[y1:y2, x1:x2] = 255
        
        # 计算面积
        area = (y2 - y1) * (x2 - x1)
        building_areas.append(area)
    
    return segmentation_mask, num_buildings, building_areas


def visualize_segmentation(image, mask, mode="overlay"):
    """
    可视化建筑物分割结果
    
    参数:
        image: numpy 数组，原始图像
        mask: numpy 数组，分割掩码
        mode: str, 可视化模式，可选 "contour"、"overlay" 或 "fill"
        
    返回:
        可视化后的图像 (numpy 数组)
    """
    # 确保图像是 numpy 数组
    if isinstance(image, Image.Image):
        img = np.array(image)
    else:
        img = image.copy()
    
    # 根据可视化模式创建可视化图像
    if mode == "contour":
        # 显示建筑物轮廓
        viz_img = img.copy()
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(viz_img, contours, -1, (0, 255, 0), 2)
    elif mode == "overlay":
        # 创建半透明掩码叠加
        viz_img = img.copy()
        overlay = np.zeros_like(viz_img)
        
        # 对于实例分割，为每个建筑物分配不同的颜色
        unique_ids = np.unique(mask)
        unique_ids = unique_ids[unique_ids > 0]  # 排除背景 (0)
        
        for building_id in unique_ids:
            # 为每个建筑物生成一个随机颜色
            color = np.random.randint(0, 255, 3).tolist()
            overlay[mask == building_id] = color
        
        # 如果没有实例ID（语义分割），则使用绿色
        if len(unique_ids) == 0 and np.max(mask) > 0:
            overlay[mask > 0] = [0, 255, 0]
            
        viz_img = cv2.addWeighted(viz_img, 0.7, overlay, 0.3, 0)
    else:  # fill
        # 填充建筑物区域
        viz_img = img.copy()
        
        # 对于实例分割，为每个建筑物分配不同的颜色
        unique_ids = np.unique(mask)
        unique_ids = unique_ids[unique_ids > 0]  # 排除背景 (0)
        
        for building_id in unique_ids:
            # 为每个建筑物生成一个随机颜色
            color = np.random.randint(0, 255, 3).tolist()
            viz_img[mask == building_id] = color
        
        # 如果没有实例ID（语义分割），则使用绿色
        if len(unique_ids) == 0 and np.max(mask) > 0:
            viz_img[mask > 0] = [0, 255, 0]
    
    return viz_img


def detect_changes(earlier_image, recent_image, threshold=0.3, method="pixel_diff"):
    """
    检测两张无人机影像之间的建筑物变化
    
    参数:
        earlier_image: numpy 数组，早期影像
        recent_image: numpy 数组，近期影像
        threshold: float, 变化检测阈值
        method: str, 检测方法，可选 "pixel_diff"、"feature_matching" 或 "segmentation_comparison"
        
    返回:
        change_mask: numpy 数组，变化掩码
        changes_stats: dict, 变化统计信息
    """
    # 确保图像是 numpy 数组
    if isinstance(earlier_image, Image.Image):
        earlier_img = np.array(earlier_image)
    else:
        earlier_img = earlier_image.copy()
        
    if isinstance(recent_image, Image.Image):
        recent_img = np.array(recent_image)
    else:
        recent_img = recent_image.copy()
    
    # 确保两张图像大小相同
    if earlier_img.shape != recent_img.shape:
        recent_img = cv2.resize(recent_img, (earlier_img.shape[1], earlier_img.shape[0]))
    
    # 根据检测方法进行变化检测
    if method == "pixel_diff":
        # 简单的像素差异检测
        diff = cv2.absdiff(earlier_img, recent_img)
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
        _, change_mask = cv2.threshold(diff_gray, int(threshold * 255), 255, cv2.THRESH_BINARY)
        
    elif method == "feature_matching":
        # 基于特征匹配的变化检测（模拟实现）
        # 在实际应用中，这应该使用SIFT、SURF或ORB等特征检测和匹配算法
        diff = cv2.absdiff(earlier_img, recent_img)
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
        _, change_mask = cv2.threshold(diff_gray, int(threshold * 255), 255, cv2.THRESH_BINARY)
        
        # 应用形态学操作以减少噪声
        kernel = np.ones((5, 5), np.uint8)
        change_mask = cv2.morphologyEx(change_mask, cv2.MORPH_OPEN, kernel)
        change_mask = cv2.morphologyEx(change_mask, cv2.MORPH_CLOSE, kernel)
        
    else:  # segmentation_comparison
        # 基于分割结果比较的变化检测
        # 首先对两张图像进行分割
        earlier_mask, _, _ = segment_buildings(earlier_img)
        recent_mask, _, _ = segment_buildings(recent_img)
        
        # 比较分割掩码
        change_mask = cv2.absdiff(earlier_mask, recent_mask)
        _, change_mask = cv2.threshold(change_mask, 0, 255, cv2.THRESH_BINARY)
    
    # 计算变化统计信息
    changes_stats = calculate_change_statistics(change_mask, earlier_img.shape[:2])
    
    return change_mask, changes_stats


def calculate_change_statistics(change_mask, image_shape):
    """
    计算变化统计信息
    
    参数:
        change_mask: numpy 数组，变化掩码
        image_shape: tuple, 图像形状 (height, width)
        
    返回:
        stats: dict, 变化统计信息
    """
    # 计算变化区域的总面积
    change_area = np.sum(change_mask > 0)
    total_area = image_shape[0] * image_shape[1]
    change_percentage = (change_area / total_area) * 100
    
    # 找到变化区域的轮廓
    contours, _ = cv2.findContours(change_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 计算新建筑物和拆除建筑物的数量（模拟）
    num_contours = len(contours)
    new_buildings = num_contours // 2  # 模拟，实际应基于真实分析
    demolished_buildings = num_contours - new_buildings
    
    # 计算扩建区域和高度变化（模拟）
    extensions = max(0, num_contours // 3)
    height_changes = max(0, num_contours // 4)
    
    # 汇总统计信息
    stats = {
        "新建筑物": new_buildings,
        "拆除建筑物": demolished_buildings,
        "扩建区域": extensions,
        "高度变化": height_changes,
        "总变化面积": f"约 {change_area} 平方像素",
        "变化率": f"{change_percentage:.2f}%"
    }
    
    return stats


def visualize_changes(earlier_image, recent_image, change_mask, mode="highlight"):
    """
    可视化建筑物变化
    
    参数:
        earlier_image: numpy 数组，早期影像
        recent_image: numpy 数组，近期影像
        change_mask: numpy 数组，变化掩码
        mode: str, 可视化模式，可选 "highlight"、"contour" 或 "heatmap"
        
    返回:
        可视化后的图像 (numpy 数组)
    """
    # 确保图像是 numpy 数组
    if isinstance(recent_image, Image.Image):
        recent_img = np.array(recent_image)
    else:
        recent_img = recent_image.copy()
    
    # 根据可视化模式创建可视化图像
    if mode == "highlight":
        # 高亮显示变化区域
        viz_img = recent_img.copy()
        viz_img[change_mask > 0] = [255, 0, 0]  # 红色高亮变化区域
    elif mode == "contour":
        # 显示变化区域轮廓
        viz_img = recent_img.copy()
        contours, _ = cv2.findContours(change_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(viz_img, contours, -1, (0, 255, 0), 2)
    else:  # heatmap
        # 创建热力图
        viz_img = recent_img.copy()
        heatmap = cv2.applyColorMap(change_mask, cv2.COLORMAP_JET)
        viz_img = cv2.addWeighted(viz_img, 0.7, heatmap, 0.3, 0)
    
    return viz_img


def generate_change_report(earlier_image, recent_image, change_mask, changes_stats):
    """
    生成变化检测报告
    
    参数:
        earlier_image: numpy 数组，早期影像
        recent_image: numpy 数组，近期影像
        change_mask: numpy 数组，变化掩码
        changes_stats: dict, 变化统计信息
        
    返回:
        report_data: dict, 报告数据
    """
    # 生成变化可视化图像
    change_viz = visualize_changes(earlier_image, recent_image, change_mask, mode="highlight")
    
    # 找到变化区域的轮廓
    contours, _ = cv2.findContours(change_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 分析每个变化区域
    change_details = []
    for i, contour in enumerate(contours):
        # 计算轮廓的面积
        area = cv2.contourArea(contour)
        
        # 计算轮廓的边界框
        x, y, w, h = cv2.boundingRect(contour)
        
        # 确定变化类型（模拟）
        change_types = ["新建筑物", "拆除建筑物", "扩建区域", "高度变化"]
        change_type = change_types[i % len(change_types)]
        
        # 计算置信度（模拟）
        confidence = np.random.uniform(0.8, 0.98)
        
        # 确定位置描述
        if x < recent_image.shape[1] / 3:
            x_pos = "左侧"
        elif x < 2 * recent_image.shape[1] / 3:
            x_pos = "中央"
        else:
            x_pos = "右侧"
            
        if y < recent_image.shape[0] / 3:
            y_pos = "上方"
        elif y < 2 * recent_image.shape[0] / 3:
            y_pos = "中部"
        else:
            y_pos = "下方"
            
        position = f"图像{x_pos}{y_pos}"
        
        # 添加到变化详情列表
        change_details.append({
            "类型": change_type,
            "位置": position,
            "面积": f"约 {area:.0f} 平方像素",
            "置信度": f"{confidence:.0%}"
        })
    
    # 汇总报告数据
    report_data = {
        "变化统计": changes_stats,
        "变化详情": change_details,
        "变化可视化": change_viz
    }
    
    return report_data