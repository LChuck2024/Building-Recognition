import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import os
from pathlib import Path

# 设置页面配置
st.set_page_config(
    page_title="建筑特征分析 - 城市建筑物识别系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 图片圆角样式 */
    img {
        border-radius: 12px;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .analysis-section {
        background: linear-gradient(to bottom right, #ffffff, #f8f9fa);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    }
    .highlight-text {
        color: #0083B8;
        font-weight: bold;
    }
    .three-column-layout {
        display: grid;
        grid-template-columns: 1fr 2fr 1fr;
        gap: 1.5rem;
    }
    .chart-container {
        height: 400px;
    }
    .report-section {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# 添加页眉图片
image_path = os.path.join(Path(__file__).parent.parent,"images")
st.image(os.path.join(image_path,"analysis_header.svg"), use_column_width=True)
# 页面标题
st.title("📊 建筑物特征分析")


# 创建示例数据
def generate_sample_data():
    return {
        '建筑风格': ['现代主义', '后现代主义', '新古典主义', '装饰艺术风格', '国际主义风格'],
        '结构类型': ['钢筋混凝土', '钢结构', '玻璃幕墙', '砌体结构', '木结构'],
        '建筑高度': ['高层', '超高层', '多层', '低层', '中层'],
        '使用功能': ['办公', '商业', '居住', '文化', '医疗'],
        '建筑年代': ['2000年代', '2010年代', '1990年代', '1980年代', '2020年代']
    }

# 生成分析数据
analysis_data = generate_sample_data()

# 主布局容器
with st.container():
    st.markdown("<div class='three-column-layout'>", unsafe_allow_html=True)
    
    # 左侧栏 - 建筑基本信息
    st.markdown("<div class='left-column'>", unsafe_allow_html=True)
    st.markdown("### 🏢 建筑基本信息")
    
    st.markdown("""
    <div class='feature-card'>
        <h4>建筑名称</h4>
        <p class='highlight-text'>城市中心大厦</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-card'>
        <h4>地理位置</h4>
        <p class='highlight-text'>北京市朝阳区</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-card'>
        <h4>建造年代</h4>
        <p class='highlight-text'>2018年</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-card'>
        <h4>建筑面积</h4>
        <p class='highlight-text'>120,000㎡</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 中间栏 - 特征可视化图表
    st.markdown("<div class='middle-column'>", unsafe_allow_html=True)
    st.markdown("### 📊 特征可视化")
    
    # 建筑风格分析
    with st.expander("🏛️ 建筑风格分析", expanded=True):
        st.markdown("""
        <div class='analysis-section'>
            <h4>风格特征分布</h4>
            <p>分析建筑物的设计风格、形式语言和美学特征</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 创建风格分布图表
        style_data = pd.DataFrame({
            '风格': analysis_data['建筑风格'],
            '数量': np.random.randint(50, 200, size=5)
        })
        fig = px.bar(style_data, x='风格', y='数量',
                     title='建筑风格分布',
                     color='数量',
                     color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
    
    # 结构特征分析
    with st.expander("🏗️ 结构特征分析", expanded=True):
        st.markdown("""
        <div class='analysis-section'>
            <h4>结构类型分布</h4>
            <p>分析建筑物的结构系统、材料使用和施工特点</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 创建结构类型分布图表
        structure_data = pd.DataFrame({
            '类型': analysis_data['结构类型'],
            '比例': np.random.uniform(0, 1, size=5)
        })
        fig = px.pie(structure_data, values='比例', names='类型',
                     title='结构类型分布',
                     hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 右侧栏 - 详细分析报告
    st.markdown("<div class='right-column'>", unsafe_allow_html=True)
    st.markdown("### 📝 分析报告")
    
    st.markdown("""
    <div class='report-section'>
        <h4>综合评价</h4>
        <p>该建筑属于现代主义风格，采用钢筋混凝土结构，具有以下特征：</p>
        <ul>
            <li>玻璃幕墙占比达到65%</li>
            <li>抗震等级为8级</li>
            <li>节能效率达到一级标准</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='report-section'>
        <h4>建议</h4>
        <ul>
            <li>定期进行结构安全检查</li>
            <li>考虑增加光伏发电系统</li>
            <li>优化室内空间利用率</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='report-section'>
        <h4>历史维护记录</h4>
        <ul>
            <li>2022年：外墙清洗</li>
            <li>2021年：电梯系统升级</li>
            <li>2020年：消防系统检查</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 建筑风格分析
st.markdown("### 🏛️ 建筑风格分析")
with st.container():
    st.markdown("""
    <div class='analysis-section'>
        <h4>风格特征分布</h4>
        <p>分析建筑物的设计风格、形式语言和美学特征</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 创建风格分布图表
    style_data = pd.DataFrame({
        '风格': analysis_data['建筑风格'],
        '数量': np.random.randint(50, 200, size=5)
    })
    fig = px.bar(style_data, x='风格', y='数量',
                 title='建筑风格分布',
                 color='数量',
                 color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

# 结构特征分析
st.markdown("### 🏗️ 结构特征分析")
with st.container():
    st.markdown("""
    <div class='analysis-section'>
        <h4>结构类型分布</h4>
        <p>分析建筑物的结构系统、材料使用和施工特点</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 创建结构类型分布图表
    structure_data = pd.DataFrame({
        '类型': analysis_data['结构类型'],
        '比例': np.random.uniform(0, 1, size=5)
    })
    fig = px.pie(structure_data, values='比例', names='类型',
                 title='结构类型分布',
                 hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

# 功能分析
st.markdown("### 🎯 功能分析")
with st.container():
    st.markdown("""
    <div class='analysis-section'>
        <h4>使用功能分布</h4>
        <p>分析建筑物的使用功能、空间组织和运营特点</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 创建功能分布图表
    function_data = pd.DataFrame({
        '功能': analysis_data['使用功能'],
        '面积': np.random.randint(1000, 5000, size=5)
    })
    fig = px.treemap(function_data, path=['功能'], values='面积',
                     title='建筑功能分布')
    st.plotly_chart(fig, use_container_width=True)

# 时代特征分析
st.markdown("### 📅 时代特征分析")
with st.container():
    st.markdown("""
    <div class='analysis-section'>
        <h4>建筑年代分布</h4>
        <p>分析建筑物的建造年代、历史背景和时代特征</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 创建年代分布图表
    era_data = pd.DataFrame({
        '年代': analysis_data['建筑年代'],
        '数量': np.random.randint(20, 100, size=5)
    })
    fig = px.line(era_data, x='年代', y='数量',
                  title='建筑年代分布',
                  markers=True)
    st.plotly_chart(fig, use_container_width=True)

# 导出分析报告
st.markdown("### 📑 导出分析报告")
col1, col2 = st.columns(2)
with col1:
    if st.button("导出PDF报告"):
        st.success("分析报告已导出为PDF格式！")
with col2:
    if st.button("导出Excel报告"):
        st.success("分析报告已导出为Excel格式！")

# 添加页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>© 2025 城市建筑物识别系统 | 技术支持：AIE52期-5组</p>
</div>
""", unsafe_allow_html=True)