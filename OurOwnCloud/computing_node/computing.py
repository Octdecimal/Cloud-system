import socket
import threading
import os

BROADCAST_PORT = 50000
COMPLETION_PORT = 50001
ASSIGN_PORT = 50002
DISCOVERY_MESSAGE = "DISTRIBUTED_NODE_DISCOVERY"
COMPLETION_MESSAGE = "TASK_DONE"
ASSIGN_MESSAGE = "ASSIGN_TASK"
SERVER_IP = None
NODE_STATUS = "idle"
UPLOAD_DIR = "/uploads"


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
                identity_2_server()
        except OSError as e:
            print(f"Server discovery error: {e}")
            break


def identity_2_server():
    if SERVER_IP:
        return_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        msg = f"{DISCOVERY_MESSAGE}|{get_local_ip()}|{NODE_STATUS}"
        return_sock.sendto(msg.encode(), (SERVER_IP, BROADCAST_PORT))
        print(f"[NODE] Notified server at {SERVER_IP} of presence")
        return_sock.close()
    else:
        print("[NODE] No server IP to notify")

def listen_4_assignment():
    global NODE_STATUS
    asign_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    asign_sock.bind((SERVER_IP, ASSIGN_PORT))
    
    asign_sock.listen(1)
    while True:
        try:
            conn, _ = asign_sock.accept()
            data = conn.recv(1024).decode()
            if data.startswith(ASSIGN_MESSAGE):
                _, task_id, task_input_path = data.split('|')
                print(f"[NODE] Received task {task_id} with input path {task_input_path}")
                NODE_STATUS = "busy"
                ### task function
                ### task funciton
                ### task function
                conn.sendall("ACK".encode())
            conn.close()
        except OSError as e:
            print(f"Assignment error: {e}")
            break

if __name__ == "__main__":
    threading.Thread(target=listen_for_server, daemon=True).start()

    while True:
        pass
