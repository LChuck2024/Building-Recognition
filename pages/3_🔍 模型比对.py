from re import S
import streamlit as st
import time
import pandas as pd
import plotly.express as px
import os
from pathlib import Path
from utils.model_detector import ModelDetector
from PIL import Image
import json

st.set_page_config(
    page_title="多模型比对",
    page_icon="🔍",
    layout="wide"
)

# 自定义CSS样式
st.markdown("""
<style>
    h3 {
        font-size: 1.0rem !important;
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
</style>
""", unsafe_allow_html=True)

# 添加页眉图片
image_path = os.path.join(Path(__file__).parent.parent,"images")
st.image(os.path.join(image_path,"comparison_header.svg"), use_container_width=True)


st.title("🔍 多模型比对")
st.write("同时使用多个模型进行检测并比对结果")

model_dir = Path(__file__).parent.parent / 'model'
model_files = list(model_dir.glob('*.pt')) + list(model_dir.glob('*.pth'))
model_options = [f.name for f in model_files]

# 模型选择
selected_models = st.multiselect(
    "选择要比较的模型",
    model_options,
    default=["build-12s.pt", "build_V8n.pt"]
)

if not selected_models:
    st.warning("请至少选择一个模型")
    st.stop()

# 图片上传
uploaded_file = st.file_uploader(
    "上传待检测图片",
    type=["jpg", "jpeg", "png"]
)

# 开始检测按钮
start_detect = st.button("🔍 开始模型比对", type="primary")

# 检查是否有上传图片
if start_detect and not uploaded_file:
    st.warning("⚠️ 请先上传需要检测的图片")
    st.stop()

