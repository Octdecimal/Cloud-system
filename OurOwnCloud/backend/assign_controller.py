from fastapi import APIRouter, HTTPException
from task_status import task_queue, update_task_status
from node_registry import get_nodes, set_node_status
from task_assign import assign_task

router = APIRouter()

@router.post("/start/{task_id}")
async def start_task(task_id: str):
    # 1. Task 是否存在？
    if task_id not in task_queue:
        raise HTTPException(status_code=404, detail="找不到此任務")
    #2. 由 new → ready，交給 scheduler
    update_task_status(task_id, 'ready')
    return {'message':'已經加入排程'}
