from celery import Celery
from backend.app.utils.file_processing import process_file, validate_file
from backend.database.redis_client import redis_client

celery = Celery(
    'tasks',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

@celery.task
def process_async_file(session_id: str, file_data: bytes):
    try:
        file_type = validate_file(file_data)
        result = process_file(file_type, file_data)
        redis_client.setex(f"result:{session_id}", 3600, result)
        return {"status": "completed", "result": result}
    except Exception as e:
        return {"status": "failed", "error": str(e)}