import streamlit as st
import pandas as pd
import time
import os
from pathlib import Path
from utils.model_detector import ModelDetector
from utils.db_manager import DBManager

# 设置页面配置
st.set_page_config(
    page_title="批量建筑物检测 - 智能建筑物检测系统",
    page_icon="📑",
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
    
    /* 响应式容器 */
    .container {
        width: 100%;
        padding-right: 15px;
        padding-left: 15px;
        margin-right: auto;
        margin-left: auto;
    }
    
    /* 图片圆角样式 */
    img {
        border-radius: 12px;
        max-width: 100%;
        height: auto;
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
    
    .batch-upload-box {
        border: 2px dashed #0083B8;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        background: rgba(0,131,184,0.05);
        margin-bottom: 1.5rem;
    }
    .result-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .progress-container {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .summary-box {
        background: linear-gradient(45deg, #0083B8, #00A3E0);
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    /* 响应式布局 */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
        .batch-upload-box {
            padding: 1rem;
        }
        .result-card,
        .progress-container,
        .summary-box {
            padding: 1rem;
        }
        h1 {
            font-size: 1.8rem;
        }
        h2 {
            font-size: 1.5rem;
        }
        h3 {
            font-size: 1.2rem;
        }
    }
    
    /* 弹性布局容器 */
    .flex-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin: 1rem 0;
    }
    .flex-item {
        flex: 1;
        min-width: 250px;
    }
</style>
""", unsafe_allow_html=True)

# 添加页眉图片
image_path = os.path.join(Path(__file__).parent.parent,"images")
st.image(os.path.join(image_path,"batch_header.svg"), use_container_width=True)

# 页面标题
st.title("📑 批量建筑物检测")
st.markdown("同时上传多张图片进行批量检测检测")



# 侧边栏设置
with st.sidebar:
    st.markdown("### 检测设置")
    # 初始化或恢复session_state中的设置
    if 'confidence_threshold' not in st.session_state:
        st.session_state.confidence_threshold = 0.5
    if 'show_label' not in st.session_state:
        st.session_state.show_label = True
    if 'model_name' not in st.session_state:
        st.session_state.model_name = 'yolo11n.pt'

    # 获取model目录下的所有模型文件
    model_dir = Path(__file__).parent.parent / 'model'
    model_files = list(model_dir.glob('*.pt')) + list(model_dir.glob('*.pth'))
    model_files = [f.name for f in model_files]
    
    if not model_files:
        st.error("未找到可用的模型文件，请确保model目录中存在.pt或.pth格式的模型文件")
        model_files = ['yolo11n.pt']  # 设置默认值
    
    model_name = st.selectbox(
        "选择模型",
        options=model_files,
        help="选择不同的预训练模型进行检测",
        on_change=lambda: setattr(st.session_state, 'model_name', model_name)
    )
    
    if 'model_name' not in st.session_state:
        st.session_state.model_name = 'yolo11n.pt'
    
    print(f'页面选择模型：{model_name}')

    
    confidence_threshold = st.slider(
        "置信度阈值",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.get('confidence_threshold', 0.5),
        help="调整检测的置信度阈值，值越高要求越严格",
        on_change=lambda: setattr(st.session_state, 'confidence_threshold', confidence_threshold)
    )

    if 'iou_threshold' not in st.session_state:
        st.session_state.iou_threshold = 0.45

    iou_threshold = st.slider(
        "IOU阈值",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.get('iou_threshold', 0.45),
        help="调整检测的IOU阈值，值越高要求越严格",
        on_change=lambda: setattr(st.session_state, 'iou_threshold', iou_threshold)
    )

# 文件上传区域
st.markdown("### 📤 上传图片")

uploaded_files = st.file_uploader(
    "拖拽或选择多张建筑物图片，支持 .jpg、.jpeg、.png 格式",
    type=['jpg', 'jpeg', 'png'],
    accept_multiple_files=True
)

# 显示上传的图片预览
if uploaded_files:
    st.markdown("### 🖼️ 图片预览")
    # 创建图片网格布局
    num_cols = 5  # 每行显示的图片数量
    image_rows = [uploaded_files[i:i+num_cols] for i in range(0, len(uploaded_files), num_cols)]
    
    for row in image_rows:
        cols = st.columns(num_cols)
        for i, image_file in enumerate(row):
            with cols[i]:
                # 显示图片,设置图片高度为200像素
                st.image(image_file, caption=image_file.name,use_container_width=True)
                # 添加文件名标签
                # st.markdown(f"<p style='text-align: center; font-size: 0.8rem;'>{image_file.name}</p>", unsafe_allow_html=True)

# 开始检测按钮
start_batch_detect = st.button("🚀 开始批量检测", type="primary")

# 检查是否有上传图片
if start_batch_detect and not uploaded_files:
    st.warning("⚠️ 请先上传需要检测的图片")
    st.stop()

if uploaded_files and start_batch_detect:
        # 显示检测进度
        st.markdown("### 📊 检测进度")
        progress_container = st.empty()
        progress_bar = st.progress(0)
        status_text = st.empty()

        detector = ModelDetector(model_name=model_name)
        
        total_files = len(uploaded_files)
        results = []
        
        # 使用横向布局显示检测后的图片
        st.markdown("### 🖼️ 检测结果预览[前5张]")
        result_cols = st.columns(5)  # 创建5列布局

        for i, file in enumerate(uploaded_files):
            start_time = time.time()
            
            # 更新进度
            progress = (i + 1) / total_files
            progress_bar.progress(progress)
            status_text.text(f"正在检测: {file.name} ({i+1}/{total_files})")
            
            try:
                # 执行检测
                detections, plotted_image = detector.detect(file, conf_thres=confidence_threshold ,iou_thres = iou_threshold)
                
                # 获取检测结果统计
                if detections:
                    # 统计检测到的目标数量
                    detection_count = len(detections)
                    # 获取最高置信度的检测结果
                    best_detection = max(detections, key=lambda x: x['confidence'])
                    confidence = best_detection['confidence'] #round(best_detection['confidence'] * 100, 1)
                    building_type = best_detection['label']
                else:
                    detection_count = 0
                    confidence = 0
                    building_type = '未检测到建筑物'
                
                # 计算检测时间
                process_time = time.time() - start_time
                
                # 保存结果
                results.append({
                    '文件名': file.name,
                    '建筑物类型': building_type,
                    '检测目标数量': detection_count,
                    '置信度': confidence,
                    '检测时间': f"{process_time:.1f}秒"
                })
                
                # 显示检测后的图片
                if i < 5:  # 只显示前5张图片的检测结果
                    with result_cols[i]:
                        st.image(plotted_image, caption=f"检测结果: {file.name}", use_container_width=True)
                    
            except Exception as e:
                st.error(f"检测文件 {file.name} 时出错: {str(e)}")
                continue
        
        # 显示检测完成信息
        st.success(f"✨ 批量检测完成！共检测 {total_files} 张图片")
        
        # 保存历史记录
        try:
            db = DBManager()
            db.add_batch_detection(
                total_images=total_files,
                success_count=len([r for r in results if r['检测目标数量'] > 0]),
                failed_count=len([r for r in results if r['检测目标数量'] == 0]),
                confidence=confidence,
                batch_result=results
            )
        except Exception as e:
            st.warning(f"保存历史记录失败: {str(e)}")
        
        # 显示检测结果摘要
        st.markdown("### 📈 检测结果摘要")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class='summary-box'>
                <h3>总检测图片</h3>
                <h2>{}</h2>
            </div>
            """.format(total_files), unsafe_allow_html=True)
        with col2:
            avg_confidence = sum(result['置信度'] for result in results) / len(results) if results else 0
            st.markdown("""
            <div class='summary-box'>
                <h3>平均置信度</h3>
                <h2>{:.1f}</h2>
            </div>
            """.format(avg_confidence), unsafe_allow_html=True)
        with col3:
            total_time = sum(float(result['检测时间'].replace('秒', '')) for result in results)
            st.markdown("""
            <div class='summary-box'>
                <h3>总耗时</h3>
                <h2>{:.1f}秒</h2>
            </div>
            """.format(total_time), unsafe_allow_html=True)
        
        # 显示详细结果
        st.markdown("### 📋 详细结果")
        results_df = pd.DataFrame(results)
        st.dataframe(results_df, use_container_width=True)
        
        # 导出选项
        st.markdown("### 📥 导出结果")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="下载CSV报告",
                data=results_df.to_csv(index=False).encode('utf-8'),
                file_name='batch_recognition_results.csv',
                mime='text/csv'
            )
        with col2:
            # 使用ExcelWriter对象检测Excel导出
            with pd.ExcelWriter('batch_recognition_results.xlsx', engine='openpyxl') as writer:
                results_df.to_excel(writer, index=False)
                # ExcelWriter会自动保存，不需要显式调用save()
            with open('batch_recognition_results.xlsx', 'rb') as f:
                excel_data = f.read()
            st.download_button(
                label="下载Excel报告",
                data=excel_data,
                file_name='batch_recognition_results.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
else:
    st.info("👆 请先上传需要检测的图片")

# 添加页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>© 2025 城市建筑物检测系统 | 技术支持：AIE52期-5组</p>
</div>
""", unsafe_allow_html=True)