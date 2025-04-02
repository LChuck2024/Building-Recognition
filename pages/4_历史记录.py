import streamlit as st
import pandas as pd
from datetime import datetime
import json
from pathlib import Path

# 设置页面配置
st.set_page_config(
    page_title="历史记录 - 城市建筑物识别系统",
    page_icon="📊",
    layout="wide"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 图片圆角样式 */
    img {
        border-radius: 12px;
    }
    
    .history-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    .history-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .metric-card {
        background: linear-gradient(45deg, #0083B8, #00A3E0);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# 页面标题
st.title("📊 识别历史记录")

# 创建示例历史数据（实际应用中应从数据库或文件中读取）
def load_history_data():
    # 这里应该实现实际的数据加载逻辑
    return pd.DataFrame({
        '时间': [datetime.now().strftime("%Y-%m-%d %H:%M:%S") for _ in range(5)],
        '建筑物类型': ['办公楼', '住宅楼', '商业建筑', '文教建筑', '医疗建筑'],
        '置信度': [95, 88, 92, 85, 90],
        '图片路径': ['image1.jpg', 'image2.jpg', 'image3.jpg', 'image4.jpg', 'image5.jpg'],
        '特征描述': [
            '现代化商务建筑，玻璃幕墙设计',
            '高层住宅，简约风格',
            '大型购物中心，开放式设计',
            '传统学院派建筑，红砖外墙',
            '综合医院，功能性设计'
        ]
    })

# 加载历史数据
history_data = load_history_data()

# 创建统计指标
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class='metric-card'>
        <h3>总识别次数</h3>
        <h2>42</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='metric-card'>
        <h3>平均置信度</h3>
        <h2>90%</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='metric-card'>
        <h3>最常见建筑类型</h3>
        <h2>办公楼</h2>
    </div>
    """, unsafe_allow_html=True)

# 添加筛选器
st.markdown("### 🔍 筛选条件")
col1, col2 = st.columns(2)
with col1:
    building_type = st.multiselect(
        "建筑物类型",
        options=history_data['建筑物类型'].unique(),
        default=[]
    )
with col2:
    confidence_range = st.slider(
        "置信度范围",
        min_value=0,
        max_value=100,
        value=(70, 100)
    )

# 显示历史记录
st.markdown("### 📜 识别记录")
for _, record in history_data.iterrows():
    st.markdown(f"""
    <div class='history-card'>
        <h4>{record['时间']}</h4>
        <p><strong>建筑物类型：</strong>{record['建筑物类型']}</p>
        <p><strong>置信度：</strong>{record['置信度']}%</p>
        <p><strong>特征描述：</strong>{record['特征描述']}</p>
    </div>
    """, unsafe_allow_html=True)

# 添加导出功能
st.markdown("### 📤 导出数据")
col1, col2 = st.columns(2)
with col1:
    if st.button("导出为CSV"):
        # 这里应该实现实际的导出逻辑
        st.success("数据已成功导出为CSV文件！")
with col2:
    if st.button("导出为JSON"):
        # 这里应该实现实际的导出逻辑
        st.success("数据已成功导出为JSON文件！")

# 添加页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>© 2025 城市建筑物识别系统 | 技术支持：AIE52期-5组</p>
</div>
""", unsafe_allow_html=True)