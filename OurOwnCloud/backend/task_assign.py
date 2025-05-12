import os
import socket
from node_registry import get_nodes, set_node_status
from task_status import update_task_status, get_waiting_tasks

TASK_INPUT_DIR = "/uploads"
ASSIGN_PORT = 50002
ASSIGN_MESSAGE = "ASSIGN_TASK"

def assign_task():
    waiting_tasks = get_waiting_tasks()
    if not waiting_tasks:
        return False
    
    nodes = get_nodes()
    if not nodes:
        return False
    
    for task_id in waiting_tasks:
        # Find the first available node
        for node in nodes:
            # Assign the task to this node
            node_ip = node["ip"]
            task_input_path = os.path.join(TASK_INPUT_DIR, task_id)
            task_data = f"{ASSIGN_MESSAGE}|{task_id}|{task_input_path}"
            
            # Send the task to the node
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((node_ip, ASSIGN_PORT))
                    sock.sendall(task_data.encode())
                    
                    response, _ = sock.recvfrom(1024)
                    
                    if response.decode() == "ACK":
                        # Update task status and node status
                        update_task_status(task_id, "assigned", node_ip)
                        set_node_status(node_ip, busy = True)
                        sock.close()
                        break
                    
                    sock.close()
                        
            except socket.error as e:
                print(f"Error sending task to node {node_ip}: {e}")
                # If the node is busy, continue to the next one
                continue
    return True