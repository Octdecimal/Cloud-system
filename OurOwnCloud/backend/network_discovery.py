import socket
import threading
import time
from task_assign import assign_task

BROADCAST_PORT = 50000
COMPLETION_PORT = 50001  # 新增的接收完成通知用 port
BROADCAST_INTERVAL = 5
DISCOVERY_MESSAGE = "DISTRIBUTED_NODE_DISCOVERY"
COMPLETION_MESSAGE = "TASK_DONE"

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
        sock.sendto(msg.encode(), ('255.255.255.255', BROADCAST_PORT))
        time.sleep(BROADCAST_INTERVAL)

def listen_for_nodes(callback):
    sock = socket.socket(socket.SOCK_DGRAM)
    sock.bind(('', BROADCAST_PORT))

    while True:
        data, _ = sock.recvfrom(1024)
        msg = data.decode()
        if msg.startswith(DISCOVERY_MESSAGE):
            parts = msg.split('|')
            if len(parts) == 3:
                _, node_ip, status = parts
                busy = status != "idle"
                callback(node_ip, busy)

def listen_for_completions():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', COMPLETION_PORT))
    print("[DISCOVERY] Listening for task completions...")

    while True:
        data, _ = sock.recvfrom(1024)
        msg = data.decode()
        if msg.startswith(COMPLETION_MESSAGE):
            parts = msg.split('|')
            if len(parts) == 2:
                _, node_ip = parts
                print(f"[DISCOVERY] Task done message from {node_ip}")
                assign_task()  # 重新分配等待中的任務

def start_discovery(callback):
    threading.Thread(target=broadcast_ip, daemon=True).start()
    threading.Thread(target=listen_for_nodes, args=(callback,), daemon=True).start()
    threading.Thread(target=listen_for_completions, daemon=True).start()
    