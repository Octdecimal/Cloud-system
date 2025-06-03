from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter()
UPLOAD_DIR = "/uploads"

@router.get("/uploads/{task_id}/{filename}")
def download_file(task_id: str, filename: str):
    file_path = os.path.join(UPLOAD_DIR, task_id, filename)
    print(f"File path: {file_path}")
    if not os.path.exists(file_path):
        return {"error": "File path not found"}
    return FileResponse(file_path, filename=filename)