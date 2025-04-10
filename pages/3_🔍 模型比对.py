from re import S
import streamlit as st
import time
import pandas as pd
import plotly.express as px
import os
from pathlib import Path
from utils.model_detector import ModelDetector
from PIL import Image
import json

st.set_page_config(
    page_title="多模型比对",
    page_icon="🔍",
    layout="wide"
)

# 自定义CSS样式
st.markdown("""
<style>
    h3 {
        font-size: 1.0rem !important;
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
</style>
""", unsafe_allow_html=True)

# 添加页眉图片
image_path = os.path.join(Path(__file__).parent.parent,"images")
st.image(os.path.join(image_path,"comparison_header.svg"), use_container_width=True)


st.title("🔍 多模型比对")
st.write("同时使用多个模型进行检测并比对结果")

model_dir = Path(__file__).parent.parent / 'model'
model_files = list(model_dir.glob('*.pt')) + list(model_dir.glob('*.pth'))
model_options = [f.name for f in model_files]

# 模型选择
selected_models = st.multiselect(
    "选择要比较的模型",
    model_options,
    default=["build-12s.pt", "build_V8n.pt"]
)

if not selected_models:
    st.warning("请至少选择一个模型")
    st.stop()

# 图片上传
uploaded_file = st.file_uploader(
    "上传待检测图片",
    type=["jpg", "jpeg", "png"]
)

# 开始检测按钮
start_detect = st.button("🔍 开始模型比对", type="primary")

# 检查是否有上传图片
if start_detect and not uploaded_file:
    st.warning("⚠️ 请先上传需要检测的图片")
    st.stop()

# 检查是否有上传图片
if start_detect and uploaded_file:
    # 加载图片
    image = Image.open(uploaded_file)

    # 创建多列布局
    cols = st.columns(len(selected_models))

    # 性能指标收集
    performance_data = []

    # 并行检测
    for i, model_name in enumerate(selected_models):
        with cols[i]:
            st.subheader(model_name.split('.')[0])
            
            try:
                # 初始化模型
                start_time = time.time()
                detector = ModelDetector(model_name)
                load_time = time.time() - start_time
                
                # 执行检测
                start_time = time.time()
                detections, plotted_image = detector.detect(image)
                detect_time = time.time() - start_time
                
                # 显示结果
                st.image(plotted_image, use_container_width=True)
                
                # 记录性能指标
                performance_data.append({
                    "模型": model_name,
                    "加载时间(秒)": round(load_time, 3),
                    "检测时间(秒)": round(detect_time, 3),
                    "检测数量": len(detections)
                })
                
                # 显示检测信息
                st.write(f"检测到 {len(detections)} 个建筑物")
                st.write(f"加载时间: {round(load_time, 3)}秒")
                st.write(f"检测时间: {round(detect_time, 3)}秒")
                
            except Exception as e:
                st.error(f"模型 {model_name} 加载失败: {str(e)}")

    # 性能对比图表
    if performance_data:
        st.subheader("性能对比")
        df = pd.DataFrame(performance_data)
        
        # 创建三列布局
        col1, col2, col3 = st.columns(3)
        
        # 加载时间对比
        fig1 = px.bar(
            df, 
            x="模型", 
            y="加载时间(秒)", 
            title="模型加载时间对比"
        )
        with col1:
            st.plotly_chart(fig1, use_container_width=True)
        
        # 检测时间对比
        fig2 = px.bar(
            df, 
            x="模型", 
            y="检测时间(秒)", 
            title="检测时间对比"
        )
        with col2:
            st.plotly_chart(fig2, use_container_width=True)
        
        # 检测数量对比
        fig3 = px.bar(
            df, 
            x="模型", 
            y="检测数量", 
            title="检测数量对比"
        )
        with col3:
            st.plotly_chart(fig3, use_container_width=True)
            
        # 保存历史记录
        from utils.db_manager import DBManager
        db = DBManager()
        
        # 保存图片到临时文件
        temp_dir = Path(__file__).parent.parent / "temp"
        temp_dir.mkdir(exist_ok=True)
        image_path = str(temp_dir / f"comparison_{int(time.time())}.jpg")
        image.save(image_path)
        
        # 保存记录
        try:
            db.add_model_comparison(
                image_path=image_path,
                models=",".join(selected_models),
                performance_data=json.dumps(performance_data),
                detection_result=json.dumps({"detections": detections})
            )
            st.success("模型比对记录已保存")
        except Exception as e:
            st.error(f"保存记录失败: {str(e)}")

else:
    st.info("👆 请先上传需要检测的图片")

# 添加页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>© 2025 城市建筑物检测系统 | 技术支持：AIE52期-5组</p>
</div>
""", unsafe_allow_html=True)