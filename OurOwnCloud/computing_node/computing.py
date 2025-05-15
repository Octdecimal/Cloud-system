import socket
import threading
import os
import time
import subprocess
from pydub import AudioSegment
import librosa
import soundfile as sf
import numpy as np
import psutil

BROADCAST_PORT = 50000
COMPLETION_PORT = 50001
ASSIGN_PORT = 50002
INFO_PORT = 50003
DISCOVERY_MESSAGE = "DISTRIBUTED_NODE_DISCOVERY"
COMPLETION_MESSAGE = "TASK_DONE"
ASSIGN_MESSAGE = "ASSIGN_TASK"
NODE_INFO = "USAGE_DATA"
SERVER_IP = None
COUNT_DOWN = 30
NODE_STATUS = "idle"
UPLOAD_DIR = "/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

count_down = 0

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

def get_system_usage():
    # Get CPU usage percentage
    cpu_usage = psutil.cpu_percent(interval=1)
    
    # Get memory usage
    mem = psutil.virtual_memory()
    mem_usage = mem.percent

    return cpu_usage, mem_usage

def monitor_system_usage():
    while True:
        try: 
            # Run the top command and get the output
            cpu_usage, mem_usage = get_system_usage()
            cpu_line = f"{cpu_usage}%"
            mem_line = f"{mem_usage}%"
            print(f"[NODE] CPU: {cpu_line}, Memory: {mem_line}")
            send_usage_data(cpu_line, mem_line)
        except Exception as e:
            print(f"[ERROR] Monitoring error: {e}")
        
        time.sleep(5)  # Adjust the interval as needed
        
def send_usage_data(cpu_line, mem_line):
    if SERVER_IP:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(('', INFO_PORT))
            message = f"{NODE_INFO}|{get_local_ip()}|{cpu_line}|{mem_line}"
            sock.sendto(message.encode(), (SERVER_IP, BROADCAST_PORT))
            print(f"[NODE] Sent usage data to {SERVER_IP}")
        except Exception as e:
            print(f"[ERROR] Sending usage data: {e}")

def listen_4_assignment():
    global NODE_STATUS
    global count_down
    while not SERVER_IP:
        print("[NODE] Waiting for server discovery...")
        time.sleep(1)
    
    asign_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    asign_sock.bind(('0.0.0.0', ASSIGN_PORT))
    asign_sock.listen(1)
    while True:
        try:
            conn, _ = asign_sock.accept()
            data = conn.recv(1024).decode()
            if data.startswith(ASSIGN_MESSAGE):
                _, task_id, task_input_path = data.split('|')
                print(f"[NODE] Received task {task_id} with input path {task_input_path}")
                NODE_STATUS = "busy"
                simulate_mashup(task_id)
                conn.sendall("ACK".encode())
                count_down = COUNT_DOWN
            conn.close()
        except OSError as e:
            print(f"Assignment error: {e}")
            break


def detect_key(filepath):
    try:
        y, sr = librosa.load(filepath)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_avg = np.mean(chroma, axis=1)
        key_index = np.argmax(chroma_avg)
        return key_index  # 0 = C, 1 = C#, ..., 11 = B
    except Exception as e:
        print(f"[ERROR] Failed to detect key for {filepath}: {e}")
        return 0


def shift_to_key(filepath, target_key_index):
    try:
        y, sr = librosa.load(filepath)
        current_key = detect_key(filepath)
        shift_steps = target_key_index - current_key
        y_shifted = librosa.effects.pitch_shift(y=y, sr=sr, n_steps=shift_steps)
        temp_path = filepath.replace(".mp3", "_shifted.wav")
        sf.write(temp_path, y_shifted, sr)
        return temp_path
    except Exception as e:
        print(f"[ERROR] Failed to shift {filepath}: {e}")
        return filepath


def mix_audio_files(input_files, output_path):
    print(f"[MASHUP] Mixing files: {input_files}")
    if not input_files:
        print("[ERROR] No input files to mix.")
        return

    key_base = detect_key(input_files[0])
    shifted_paths = [shift_to_key(f, key_base) for f in input_files]
    tracks = []
    for f in shifted_paths:
        try:
            tracks.append(AudioSegment.from_file(f))
        except Exception as e:
            print(f"[ERROR] Failed to load {f}: {e}")
    if not tracks:
        print("[ERROR] No valid audio tracks loaded.")
        return

    base = tracks[0]
    for track in tracks[1:]:
        base = base.overlay(track)
    base.export(output_path, format="mp3")
    print(f"[MASHUP] Output saved to {output_path}")


def simulate_mashup(task_id):
    print("[NODE] Simulating mashup task...")
    input_files = []
    for i in range(2):
        path = os.path.join(UPLOAD_DIR, f"audio{i+1}.mp3")
        if not os.path.exists(path):
            print(f"[WARN] Missing {path}, creating silent track")
            silent = AudioSegment.silent(duration=3000)
            silent.export(path, format="mp3")
        input_files.append(path)

    output_path = os.path.join(UPLOAD_DIR, f"{task_id}.mp3")
    mix_audio_files(input_files, output_path)

def coutdown():
    global count_down
    global SERVER_IP
    while count_down > 0:
        time.sleep(1)
        count_down -= 1
    SERVER_IP = None
    

if __name__ == "__main__":
    # threading.Thread(target=listen_for_server, daemon=True).start()
    threading.Thread(target=monitor_system_usage, daemon=True).start()
    threading.Thread(target=listen_4_assignment, daemon=True).start()
    threading.Thread(target=coutdown, daemon=True).start()
    
    while True:
        if SERVER_IP is None:
            listen_for_server()
        time.sleep(1)
