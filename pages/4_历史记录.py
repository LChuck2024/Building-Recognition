import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
from pathlib import Path
from utils.db_manager import DBManager

# 设置页面配置
st.set_page_config(
    page_title="历史记录 - 城市建筑物检测系统",
    page_icon="📊",
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
    
    /* 图片圆角样式 */
    img {
        border-radius: 12px;
        max-width: 100%;
        height: auto;
    }
    
    /* 历史记录卡片 */
    .history-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    .history-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }
    
    /* 统计卡片 */
    .metric-card {
        background: linear-gradient(45deg, #0083B8, #00A3E0);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }
    
    /* 响应式布局 */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
        .history-card,
        .metric-card {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# 页面标题
st.title("📊 检测历史记录")

# 初始化数据库管理器
db = DBManager()

# 获取统计信息
stats = db.get_statistics()

# 创建统计指标
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    <div class='metric-card'>
        <h3>总检测次数</h3>
        <h2>{stats['total_detections']}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='metric-card'>
        <h3>平均置信度</h3>
        <h2>{stats['avg_confidence']:.2f}</h2>
    </div>
    """, unsafe_allow_html=True)

# 检测模式分布
detection_mode_counts = db.get_detection_mode_distribution()
if detection_mode_counts is not None:
    st.markdown("### 📊 检测模式分布")
    col1, col2 = st.columns(2)
    with col1:
        # 按照页面顺序排序检测模式
        detection_mode_order = ['单图检测', '批量检测', '变化检测']
        detection_mode_counts['detection_mode'] = pd.Categorical(
            detection_mode_counts['detection_mode'], 
            categories=detection_mode_order,
            ordered=True
        )
        detection_mode_counts = detection_mode_counts.sort_values('detection_mode')
        
        fig = px.bar(detection_mode_counts, x='detection_mode', y='count', 
                    title='检测模式分布', 
                    labels={'detection_mode': '检测模式', 'count': '数量'},
                    color='detection_mode')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.pie(detection_mode_counts, values='count', names='detection_mode',
                    title='检测模式占比', hole=0.3,
                    labels={'count':'数量', 'detection_mode':'检测模式'})
        st.plotly_chart(fig, use_container_width=True)

# 添加筛选器
st.markdown("### 🔍 筛选条件")

# 选择记录类型
record_type = st.selectbox("记录类型",options=["单图检测", "批量检测", "变化检测"],index=0)
# 根据记录类型显示不同的筛选选项
if record_type == "单图检测" or record_type == "批量检测":
    confidence_range = st.slider(
            "置信度范围",
            min_value=0.0,
            max_value=1.0,
            value=(0.7, 1.0)
    )
    if record_type == "单图检测":
        history_records = db.get_detection_history(min_confidence=confidence_range[0], max_confidence=confidence_range[1])
    else:
        history_records = db.get_batch_history(min_confidence=confidence_range[0], max_confidence=confidence_range[1])
    
else:  # 变化检测
    min_confidence = st.slider(
        "最小置信度",
        min_value=0.0,
        max_value=1.0,
        value=0.7
    )
    history_records = db.get_change_history()

# 添加清空按钮
if st.button("⚠️ 清空所有历史记录", type="primary"):
    try:
        db.clear_all_history(reset_flag=True)
        st.success("历史记录已清空")
        st.rerun()
    except Exception as e:
        st.error(f"清空历史记录失败: {str(e)}")

# 显示历史记录
st.markdown("### 📜 检测记录")

if not history_records:
    st.info("暂无历史记录")
else:
    for record in history_records:
        with st.expander(f"记录时间：{record['detection_time']}"):
            if record_type == "单图检测":
                try:
                    if Path(record['image_path']).exists():
                        st.image(record['image_path'], caption="检测图片", use_container_width=True)
                    else:
                        st.warning(f"图片文件不存在: {record['image_path']}")
                except Exception as e:
                    st.error(f"加载图片时出错: {str(e)}")
                
                st.markdown(f"**置信度：** {record['confidence']*100:.1f}%")
                st.markdown(f"**特征描述：** {record['feature_description']}")
                st.markdown(f"**检测模式：** {record['detection_mode']}")
                
                # 显示详细结果
                st.markdown("**详细结果：**")
                st.json(json.loads(record['detection_result']))
            
            elif record_type == "批量检测":
                st.markdown(f"**总图片数：** {record['total_images']}")
                st.markdown(f"**成功数量：** {record['success_count']}")
                st.markdown(f"**失败数量：** {record['failed_count']}")
                st.markdown(f"**平均置信度：** {record['confidence']}")
                
                # 显示批量结果
                st.markdown("**批量结果：**")
                st.json(json.loads(record['batch_result']))
            
            else:  # 变化检测
                col1, col2 = st.columns(2)
                with col1:
                    try:
                        if Path(record['earlier_image_path']).exists():
                            st.image(record['earlier_image_path'], caption="早期图片")
                        else:
                            st.warning(f"早期图片文件不存在: {record['earlier_image_path']}")
                    except Exception as e:
                        st.error(f"加载早期图片时出错: {str(e)}")
                with col2:
                    try:
                        if Path(record['recent_image_path']).exists():
                            st.image(record['recent_image_path'], caption="近期图片")
                        else:
                            st.warning(f"近期图片文件不存在: {record['recent_image_path']}")
                    except Exception as e:
                        st.error(f"加载近期图片时出错: {str(e)}")
                
                st.markdown(f"**变化类型：** {record['change_type']}")
                st.markdown(f"**变化面积：** {record['change_area']:.2f} 平方像素")
                st.markdown(f"**置信度：** {record['confidence']*100:.1f}%")
                
                # 显示检测结果
                st.markdown("**检测结果：**")
                st.json(json.loads(record['detection_result']))

# 添加导出功能
st.markdown("### 📤 导出数据")
col1, col2 = st.columns(2)
with col1:
    if st.button("导出为CSV"):
        if history_records:
            # 将记录转换为DataFrame
            df = pd.DataFrame(history_records)
            # 转换为CSV
            csv = df.to_csv(index=False).encode('utf-8')
            # 提供下载
            st.download_button(
                label="📥 下载CSV文件",
                data=csv,
                file_name=f"{record_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime='text/csv'
            )
with col2:
    if st.button("导出为JSON"):
        if history_records:
            # 转换为JSON字符串
            json_str = json.dumps(history_records, ensure_ascii=False, indent=2)
            # 提供下载
            st.download_button(
                label="📥 下载JSON文件",
                data=json_str,
                file_name=f"{record_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime='application/json'
            )

# 添加页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>© 2025 城市建筑物检测系统 | 技术支持：AIE52期-5组</p>
</div>
""", unsafe_allow_html=True)