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
with st.sidebar:
    # 使用说明区域
    st.markdown("### 📖 使用指南")
    st.markdown("""
    <div class='card'>
        <h4>快速开始</h4>
        <ol>
            <li>选择需要使用的功能</li>
            <li>上传建筑物图片</li>
            <li>点击开始检测</li>
            <li>等待系统分析处理</li>
            <li>查看识别结果和分析报告</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

# 功能展示区域
st.markdown("### 🚀 核心功能")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div class='card'>
            <h5>🔍 单图识别</h5>
            <p>上传单张建筑物图片，系统将自动识别建筑类型，并提供详细的分析结果。支持多种建筑类型，识别准确率高。</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class='card'>
            <h5>📑 批量识别</h5>
            <p>同时上传多张图片进行批量识别，适合大规模建筑物分析任务。自动生成分析报告，提供数据导出功能。</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class='card'>
            <h5>🔄 变化检测</h5>
            <p>对比不同时期的建筑物图片，自动检测和标注建筑物的变化情况。帮助您快速发现建筑物的结构变化。</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class='card'>
            <h5>📊 历史记录</h5>
            <p>查看和管理所有历史检测记录，支持按时间、类型等多维度筛选。方便您追踪和对比历史识别结果。</p>
        </div>
    """, unsafe_allow_html=True)


# 项目背景与价值
st.markdown("### 🌟 项目背景与价值")
st.markdown("""
<div class='card'>
    <h5>项目背景</h5>
    <p>随着城市化的快速发展，建筑物识别技术在城市规划、建筑监测和房地产评估等领域发挥着越来越重要的作用。传统的人工识别方法效率低下、成本高昂，难以满足现代城市管理的需求。</p>
    <h5>实际应用价值</h5>
    <ul>
        <li>🏙️ 城市规划：快速获取城市建筑分布信息，为城市规划决策提供数据支持</li>
        <li>🏗️ 建筑监测：实时监测建筑物变化，及时发现违规建筑和安全隐患</li>
        <li>🏘️ 房地产评估：准确识别建筑类型和特征，为房地产价值评估提供参考</li>
        <li>📊 数据分析：为政府部门和科研机构提供建筑数据统计分析服务</li>
    </ul>
    <h5>系统优势</h5>
    <ul>
        <li>🚀 高效：相比人工识别，效率提升80%以上</li>
        <li>💵 经济：降低人工成本，节省运营开支</li>
        <li>🔍 精准：采用深度学习算法，识别准确率高达95%</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>© 2025 智能建筑物识别系统 | 技术支持：AIE52期-5组</p>
</div>
""", unsafe_allow_html=True)