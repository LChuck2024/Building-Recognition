import streamlit as st
from pathlib import Path

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
    
    /* 卡片样式 */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* 特性卡片 */
    .feature-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin: 0.5rem;
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* 图片样式 */
    img {
        border-radius: 12px;
        max-width: 100%;
        height: auto;
    }
    
    /* 标题和文本样式 */
    h1, h2, h3, h4 {
        color: #2C3E50;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    p {
        color: #34495E;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    /* 响应式布局 */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
        .card {
            padding: 1rem;
        }
        h1 {
            font-size: 1.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# 获取当前文件路径
current_dir = Path(__file__).parent

# 页面头部
st.image(f"{current_dir}/images/home_header.svg", use_container_width=True)
st.title("🏢 智能建筑物识别系统")

# 欢迎区域
st.markdown("""
<div style='background: linear-gradient(to right, #0083B8, #00A3E0); color: white; padding: 2rem; border-radius: 12px; margin-bottom: 2rem;'>
    <h2 style='color: white; margin-bottom: 1rem;'>👋 欢迎使用智能建筑物识别系统</h2>
    <p style='color: white; font-size: 1.1rem;'>本系统采用先进的深度学习技术，为您提供精准的建筑物识别和分类服务。无论是单张图片识别还是批量处理，我们都能为您提供专业的解决方案。</p>
</div>
""", unsafe_allow_html=True)

# 功能展示区域
st.markdown("### 🚀 核心功能")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔍 单图识别", key="single_detection", use_container_width=True):
        st.switch_page("pages/1_单图识别.py")
    st.markdown("""
        <div class='card'>
            <h3>🔍 单图识别</h3>
            <p>上传单张建筑物图片，系统将自动识别建筑类型，并提供详细的分析结果。支持多种建筑类型，识别准确率高。</p>
            <ul>
                <li>快速精准的识别</li>
                <li>详细的分析报告</li>
                <li>可视化结果展示</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("📑 批量识别", key="batch_detection", use_container_width=True):
        st.switch_page("pages/2_批量识别.py")
    st.markdown("""
        <div class='card'>
            <h3>📑 批量识别</h3>
            <p>同时上传多张图片进行批量识别，适合大规模建筑物分析任务。自动生成分析报告，提供数据导出功能。</p>
            <ul>
                <li>批量处理能力</li>
                <li>自动报告生成</li>
                <li>数据导出功能</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col3:
    if st.button("🔄 变化检测", key="change_detection", use_container_width=True):
        st.switch_page("pages/3_变化检测.py")
    st.markdown("""
        <div class='card'>
            <h3>🔄 变化检测</h3>
            <p>对比不同时期的建筑物图片，自动检测和标注建筑物的变化情况。帮助您快速发现建筑物的结构变化。</p>
            <ul>
                <li>自动变化检测</li>
                <li>变化区域标注</li>
                <li>变化程度分析</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col4:
    if st.button("📊 历史记录", key="history_record", use_container_width=True):
        st.switch_page("pages/4_历史记录.py")
    st.markdown("""
        <div class='card'>
            <h3>📊 历史记录</h3>
            <p>查看和管理所有历史检测记录，支持按时间、类型等多维度筛选。方便您追踪和对比历史识别结果。</p>
            <ul>
                <li>完整历史记录</li>
                <li>多维度筛选</li>
                <li>结果对比分析</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# 使用说明区域
st.markdown("### 📖 使用指南")
st.markdown("""
<div class='card'>
    <h4>快速开始</h4>
    <ol>
        <li>选择需要使用的功能（单图识别/批量识别）</li>
        <li>上传建筑物图片（支持.jpg、.jpeg、.png格式）</li>
        <li>等待系统分析处理</li>
        <li>查看识别结果和分析报告</li>
    </ol>
    <h4>支持的建筑物类型</h4>
    <div style='display: flex; flex-wrap: wrap; gap: 1rem;'>
        <div class='feature-card'>🏢 办公楼</div>
        <div class='feature-card'>🏠 住宅楼</div>
        <div class='feature-card'>🏪 商业建筑</div>
        <div class='feature-card'>🏭 工业建筑</div>
        <div class='feature-card'>🏫 教育建筑</div>
        <div class='feature-card'>🏥 医疗建筑</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>© 2025 智能建筑物识别系统 | 技术支持：AIE52期-5组</p>
</div>
""", unsafe_allow_html=True)