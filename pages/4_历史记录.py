import streamlit as st
import pandas as pd
from datetime import datetime
import json
from pathlib import Path
from utils.db_manager import DBManager

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

# 初始化数据库管理器
db = DBManager()

# 获取统计信息
stats = db.get_statistics()

# 创建统计指标
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class='metric-card'>
        <h3>总识别次数</h3>
        <h2>{stats['total_detections']}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='metric-card'>
        <h3>平均置信度</h3>
        <h2>{stats['avg_confidence']:.1f}%</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='metric-card'>
        <h3>最常见建筑类型</h3>
        <h2>{stats['most_common_type'] or '暂无数据'}</h2>
    </div>
    """, unsafe_allow_html=True)

# 添加筛选器
st.markdown("### 🔍 筛选条件")

# 选择记录类型
record_type = st.selectbox(
    "记录类型",
    options=["单图识别", "批量识别", "变化检测"],
    index=0
)

# 分页控制
page_size = 10
page_number = st.number_input("页码", min_value=1, value=1)
offset = (page_number - 1) * page_size

# 根据记录类型显示不同的筛选选项
if record_type == "单图识别":
    col1, col2 = st.columns(2)
    with col1:
        building_type = st.text_input("建筑物类型")
    with col2:
        confidence_range = st.slider(
            "置信度范围",
            min_value=0.0,
            max_value=1.0,
            value=(0.7, 1.0)
        )
    
    # 获取筛选后的历史记录
    history_records = db.get_detection_history(
        limit=page_size,
        offset=offset,
        building_type=building_type if building_type else None,
        min_confidence=confidence_range[0],
        max_confidence=confidence_range[1]
    )

elif record_type == "批量识别":
    process_mode = st.selectbox(
        "处理模式",
        options=["标准模式", "快速模式", "高精度模式", "无人机影像专用模式"],
        index=0
    )
    
    # 获取批量识别历史记录
    history_records = db.get_batch_history(
        limit=page_size,
        offset=offset,
        process_mode=process_mode
    )

else:  # 变化检测
    col1, col2 = st.columns(2)
    with col1:
        change_type = st.selectbox(
            "变化类型",
            options=["新建筑物", "拆除建筑物", "扩建区域"],
            index=0
        )
    with col2:
        min_confidence = st.slider(
            "最小置信度",
            min_value=0.0,
            max_value=1.0,
            value=0.7
        )
    
    # 获取变化检测历史记录
    history_records = db.get_change_history(
        limit=page_size,
        offset=offset,
        change_type=change_type,
        min_confidence=min_confidence
    )

# 添加清空按钮
if st.button("⚠️ 清空所有历史记录", type="primary"):
    try:
        db.clear_all_history()
        st.success("历史记录已清空")
        st.rerun()
    except Exception as e:
        st.error(f"清空历史记录失败: {str(e)}")

# 数据分析
st.markdown("### 📊 数据分析")

# 建筑物类型分布饼图
building_type_counts = db.get_building_type_distribution()
if building_type_counts:
    st.markdown("#### 🏢 建筑物类型分布")
    # 导入plotly express
    import plotly.express as px
    fig1 = px.pie(building_type_counts, values='count', names='building_type', title='建筑物类型分布')
    st.plotly_chart(fig1, use_container_width=True)

# 检测时间趋势图
detection_trend = db.get_detection_trend()
if detection_trend:
    st.markdown("#### 📈 检测时间趋势")
    fig2 = px.line(detection_trend, x='detection_time', y='count', title='每日检测数量趋势')
    st.plotly_chart(fig2, use_container_width=True)

# 置信度分布直方图
confidence_distribution = db.get_confidence_distribution()
if confidence_distribution:
    st.markdown("#### 📊 置信度分布")
    fig3 = px.histogram(confidence_distribution, x='confidence', nbins=20, title='置信度分布')
    st.plotly_chart(fig3, use_container_width=True)

# 显示历史记录
st.markdown("### 📜 识别记录")

if not history_records:
    st.info("暂无历史记录")
else:
    for record in history_records:
        with st.expander(f"记录时间：{record['detection_time']}"):
            if record_type == "单图识别":
                try:
                    if Path(record['image_path']).exists():
                        st.image(record['image_path'], caption="识别图片", use_column_width=True)
                    else:
                        st.warning(f"图片文件不存在: {record['image_path']}")
                except Exception as e:
                    st.error(f"加载图片时出错: {str(e)}")
                st.markdown(f"**建筑物类型：** {record['building_type']}")
                st.markdown(f"**置信度：** {record['confidence']*100:.1f}%")
                st.markdown(f"**特征描述：** {record['feature_description']}")
                st.markdown(f"**检测模式：** {record['detection_mode']}")
                
                # 显示详细结果
                st.markdown("**详细结果：**")
                st.json(json.loads(record['detection_result']))
            
            elif record_type == "批量识别":
                st.markdown(f"**处理模式：** {record['process_mode']}")
                st.markdown(f"**总图片数：** {record['total_images']}")
                st.markdown(f"**成功数量：** {record['success_count']}")
                st.markdown(f"**失败数量：** {record['failed_count']}")
                
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
    <p>© 2025 城市建筑物识别系统 | 技术支持：AIE52期-5组</p>
</div>
""", unsafe_allow_html=True)