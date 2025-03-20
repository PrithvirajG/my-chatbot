import magic
import tempfile
from typing import Dict, Any
from loguru import logger
from PyPDF2 import PdfReader
import cv2
from ..core.model_router import model_router

SUPPORTED_MIME_TYPES = {
    "application/pdf": "pdf",
    "image/jpeg": "image",
    "image/png": "image",
    "video/mp4": "video",
    "audio/wav": "audio"
}

class FileProcessor:
    def __init__(self):
        self.max_file_size = 100 * 1024 * 1024  # 100MB

    def validate_file(self, file_data: bytes) -> str:
        """Validate file type and size"""
        if len(file_data) > self.max_file_size:
            raise ValueError(f"File size exceeds {self.max_file_size//(1024*1024)}MB limit")
        
        mime_type = magic.from_buffer(file_data, mime=True)
        file_type = SUPPORTED_MIME_TYPES.get(mime_type)
        
        if not file_type:
            raise ValueError(f"Unsupported file type: {mime_type}")
            
        return file_type

    def process(self, file_type: str, file_data: bytes) -> Dict[str, Any]:
        """Route processing based on file type"""
        processors = {
            "pdf": self._process_pdf,
            "image": self._process_image,
            "video": self._process_video,
            "audio": self._process_audio
        }
        
        if file_type not in processors:
            raise ValueError(f"No processor for file type: {file_type}")
            
        return processors[file_type](file_data)

    def _process_pdf(self, file_data: bytes) -> Dict[str, Any]:
        """Extract text from PDF"""
        with tempfile.NamedTemporaryFile(delete=True) as tmp:
            tmp.write(file_data)
            reader = PdfReader(tmp.name)
            text = "\n".join([page.extract_text() for page in reader.pages])
            return {"type": "pdf", "content": text}

    def _process_image(self, file_data: bytes) -> Dict[str, Any]:
        """Analyze image using vision model"""
        vision_model = model_router.get_model("vision")
        
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as tmp:
            tmp.write(file_data)
            result = vision_model(tmp.name)
            
        return {
            "type": "image",
            "analysis": result[0]['generated_text'],
            "model": os.getenv("VISION_MODEL")
        }

    def _process_video(self, file_data: bytes) -> Dict[str, Any]:
        """Extract key frames from video"""
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=True) as tmp:
            tmp.write(file_data)
            cap = cv2.VideoCapture(tmp.name)
            
            frames = []
            frame_interval = 30  # Process 1 frame per second (assuming 30fps)
            frame_count = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    frames.append(frame)
                
                frame_count += 1
                
            return {"type": "video", "frame_count": len(frames)}

    def _process_audio(self, file_data: bytes) -> Dict[str, Any]:
        """Transcribe audio using voice model"""
        voice_model = model_router.get_model("voice")
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
            tmp.write(file_data)
            result = voice_model.transcribe(tmp.name)
            
        return {"type": "audio", "transcript": result["text"]}

file_processor = FileProcessor()