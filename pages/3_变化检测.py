import streamlit as st
# import torch
from PIL import Image
import numpy as np
from pathlib import Path
import time
import os
import pandas as pd
import cv2
cv2.setUseOptimized(True)
cv2.setNumThreads(4)


# 设置页面配置
st.set_page_config(
    page_title="建筑物变化检测 - 城市建筑物识别系统",
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
    st.title("变化检测设置")
    st.markdown("### 检测参数")
    
    detection_threshold = st.slider(
        "变化检测阈值", 
        min_value=0.1, 
        max_value=1.0, 
        value=0.3, 
        step=0.05,
        help="降低阈值可以检测更细微的变化，提高阈值则只检测显著变化"
    )
    
    detection_method = st.selectbox(
        "检测方法",
        options=["像素差异检测", "特征匹配检测", "语义分割比对"],
        index=2,
        help="不同的检测方法适用于不同的场景"
    )
    
    visualization_mode = st.radio(
        "可视化模式",
        options=["变化区域高亮", "变化区域轮廓", "变化热力图"],
        index=0
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
options_col1, options_col2 = st.columns(2)

with options_col1:
    detect_new_buildings = st.checkbox("检测新建筑", value=True)
    detect_demolished = st.checkbox("检测拆除建筑", value=True)

with options_col2:
    detect_extensions = st.checkbox("检测建筑扩建", value=True)
    detect_height_changes = st.checkbox("检测高度变化", value=True)

# 开始检测按钮
if earlier_image is not None and recent_image is not None:
    if st.button("🔍 开始变化检测", type="primary"):
        with st.spinner('正在进行建筑物变化检测分析...'):
            # 显示进度条
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.03)
                progress_bar.progress(i + 1)
            
            # 加载和预处理图像
            earlier_img = Image.open(earlier_image)
            recent_img = Image.open(recent_image)
            
            # 确保两张图片大小一致
            target_size = (800, 800)  # 设置统一的目标大小
            earlier_img = earlier_img.resize(target_size)
            recent_img = recent_img.resize(target_size)
            
            # 转换为numpy数组
            earlier_array = np.array(earlier_img)
            recent_array = np.array(recent_img)
            
            # 转换为灰度图像
            earlier_gray = cv2.cvtColor(earlier_array, cv2.COLOR_RGB2GRAY)
            recent_gray = cv2.cvtColor(recent_array, cv2.COLOR_RGB2GRAY)
            
            # 应用高斯模糊减少噪声
            earlier_blur = cv2.GaussianBlur(earlier_gray, (5, 5), 0)
            recent_blur = cv2.GaussianBlur(recent_gray, (5, 5), 0)
            
            # 计算差异图
            diff = cv2.absdiff(earlier_blur, recent_blur)
            
            # 应用阈值处理
            threshold = int(detection_threshold * 255)
            _, change_mask = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
            
            # 应用形态学操作来减少噪声和连接相近区域
            kernel = np.ones((5,5), np.uint8)
            change_mask = cv2.morphologyEx(change_mask, cv2.MORPH_CLOSE, kernel)
            change_mask = cv2.morphologyEx(change_mask, cv2.MORPH_OPEN, kernel)
            
            # 查找变化区域的轮廓
            contours, _ = cv2.findContours(change_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 计算变化统计信息
            total_change_area = 0
            significant_changes = []
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # 过滤掉太小的变化区域
                    x, y, w, h = cv2.boundingRect(contour)
                    total_change_area += area
                    
                    # 分析变化类型
                    earlier_region = earlier_gray[y:y+h, x:x+w]
                    recent_region = recent_gray[y:y+h, x:x+w]
                    intensity_diff = np.mean(recent_region) - np.mean(earlier_region)
                    
                    change_type = "扩建区域"
                    if intensity_diff > 50:
                        change_type = "新建筑物"
                    elif intensity_diff < -50:
                        change_type = "拆除建筑物"
                    
                    significant_changes.append({
                        "类型": change_type,
                        "位置": f"({x}, {y})",
                        "面积": f"约 {int(area)} 平方像素",
                        "置信度": f"{int((1 - abs(intensity_diff)/255) * 100)}%"
                    })
            
            # 创建变化可视化图像
            if visualization_mode == "变化区域高亮":
                change_viz = recent_array.copy()
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 100:
                        mask = np.zeros_like(recent_array, dtype=np.uint8)
                        cv2.drawContours(mask, [contour], -1, (255, 255, 255), -1)
                        change_viz[mask > 0] = [255, 0, 0]  # 红色高亮
            
            elif visualization_mode == "变化区域轮廓":
                change_viz = recent_array.copy()
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 100:
                        cv2.drawContours(change_viz, [contour], -1, (0, 255, 0), 2)
            
            else:  # 变化热力图
                change_viz = recent_array.copy()
                heatmap = np.zeros_like(change_mask, dtype=np.uint8)  # 确保数据类型为uint8
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 100:
                        cv2.drawContours(heatmap, [contour], -1, (255,), thickness=cv2.FILLED)  # 修改参数设置
                heatmap = cv2.GaussianBlur(heatmap, (21, 21), 0)
                heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
                change_viz = cv2.addWeighted(change_viz, 0.7, heatmap, 0.3, 0)
            
            # 统计检测结果
            changes_detected = {
                "新建筑物": len([c for c in significant_changes if c["类型"] == "新建筑物"]),
                "拆除建筑物": len([c for c in significant_changes if c["类型"] == "拆除建筑物"]),
                "扩建区域": len([c for c in significant_changes if c["类型"] == "扩建区域"]),
                "高度变化": 0,  # 需要额外的3D数据才能检测高度变化
                "总变化面积": f"约 {int(total_change_area)} 平方像素",
                "变化率": f"{(total_change_area / (target_size[0] * target_size[1]) * 100):.1f}%"
            }
            
            st.success("✨ 变化检测完成！")
            
            # 显示检测结果
            st.markdown("### 📊 检测结果")
            
            # 显示变化统计
            st.markdown("#### 变化统计")
            stats_col1, stats_col2 = st.columns(2)
            
            with stats_col1:
                st.metric("检测到的新建筑物", changes_detected["新建筑物"])
                st.metric("检测到的拆除建筑物", changes_detected["拆除建筑物"])
                st.metric("检测到的扩建区域", changes_detected["扩建区域"])
            
            with stats_col2:
                st.metric("检测到的高度变化", changes_detected["高度变化"])
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
    <p>© 2025 城市建筑物识别系统 | 技术支持：AIE52期-5组</p>
</div>
""", unsafe_allow_html=True)