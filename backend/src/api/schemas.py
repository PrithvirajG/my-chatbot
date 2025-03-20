from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
    session_id: str
    message: str

class FileUploadRequest(BaseModel):
    """Schema for file uploads"""
    session_id: str = Field(..., example="a1b2c3d4")
    file_type: Optional[str] = Field(
        None,
        description="Optional override for automatic type detection",
        example="pdf"
    )

class SessionCreateResponse(BaseModel):
    """Schema for session creation response"""
    session_id: str
    created_at: str
    expires_at: str

class ProcessedFileResponse(BaseModel):
    """Schema for processed file response"""
    file_id: str
    content_type: str
    processing_result: Dict[str, Any]
    model_used: str
    processing_time_ms: float

class ErrorResponse(BaseModel):
    """Standard error response schema"""
    error_code: str
    detail: str
    context: Optional[Dict[str, Any]]


class ChatResponse(BaseModel):
    response: str