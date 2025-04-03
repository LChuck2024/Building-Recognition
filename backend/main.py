from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import io
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

# 导入YOLO检测器
from utils.yolo_detector import YOLODetector

app = FastAPI(
    title="建筑物识别API",
    description="城市建筑物识别系统的后端API服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化检测器
detector = YOLODetector()

@app.get("/")
async def read_root():
    return {"message": "欢迎使用建筑物识别API"}

@app.post("/detect/single")
async def detect_single_image(
    file: UploadFile = File(...),
    confidence_threshold: float = 0.5,
    show_label: bool = True
):
    try:
        # 读取上传的图片
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # 执行检测
        detections = detector.detect(image, conf_thres=confidence_threshold)
        
        # 处理检测结果
        results = []
        for det in detections:
            results.append({
                "class": det["class"],
                "confidence": det["confidence"],
                "bbox": det["bbox"]
            })
        
        return JSONResponse({
            "status": "success",
            "message": "检测完成",
            "data": {
                "detections": results,
                "total_objects": len(results)
            }
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect/batch")
async def detect_batch_images(
    files: list[UploadFile] = File(...),
    confidence_threshold: float = 0.5,
    show_label: bool = True
):
    try:
        results = []
        for file in files:
            # 读取图片
            contents = await file.read()
            image = Image.open(io.BytesIO(contents))
            
            # 执行检测
            detections = detector.detect(image, conf_thres=confidence_threshold)
            
            # 处理检测结果
            image_results = []
            for det in detections:
                image_results.append({
                    "class": det["class"],
                    "confidence": det["confidence"],
                    "bbox": det["bbox"]
                })
            
            results.append({
                "filename": file.filename,
                "detections": image_results,
                "total_objects": len(image_results)
            })
        
        return JSONResponse({
            "status": "success",
            "message": "批量检测完成",
            "data": {
                "results": results,
                "total_files": len(files)
            }
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)