import os
import numpy as np
import librosa
from librosa.effects import time_stretch, pitch_shift
import soundfile as sf
from pydub import AudioSegment, effects
from spleeter.separator import Separator
import pyloudnorm as pyln

def separate_stems(input_path, out_dir, stems="2stems"):
    """
    使用 Spleeter 做 Stem 分離（vocals / accompaniment）。
    """
    os.makedirs(out_dir, exist_ok=True)
    separator = Separator(f'spleeter:{stems}')
    separator.separate_to_file(input_path, out_dir)
    # 回傳分離後的主 stem
    stem = os.path.join(
        out_dir,
        os.path.basename(input_path).replace('.mp3', ''),
        'accompaniment.wav'
    )
    return stem if os.path.exists(stem) else input_path

def analyze_track(y, sr):
    """
    回傳 BPM(float)、調性(int)、響度(LUFS, float)。
    """
    # 1. 節拍 / BPM
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(tempo)

    # 2. 調性 (chroma)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    # chroma.shape = (12, frames)，對每列求平均
    chroma_mean = np.mean(chroma, axis=1)
    key_index = int(np.argmax(chroma_mean))

    # 3. 響度 (LUFS)
    meter = pyln.Meter(sr)
    loudness = meter.integrated_loudness(y)
    loudness = float(loudness)

    return tempo, key_index, loudness

def load_and_analyze(path):
    y, sr = librosa.load(path, sr=None, mono=True)
    return y, sr, analyze_track(y, sr)

def match_tempo_and_key(y, sr, src_tempo, src_key, target_tempo, target_key):
    """
    先做 tempo time-stretch，再做 key pitch-shift。
    """
    # Rate 必須用 keyword 傳
    rate = float(target_tempo / src_tempo) if src_tempo > 0 else 1.0
    y_ts = time_stretch(y=y, rate=rate)

    # Key shift steps
    n_steps = int(target_key - src_key)
    y_shift = pitch_shift(y=y_ts, sr=sr, n_steps=n_steps)

    return y_shift

def normalize_loudness(y, sr, target_lufs=-14.0):
    """
    使用 pyloudnorm 正規化響度。
    """
    meter = pyln.Meter(sr)
    orig_loudness = meter.integrated_loudness(y)
    # pysoundfile 跟 pydub 都能吃 numpy array
    y_norm = pyln.normalize.loudness(y, orig_loudness, target_lufs)
    return y_norm

def mix_tracks(input_paths, output_path):
    """
    全流程：stem 分離 → 分析 BPM/key/loudness
    → 轉調 / 時間拉伸 / 響度正規化
    → Pydub overlay + 交叉淡出 → 輸出 mp3
    """
    if not input_paths:
        raise ValueError("No input files to mix.")

    # 1. 分析第一軌做基準
    y0, sr0, (bpm0, key0, lufs0) = load_and_analyze(input_paths[0])
    processed_files = []

    # 2. 對每條音軌做處理
    for path in input_paths:
        stem = separate_stems(path, out_dir="/tmp/spleeter_out")
        y, sr, (bpm, key, lufs) = load_and_analyze(stem)

        # Tempo + Key match
        y2 = match_tempo_and_key(y, sr, bpm, key, bpm0, key0)

        # Loudness normalize
        y3 = normalize_loudness(y2, sr, target_lufs=lufs0)

        # 暫存成 wav
        tmp_path = stem.replace('.wav', '_proc.wav')
        sf.write(tmp_path, y3, sr)
        processed_files.append(tmp_path)

    # 3. Pydub 交疊 + 交叉淡出
    tracks = [AudioSegment.from_file(f) for f in processed_files]
    base = tracks[0]
    for tr in tracks[1:]:
        base = base.append(tr, crossfade=2000)  # 2 秒交叉淡出

    # 4. 最後整段 normalize
    base = effects.normalize(base)
    base.export(output_path, format="mp3")

    return output_path
