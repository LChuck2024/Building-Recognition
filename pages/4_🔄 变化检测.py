import streamlit as st
from PIL import Image
import numpy as np
from pathlib import Path
import time
import os
import pandas as pd
import cv2
cv2.setUseOptimized(True)
cv2.setNumThreads(4)

from utils.db_manager import DBManager
from utils.model_detector import ModelDetector
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim


# 设置页面配置
st.set_page_config(
    page_title="建筑物变化检测 - 城市建筑物检测系统",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加页眉图片
image_path = os.path.join(Path(__file__).parent.parent,"images")
st.image(os.path.join(image_path,"change_header.svg"), use_container_width=True)

# 自定义CSS样式
st.markdown("""
<style>
    /* 全局样式 */
    .main {
        padding: 1rem;
        width: 100%;
        max-width: 100%;
        margin: 0 auto;
        box-sizing: border-box;
    }
    body {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 16px;
        line-height: 1.5;
    }
    
    /* 响应式容器 */
    .container {
        width: 100%;
        padding-right: 15px;
        padding-left: 15px;
        margin-right: auto;
        margin-left: auto;
    }
    
    /* 图片圆角样式 */
    img {
        border-radius: 12px;
        max-width: 100%;
        height: auto;
    }
    
    /* 按钮样式 */
    .stButton>button {
        width: 100%;
        background: linear-gradient(45deg, #0083B8, #00A3E0);
        color: white;
        border: none;
        padding: 0.8rem;
        border-radius: 8px;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #00669E, #0083B8);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* 上传区域样式 */
    .upload-box {
        border: 2px dashed #ccc;
        padding: 1.5rem;
        text-align: center;
        border-radius: 12px;
        background: #ffffff;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin: 1rem 0;
    }
    .upload-box:hover {
        border-color: #0083B8;
        box-shadow: 0 4px 12px rgba(0,131,184,0.1);
    }
    
    /* 结果区域样式 */
    .result-box {
        background: linear-gradient(to bottom right, #ffffff, #f8f9fa);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        margin: 1rem 0;
    }
    .result-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }
    
    /* 变化检测结果样式 */
    .change-highlight {
        background-color: rgba(255, 87, 51, 0.2);
        border-left: 4px solid #FF5733;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    
    .no-change {
        background-color: rgba(46, 204, 113, 0.2);
        border-left: 4px solid #2ECC71;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    
    /* 图像对比容器 */
    .comparison-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .image-pair {
        display: flex;
        gap: 1rem;
        align-items: center;
    }
    
    .image-card {
        flex: 1;
        background: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .change-indicator {
        background: #FF5733;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        display: inline-block;
        margin-top: 0.5rem;
    }
    
    /* 响应式布局 */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
        .upload-box {
            padding: 1rem;
        }
        .result-box {
            padding: 1rem;
        }
        h1 {
            font-size: 1.8rem;
        }
        h2 {
            font-size: 1.5rem;
        }
        h3 {
            font-size: 1.2rem;
        }
        .image-pair {
            flex-direction: column;
        }
    }
    
    /* 弹性布局容器 */
    .flex-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin: 1rem 0;
    }
    .flex-item {
        flex: 1;
        min-width: 250px;
    }
</style>
""", unsafe_allow_html=True)

# 侧边栏设置
with st.sidebar:
    st.markdown("### 检测设置")
    
    # 初始化或恢复session_state中的设置
    if 'confidence_threshold' not in st.session_state:
        st.session_state.confidence_threshold = 0.5
    if 'model_name' not in st.session_state:
        st.session_state.model_name = 'yolo11n.pt'

    # 获取model目录下的所有模型文件
    model_dir = Path(__file__).parent.parent / 'model'
    model_files = list(model_dir.glob('*.pt')) + list(model_dir.glob('*.pth'))
    model_files = [f.name for f in model_files]
    
    if not model_files:
        st.error("未找到可用的模型文件，请确保model目录中存在.pt或.pth格式的模型文件")
        model_files = ['yolo11n.pt']  # 设置默认值
    
    model_name = st.selectbox(
        "选择模型",
        options=model_files,
        help="选择不同的预训练模型进行检测",
        on_change=lambda: setattr(st.session_state, 'model_name', model_name)
    )

    print(f'页面选择模型：{model_name}')
    
    confidence_threshold = st.slider(
        "置信度阈值",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.get('confidence_threshold', 0.5),
        help="调整检测的置信度阈值，值越高要求越严格",
        on_change=lambda: setattr(st.session_state, 'confidence_threshold', confidence_threshold)
    )
    
    detection_threshold = st.slider(
        "变化检测阈值", 
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        help="调整变化检测的敏感度，值越低对变化越敏感"
    )
    
    visualization_mode = st.selectbox(
        "可视化模式",
        options=["变化区域高亮", "变化区域轮廓", "变化热力图"],
        index=0,
        help="选择不同的可视化方式来展示变化区域"
    )
    

# 主页面标题和介绍
st.title("🔄 建筑物变化检测")
st.markdown("上传不同时期的建筑物影像，自动检测并标记变化区域")

# 创建两列布局用于上传图片
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📤 早期影像上传")
    earlier_image = st.file_uploader("选择早期影像", type=['jpg', 'jpeg', 'png'], key="earlier_image")
    
    if earlier_image is not None:
        st.image(earlier_image, caption="早期影像预览", use_container_width=True)

with col2:
    st.markdown("### 📤 近期影像上传")
    recent_image = st.file_uploader("选择近期影像", type=['jpg', 'jpeg', 'png'], key="recent_image")
    
    if recent_image is not None:
        st.image(recent_image, caption="近期影像预览", use_container_width=True)

# 检测选项
st.markdown("### ⚙️ 检测选项")
options_col1, options_col2, options_col3 = st.columns(3)

with options_col1:
    detect_new_buildings = st.checkbox("检测新建筑", value=True)
with options_col2:
    detect_demolished = st.checkbox("检测拆除建筑", value=True)
with options_col3:
    detect_extensions = st.checkbox("检测建筑扩建", value=True)

# 开始检测按钮
if earlier_image is not None and recent_image is not None:
    if st.button("🔍 开始变化检测", type="primary"):
        with st.spinner('正在进行建筑物变化检测分析...'):
            # 显示进度条
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.03)
                progress_bar.progress(i + 1)
            
            # 初始化模型检测器
            detector = ModelDetector(model_name)
            
            # 对早期和近期图片进行建筑物检测
            earlier_detections, earlier_viz = detector.detect(earlier_image, conf_thres=confidence_threshold)
            recent_detections, recent_viz = detector.detect(recent_image, conf_thres=confidence_threshold)
            
            # 计算变化统计信息
            total_change_area = 0
            significant_changes = []
            
            # 设置变化检测的阈值
            area_change_threshold = 0.3  # 面积变化阈值
            position_change_threshold = 20  # 位置变化阈值（像素）
            
            # 计算IOU函数
            def calculate_iou(box1, box2):
                # box格式: [x1, y1, x2, y2]
                x1_1, y1_1, x2_1, y2_1 = box1
                x1_2, y1_2, x2_2, y2_2 = box2
                
                # 计算交集区域的坐标
                x1_i = max(x1_1, x1_2)
                y1_i = max(y1_1, y1_2)
                x2_i = min(x2_1, x2_2)
                y2_i = min(y2_1, y2_2)
                
                # 如果没有交集，返回0
                if x2_i < x1_i or y2_i < y1_i:
                    return 0.0
                
                # 计算交集面积
                intersection = (x2_i - x1_i) * (y2_i - y1_i)
                
                # 计算两个框的面积
                area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
                area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
                
                # 计算并集面积
                union = area1 + area2 - intersection
                
                # 返回IOU
                return intersection / union if union > 0 else 0.0
            
            # 将检测结果转换为列表，包含更多信息
            earlier_buildings = []
            recent_buildings = []
            
            for det in earlier_detections:
                if 'bbox' in det:
                    bbox = det['bbox']
                    area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                    center = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
                    earlier_buildings.append({
                        'bbox': bbox,
                        'area': area,
                        'center': center,
                        'confidence': det.get('confidence', 0.0)
                    })
            
            for det in recent_detections:
                if 'bbox' in det:
                    bbox = det['bbox']
                    area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                    center = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
                    recent_buildings.append({
                        'bbox': bbox,
                        'area': area,
                        'center': center,
                        'confidence': det.get('confidence', 0.0)
                    })
            
            # 分析变化
            # 使用IOU阈值判断建筑物变化
            iou_threshold = detection_threshold  # 使用用户设置的检测阈值
            
            # 标记已匹配的建筑物
            matched_earlier = [False] * len(earlier_buildings)
            matched_recent = [False] * len(recent_buildings)
            
            # 检查每个近期建筑物
            for i, recent_building in enumerate(recent_buildings):
                best_iou = 0
                best_match = -1
                
                # 寻找最佳匹配的早期建筑物
                for j, earlier_building in enumerate(earlier_buildings):
                    if not matched_earlier[j]:
                        iou = calculate_iou(recent_building['bbox'], earlier_building['bbox'])
                        # 计算中心点距离
                        dx = recent_building['center'][0] - earlier_building['center'][0]
                        dy = recent_building['center'][1] - earlier_building['center'][1]
                        center_distance = np.sqrt(dx*dx + dy*dy)
                        
                        # 综合考虑IOU和中心点距离
                        if iou > best_iou and center_distance < position_change_threshold:
                            best_iou = iou
                            best_match = j
                
                # 根据IOU值和其他指标判断变化类型
                if best_iou > iou_threshold:
                    matched_recent[i] = True
                    matched_earlier[best_match] = True
                    
                    # 计算面积变化
                    area_change = recent_building['area'] - earlier_buildings[best_match]['area']
                    area_change_ratio = abs(area_change) / earlier_buildings[best_match]['area']
                    
                    # 计算位置变化
                    dx = recent_building['center'][0] - earlier_buildings[best_match]['center'][0]
                    dy = recent_building['center'][1] - earlier_buildings[best_match]['center'][1]
                    position_change = np.sqrt(dx*dx + dy*dy)
                    
                    # 综合判断变化
                    if area_change_ratio > area_change_threshold:
                        total_change_area += abs(area_change)
                        change_type = "扩建区域" if area_change > 0 else "建筑缩小"
                        significant_changes.append({
                            "类型": change_type,
                            "位置": f"({int(recent_building['center'][0])}, {int(recent_building['center'][1])})",
                            "面积变化": f"约 {int(abs(area_change))} 平方像素",
                            "变化比例": f"{int(area_change_ratio * 100)}%",
                            "位置偏移": f"{int(position_change)} 像素",
                            "置信度": f"{int(recent_building['confidence'] * 100)}%"
                        })
            
            # 处理未匹配的建筑物（新建和拆除）
            for i, recent_building in enumerate(recent_buildings):
                if not matched_recent[i]:
                    # 新建筑
                    total_change_area += recent_building['area']
                    significant_changes.append({
                        "类型": "新建筑物",
                        "位置": f"({int(recent_building['center'][0])}, {int(recent_building['center'][1])})",
                        "面积": f"约 {int(recent_building['area'])} 平方像素",
                        "置信度": f"{int(recent_building['confidence'] * 100)}%"
                    })
            
            for i, earlier_building in enumerate(earlier_buildings):
                if not matched_earlier[i]:
                    # 拆除的建筑
                    total_change_area += earlier_building['area']
                    significant_changes.append({
                        "类型": "拆除建筑物",
                        "位置": f"({int(earlier_building['center'][0])}, {int(earlier_building['center'][1])})",
                        "面积": f"约 {int(earlier_building['area'])} 平方像素",
                        "置信度": f"{int(earlier_building['confidence'] * 100)}%"
                    })
            
            # 创建基于模型检测框的变化可视化图像
            if visualization_mode == "变化区域高亮":
                change_viz = recent_viz.copy()
                for det in recent_detections:
                    if 'bbox' in det:
                        x1, y1, x2, y2 = map(int, det['bbox'])
                        cv2.rectangle(change_viz, (x1, y1), (x2, y2), (255, 0, 0), 3)
            
            elif visualization_mode == "变化区域轮廓":
                change_viz = recent_viz.copy()
                for det in recent_detections:
                    if 'bbox' in det:
                        x1, y1, x2, y2 = map(int, det['bbox'])
                        cv2.rectangle(change_viz, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            else:  # 变化热力图
                change_viz = recent_viz.copy()
                heatmap = np.zeros((change_viz.shape[0], change_viz.shape[1]), dtype=np.uint8)
                for det in recent_detections:
                    if 'bbox' in det:
                        x1, y1, x2, y2 = map(int, det['bbox'])
                        cv2.rectangle(heatmap, (x1, y1), (x2, y2), 255, -1)
                heatmap = cv2.GaussianBlur(heatmap, (21, 21), 0)
                heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
                change_viz = cv2.addWeighted(change_viz, 0.7, heatmap, 0.3, 0)
            
            # 获取图片尺寸并统一化
            earlier_img = Image.open(earlier_image)
            recent_img = Image.open(recent_image)
            
            # 统一图片尺寸为较大的那个尺寸
            target_size = (max(earlier_img.size[0], recent_img.size[0]), max(earlier_img.size[1], recent_img.size[1]))
            earlier_img = earlier_img.resize(target_size, Image.Resampling.LANCZOS)
            recent_img = recent_img.resize(target_size, Image.Resampling.LANCZOS)
            
            # 转换为numpy数组以便进行OpenCV操作
            earlier_array = np.array(earlier_img)
            recent_array = np.array(recent_img)
            
            # 计算平均变化强度
            intensity_diff = 0
            if significant_changes:
                intensity_diff = total_change_area / len(significant_changes)
            
            # 统计检测结果
            changes_detected = {
                "新建筑物": len([c for c in significant_changes if c["类型"] == "新建筑物"]),
                "拆除建筑物": len([c for c in significant_changes if c["类型"] == "拆除建筑物"]),
                "扩建区域": len([c for c in significant_changes if c["类型"] == "扩建区域"]),
                "总变化面积": f"约 {int(total_change_area)} 平方像素",
                "变化率": f"{min(100.0, (total_change_area / (target_size[0] * target_size[1]) * 100)):.1f}%"
            }
            
            st.success("✨ 变化检测完成！")
            
            # 显示检测结果
            st.markdown("### 🔍 检测结果")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 早期图像检测结果") 
                st.image(earlier_viz, use_container_width=True)
            with col2:
                st.markdown("#### 近期图像检测结果")
                st.image(recent_viz, use_container_width=True)
                
            # 保存历史记录
            try:
                # 定义图片路径变量
                earlier_image_path = os.path.join('data/detection_results', f'{int(time.time())}_earlier.jpg')
                recent_image_path = os.path.join('data/detection_results', f'{int(time.time())}_recent.jpg')
                
                # 保存图片到本地
                earlier_img.save(earlier_image_path)
                recent_img.save(recent_image_path)
                
                # 确定主要变化类型
                change_type = "混合变化"
                if changes_detected["新建筑物"] > 0 and changes_detected["拆除建筑物"] == 0 and changes_detected["扩建区域"] == 0:
                    change_type = "新增建筑"
                elif changes_detected["拆除建筑物"] > 0 and changes_detected["新建筑物"] == 0 and changes_detected["扩建区域"] == 0:
                    change_type = "拆除建筑"
                elif changes_detected["扩建区域"] > 0 and changes_detected["新建筑物"] == 0 and changes_detected["拆除建筑物"] == 0:
                    change_type = "建筑扩建"
                
                earlier_confidence = earlier_detections[0]['confidence'] if earlier_detections else 0.5
                recent_confidence = recent_detections[0]['confidence'] if recent_detections else 0.5

                db = DBManager()
                db.add_change_detection(
                    earlier_image_path=str(earlier_image_path),
                    recent_image_path=str(recent_image_path), 
                    change_type=change_type,
                    change_area=total_change_area,
                    confidence = (earlier_confidence + recent_confidence) / 2,
                    detection_result={
                        'changes_detected': changes_detected,
                        'significant_changes': significant_changes,
                        'visualization_mode': visualization_mode
                    }
                )
            except Exception as e:
                st.warning(f"保存历史记录失败: {str(e)}")

            # 显示变化统计
            st.markdown("#### 变化统计") 
            stats_col1, stats_col2 = st.columns(2)
            
            with stats_col1:
                st.metric("检测到的新建筑物", changes_detected["新建筑物"])
                st.metric("检测到的拆除建筑物", changes_detected["拆除建筑物"])
                st.metric("检测到的扩建区域", changes_detected["扩建区域"])
            
            with stats_col2:
                st.metric("总变化面积", changes_detected["总变化面积"])
                st.metric("变化率", changes_detected["变化率"])
            
            # 显示变化可视化
            st.markdown("#### 变化可视化")
            
            viz_col1, viz_col2, viz_col3 = st.columns([1, 1, 1])
            
            with viz_col1:
                st.image(earlier_img, caption="早期影像", use_container_width=True)
            
            with viz_col2:
                st.image(recent_img, caption="近期影像", use_container_width=True)
            
            with viz_col3:
                st.image(Image.fromarray(change_viz), caption="变化检测结果", use_container_width=True)
            
            # 显示详细变化列表
            st.markdown("#### 详细变化列表")
            
            # 从实际检测结果生成变化详情数据
            changes_data = []
            try:
                # 获取变化区域的轮廓
                earlier_gray = cv2.cvtColor(np.array(earlier_img), cv2.COLOR_BGR2GRAY)
                recent_gray = cv2.cvtColor(np.array(recent_img), cv2.COLOR_BGR2GRAY)
                diff = cv2.absdiff(earlier_gray, recent_gray)
                _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 100:  # 过滤小区域
                        x, y, w, h = cv2.boundingRect(contour)
                        earlier_region = earlier_gray[y:y+h, x:x+w]
                        recent_region = recent_gray[y:y+h, x:x+w]
                        intensity_diff = np.mean(recent_region) - np.mean(earlier_region)
                        
                        # 根据实际检测结果确定变化类型
                        change_type = "扩建区域"
                        if intensity_diff > 50:
                            change_type = "新建筑物"
                        elif intensity_diff < -50:
                            change_type = "拆除建筑物"
                        
                        # 计算置信度
                        confidence = int((1 - abs(intensity_diff)/255) * 100)
                        
                        changes_data.append({
                            "类型": change_type,
                            "位置": f"({x}, {y})",
                            "面积": f"约 {int(area)} 平方像素",
                            "置信度": f"{confidence}%"
                        })
            except Exception as e:
                st.error(f"处理变化详情时发生错误: {str(e)}")
                changes_data = []  # 发生错误时使用空列表
            
            # 创建DataFrame并显示
            changes_df = pd.DataFrame(changes_data)
            st.dataframe(changes_df, use_container_width=True)
            
            # 提供导出选项
            st.markdown("#### 导出结果")
            export_col1, export_col2 = st.columns(2)
            
            with export_col1:
                st.download_button(
                    label="📊 导出变化数据 (CSV)",
                    data=changes_df.to_csv(index=False).encode('utf-8'),
                    file_name="building_changes.csv",
                    mime="text/csv"
                )
            
            with export_col2:
                # 在实际应用中，这里应该生成一个包含所有结果的PDF报告
                st.download_button(
                    label="📑 导出完整报告 (PDF)",
                    data="模拟PDF报告数据",  # 实际应用中应该是真实的PDF数据
                    file_name="change_detection_report.pdf",
                    mime="application/pdf"
                )

# 添加页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>© 2025 城市建筑物检测系统 | 技术支持：AIE52期-5组</p>
</div>
""", unsafe_allow_html=True)
