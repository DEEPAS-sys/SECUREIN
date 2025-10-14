"""
FFmpeg wrapper for video stream processing
"""
import subprocess
import asyncio
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class FFmpegWrapper:
    """Wrapper for FFmpeg operations"""
    
    @staticmethod
    async def probe_stream(rtsp_url: str, timeout: int = 5) -> dict:
        """Probe RTSP stream to check connectivity"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'stream=codec_type,width,height,r_frame_rate',
                '-of', 'json',
                '-rtsp_transport', 'tcp',
                '-timeout', str(timeout * 1000000),  # microseconds
                rtsp_url
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            if process.returncode != 0:
                logger.error(f"FFprobe error: {stderr.decode()}")
                return {"success": False, "error": stderr.decode()}
            
            import json
            result = json.loads(stdout.decode())
            return {"success": True, "info": result}
            
        except asyncio.TimeoutError:
            return {"success": False, "error": "Probe timeout"}
        except Exception as e:
            logger.error(f"Probe error: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def extract_frame(rtsp_url: str, output_path: str, timestamp: Optional[float] = None):
        """Extract a single frame from stream"""
        cmd = ['ffmpeg', '-y']
        
        if timestamp:
            cmd.extend(['-ss', str(timestamp)])
        
        cmd.extend([
            '-rtsp_transport', 'tcp',
            '-i', rtsp_url,
            '-frames:v', '1',
            '-q:v', '2',
            output_path
        ])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=10)
            return True
        except Exception as e:
            logger.error(f"Frame extraction error: {e}")
            return False
    
    @staticmethod
    def create_hls_stream(rtsp_url: str, output_dir: str, segment_duration: int = 4):
        """Create HLS stream from RTSP source"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        cmd = [
            'ffmpeg',
            '-rtsp_transport', 'tcp',
            '-i', rtsp_url,
            '-c:v', 'libx264',
            '-preset', 'veryfast',
            '-g', '48',
            '-sc_threshold', '0',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-f', 'hls',
            '-hls_time', str(segment_duration),
            '-hls_list_size', '10',
            '-hls_flags', 'delete_segments',
            f'{output_dir}/playlist.m3u8'
        ]
        
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
