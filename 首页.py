import streamlit as st
import torch
from PIL import Image
import numpy as np
import cv2
from pathlib import Path
import time

# 设置页面主题和样式
st.set_page_config(
    page_title="智能建筑物识别系统",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 自定义CSS样式
st.markdown("""
<style>
    /* 全局样式 */
    .main {padding: 2rem; max-width: 1200px; margin: 0 auto;}
    body {font-family: 'Helvetica Neue', sans-serif;}
    
    /* 图片圆角样式 */
    img {
        border-radius: 12px;
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

st.image("images/home_header.svg", use_container_width=True)

# 侧边栏设置
with st.sidebar:
    st.title("系统信息")
    st.markdown("### 支持的建筑物类型")
    building_types = ["住宅楼", "办公楼", "商业建筑", "工业建筑", "文教建筑", "医疗建筑", "酒店建筑"]
    for bt in building_types:
        st.markdown(f"- {bt}")

# 主页面标题和介绍
# 主页面标题和介绍
st.title("🏢 城市建筑物识别系统")

# 创建两列布局
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("""
    <div style='background: linear-gradient(to bottom right, #0083B8, #00A3E0); color: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;'>
        <h3 style='color: white;'>欢迎使用城市建筑物智能识别系统</h3>
        <p style='color: white;'>本系统使用先进的深度学习技术，可以准确识别和分类不同类型的建筑物。</p>
    </div>
    """, unsafe_allow_html=True)

    # 系统功能介绍
    st.markdown("### 🚀 核心功能")
    st.markdown("""
    <div class='feature-box'>
        <div style='display: flex; justify-content: space-between;'>
            <div style='flex: 1; margin: 0.5rem; padding: 1rem; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                <h4 style='color: #0083B8;'>🔍 智能识别</h4>
                <p>上传建筑物图片，自动识别建筑类型</p>
            </div>
            <div style='flex: 1; margin: 0.5rem; padding: 1rem; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                <h4 style='color: #0083B8;'>📊 特征分析</h4>
                <p>详细分析建筑特征和结构</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # 使用指南
    st.markdown("### 📖 快速开始")
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
        <div style='display: flex; align-items: center; margin-bottom: 1rem;'>
            <div style='background: #0083B8; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 1rem;'>1</div>
            <p style='margin: 0;'>点击左侧导航栏选择功能</p>
        </div>
        <div style='display: flex; align-items: center; margin-bottom: 1rem;'>
            <div style='background: #0083B8; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 1rem;'>2</div>
            <p style='margin: 0;'>上传建筑物图片</p>
        </div>
        <div style='display: flex; align-items: center;'>
            <div style='background: #0083B8; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 1rem;'>3</div>
            <p style='margin: 0;'>查看分析结果和历史记录</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 添加页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>© 2025 城市建筑物识别系统 | 技术支持：AIE52期-5组</p>
</div>
""", unsafe_allow_html=True)