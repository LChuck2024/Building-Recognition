import streamlit as st
from pathlib import Path
from utils.db_manager import DBManager
import os

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
        padding: 1.5rem;
        width: 100%;
        max-width: 100%;
        margin: 0 auto;
        box-sizing: border-box;
        background: linear-gradient(135deg, #f0f4f8 0%, #ffffff 100%);
    }
    body {
        font-family: 'Helvetica Neue', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 16px;
        line-height: 1.6;
        color: #2C3E50;
        background: linear-gradient(135deg, #f0f4f8 0%, #ffffff 100%);
    }
    
    /* 卡片样式 */
    .card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0,131,184,0.12);
        margin-bottom: 2rem;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(0,131,184,0.08);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
    }
    .card:hover {
        transform: translateY(-6px) scale(1.01);
        box-shadow: 0 12px 40px rgba(0,131,184,0.18);
        border-color: rgba(0,131,184,0.15);
    }
    .card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 200%;
        height: 100%;
        background: linear-gradient(120deg, transparent, rgba(255,255,255,0.6), transparent);
        transform: translateX(-100%);
        transition: 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .card:hover::after {
        transform: translateX(100%);
    }
    
    /* 特性卡片 */
    .feature-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        padding: 1.8rem;
        border-radius: 18px;
        box-shadow: 0 8px 25px rgba(0,131,184,0.1);
        margin: 1rem;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(0,131,184,0.08);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
    }
    .feature-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 15px 35px rgba(0,131,184,0.15);
        border-color: rgba(0,131,184,0.2);
    }
    .feature-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 150%;
        height: 100%;
        background: linear-gradient(120deg, transparent, rgba(255,255,255,0.4), transparent);
        transform: translateX(-100%) rotate(25deg);
        transition: 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .feature-card:hover::after {
        transform: translateX(100%) rotate(25deg);
    }
    
    /* 图片样式 */
    img {
        border-radius: 20px;
        max-width: 100%;
        height: auto;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        filter: brightness(1);
    }
    img:hover {
        transform: scale(1.03);
        filter: brightness(1.05);
        box-shadow: 0 8px 25px rgba(0,131,184,0.15);
    }
    
    /* 标题和文本样式 */
    h1, h2, h3, h4 {
        color: #1a202c;
        font-weight: 700;
        margin-bottom: 1.2rem;
        letter-spacing: -0.02em;
        transition: all 0.3s ease;
    }
    h1 {
        font-size: 2.8rem;
        background: linear-gradient(135deg, #0083B8, #00A3E0, #0083B8);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient 3s linear infinite;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    p {
        color: #4a5568;
        line-height: 1.8;
        margin-bottom: 1.2rem;
    }
    
    /* 按钮样式 */
    button {
        background: linear-gradient(45deg, #0083B8, #00A3E0);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 6px 20px rgba(0,131,184,0.25);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
    }
    button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0,131,184,0.35);
        background: linear-gradient(45deg, #00A3E0, #0083B8);
    }
    button::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 200%;
        height: 100%;
        background: linear-gradient(120deg, transparent, rgba(255,255,255,0.3), transparent);
        transform: translateX(-100%);
        transition: 0.6s;
    }
    button:hover::after {
        transform: translateX(100%);
    }
    
    /* 表单样式 */
    input[type="text"],
    input[type="password"] {
        width: 100%;
        padding: 1rem 1.2rem;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        margin-bottom: 1.2rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 1rem;
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }
    input[type="text"]:hover,
    input[type="password"]:hover {
        border-color: #cbd5e0;
        background: rgba(255, 255, 255, 0.95);
    }
    input[type="text"]:focus,
    input[type="password"]:focus {
        border-color: #0083B8;
        box-shadow: 0 0 0 4px rgba(0,131,184,0.15);
        outline: none;
        background: white;
    }
    
    /* 响应式布局 */
    @media (max-width: 768px) {
        .main {
            padding: 1rem;
        }
        .card {
            padding: 1.2rem;
        }
        h1 {
            font-size: 2rem;
        }
        .feature-card {
            margin: 0.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# 获取当前文件路径
current_dir = Path(__file__).parent

# 页面头部
st.image(f"{current_dir}/images/home_header.svg", use_container_width=True)
st.title("🏢 智能建筑物识别系统")

# 导入数据库管理器
from utils.db_manager import DBManager

# 初始化数据库管理器
db = DBManager()

# 获取统计信息
stats = db.get_statistics()

# 欢迎区域
st.markdown("""
<div style='background: linear-gradient(to right, #0083B8, #00A3E0); color: white; padding: 2rem; border-radius: 12px; margin-bottom: 2rem;'>
    <h2 style='color: white; margin-bottom: 1rem;'>👋 欢迎使用智能建筑物识别系统</h2>
    <p style='color: white; font-size: 1.1rem;'>本系统采用先进的深度学习技术，为您提供精准的建筑物识别和分类服务。无论是单张图片识别还是批量处理，我们都能为您提供专业的解决方案。</p>
</div>
""", unsafe_allow_html=True)

# 添加实时数据统计展示区
st.markdown("### 📈 系统运行状态")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class='card' style='text-align: center;'>
        <h3 style='color: #0083B8; text-align: center;'>{stats['total_detections']}</h3>
        <p style='text-align: center;'>总检测次数</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='card' style='text-align: center;'>
        <h3 style='color: #0083B8; text-align: center;'>{stats['avg_confidence']:.2f}</h3>
        <p style='text-align: center;'>平均置信度</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='card' style='text-align: center;'>
        <h3 style='color: #0083B8; text-align: center;'>{stats.get('today_detections', 0)}</h3>
        <p style='text-align: center;'>今日检测次数</p>
    </div>
    """, unsafe_allow_html=True)

with st.sidebar:
    # 使用说明区域
    st.markdown("### 📖 使用指南")
    
    # 主要功能说明
    with st.expander("🎯 功能选择"):
        st.markdown("""
        - 🏢 **单图识别**：单张建筑物图片分析
        - 📑 **批量识别**：多张图片批量处理
        - 🔍 **模型比对**：比较不同模型的检测效果
        - 🔄 **变化检测**：建筑物变化分析
        - 📊 **历史记录**：查看和管理历史检测记录
        """)
    
    # 图片要求说明
    with st.expander("📸 图片要求"):
        st.markdown("""
        - 📁 格式：JPG、PNG、JPEG
        - 🖼️ 分辨率：≥1024×1024
        - 📦 大小：≤10MB
        """)
    
    # 使用流程说明
    with st.expander("📝 操作步骤"):
        st.markdown("""
        1. 选择所需功能模块
        2. 上传符合要求的图片
        3. 等待系统分析处理
        4. 查看分析结果报告
        """)
    
    # 注意事项
    with st.expander("⚠️ 注意事项"):
        st.markdown("""
        - 请确保图片清晰度良好
        - 建议图片中建筑物占比较大
        - 分析结果仅供参考
        """)


# 功能展示区域
st.markdown("### 🚀 核心功能")
col1, col2, col3, col4, col5 = st.columns(5)

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
            <h5>🔍 模型对比</h5>
            <p>比较不同模型的检测效果，直观展示各模型在精度、速度和资源消耗等方面的差异，帮助您选择最适合的模型。</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class='card'>
            <h5>🔄 变化检测</h5>
            <p>对比不同时期的建筑物图片，自动检测和标注建筑物的变化情况。帮助您快速发现建筑物的结构变化。</p>
        </div>
    """, unsafe_allow_html=True)

with col5:
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
        <li>🚁 低空经济：政策大力推广低空经济，无人机在各行业的应用将会到达一个顶峰</li>
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