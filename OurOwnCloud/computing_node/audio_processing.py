import os
import numpy as np
import librosa
from librosa.effects import time_stretch, pitch_shift
import soundfile as sf
from pydub import AudioSegment, effects
from spleeter.separator import Separator
import pyloudnorm as pyln

# … 你原本的所有函式（separate_stems, analyze_track, load_and_analyze,
#    match_tempo_and_key, normalize_loudness, mix_tracks, _simple_overlay）都不變 …

def extract_loudest_segment(path,
                            segment_sec: float = 20.0,
                            lead_in_sec: float = 5.0,
                            hop_length: int = 512):
    """
    找出最高潮段（能量最高的 segment_sec 秒），
    前面再保留 lead_in_sec 做鋪陳，輸出暫存 wav，回傳路徑。
    """
    y, sr = librosa.load(path, sr=None, mono=True)
    # 短時 STFT → magnitude → RMS
    S, _ = librosa.magphase(librosa.stft(y))
    rms = librosa.feature.rms(S=S, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)

    win = int(segment_sec * sr / hop_length)
    if win >= len(rms):
        start = 0.0
    else:
        energy = np.convolve(rms, np.ones(win), mode='valid')
        idx = int(np.argmax(energy))
        start = times[idx]

    t0 = max(0.0, start - lead_in_sec)
    t1 = min(len(y)/sr, start + segment_sec)
    s0, s1 = int(t0*sr), int(t1*sr)
    y_seg = y[s0:s1]

    basename = os.path.splitext(os.path.basename(path))[0]
    tmp = f"/tmp/chorus_{basename}.wav"
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    sf.write(tmp, y_seg, sr)
    return tmp

def splice_choruses(input_paths,
                    output_path: str,
                    segment_sec: float = 20.0,
                    lead_in_sec: float = 5.0,
                    crossfade_ms: int = 2000):
    """
    1. 對每支 input_path 擷取最高潮段（extract_loudest_segment）
    2. 用 crossfade_ms 淡入淡出串接
    3. normalize & export mp3
    """
    if not input_paths:
        raise ValueError("No input files to splice.")

    segments = []
    for p in input_paths:
        tmpwav = extract_loudest_segment(p, segment_sec, lead_in_sec)
        segments.append(AudioSegment.from_file(tmpwav))

    out = segments[0]
    for seg in segments[1:]:
        out = out.append(seg, crossfade=crossfade_ms)

    out = effects.normalize(out)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    out.export(output_path, format="mp3")
    return output_path
