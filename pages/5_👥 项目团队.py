import streamlit as st
from pathlib import Path

# 设置页面配置
st.set_page_config(
    page_title="项目团队 - 智能建筑物识别系统",
    page_icon="👥",
    layout="wide"
)

# 继承主页面样式
st.markdown("""
<style>
    /* 继承主页面样式 */
    .main {
        padding: 1rem;
        width: 100%;
        max-width: 100%;
        margin: 0 auto;
        box-sizing: border-box;
        height: 100vh;
        overflow-y: auto;
    }
    
    /* 团队成员卡片 */
    .team-card {
        background: white;
        padding: 0.8rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        margin-right: 1rem;
        transition: all 0.3s ease;
        min-height: 280px;
        display: flex;
        flex-direction: column;
        width: 100%;
        justify-content: space-between;
        text-align: center;
    }
    .team-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
        background: #f8f9fa;
    }
    
    /* 团队成员头像 */
    .team-avatar {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        object-fit: cover;
        margin: 0 auto;
        display: block;
        border: 4px solid #0083B8;
    }
    
    /* 社交媒体图标 */
    .social-icon {
        width: 24px;
        height: 24px;
        margin-right: 8px;
        vertical-align: middle;
    }
    
    /* 移除列表点符号 */
    .team-card ul {
        list-style-type: none;
        padding-left: 0;
    }
</style>
""", unsafe_allow_html=True)

# 页面标题
st.title("👥 项目团队")

# 团队介绍
st.markdown("""
<div class='card'>
    <h3>关于我们的团队</h3>
    <p>我们是一支来自AIE52期-5组的技术团队，专注于计算机视觉和深度学习技术的应用开发。团队成员各有所长，共同打造了这套智能建筑物识别系统。</p>
    
</div>
""", unsafe_allow_html=True)

# 项目经理展示
st.markdown("### 🏆 项目结构")

col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("""
    <div class='team-card'>
        <h4 style='text-align: center; margin-top: 1rem;'>项目经理</h4>
        <p style='text-align: center; color: #666;'>项目总负责人：刘卫华</p>
        <p style='text-align: center;'>负责项目整体规划、进度控制和团队协调，确保项目按时高质量交付。</p>
        <div style='text-align: center; margin-top: 1rem;'>
            <a href="#"><img src="https://cdn-icons-png.flaticon.com/512/2111/2111463.png" class='social-icon' alt='GitHub'></a>
            <a href="#"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" class='social-icon' alt='LinkedIn'></a>
        </div>
    </div>
    """, unsafe_allow_html=True)


# 团队分组展示 - 统一卡片式布局
team_groups = [
    {
        "name": "📈 数据组",
        "leader": "王欢",
        "description": "负责数据收集、清洗和预处理工作，构建高质量建筑数据集。",
        "members": ["李平", "杨士震", "孙宇", "康确华", "高阳", "曹野", "曹文威"]
    },
    {
        "name": "💻 程序组",
        "leader": "杨袖清",
        "description": "负责算法开发、模型训练和系统实现。",
        "members": ["陈亿斌", "李梦洋", "蓝杰", "凌云志", "朱付振"]
    },
    {
        "name": "✍️ 文案组",
        "leader": "高阳",
        "description": "负责文档编写、用户界面文案和宣传材料制作。",
        "members": ["许俊亮"]
    }
]

# 团队分组展示 - 水平排列
cols = st.columns(len(team_groups))
for idx, group in enumerate(team_groups):
    with cols[idx]:
        st.markdown(f"""
        <div class='team-card' style='height: 100%; display: flex; flex-direction: column;'>
            <h4 style='text-align: center;'>{group['name']}</h4>
            <h5 style='text-align: center; color: #666;'>组长: {group['leader']}</h5>
            <p style='flex-grow: 1;'>{group['description']}</p>
            <ul style='column-count: 3; -webkit-column-count: 3; -moz-column-count: 3; margin: 0.3rem 0; padding: 0; text-align: center; line-height: 1.4;'>
                {"".join([f"<li style='margin: 0.1rem 0;'>{member}</li>" for member in group['members']])}
            </ul>
            <div style='text-align: center; margin-top: auto; padding-top: 1rem;'>
                <a href="#"><img src="https://cdn-icons-png.flaticon.com/512/2111/2111463.png" class='social-icon' alt='GitHub'></a>
                <a href="#"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" class='social-icon' alt='LinkedIn'></a>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 侧边栏技术栈
with st.sidebar:
    st.markdown("### 🛠️ 技术栈")
    st.markdown("""
    <div style='margin-bottom: 1rem;'>
        <ul>
            <li>🖥️ 前端：Streamlit, HTML/CSS</li>
            <li>⚙️ 后端：Python</li>
            <li>🧠 AI框架：PyTorch, YOLOv12</li>
            <li>🗄️ 数据库：SQLite</li>
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