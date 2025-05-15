import socket
import threading
import os
import requests
from pydub import AudioSegment
import librosa
import soundfile as sf
import numpy as np

BROADCAST_PORT = 50000
COMPLETION_PORT = 50001
DISCOVERY_MESSAGE = "DISTRIBUTED_NODE_DISCOVERY"
COMPLETION_MESSAGE = "TASK_DONE"
SERVER_IP = None
NODE_STATUS = "idle"

UPLOAD_DIR = "received_audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)


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
                # Simulate mashup
                simulate_mashup()
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


def simulate_mashup():
    print("[NODE] Simulating mashup task...")
    input_files = []
    for i in range(2):
        path = os.path.join(UPLOAD_DIR, f"audio{i+1}.mp3")
        if not os.path.exists(path):
            print(f"[WARN] Missing {path}, creating silent track")
            silent = AudioSegment.silent(duration=3000)
            silent.export(path, format="mp3")
        input_files.append(path)

    output_path = os.path.join(UPLOAD_DIR, "mashup_result.mp3")
    mix_audio_files(input_files, output_path)


if __name__ == "__main__":
    threading.Thread(target=listen_for_server, daemon=True).start()
    while True:
        pass
