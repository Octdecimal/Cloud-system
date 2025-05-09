from fastapi import FastAPI, UploadFile, File
import os
import librosa
import numpy as np
import scipy.signal
from pydub import AudioSegment

# Initialize FastAPI
app = FastAPI()

# Directory for uploaded files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def home():
    return {"message": "Welcome to Cloud-Based Music Mashup Composer API!"}

@app.post("/upload/")
async def upload_song(file: UploadFile = File(...)):
    """ Upload a song, convert if needed, and analyze beats """

    try:
        # Save uploaded file
        filepath = os.path.join(UPLOAD_DIR, file.filename)
        with open(filepath, "wb") as f:
            f.write(await file.read())

        print(f"✅ File received: {filepath}")

        # Convert file to WAV format if necessary
        processed_filepath = convert_to_wav(filepath)

        # Analyze beats
        bpm = detect_beats(processed_filepath)

        # Fix: Ensure BPM is returned as a float, not a NumPy array
        bpm_value = float(bpm) if bpm is not None else None

        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "processed_file": processed_filepath,
            "bpm": bpm_value if bpm_value is not None else "Beat detection failed"
        }

    except Exception as e:
        print(f"❌ Error processing file: {e}")
        return {"error": str(e)}
def convert_to_wav(filepath):
    """ Convert audio to WAV format using PCM encoding for better compatibility """
    try:
        print(f"🔄 Converting to WAV: {filepath}")

        if filepath.endswith(".m4a"):
            audio = AudioSegment.from_file(filepath, format="m4a")
            wav_path = filepath.replace(".m4a", ".wav")
            audio.export(wav_path, format="wav", parameters=["-ac", "2", "-ar", "44100", "-sample_fmt", "s16"])

            print(f"✅ Converted file saved as: {wav_path}")
            return wav_path

        return filepath
    except Exception as e:
        print(f"❌ Conversion Error: {e}")
        return filepath  # Return original file if conversion fails

def detect_beats(filepath):
    """ Analyze beat tempo of an audio file with enhanced debugging """
    try:
        print(f"🎵 Loading audio for beat detection: {filepath}")

        y, sr = librosa.load(filepath, sr=None)
        print(f"✅ Sample Rate: {sr}, Audio Length: {len(y)} samples")

        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

        print(f"✅ Detected BPM: {tempo}")
        print(f"✅ Beats Array: {beats}")

        # Run an isolated test before using Scipy convolution
        test_array = np.array([1, 2, 3, 4, 5])
        smooth_test = scipy.signal.convolve(test_array, np.hanning(len(test_array)), "same")
        print("✅ Scipy Convolution Test Inside FastAPI Works!")

        # Ensure beats are detected before applying smoothing
        if beats.size > 0:
            smooth_boe = scipy.signal.convolve(beats.astype(float), np.hanning(5), "same")
            return tempo

        return None  # Return None if no beats detected
    except Exception as e:
        print(f"❌ Beat Detection Error: {e}")
        return None
