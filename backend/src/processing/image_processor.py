from PIL import Image
from io import BytesIO
from loguru import logger
from src.core.model_router import model_router
from src.core.config_loader import settings

class ImageProcessor:
    def __init__(self):
        self.vision_model = model_router.get_model("vision")
        self.min_size = (224, 224)  # Minimum size for vision models

    def preprocess_image(self, image_data: bytes) -> Image.Image:
        """Validate and preprocess image data"""
        try:
            img = Image.open(BytesIO(image_data))
            
            # Convert to RGB if needed
            if img.mode != "RGB":
                img = img.convert("RGB")
                
            # Resize if below minimum size
            if any(dim < min_dim for dim, min_dim in zip(img.size, self.min_size)):
                img = img.resize(self.min_size)
                
            return img
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            raise ValueError("Invalid image data")

    def analyze_image(self, image_data: bytes) -> dict:
        """Analyze image using vision model"""
        try:
            img = self.preprocess_image(image_data)
            result = self.vision_model(img)
            
            return {
                "description": result[0]['generated_text'],
                "model": settings.VISION_MODEL_NAME,
                "dimensions": img.size
            }
        except Exception as e:
            logger.error(f"Image analysis failed: {str(e)}")
            raise RuntimeError("Image processing error")

image_processor = ImageProcessor()