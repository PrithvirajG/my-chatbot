from pydantic_settings import BaseSettings
from pydantic import Field, DirectoryPath
from pathlib import Path


import os

class Config:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "/data/chroma")
    TEXT_MODEL_PATH = os.getenv("TEXT_MODEL_PATH", "models/text/llama-2-7b-chat.Q4_K_M.gguf")

config = Config()

#
# class Settings(BaseSettings):
#
#
#     TEXT_MODEL_PATH: str = Field(
#         "models/text/llama-2-7b-chat.Q4_K_M.gguf",
#         env="TEXT_MODEL_PATH"
#     )
#     VISION_MODEL_NAME: str = Field(
#         "Salesforce/blip-image-captioning-base",
#         env="VISION_MODEL"
#     )
#     VOICE_MODEL_SIZE: str = Field(
#         "base",
#         env="VOICE_MODEL_SIZE"
#     )
#
#     # System configurations
#     MAX_FILE_SIZE_MB: int = Field(100, env="MAX_FILE_SIZE")
#     SESSION_TIMEOUT_MIN: int = Field(60, env="SESSION_TIMEOUT")
#     REDIS_URL: str = Field("redis://redis:6379", env="REDIS_URL")
#
#     # Vector DB configurations
#     CHROMA_COLLECTION: str = Field("main_docs", env="CHROMA_COLLECTION")
#     EMBEDDING_MODEL: str = Field(
#         "sentence-transformers/all-mpnet-base-v2",
#         env="EMBEDDING_MODEL"
#     )
#
#     # Model configurations
#     MODEL_DIR: Path = Path(__file__).parent.parent.parent / "models"
#     CACHE_DIR: Path = Path(__file__).parent.parent.parent / "cache"
#
#
#     class Config:
#         env_file = ".env"
#         env_file_encoding = "utf-8"
#         validate_assignment = True
#
# settings = Settings()

