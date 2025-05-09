from fastapi import APIRouter, Form
from task_status import update_task_status
from node_registry import set_node_status

router = APIRouter()

@router.post("/")
def notify_completion(
    task_id: str = Form(...),
    node_ip: str = Form(...),
    result_path: str = Form(...)
):
    # Update internal task registry
    set_node_status(node_ip, busy=False)
    update_task_status(task_id, "done", node=node_ip, result=result_path)
    print(f"[NOTIFY] Task {task_id} complete by {node_ip}")
    return {"message": "Acknowledged"}
