import socket
import threading
import time
from task_assign import assign_task
from node_registry import set_node_status

BROADCAST_PORT = 50000
COMPLETION_PORT = 50001  # 新增的接收完成通知用 port
BROADCAST_INTERVAL = 5
DISCOVERY_MESSAGE = "DISTRIBUTED_NODE_DISCOVERY"
COMPLETION_MESSAGE = "TASK_DONE"
COUNTDOWN = 30 # 節點的存活時間

map = {}  # 用來存放節點的 IP 和狀態

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
                        map[node_ip] = COUNTDOWN
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
                    if len(parts) == 2:
                        _, node_ip = parts
                        print(f"[DISCOVERY] Task done message from {node_ip}")
                        if assign_task():
                            set_node_status(node_ip, busy=False)
            except OSError as e:
                print(f"Completion listening error: {e}")
                break
    finally:
        sock.close()

def countdown():
    while True:
        time.sleep(1)
        for ip in list(map.keys()):
            map[ip] -= 1
            if map[ip] <= 0:
                del map[ip]
                print(f"[DISCOVERY] Node {ip} timed out and removed from the list.")

def start_discovery(callback):
    threading.Thread(target=broadcast_ip, daemon=True).start()
    threading.Thread(target=listen_for_nodes, args=(callback,), daemon=True).start()
    threading.Thread(target=listen_for_completions, daemon=True).start()
    threading.Thread(target=countdown, daemon=True).start()
