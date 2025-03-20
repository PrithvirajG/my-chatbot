import os
from typing import Dict, Any, Optional
from langchain_community.llms import LlamaCpp
from transformers import pipeline, AutoProcessor
import whisper
from loguru import logger
import torch

class ModelRouter:
    def __init__(self):
        self.models: Dict[str, Any] = {
            "text": None,
            "vision": None,
            "voice": None,
            "multimodal": None
        }
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.initialized = False

    def initialize_models(self):
        """Initialize all models with configuration from environment variables"""
        try:
            # Text Model
            self._load_text_model(os.getenv("TEXT_MODEL_PATH", "models/text/llama-2-7b-chat.Q4_K_M.gguf"))
            
            # Vision Model
            # self._load_vision_model(os.getenv("VISION_MODEL", "Salesforce/blip-image-captioning-base"))
            
            # Voice Model
            # self._load_voice_model(os.getenv("VOICE_MODEL_SIZE", "base"))
            self.initialized = True
            logger.success("All models initialized successfully")
        except Exception as e:
            logger.error(f"Model initialization failed: {str(e)}")
            raise

    def _load_text_model(self, model_path: str):
        logger.info(f"Loading text model from {model_path}")
        self.models["text"] = LlamaCpp(
            model_path=model_path,
            temperature=0.7,
            max_tokens=2000,
            n_ctx=4096,
            n_gpu_layers=-1 if self.device == "cuda" else 0,
            verbose=False
        )

    def _load_vision_model(self, model_name: str):
        logger.info(f"Loading vision model: {model_name}")
        self.models["vision"] = pipeline(
            "image-to-text",
            model=model_name,
            device=0 if self.device == "cuda" else -1
        )

    def _load_voice_model(self, model_size: str):
        logger.info(f"Loading voice model (size: {model_size})")
        try:
            self.models["voice"] = whisper.load_model(
                name=model_size,
                device=self.device
            )
        except ImportError:
            logger.error("Whisper not installed. Install with: pip install openai-whisper")
            raise


    def get_model(self, modality: str) -> Any:
        """Get model instance for specified modality"""
        if not self.initialized:
            raise RuntimeError("Models not initialized")
            
        model = self.models.get(modality)
        if not model:
            raise ValueError(f"Unsupported modality: {modality}")
        return model

    def switch_model(self, modality: str, model_identifier: str):
        """Hot-swap models at runtime"""
        logger.warning(f"Switching {modality} model to {model_identifier}")
        try:
            if modality == "text":
                self._load_text_model(model_identifier)
            elif modality == "vision":
                self._load_vision_model(model_identifier)
            elif modality == "voice":
                self._load_voice_model(model_identifier)
            else:
                raise ValueError(f"Unsupported modality for hot-swap: {modality}")
        except Exception as e:
            logger.error(f"Model switch failed: {str(e)}")
            raise

model_router = ModelRouter()