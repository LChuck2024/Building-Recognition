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
│   ├── build_V8n.pt    # 建筑物识别模型
│   └── yolo11n.pt      # YOLO检测模型
├── pages/              # 功能页面
│   ├── 1_单图检测.py    # 单图检测页面
│   ├── 2_批量检测.py    # 批量检测页面
│   ├── 3_变化检测.py    # 变化检测页面
│   └── 4_历史记录.py    # 历史记录页面
├── utils/              # 工具模块
│   ├── db_manager.py   # 数据库管理工具
│   ├── model_detector.py # 模型检测工具
│   ├── fcn_resnet50_model_test.py # ResNet50测试
│   ├── unet_model_test.py # U-Net测试
│   └── test_db_manager.py # 数据库管理测试
├── 首页.py             # 系统首页
└── README.md           # 项目说明
```

## 项目部署
### 环境配置
1. 确保已安装Python 3.8或以上版本
2. 推荐使用conda或virtualenv创建虚拟环境

### 依赖安装
1. 安装项目依赖：`pip install -r requirements.txt`
2. 安装PyTorch：根据系统配置选择合适的版本

### 数据库初始化
1. 首次运行时，系统会自动创建SQLite数据库
2. 数据库文件位于`data/history.db`

### 启动项目
1. 运行命令：`streamlit run 首页.py`
2. 访问 http://localhost:8501 使用系统

## 使用说明
### 单图识别
1. 点击'单图识别'按钮
2. 上传单张建筑物图片
3. 查看识别结果和详细分析报告

### 批量识别
1. 点击'批量识别'按钮
2. 上传多张建筑物图片（支持.zip压缩包）
3. 系统自动处理并生成批量报告
4. 下载完整分析报告

### 变化检测
1. 点击'变化检测'按钮
2. 上传同一位置不同时期的建筑物图片
3. 系统自动分析变化区域
4. 查看变化检测报告

## 技术细节
- 前端框架：Streamlit
- 深度学习框架：PyTorch
- 数据库：SQLite

## 许可证
MIT License

## 联系方式
技术支持：AIE52期-5组