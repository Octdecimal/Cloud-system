import os
import numpy as np
import librosa
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
    stem = os.path.join(out_dir, os.path.basename(input_path).replace('.mp3',''), 
                        'accompaniment.wav')
    return stem if os.path.exists(stem) else input_path

def analyze_track(y, sr):
    """
    回傳 BPM、調性（key）、響度(LUFS)。
    """
    # 節拍 / BPM
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    # 調性 (chroma)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    key_index = np.argmax(np.mean(chroma, axis=1))
    # 響度 (LUFS)
    meter = pyln.Meter(sr)
    loudness = meter.integrated_loudness(y)
    return tempo, key_index, loudness

def load_and_analyze(path):
    y, sr = librosa.load(path, sr=None, mono=True)
    return y, sr, analyze_track(y, sr)

def match_tempo_and_key(y, sr, src_tempo, src_key, target_tempo, target_key):
    # 1. Tempo 時間拉伸
    rate = target_tempo / src_tempo if src_tempo>0 else 1.0
    y_ts = librosa.effects.time_stretch(y, rate)
    # 2. Key 轉調
    n_steps = target_key - src_key
    y_shift = librosa.effects.pitch_shift(y_ts, sr, n_steps)
    return y_shift

def normalize_loudness(y, sr, target_lufs=-14.0):
    meter = pyln.Meter(sr)
    loudness = meter.integrated_loudness(y)
    y_norm = pyln.normalize.loudness(y, loudness, target_lufs)
    return y_norm

def mix_tracks(input_paths, output_path):
    """
    全流程：stem 分離 → 分析 BPM/key/loudness → 轉調 / 時間拉伸 / 響度正規化 → Pydub overlay + 交叉淡出
    """
    if not input_paths:
        raise ValueError("No input files")

    # 先分析第一軌當作基準
    y0, sr0, (bpm0, key0, lufs0) = load_and_analyze(input_paths[0])
    processed = []

    for p in input_paths:
        # Stem 分離（可選）
        stem = separate_stems(p, out_dir="/tmp/spleeter_out")
        y, sr, (bpm, key, lufs) = load_and_analyze(stem)
        # Tempo/key match
        y2 = match_tempo_and_key(y, sr, bpm, key, bpm0, key0)
        # 響度正規化
        y3 = normalize_loudness(y2, sr, target_lufs=lufs0)
        # 暫存成 wav
        tmp = stem.replace('.wav','_proc.wav')
        sf.write(tmp, y3, sr)
        processed.append(tmp)

    # 用 pydub 做 overlay + 交叉淡出
    tracks = [AudioSegment.from_file(t) for t in processed]
    base = tracks[0]
    for tr in tracks[1:]:
        base = base.append(tr, crossfade=2000)  # 2 秒交叉淡出
    # 最後再做一次 loudness normalize
    base = effects.normalize(base)
    base.export(output_path, format="mp3")
    return output_path
