import socket
import threading
import time
from task_status import update_task_status
from task_assign import assign_task
from node_registry import add_node, get_nodes, set_node_status
from fastapi import APIRouter
from dataclasses import dataclass

@dataclass
class NodeInfo:
    ip: str
    cpu_usage: str
    mem_usage: str
    countdown: int


BROADCAST_PORT = 50000
COMPLETION_PORT = 50001  # 新增的接收完成通知用 port
INFO_PORT = 50003
BROADCAST_INTERVAL = 5
DISCOVERY_MESSAGE = "DISTRIBUTED_NODE_DISCOVERY"
COMPLETION_MESSAGE = "TASK_DONE"
NODE_INFO = "USAGE_DATA"
COUNTDOWN = 30 # 節點的存活時間

nodes = {}# 用來存放節點的 IP 和狀態


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def broadcast_ip():
    ip = get_local_ip()
    msg = f"{DISCOVERY_MESSAGE}|{ip}"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        try:
            sock.sendto(msg.encode(), ('255.255.255.255', BROADCAST_PORT))
        except OSError as e:
            print(f"Broadcast error: {e}")
        time.sleep(BROADCAST_INTERVAL)


def listen_for_nodes(callback):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(('', BROADCAST_PORT))
        while True:
            try:
                data, _ = sock.recvfrom(1024)
                msg = data.decode()
                if msg.startswith(DISCOVERY_MESSAGE):
                    parts = msg.split('|')
                    if len(parts) == 3:
                        _, node_ip, status = parts
                        busy = status != "idle"
                        add_node(node_ip, busy)
                        callback(node_ip, busy)
            except OSError as e:
                print(f"Node listening error: {e}")
                break
    finally:
        sock.close()


def listen_for_completions():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(('', COMPLETION_PORT))
        print("[DISCOVERY] Listening for task completions...")
        while True:
            try:
                data, _ = sock.recvfrom(1024)
                msg = data.decode()
                if msg.startswith(COMPLETION_MESSAGE):
                    parts = msg.split('|')
                    if len(parts) == 3:
                        _, task_id, node_ip = parts
                        print(f"[DISCOVERY] Task done message from {node_ip}")
                        set_node_status(node_ip, busy=False)
                        result_path = f"/uploads/{task_id}/{task_id}.mp3"
                        update_task_status(task_id, "done", node_ip, result_path)
            except OSError as e:
                print(f"Completion listening error: {e}")
                break
    finally:
        sock.close()
        
def listen_for_node_info():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(('', INFO_PORT))
        print("[DISCOVERY] Listening for node status...")
        while True:
            try:
                data, _ = sock.recvfrom(1024)
                msg = data.decode()
                if msg.startswith(NODE_INFO):
                    parts = msg.split('|')
                    if len(parts) == 4:
                        _, node_ip, cpu_usage, mem_usage = parts
                        print(f"[DISCOVERY] Node {node_ip} CPU: {cpu_usage}%, Memory: {mem_usage}%")
                        nodes[node_ip] = NodeInfo(ip=node_ip, cpu_usage=cpu_usage, mem_usage=mem_usage, countdown=COUNTDOWN)
                        
            except OSError as e:
                print(f"Node status listening error: {e}")
                break
    finally:
        sock.close()

def countdown_nodes():
    while True:
        time.sleep(1)
        for ip in list(nodes.keys()):
            node = nodes[ip]
            node.countdown -= 1
            if node.countdown <= 0:
                print(f"[DISCOVERY] Node {ip} is no longer available.")
                del nodes[ip]

def assign_2_node():
    while True:
        for ip in list(nodes.keys()):
            usable_node = get_nodes()
            if ip in usable_node:
                print(f"[DISCOVERY] Assigning task to node {ip}")
                assign_task(ip)
            
            time.sleep(1)
        

def start_discovery(callback):
    threading.Thread(target=broadcast_ip, daemon=True).start()
    threading.Thread(target=listen_for_nodes, args=(callback,), daemon=True).start()
    threading.Thread(target=listen_for_completions, daemon=True).start()
    threading.Thread(target=listen_for_node_info, daemon=True).start()
    threading.Thread(target=countdown_nodes, daemon=True).start()
    threading.Thread(target=assign_2_node, daemon=True).start()
    
router = APIRouter()
@router.get("/node_usage")
async def get_node_usage():
    return {ip: node.__dict__ for ip, node in nodes.items()}