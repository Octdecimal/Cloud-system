from fastapi import APIRouter, HTTPException
import os, socket
from task_status import task_queue, update_task_status
from node_registry import discovered_nodes, set_node_status
from network_discovery import nodes

router = APIRouter()

ASSIGN_PORT    = 50002
ASSIGN_MESSAGE = "ASSIGN_TASK"
UPLOAD_DIR     = "/uploads"

@router.post("/start/{task_id}")
async def start_task(task_id: str):
   if task_id not in task_queue:
	   raise HTTPException(404, "Task not found")
   if task_queue[task_id]["status"] != "waiting":
	   raise HTTPException(400, "只能啟動 waiting 任務")
   # 選 node
   # …（select_best_node、socket.connect、ACK 邏輯）…
   update_task_status(task_id, "assigned", node_ip)
   set_node_status(node_ip, True)
   return {"message": f"已分派到 {node_ip}"}
