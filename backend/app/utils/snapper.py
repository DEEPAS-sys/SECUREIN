"""
Snapshot utility for capturing and saving frames.
"""
import cv2
import numpy as np
from datetime import datetime
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Snapper:
    """Utility for capturing and processing snapshots."""
    
    @staticmethod
    def save_frame(frame: np.ndarray, output_path: str, quality: int = 95) -> bool:
        """Save frame as JPEG image."""
        try:
            cv2.imwrite(
                output_path,
                frame,
                [cv2.IMWRITE_JPEG_QUALITY, quality]
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save frame: {e}")
            return False
    
    @staticmethod
    def draw_detections(
        frame: np.ndarray,
        detections: list,
        show_labels: bool = True
    ) -> np.ndarray:
        """Draw bounding boxes and labels on frame."""
        annotated = frame.copy()
        
        for detection in detections:
            bbox = detection.get("bbox", [])
            if len(bbox) != 4:
                continue
            
            x1, y1, x2, y2 = map(int, bbox)
            
            # Draw rectangle
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            if show_labels:
                label = detection.get("class", "unknown")
                confidence = detection.get("confidence", 0)
                text = f"{label} {confidence:.2f}"
                
                # Draw label background
                (w, h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(annotated, (x1, y1 - 20), (x1 + w, y1), (0, 255, 0), -1)
                
                # Draw label text
                cv2.putText(
                    annotated,
                    text,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 0),
                    1
                )
        
        return annotated
    
    @staticmethod
    def encode_frame_jpeg(frame: np.ndarray, quality: int = 95) -> Optional[bytes]:
        """Encode frame to JPEG bytes."""
        try:
            encode_param = [cv2.IMWRITE_JPEG_QUALITY, quality]
            _, encoded = cv2.imencode('.jpg', frame, encode_param)
            return encoded.tobytes()
        except Exception as e:
            logger.error(f"Failed to encode frame: {e}")
            return None
    
    @staticmethod
    def decode_frame_jpeg(data: bytes) -> Optional[np.ndarray]:
        """Decode JPEG bytes to frame."""
        try:
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return frame
        except Exception as e:
            logger.error(f"Failed to decode frame: {e}")
            return None
