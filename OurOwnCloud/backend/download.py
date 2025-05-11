from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/download/{task_id}/{filename}")
def download_file(task_id: str, filename: str):
    file_path = os.path.join("results", task_id, filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    return FileResponse(file_path, filename=filename)