# 检查是否有上传图片
if start_detect and uploaded_file:
    # 加载图片
    image = Image.open(uploaded_file)

    # 创建多列布局
    cols = st.columns(len(selected_models)+1)

    with cols[0]:
        st.subheader("原始图片")
        st.image(image, use_container_width=True)
        
    # 性能指标收集
    performance_data = []

    # 创建总进度条
    progress_text = '正在进行模型比对...'
    progress_bar = st.progress(0, text=progress_text)
    
    # 并行检测
    for i, model_name in enumerate(selected_models):
        # 更新总进度
        progress = (i) / len(selected_models)
        progress_bar.progress(progress, text=f'正在处理模型 {model_name} ({int(progress*100)}%)')
        
        with cols[i+1]:
            st.subheader(model_name.split('.')[0])
            
            try:
                # 初始化模型
                start_time = time.time()
                detector = ModelDetector(model_name)
                load_time = time.time() - start_time
                
                # 执行检测
                start_time = time.time()
                detections, plotted_image = detector.detect(image)
                detect_time = time.time() - start_time
                
                # 显示结果
                st.image(plotted_image, use_container_width=True)
                
                # 计算平均置信度
                avg_confidence = sum(d['confidence'] for d in detections) / len(detections) if detections else 0
                
                # 记录性能指标
                performance_data.append({
                    "模型": model_name,
                    "加载时间(秒)": round(load_time, 3),
                    "检测时间(秒)": round(detect_time, 3),
                    "检测数量": len(detections),
                    "平均置信度": round(avg_confidence, 3)
                })
                
                # 显示检测信息
                st.write(f"检测到 {len(detections)} 个建筑物")
                st.write(f"加载时间: {round(load_time, 3)}秒")
                st.write(f"检测时间: {round(detect_time, 3)}秒")
                st.write(f"平均置信度: {round(avg_confidence, 3)}")
                
                # 完成所有检测后，将进度条设置为100%
                progress_bar.progress(1.0, text='模型比对完成！')
                
            except Exception as e:
                st.error(f"模型 {model_name} 加载失败: {str(e)}")

    # 性能对比图表
    if performance_data:
        st.markdown("## 性能对比")
        # 分割线
        st.markdown("---")
        df = pd.DataFrame(performance_data)
        
            
        # 计算综合得分
        weights = {
            '加载时间(秒)': -0.2,  # 负权重，因为越小越好
            '检测时间(秒)': -0.2,  # 负权重，因为越小越好
            '检测数量': 0.3,      # 正权重
            '平均置信度': 0.3      # 正权重
        }
        
        # 数据标准化
        normalized_df = df.copy()
        for col in weights.keys():
            if weights[col] < 0:  # 对于需要最小化的指标
                normalized_df[col] = (df[col].max() - df[col]) / (df[col].max() - df[col].min())
            else:  # 对于需要最大化的指标
                normalized_df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
        
        # 计算综合得分
        total_score = pd.Series(0, index=df.index)
        for col, weight in weights.items():
            total_score += normalized_df[col] * abs(weight)
        
        # 添加综合得分到原始数据框
        df['综合得分'] = total_score.round(3)
        df = df.sort_values('综合得分', ascending=False)
        
        # 添加性能指标和综合得分表格
        st.markdown("### 📊 性能指标与综合评分")
        st.dataframe(
            df.style.background_gradient(
                subset=['加载时间(秒)', '检测时间(秒)', '检测数量', '平均置信度', '综合得分'],
                cmap='RdYlGn'
            ),
            use_container_width=True
        )
        
        # 计算综合评分
        # st.markdown("### 🏆 综合评估结果")
        # 创建四列布局
        col1, col2, col3, col4 = st.columns(4)
        
        # 加载时间对比
        fig1 = px.bar(
            df, 
            x="模型", 
            y="加载时间(秒)", 
            title="模型加载时间对比"
        )
        with col1:
            st.plotly_chart(fig1, use_container_width=True)
        
        # 检测时间对比
        fig2 = px.bar(
            df, 
            x="模型", 
            y="检测时间(秒)", 
            title="检测时间对比"
        )
        with col2:
            st.plotly_chart(fig2, use_container_width=True)
        
        # 检测数量对比
        fig3 = px.bar(
            df, 
            x="模型", 
            y="检测数量", 
            title="检测数量对比"
        )
        with col3:
            st.plotly_chart(fig3, use_container_width=True)
            
        # 平均置信度对比
        fig4 = px.bar(
            df, 
            x="模型", 
            y="平均置信度", 
            title="平均置信度对比"
        )
        with col4:
            st.plotly_chart(fig4, use_container_width=True)


        # 设定各指标权重
        weights = {
            '加载时间(秒)': -0.2,  # 负权重，因为越小越好
            '检测时间(秒)': -0.2,  # 负权重，因为越小越好
            '检测数量': 0.3,      # 正权重
            '平均置信度': 0.3      # 正权重
        }
        
        # 数据标准化
        normalized_df = df.copy()
        for col in weights.keys():
            if weights[col] < 0:  # 对于需要最小化的指标
                normalized_df[col] = (df[col].max() - df[col]) / (df[col].max() - df[col].min())
            else:  # 对于需要最大化的指标
                normalized_df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
        
        # 计算综合得分
        total_score = pd.Series(0, index=df.index)
        for col, weight in weights.items():
            total_score += normalized_df[col] * abs(weight)
        
        # 添加综合得分到原始数据框
        df['综合得分'] = total_score
        df = df.sort_values('综合得分', ascending=False)
        
        # 显示综合评估结果
        best_model = df.iloc[0]
        st.markdown(f"#### 🥇 最优模型推荐：{best_model['模型']}")
        
        # 创建优势分析文本
        advantages = []
        if best_model['加载时间(秒)'] == df['加载时间(秒)'].min():
            advantages.append("最快的模型加载速度")
        if best_model['检测时间(秒)'] == df['检测时间(秒)'].min():
            advantages.append("最快的检测速度")
        if best_model['检测数量'] == df['检测数量'].max():
            advantages.append("最高的检测数量")
        if best_model['平均置信度'] == df['平均置信度'].max():
            advantages.append("最高的平均置信度")
        
        # 显示优势分析
        st.markdown("### 💪 优势分析：")
        
        # 创建每个模型的优势分析
        for idx, model_data in df.iterrows():
            model_name = model_data['模型']
            st.markdown(f"#### {model_name}")
            
            advantages = []
            disadvantages = []
            
            # 分析加载时间
            if model_data['加载时间(秒)'] <= df['加载时间(秒)'].mean():
                advantages.append("✅ 模型加载速度较快")
            else:
                disadvantages.append("❌ 模型加载时间较长")
                
            # 分析检测时间
            if model_data['检测时间(秒)'] <= df['检测时间(秒)'].mean():
                advantages.append("✅ 检测速度优秀")
            else:
                disadvantages.append("❌ 检测速度较慢")
                
            # 分析检测数量
            if model_data['检测数量'] >= df['检测数量'].mean():
                advantages.append("✅ 检测数量较多，适合复杂场景")
            else:
                disadvantages.append("❌ 检测数量较少，可能会遗漏目标")
                
            # 分析平均置信度
            if model_data['平均置信度'] >= df['平均置信度'].mean():
                advantages.append("✅ 检测置信度高，结果可靠性好")
            else:
                disadvantages.append("❌ 检测置信度较低，可能存在误检")
                
            # 显示优势
            if advantages:
                st.markdown("**优势：**")
                for adv in advantages:
                    st.markdown(adv)
                    
            # 显示劣势
            if disadvantages:
                st.markdown("**劣势：**")
                for dis in disadvantages:
                    st.markdown(dis)
                    
            # 添加使用建议
            st.markdown("**适用场景：**")
            scenarios = []
            
            # 根据性能特点推荐适用场景
            if model_data['检测时间(秒)'] <= df['检测时间(秒)'].mean():
                scenarios.append("• 实时检测场景")
            if model_data['平均置信度'] >= df['平均置信度'].mean():
                scenarios.append("• 高精度要求场景")
            if model_data['检测数量'] >= df['检测数量'].mean():
                scenarios.append("• 密集建筑区域")
            if model_data['加载时间(秒)'] <= df['加载时间(秒)'].mean():
                scenarios.append("• 快速启动场景")
                
            for scenario in scenarios:
                st.markdown(scenario)
            
            st.markdown("---")  # 添加分隔线
        
        # # 显示详细得分
        # st.markdown("#### 📊 各模型得分排名：")
        # score_df = df[['模型', '综合得分']].copy()
        # score_df['综合得分'] = score_df['综合得分'].round(3)
        # st.dataframe(
        #     score_df.style.background_gradient(subset=['综合得分'], cmap='RdYlGn'),
        #     use_container_width=True
        # )
        
        # 添加建议
        st.markdown("#### 🎯 使用建议：")
        st.markdown(f"- 如果追求综合性能，推荐使用 **{best_model['模型']}**")
        fastest_model = df[df['检测时间(秒)'] == df['检测时间(秒)'].min()]['模型'].iloc[0]
        most_accurate_model = df[df['平均置信度'] == df['平均置信度'].max()]['模型'].iloc[0]
        st.markdown(f"- 如果追求检测速度，可以选择 **{fastest_model}**")
        st.markdown(f"- 如果追求检测准确度，建议使用 **{most_accurate_model}**")
            
        # 保存历史记录
        from utils.db_manager import DBManager
        db = DBManager()
        
        # 保存图片到临时文件
        temp_dir = Path(__file__).parent.parent / "temp"
        temp_dir.mkdir(exist_ok=True)
        image_path = str(temp_dir / f"comparison_{int(time.time())}.jpg")
        image.save(image_path)
        
        # 保存记录
        try:
            db.add_model_comparison(
                image_path=image_path,
                models=",".join(selected_models),
                performance_data=json.dumps(performance_data),
                detection_result=json.dumps({"detections": detections})
            )
            st.success("模型比对记录已保存")
        except Exception as e:
            st.error(f"保存记录失败: {str(e)}")

else:
    st.info("👆 请先上传需要检测的图片")

# 添加页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>© 2025 城市建筑物检测系统 | 技术支持：AIE52期-5组</p>
</div>
""", unsafe_allow_html=True)