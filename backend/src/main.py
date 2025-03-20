from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.src.api.routes import chat_routes, file_routes, session_routes
from loguru import logger
from backend.src.core.model_router import model_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing models...")
    model_router.initialize_models()
    logger.success("Models initialized successfully")
    yield  # Let the app run
    logger.info("Shutting down...")  # Cleanup logic (if needed)

app = FastAPI(title="Multi-Modal Chatbot API", version="1.0.0", lifespan=lifespan)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(chat_routes.router, prefix="/api/v1")
app.include_router(file_routes.router, prefix="/api/v1")
app.include_router(session_routes.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": app.version}
