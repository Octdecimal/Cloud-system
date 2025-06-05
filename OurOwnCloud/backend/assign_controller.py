from fastapi import APIRouter, HTTPException
from task_status import task_queue, update_task_status
from node_registry import get_nodes, set_node_status
from task_assign import assign_task

router = APIRouter()

@router.post("/start/{task_id}")
async def start_task(task_id: str):
    if task_id not in task_queue:
        raise HTTPException(404, "Task not found")
    if task_queue[task_id]["status"] != "waiting":
        raise HTTPException(400, "只能啟動 waiting 任務")
    # 選一個空閒節點
    nodes = get_nodes(only_available=True)
    if not nodes:
        raise HTTPException(503, "目前無可用節點")
    node_ip = nodes[0]
    # 派工
    ok = assign_task(task_id, node_ip)
    if not ok:
        raise HTTPException(500, "派工失敗")
    # 更新狀態
    set_node_status(node_ip, True)
    update_task_status(task_id, "assigned", node_ip)
    return {"message": f"已分派到 {node_ip}"}
