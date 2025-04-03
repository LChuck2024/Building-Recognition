import streamlit as st
import pandas as pd
# from datetime import datetime
import time
# from io import BytesIO
import os
from pathlib import Path

# 设置页面配置
st.set_page_config(
    page_title="批量建筑物识别 - 智能建筑物识别系统",
    page_icon="📑",
    layout="wide"
)

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
    
    .batch-upload-box {
        border: 2px dashed #0083B8;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        background: rgba(0,131,184,0.05);
        margin-bottom: 1.5rem;
    }
    .result-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .progress-container {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .summary-box {
        background: linear-gradient(45deg, #0083B8, #00A3E0);
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    /* 响应式布局 */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
        .batch-upload-box {
            padding: 1rem;
        }
        .result-card,
        .progress-container,
        .summary-box {
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

# 添加页眉图片
image_path = os.path.join(Path(__file__).parent.parent,"images")
st.image(os.path.join(image_path,"batch_header.svg"), use_container_width=True)

# 页面标题
st.title("📑 批量建筑物识别")
st.markdown("同时上传多张图片进行批量识别检测")

# 文件上传区域
st.markdown("### 📤 上传图片")

uploaded_files = st.file_uploader(
    "拖拽或选择多张建筑物图片，支持 .jpg、.jpeg、.png 格式",
    type=['jpg', 'jpeg', 'png'],
    accept_multiple_files=True
)
# 显示批量上传区域
# st.markdown("""
# <div class='batch-upload-box'>
#     <h4>拖拽或选择多张建筑物图片</h4>
#     <p>支持 .jpg、.jpeg、.png 格式</p>
# </div>
# """, unsafe_allow_html=True)

# 显示上传的图片预览
if uploaded_files:
    st.markdown("### 🖼️ 图片预览")
    # 创建图片网格布局
    num_cols = 5  # 每行显示的图片数量
    image_rows = [uploaded_files[i:i+num_cols] for i in range(0, len(uploaded_files), num_cols)]
    
    for row in image_rows:
        cols = st.columns(num_cols)
        for i, image_file in enumerate(row):
            with cols[i]:
                # 显示图片,设置图片高度为200像素
                st.image(image_file, caption=image_file.name,use_container_width=True)
                # 添加文件名标签
                # st.markdown(f"<p style='text-align: center; font-size: 0.8rem;'>{image_file.name}</p>", unsafe_allow_html=True)

# 批量检测选项
st.markdown("### ⚙️ 检测选项")
col1, col2 = st.columns(2)
with col1:
    # 初始化或恢复session_state中的设置
    if 'process_mode' not in st.session_state:
        st.session_state.process_mode = "标准模式"
    if 'save_results' not in st.session_state:
        st.session_state.save_results = True
    if 'enable_segmentation' not in st.session_state:
        st.session_state.enable_segmentation = True
    if 'segmentation_method' not in st.session_state:
        st.session_state.segmentation_method = "实例分割"
    if 'visualization_mode' not in st.session_state:
        st.session_state.visualization_mode = "掩码叠加"
    if 'export_masks' not in st.session_state:
        st.session_state.export_masks = True
        
    process_mode = st.selectbox(
        "检测模式",
        options=["标准模式", "快速模式", "高精度模式", "无人机影像专用模式"],
        help="选择不同的检测模式会影响识别的速度和准确度",
        index=["标准模式", "快速模式", "高精度模式", "无人机影像专用模式"].index(st.session_state.process_mode),
        on_change=lambda: setattr(st.session_state, 'process_mode', process_mode)
    )
    
    if process_mode == "无人机影像专用模式":
        st.info("无人机影像专用模式针对低空影像特点进行了优化，可以更好地识别建筑物。")
    
with col2:
    save_results = st.checkbox(
        "保存识别结果",
        value=st.session_state.save_results,
        help="将识别结果保存到历史记录中",
        on_change=lambda: setattr(st.session_state, 'save_results', save_results)
    )

# 添加分割选项
st.markdown("#### 分割选项")
seg_col1, seg_col2 = st.columns(2)

with seg_col1:
    enable_segmentation = st.checkbox(
        "启用建筑物分割",
        value=st.session_state.enable_segmentation,
        help="对每张图片进行建筑物分割，生成分割掩码",
        on_change=lambda: setattr(st.session_state, 'enable_segmentation', enable_segmentation)
    )
    
    if enable_segmentation:
        segmentation_method = st.selectbox(
            "分割方法",
            options=["语义分割", "实例分割", "全景分割"],
            index=["语义分割", "实例分割", "全景分割"].index(st.session_state.segmentation_method),
            help="不同的分割方法适用于不同场景",
            on_change=lambda: setattr(st.session_state, 'segmentation_method', segmentation_method)
        )

with seg_col2:
    if enable_segmentation:
        visualization_mode = st.selectbox(
            "可视化模式",
            options=["轮廓显示", "掩码叠加", "区域填充", "不显示"],
            index=["轮廓显示", "掩码叠加", "区域填充", "不显示"].index(st.session_state.visualization_mode),
            help="选择分割结果的可视化方式",
            on_change=lambda: setattr(st.session_state, 'visualization_mode', visualization_mode)
        )
        
        export_masks = st.checkbox(
            "导出分割掩码",
            value=st.session_state.export_masks,
            help="将分割掩码作为单独的文件导出",
            on_change=lambda: setattr(st.session_state, 'export_masks', export_masks)
        )

# 开始检测按钮
if uploaded_files:
    if st.button("🚀 开始批量检测", type="primary"):
        # 显示检测进度
        st.markdown("### 📊 检测进度")
        progress_container = st.empty()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 初始化YOLO检测器
        from utils.yolo_detector import YOLODetector
        detector = YOLODetector()
        
        total_files = len(uploaded_files)
        results = []
        
        # 使用横向布局显示检测后的图片
        st.markdown("### 🖼️ 检测结果预览[前5张]")
        result_cols = st.columns(5)  # 创建5列布局

        for i, file in enumerate(uploaded_files):
            start_time = time.time()
            
            # 更新进度
            progress = (i + 1) / total_files
            progress_bar.progress(progress)
            status_text.text(f"正在检测: {file.name} ({i+1}/{total_files})")
            
            try:
                # 执行检测
                detections, plotted_image = detector.detect(file)
                
                # 获取最高置信度的检测结果
                if detections:
                    best_detection = max(detections, key=lambda x: x['confidence'])
                    confidence = round(best_detection['confidence'] * 100, 1)
                    building_type = best_detection['label']
                else:
                    confidence = 0
                    building_type = '未检测到建筑物'
                
                # 计算检测时间
                process_time = time.time() - start_time
                
                # 保存结果
                results.append({
                    '文件名': file.name,
                    '建筑物类型': building_type,
                    '置信度': confidence,
                    '检测时间': f"{process_time:.1f}秒"
                })
                
                # 显示检测后的图片
                if i < 5:  # 只显示前5张图片的检测结果
                    with result_cols[i]:
                        st.image(plotted_image, caption=f"检测结果: {file.name}", use_container_width=True)
                    
            except Exception as e:
                st.error(f"检测文件 {file.name} 时出错: {str(e)}")
                continue
        
        # 显示检测完成信息
        st.success(f"✨ 批量检测完成！共检测 {total_files} 张图片")
        
        # 显示检测结果摘要
        st.markdown("### 📈 检测结果摘要")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class='summary-box'>
                <h3>总检测图片</h3>
                <h2>{}</h2>
            </div>
            """.format(total_files), unsafe_allow_html=True)
        with col2:
            avg_confidence = sum(result['置信度'] for result in results) / len(results) if results else 0
            st.markdown("""
            <div class='summary-box'>
                <h3>平均置信度</h3>
                <h2>{:.1f}%</h2>
            </div>
            """.format(avg_confidence), unsafe_allow_html=True)
        with col3:
            total_time = sum(float(result['检测时间'].replace('秒', '')) for result in results)
            st.markdown("""
            <div class='summary-box'>
                <h3>总耗时</h3>
                <h2>{:.1f}秒</h2>
            </div>
            """.format(total_time), unsafe_allow_html=True)
        
        # 显示详细结果
        st.markdown("### 📋 详细结果")
        results_df = pd.DataFrame(results)
        st.dataframe(results_df, use_container_width=True)
        
        # 导出选项
        st.markdown("### 📥 导出结果")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="下载CSV报告",
                data=results_df.to_csv(index=False).encode('utf-8'),
                file_name='batch_recognition_results.csv',
                mime='text/csv'
            )
        with col2:
            # 使用ExcelWriter对象检测Excel导出
            with pd.ExcelWriter('batch_recognition_results.xlsx', engine='openpyxl') as writer:
                results_df.to_excel(writer, index=False)
                # ExcelWriter会自动保存，不需要显式调用save()
            with open('batch_recognition_results.xlsx', 'rb') as f:
                excel_data = f.read()
            st.download_button(
                label="下载Excel报告",
                data=excel_data,
                file_name='batch_recognition_results.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
else:
    st.info("👆 请先上传需要检测的图片")

# 添加页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>© 2025 城市建筑物识别系统 | 技术支持：AIE52期-5组</p>
</div>
""", unsafe_allow_html=True)