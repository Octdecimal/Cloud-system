import socket
import threading
import os
import requests

BROADCAST_PORT = 50000
COMPLETION_PORT = 50001
DISCOVERY_MESSAGE = "DISTRIBUTED_NODE_DISCOVERY"
COMPLETION_MESSAGE = "TASK_DONE"
SERVER_IP = None
NODE_STATUS = "idle"


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def listen_for_server():
    global SERVER_IP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', BROADCAST_PORT))
    while True:
        try:
            data, _ = sock.recvfrom(1024)
            msg = data.decode()
            if msg.startswith(DISCOVERY_MESSAGE):
                _, server_ip = msg.split('|')
                SERVER_IP = server_ip
                print(f"[NODE] Discovered server at {SERVER_IP}")
                # Notify server of presence
                notify_server()
        except OSError as e:
            print(f"Server discovery error: {e}")
            break


def notify_server():
    if SERVER_IP:
        try:
            requests.post(f"http://{SERVER_IP}:8000/notify", json={"status": NODE_STATUS})
            print(f"[NODE] Notified server at {SERVER_IP} of presence")
        except requests.RequestException as e:
            print(f"Failed to notify server: {e}")


if __name__ == "__main__":
    threading.Thread(target=listen_for_server, daemon=True).start()

    while True:
        pass
