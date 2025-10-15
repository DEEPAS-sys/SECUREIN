"""
FFmpeg wrapper utilities.
"""
import subprocess
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


class FFmpegWrapper:
    """Wrapper for FFmpeg operations."""
    
    @staticmethod
    def probe_stream(rtsp_url: str, timeout: int = 5) -> dict:
        """Probe RTSP stream and return stream information."""
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            '-rtsp_transport', 'tcp',
            rtsp_url
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
            else:
                logger.error(f"FFprobe error: {result.stderr}")
                return {}
        except subprocess.TimeoutExpired:
            logger.error(f"FFprobe timeout for {rtsp_url}")
            return {}
        except Exception as e:
            logger.error(f"FFprobe failed: {e}")
            return {}
    
    @staticmethod
    def extract_frame(rtsp_url: str, output_path: str, timestamp: Optional[str] = None) -> bool:
        """Extract a single frame from RTSP stream."""
        cmd = [
            'ffmpeg',
            '-rtsp_transport', 'tcp',
            '-i', rtsp_url,
            '-vframes', '1',
            '-f', 'image2',
            output_path
        ]
        
        if timestamp:
            cmd.insert(3, '-ss')
            cmd.insert(4, timestamp)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Frame extraction failed: {e}")
            return False
    
    @staticmethod
    def create_clip(
        input_file: str,
        output_file: str,
        start_time: str,
        duration: int = 10
    ) -> bool:
        """Create video clip from stream."""
        cmd = [
            'ffmpeg',
            '-ss', start_time,
            '-i', input_file,
            '-t', str(duration),
            '-c', 'copy',
            output_file
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Clip creation failed: {e}")
            return False
    
    @staticmethod
    def create_hls_stream(
        rtsp_url: str,
        output_dir: str,
        segment_time: int = 2
    ) -> subprocess.Popen:
        """Create HLS stream from RTSP."""
        cmd = [
            'ffmpeg',
            '-rtsp_transport', 'tcp',
            '-i', rtsp_url,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-f', 'hls',
            '-hls_time', str(segment_time),
            '-hls_list_size', '10',
            '-hls_flags', 'delete_segments',
            f'{output_dir}/index.m3u8'
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return process
        except Exception as e:
            logger.error(f"HLS stream creation failed: {e}")
            raise
