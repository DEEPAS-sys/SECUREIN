"""
Object detection runner using PyTorch/ONNX
"""
import torch
import torchvision
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.transforms import functional as F
import numpy as np
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DetectionRunner:
    """Object detection inference runner"""
    
    def __init__(self, model_path: str = None, device: str = "cuda"):
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Load pretrained model (using Faster R-CNN as example)
        if model_path:
            self.model = torch.load(model_path, map_location=self.device)
        else:
            # Use pretrained model
            self.model = fasterrcnn_resnet50_fpn(pretrained=True)
        
        self.model.to(self.device)
        self.model.eval()
        
        # COCO class names
        self.class_names = [
            '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
            'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
            'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse',
            'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
            'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis',
            'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
            'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass',
            'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
            'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
            'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
            'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
            'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
            'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
            'hair drier', 'toothbrush'
        ]
    
    def preprocess(self, frames: List[np.ndarray]) -> torch.Tensor:
        """Preprocess frames for inference"""
        tensors = []
        for frame in frames:
            # Convert BGR to RGB
            frame_rgb = frame[:, :, ::-1].copy()
            # Convert to tensor and normalize
            tensor = F.to_tensor(frame_rgb)
            tensors.append(tensor)
        
        return tensors
    
    def run_batch(self, frames: List[np.ndarray], confidence_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Run inference on batch of frames"""
        if not frames:
            return []
        
        try:
            # Preprocess
            tensors = self.preprocess(frames)
            tensors = [t.to(self.device) for t in tensors]
            
            # Run inference
            with torch.no_grad():
                predictions = self.model(tensors)
            
            # Post-process results
            results = []
            for pred in predictions:
                detections = []
                boxes = pred['boxes'].cpu().numpy()
                labels = pred['labels'].cpu().numpy()
                scores = pred['scores'].cpu().numpy()
                
                for box, label, score in zip(boxes, labels, scores):
                    if score >= confidence_threshold:
                        detections.append({
                            'class': self.class_names[label],
                            'confidence': float(score),
                            'bbox': box.tolist(),  # [x1, y1, x2, y2]
                        })
                
                results.append({'detections': detections})
            
            return results
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return [{'detections': []} for _ in frames]
    
    def export_to_onnx(self, output_path: str, input_shape: tuple = (3, 640, 640)):
        """Export model to ONNX format"""
        dummy_input = torch.randn(1, *input_shape).to(self.device)
        
        torch.onnx.export(
            self.model,
            dummy_input,
            output_path,
            export_params=True,
            opset_version=11,
            do_constant_folding=True,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={
                'input': {0: 'batch_size'},
                'output': {0: 'batch_size'}
            }
        )
        
        logger.info(f"Model exported to {output_path}")


if __name__ == "__main__":
    # Test runner
    runner = DetectionRunner(device="cpu")
    
    # Create dummy frame
    dummy_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Run inference
    results = runner.run_batch([dummy_frame])
    print(f"Detections: {results}")
