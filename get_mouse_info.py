
from ultralytics import YOLO

# 모델 로드 및 훈련
model = YOLO("yolov8n.pt")  # 기본 YOLOv8 Nano 모델
model.train(data="C:/Users/redblonze/Documents/RedB/TrainImage/Mapleland-1/data.yaml", epochs=100, imgsz=640)