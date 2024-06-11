from pyAudioAnalysis import audioSegmentation
import numpy as np

def diarize_audio_live(audio_data, fs=16000):
    try:
        if len(audio_data) == 0:
            raise ValueError("Audio data is empty.")
        
        print(f"Audio data length: {len(audio_data)}")
        print(f"Sampling rate: {fs}")

        segments = audioSegmentation.speaker_diarization(audio_data, fs, lda_dim=0)
    except Exception as e:
        print(f"Error during diarization: {e}")
        segments = []
    return segments
