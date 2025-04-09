import streamlit as st
# import torch
from PIL import Image
import numpy as np
import cv2
cv2.setUseOptimized(True)
cv2.setNumThreads(4)

from pathlib import Path
import time
import os
from utils.model_detector import ModelDetector
from utils.db_manager import DBManager

# 设置页面配置
st.set_page_config(
    page_title="单张图片检测 - 城市建筑物检测系统",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加页眉图片
image_path = os.path.join(Path(__file__).parent.parent,"images")
st.image(os.path.join(image_path,"single_header.svg"), use_container_width=True)

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
    
    /* 上传区域样式 */
    .upload-box {
        border: 2px dashed #ccc;
        padding: 1.5rem;
        text-align: center;
        border-radius: 12px;
        background: #ffffff;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin: 1rem 0;
    }
    .upload-box:hover {
        border-color: #0083B8;
        box-shadow: 0 4px 12px rgba(0,131,184,0.1);
    }
    
    /* 结果区域样式 */
    .result-box {
        background: linear-gradient(to bottom right, #ffffff, #f8f9fa);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        margin: 1rem 0;
    }
    .result-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }
    
    /* 置信度条样式 */
    .confidence-meter {
        height: 24px;
        background-color: #e9ecef;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
    }
    .confidence-bar {
        height: 100%;
        background: linear-gradient(90deg, #0083B8, #00A3E0);
        transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
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
        .upload-box {
            padding: 1rem;
        }
        .result-box {
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

# 主页面标题和介绍
st.title("🏢 单张图片检测")

# 上传区域单独一行
st.markdown("### 📤 上传区域")
# st.markdown("<div class='upload-box' style='min-height: 100px;'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("选择一张包含建筑物的图片", type=['jpg', 'jpeg', 'png'])

start_dect = st.button("🔍 开始检测", type="primary")

# 创建两列布局用于图片预览和检测结果
col1, col2 = st.columns([1, 1])

# 检查是否有上传图片
if start_dect and uploaded_file is None:
    st.warning("⚠️ 请先上传需要检测的图片")
    st.stop()

if uploaded_file is not None:
    # 检查是否是新上传的文件
    if 'last_uploaded_file' not in st.session_state or st.session_state['last_uploaded_file'] != uploaded_file.name:
        # 上传新图片时清空之前的检测结果
        if 'processed' in st.session_state:
            del st.session_state['processed']
        if 'detections' in st.session_state:
            del st.session_state['detections']
        if 'viz_img' in st.session_state:
            del st.session_state['viz_img']
        # 记录当前上传的文件名
        st.session_state['last_uploaded_file'] = uploaded_file.name
        
    if start_dect:
        with st.spinner('正在进行建筑物检测分析...'):
            # 初始化YOLO检测器
            detector = ModelDetector(model_name=model_name)
            
            # 加载并处理图像
            image = Image.open(uploaded_file)
            if not isinstance(image, Image.Image):
                st.error("无法加载图像文件，请确保上传的是有效的图像文件")
                st.stop()
            
            # 执行检测
            detections, viz_img = detector.detect(image, conf_thres=confidence_threshold)
            
            # 确保viz_img是RGB格式的numpy数组
            if isinstance(viz_img, Image.Image):
                viz_img = np.array(viz_img)
            elif isinstance(viz_img, np.ndarray):
                if len(viz_img.shape) == 3 and viz_img.shape[2] == 3:
                    # YOLODetector返回BGR格式，需要转换为RGB
                    viz_img = cv2.cvtColor(viz_img, cv2.COLOR_BGR2RGB)
            
            # 确保检测结果图像是正确的格式
            if viz_img is None:
                st.error("图像处理失败，请重试")
                st.stop()
            
            st.success("✨ 检测完成！")
            st.session_state['processed'] = True
            st.session_state['detections'] = detections
            st.session_state['viz_img'] = viz_img
            
            # 保存检测结果到数据库
            db_manager = DBManager()
            try:
                # 创建保存检测结果的目录
                results_dir = Path(__file__).parent.parent / 'data' / 'detection_results'
                results_dir.mkdir(parents=True, exist_ok=True)
            
                # 保存图片到结果目录，使用相对路径
                result_img_name = f"{int(time.time())}_{uploaded_file.name}"
                result_img_path = results_dir / result_img_name
                Image.fromarray(viz_img).save(result_img_path)
                # 使用相对路径保存到数据库
                relative_img_path = f"data/detection_results/{result_img_name}"
            
                # 获取置信度最高的检测结果作为主要建筑类型
                valid_detections = [d for d in detections if d['confidence'] >= confidence_threshold]
                if valid_detections:
                    main_detection = max(valid_detections, key=lambda x: x['confidence'])
                    print(f"准备写入数据库的数据：\n图片路径: {relative_img_path}\n建筑类型: {main_detection['class']}\n置信度: {main_detection['confidence']}\n检测到的建筑物数量: {len(valid_detections)}")
                    try:
                        db_manager.add_single_detection(
                            image_path=relative_img_path,
                            building_type=main_detection['class'],
                            confidence=main_detection['confidence'],
                            feature_description=f"检测到 {len(valid_detections)} 个建筑物",
                            detection_mode="单图检测",
                            detection_result={
                                'main_detection': main_detection,
                                'all_detections': valid_detections
                            }
                        )
                        print("✅ 数据库写入成功")
                        st.success("✅ 检测结果已成功保存到历史记录")
                    except Exception as db_error:
                        print(f"❌ 数据库写入失败: {str(db_error)}")
                        st.error(f"❌ 保存到数据库失败: {str(db_error)}")
                        # 记录详细错误信息以便调试
                        print(f"数据库保存错误: {str(db_error)}")
                else:
                    print("⚠️ 未检测到置信度达标的建筑物，结果未保存")
                    st.warning("⚠️ 未检测到置信度达标的建筑物，结果未保存")
            except Exception as e:
                print(f"❌ 保存检测结果失败: {str(e)}")
                st.error(f"❌ 保存检测结果失败: {str(e)}")
                # 记录详细错误信息以便调试
                print(f"文件保存错误: {str(e)}")

st.markdown("</div>", unsafe_allow_html=True)

with col1:
    st.markdown("### 🖼️ 图片预览")
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='预览图片', use_container_width=True)

with col2:
    st.markdown("### 📊 检测结果")
    if uploaded_file is not None and st.session_state.get('processed', False):
        detections = st.session_state.get('detections', [])
        viz_img = st.session_state.get('viz_img')
        
        # 显示检测结果图像
        # 检查viz_img是否为None或空数组
        if viz_img is not None and viz_img.size > 0:
            try:
                st.image(viz_img, caption="建筑物检测结果", use_container_width=True)
            except Exception as e:
                st.error(f"显示检测结果图像时出错: {str(e)}")
        else:
            st.warning("未能生成检测结果图像")
        
        # 显示检测统计信息
        st.markdown("#### 📊 检测统计")
        valid_detections = [d for d in detections if d['confidence'] >= confidence_threshold]
        
        stats_col1, stats_col2 = st.columns(2)
        with stats_col1:
            st.metric("检测到的建筑物数量", len(valid_detections))
        with stats_col2:
            if valid_detections:
                avg_conf = sum(d['confidence'] for d in valid_detections) / len(valid_detections)
                st.metric("平均置信度", f"{avg_conf:.2%}")
            else:
                st.metric("平均置信度", "0%")
        
        # 提供导出选项
        st.markdown("#### 💾 导出选项")
        st.download_button(
            label="📥 导出检测结果图像",
            data=cv2.imencode('.png', viz_img if viz_img is not None else np.zeros((100,100,3), dtype=np.uint8))[1].tobytes(),
            file_name="detection_result.png",
            mime="image/png"
        )
        
        st.markdown("</div>", unsafe_allow_html=True)

# 添加页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>© 2025 城市建筑物检测系统 | 技术支持：AIE52期-5组</p>
</div>
""", unsafe_allow_html=True)