from fastapi import APIRouter, UploadFile, File
from typing import List
import os
from task_status import register_task
from task_assign import assign_task
import hashlib
import time

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def generate_folder_name(files: List[UploadFile]) -> str:
    hasher = hashlib.sha256()
    hasher.update(str(time.time()).encode())
    for file in files:
        hasher.update(file.filename.encode())
    return hasher.hexdigest()[:16]

@router.post("/")
async def upload_files(files: List[UploadFile] = File(...)):
    folder = generate_folder_name(files)
    folder_path = os.path.join(UPLOAD_DIR, folder)
    os.makedirs(folder_path, exist_ok=True)

    for file in files:
        with open(os.path.join(folder_path, file.filename), "wb") as f:
            f.write(await file.read())

    register_task(folder)
    assign_task()
    # Notify task queue / assign later
    return {"message": "Uploaded", "folder": folder}
