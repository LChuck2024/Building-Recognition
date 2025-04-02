import streamlit as st
import torch
from PIL import Image
import numpy as np
import cv2
from pathlib import Path
import time

# 设置页面配置
st.set_page_config(
    page_title="单张图片识别 - 城市建筑物识别系统",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加页眉图片
st.image("images/single_header.svg", use_container_width=True)

# 自定义CSS样式
st.markdown("""
<style>
    /* 图片圆角样式 */
    img {
        border-radius: 12px;
    }
    /* 全局样式 */
    .main {padding: 2rem; max-width: 1200px; margin: 0 auto;}
    body {font-family: 'Helvetica Neue', sans-serif;}
    
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
        padding: 2.5rem;
        text-align: center;
        border-radius: 12px;
        background: #ffffff;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .upload-box:hover {
        border-color: #0083B8;
        box-shadow: 0 4px 12px rgba(0,131,184,0.1);
    }
    
    /* 结果区域样式 */
    .result-box {
        background: linear-gradient(to bottom right, #ffffff, #f8f9fa);
        padding: 2.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    .result-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }
    
    /* 置信度条样式 */
    .confidence-meter {
        height: 24px;
        background-color: #e9ecef;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
    }
    .confidence-bar {
        height: 100%;
        background: linear-gradient(90deg, #0083B8, #00A3E0);
        transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* 标题和文本样式 */
    h1, h2, h3, h4 {
        color: #2C3E50;
        font-weight: 600;
    }
    p {
        color: #34495E;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)


# 侧边栏设置
with st.sidebar:
    st.title("系统信息")
    st.markdown("### 支持的建筑物类型")
    building_types = ["住宅楼", "办公楼", "商业建筑", "工业建筑", "文教建筑", "医疗建筑", "酒店建筑"]
    for bt in building_types:
        st.markdown(f"- {bt}")

# 主页面标题和介绍
st.title("🏢 单张图片识别")

# 创建三列布局
col1, col2, col3 = st.columns([1.5, 3, 3])

with col1:
    st.markdown("### 📤 上传区域")
    st.markdown("<div class='upload-box' style='min-height: 100px;'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("选择一张包含建筑物的图片", type=['jpg', 'jpeg', 'png'], key="file_uploader")
    
    if uploaded_file is not None:
        if st.button("🔍 开始识别", key="recognize_btn", use_container_width=True):
            with st.spinner('正在进行建筑物识别分析...'):
                # 显示进度条
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(i + 1)
                
                st.success("✨ 识别完成！")
                st.session_state['processed'] = True
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("### 🖼️ 图片预览")
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='预览图片', use_container_width=True)

with col3:
    st.markdown("### 📊 识别结果")
    if uploaded_file is not None and st.session_state.get('processed', False):
        st.markdown("<div class='result-box' style='min-height: 500px;'>", unsafe_allow_html=True)
        
        # 示例结果（后续替换为实际模型输出）
        result = {
            "建筑物类型": "办公楼",
            "置信度": 95,
            "特征描述": "现代化商务建筑，玻璃幕墙设计",
            "建议用途": "适合作为企业总部或商务中心",
            "建筑年代": "2010-2015年",
            "楼层数": "25层",
            "主要材料": "钢结构+玻璃幕墙"
        }
        
        # 显示主要结果
        st.markdown(f"#### 🏢 识别类型")
        st.markdown(f"<div style='background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;'>{result['建筑物类型']}</div>", unsafe_allow_html=True)
        
        # 显示置信度条
        st.markdown("#### 📈 置信度")
        st.markdown(f"""
        <div class='confidence-meter' style='margin-bottom: 1.5rem;'>
            <div class='confidence-bar' style='width: {result['置信度']}%;'></div>
        </div>
        <p style='text-align: right; margin-bottom: 1.5rem;'>{result['置信度']}%</p>
        """, unsafe_allow_html=True)
        
        # 显示建筑特征
        st.markdown("#### 🏗️ 建筑特征")
        # st.markdown(f"<div style='margin-bottom: 1.5rem;'>")
        st.markdown(f"**建筑年代：** {result['建筑年代']}")
        st.markdown(f"**楼层数：** {result['楼层数']}")
        st.markdown(f"**主要材料：** {result['主要材料']}")
        st.markdown(f"</div>")
        
        # 显示详细信息
        st.markdown("#### 📝 详细描述")
        st.markdown(f"<div style='background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;'>{result['特征描述']}</div>", unsafe_allow_html=True)
        
        # 显示建议用途
        st.markdown("#### 💡 建议用途")
        st.markdown(f"<div style='background: #f8f9fa; padding: 1rem; border-radius: 8px;'>{result['建议用途']}</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# 添加页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>© 2025 城市建筑物识别系统 | 技术支持：AIE52期-5组</p>
</div>
""", unsafe_allow_html=True)