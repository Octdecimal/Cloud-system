import os
import requests
from node_registry import get_nodes, set_node_status
from task_status import update_task_status, get_waiting_tasks

TASK_INPUT_DIR = "uploads"

def assign_task():
    waiting_tasks = get_waiting_tasks()
    if not waiting_tasks:
        return
    
    nodes = get_nodes()
    if not nodes:
        return
    
    for task_id in waiting_tasks:
        # Find the first available node
        for node in nodes:
            if not node["busy"]:
                # Assign the task to this node
                node_ip = node["ip"]
                task_input_path = os.path.join(TASK_INPUT_DIR, task_id)
                
                # Send the task to the node
                try:
                    response = requests.post(f"http://{node_ip}/process_task", json={"task_id": task_id, "input_path": task_input_path})
                    if response.status_code == 200:
                        update_task_status(task_id, "assigned", node_ip)
                        set_node_status(node_ip, busy=True)
                        break
                except requests.RequestException as e:
                    print(f"Failed to assign task {task_id} to node {node_ip}: {e}")