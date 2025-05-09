import socket
import threading
import time

BROADCAST_PORT = 50000
BROADCAST_INTERVAL = 5  # seconds
DISCOVERY_MESSAGE = "DISTRIBUTED_NODE_DISCOVERY"

def get_local_ip():
    """Get the local LAN IP address of this machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # doesn't have to be reachable
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def broadcast_ip():
    """Broadcast the local IP to the local network."""
    ip = get_local_ip()
    message = f"{DISCOVERY_MESSAGE}|{ip}"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        sock.sendto(message.encode(), ('255.255.255.255', BROADCAST_PORT))
        print(f"[BROADCAST] Sent: {message}")
        time.sleep(BROADCAST_INTERVAL)

def listen_for_nodes(callback):
    """Listen for other nodes broadcasting their IP."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', BROADCAST_PORT))

    while True:
        data, _ = sock.recvfrom(1024)
        try:
            msg = data.decode()
            if msg.startswith(DISCOVERY_MESSAGE):
                _, node_ip = msg.split("|")
                callback(node_ip)
        except Exception as e:
            print("[ERROR] Invalid broadcast:", e)

def start_discovery(callback):
    """Start both broadcasting and listening threads."""
    threading.Thread(target=broadcast_ip, daemon=True).start()
    threading.Thread(target=listen_for_nodes, args=(callback,), daemon=True).start()
