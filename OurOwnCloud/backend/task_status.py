from fastapi import APIRouter
from typing import Dict
import os

UPLOAD_DIR = "/uploads"

router = APIRouter()

# In-memory task registry
task_queue: Dict[str, Dict] = {}

def all_tasks_search():
    # search all folders in the UPLOAD_DIR
    for folder in os.listdir(UPLOAD_DIR):
        folder_path = os.path.join(UPLOAD_DIR, folder)
        if os.path.isdir(folder_path):
            goal = os.path.join(folder_path, folder_path)
            if os.path.exists(goal):
                task_queue[folder] = {"status": "done", "node": None, "result": goal}
            else:
                task_queue[folder] = {"status": "waiting", "node": None, "result": None}

def register_task(task_id: str):
    task_queue[task_id] = {"status": "waiting", "node": None, "result": None}

def update_task_status(task_id: str, status: str, node: str = None, result: str = None):
    if task_id in task_queue:
        task_queue[task_id]["status"] = status
        if node:
            task_queue[task_id]["node"] = node
        if result:
            task_queue[task_id]["result"] = result

@router.get("/status")
def get_task_status():
    return {"tasks": task_queue}

def get_waiting_tasks():
    return [task_id for task_id, info in task_queue.items() if info["status"] == "waiting"]

@router.get("/remove/{task_id}")
def remove_task(task_id):
    if task_id in task_queue:
        del task_queue[task_id]
        return {"message": f"Task {task_id} removed"}