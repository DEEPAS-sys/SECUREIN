# Model storage directory

This directory stores AI models for inference.

## Model Downloads

Due to size constraints, models are not included in the repository.

### Object Detection
Download pretrained models:
```bash
# YOLOv5
wget https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt

# Or use torchvision models (automatic download)
# Models will be cached in ~/.cache/torch/hub/
```

### Face Recognition
```bash
# Download face recognition models
# Example: InsightFace ArcFace
# https://github.com/deepinsight/insightface
```

### License Plate Recognition
```bash
# Download LPR models
# Example: PaddleOCR models
# https://github.com/PaddlePaddle/PaddleOCR
```

## Model Conversion

Convert PyTorch models to ONNX/TensorRT:

```bash
# ONNX export
python3 runners/detect.py --export-onnx

# TensorRT conversion (requires TensorRT installed)
trtexec --onnx=model.onnx --saveEngine=model.trt --fp16
```

## Supported Formats
- PyTorch (.pt, .pth)
- ONNX (.onnx)
- TensorRT (.trt, .engine)
- OpenVINO (.xml, .bin)
