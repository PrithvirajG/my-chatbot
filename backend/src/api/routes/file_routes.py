from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from ...processing.file_handler import file_processor
from ...data.redis_manager import redis_client
import uuid

router = APIRouter()

@router.post("/files/upload")
async def upload_file(file: UploadFile, session_id: str):
    try:
        # Validate session
        if not redis_client.exists(session_id):
            raise HTTPException(status_code=404, detail="Session not found")

        # Read file
        file_data = await file.read()

        # Validate file type and size
        file_type = file_processor.validate_file(file_data)

        # Process file based on type
        result = file_processor.process_file(file_type, file_data)

        # Store result in Redis (for session history)
        file_id = str(uuid.uuid4())
        redis_client.hset(f"session:{session_id}:files", file_id, result)

        return JSONResponse(content={
            "file_id": file_id,
            "result": result
        })

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")