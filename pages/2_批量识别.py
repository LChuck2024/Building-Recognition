import streamlit as st
import pandas as pd
from datetime import datetime
import time
from io import BytesIO
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
st.image(os.path.join(image_path,"batch_header.svg"), use_column_width=True)

# 页面标题
st.title("📑 批量建筑物识别")
st.markdown("同时上传多张图片进行批量识别处理")

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

# 批量处理选项
st.markdown("### ⚙️ 处理选项")
col1, col2 = st.columns(2)
with col1:
    process_mode = st.selectbox(
        "处理模式",
        options=["标准模式", "快速模式", "高精度模式"],
        help="选择不同的处理模式会影响识别的速度和准确度"
    )
with col2:
    save_results = st.checkbox(
        "保存识别结果",
        value=True,
        help="将识别结果保存到历史记录中"
    )

# 开始处理按钮
if uploaded_files:
    if st.button("🚀 开始批量处理", type="primary"):
        # 显示处理进度
        st.markdown("### 📊 处理进度")
        progress_container = st.empty()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 模拟批量处理过程
        total_files = len(uploaded_files)
        results = []
        
        for i, file in enumerate(uploaded_files):
            # 更新进度
            progress = (i + 1) / total_files
            progress_bar.progress(progress)
            status_text.text(f"正在处理: {file.name} ({i+1}/{total_files})")
            
            # 模拟处理延迟
            time.sleep(0.5)
            
            # 模拟识别结果
            results.append({
                '文件名': file.name,
                '建筑物类型': '办公楼',
                '置信度': 95,
                '处理时间': f"{0.5:.1f}秒"
            })
        
        # 显示处理完成信息
        st.success(f"✨ 批量处理完成！共处理 {total_files} 张图片")
        
        # 显示处理结果摘要
        st.markdown("### 📈 处理结果摘要")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class='summary-box'>
                <h3>总处理图片</h3>
                <h2>{}</h2>
            </div>
            """.format(total_files), unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class='summary-box'>
                <h3>平均置信度</h3>
                <h2>95%</h2>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class='summary-box'>
                <h3>总耗时</h3>
                <h2>{:.1f}秒</h2>
            </div>
            """.format(total_files * 0.5), unsafe_allow_html=True)
        
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
            # 使用ExcelWriter对象处理Excel导出
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
    st.info("👆 请先上传需要处理的图片")

# 添加页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>© 2025 城市建筑物识别系统 | 技术支持：AIE52期-5组</p>
</div>
""", unsafe_allow_html=True)