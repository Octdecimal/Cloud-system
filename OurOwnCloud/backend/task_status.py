from fastapi import APIRouter
from typing import Dict

router = APIRouter()

# In-memory task registry
task_queue: Dict[str, Dict] = {}

def register_task(task_id: str):
    task_queue[task_id] = {"status": "waiting", "node": None, "result": None}

def update_task_status(task_id: str, status: str, node: str = None, result: str = None):
    if task_id in task_queue:
        task_queue[task_id]["status"] = status
        if node:
            task_queue[task_id]["node"] = node
        if result:
            task_queue[task_id]["result"] = result

@router.get("/")
def get_task_status():
    if not task_queue:
        return {"tasks": []}
    else:
        return {"tasks": task_queue}

def get_waiting_tasks():
    return [task_id for task_id, info in task_queue.items() if info["status"] == "waiting"]