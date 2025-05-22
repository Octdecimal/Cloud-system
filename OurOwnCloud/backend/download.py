from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter()
UPLOAD_DIR = "/uploads"

@router.get("/download/{task_id}/{filename}")
def download_file(task_id: str, filename: str):
    file_path = os.path.join(UPLOAD_DIR, task_id, filename)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return {"error": "File path not found"}
    return FileResponse(file_path, filename=filename)