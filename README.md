# 智能建筑物识别系统

## 项目简介
本系统采用先进的深度学习技术，提供精准的建筑物识别和分类服务。支持单图识别、批量处理和变化检测功能。

## 核心功能
- 🔍 单图识别：快速精准的识别，提供详细的分析报告
- 📑 批量识别：支持大规模建筑物分析，自动生成报告
- 🔄 变化检测：自动检测和标注建筑物的变化情况
- 📊 历史记录：查看和管理所有历史检测记录

## 目录结构
```
Building-Recognition/
├── .devcontainer/      # 开发容器配置
│   └── devcontainer.json
├── data/               # 数据存储
│   ├── history.db      # 历史记录数据库
│   └── db_operations.log # 数据库操作日志
├── images/             # 系统图片资源
│   ├── batch_header.svg # 批量检测页头图
│   ├── change_header.svg # 变化检测页头图
│   ├── home_header.svg  # 首页头图
│   └── single_header.svg # 单图检测页头图
├── model/              # 模型文件
│   ├── build-12s.pt    # 建筑物识别模型(轻量版)
│   ├── build_V8n.pt    # 建筑物识别模型(标准版)
│   └── yolo11n.pt      # YOLO检测模型
├── pages/              # 功能页面
│   ├── 1_🏢 单图检测.py    # 单图检测页面
│   ├── 2_📑 批量检测.py    # 批量检测页面
│   ├── 3_🔄 变化检测.py    # 变化检测页面
│   ├── 4_📊 历史记录.py    # 历史记录页面
│   └── 5_👥 项目团队.py    # 项目团队页面
├── utils/              # 工具模块
│   ├── db_manager.py   # 数据库管理工具
│   └── model_detector.py # 模型检测工具
├── 首页.py             # 系统首页
└── README.md           # 项目说明
```

## 项目部署
### 环境配置
1. 确保已安装Python 3.8或以上版本
2. 推荐使用conda或virtualenv创建虚拟环境

### 依赖安装
1. 安装项目依赖：`pip install -r requirements.txt`
2. 系统要求：Python 3.8+，支持CUDA的GPU（可选）
3. 主要依赖版本：
   - PyTorch >= 2.0.0
   - Torchvision >= 0.15.0
   - Streamlit >= 1.28.0
   - Ultralytics >= 8.0.0

### 数据库初始化
1. 首次运行时，系统会自动创建SQLite数据库
2. 数据库文件位于`data/history.db`

### 启动项目
1. 运行命令：`streamlit run 首页.py`
2. 访问 http://localhost:8501 使用系统

## 贡献指南
1. Fork本项目
2. 创建新的分支：`git checkout -b feature/YourFeature`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送分支：`git push origin feature/YourFeature`
5. 发起Pull Request

## 许可证
MIT License

## 联系方式
技术支持：AIE52期-5组