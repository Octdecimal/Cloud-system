import os
import socket
from node_registry import  set_node_status
from task_status import update_task_status, get_ready_tasks

TASK_INPUT_DIR = "/uploads"
ASSIGN_PORT = 50002
ASSIGN_MESSAGE = "ASSIGN_TASK"

def assign_task(task_id:str, node_ip:str)->bool:
    task_input = os.path.join(TASK_INPUT_DIR, task_id)
    msg = f"{ASSIGN_MESSAGE}|{task_id}|{task_input}"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((node_ip, ASSIGN_PORT))
            sock.sendall(msg.encode())
            ack = sock.recv(16).decode()
            return ack == "ACK"
    except:
        return False
