import numpy as np
import pyaudio
import torch
import DataController
import SpeechController as sc
from speechbrain.inference import SpeakerRecognition  # Updated import
from pyAudioAnalysis import audioSegmentation  # Import for diarization

# Load pre-trained model
recognizer = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="tmp")

# Process audio chunks and generate embeddings
def process_chunk(chunk_data, fs=16000):
    # Convert raw bytes to numpy array
    audio_data = np.frombuffer(chunk_data, dtype=np.int16).astype(np.float32)
    # Normalize audio data
    audio_data = audio_data / np.max(np.abs(audio_data))
    # Convert numpy array to PyTorch tensor
    audio_tensor = torch.tensor(audio_data).unsqueeze(0)
    # Generate embedding
    embedding = recognizer.encode_batch(audio_tensor)
    embedding_np = embedding.squeeze().numpy()
    # print(f"Generated embedding: {embedding_np}")  # Debugging print
    return embedding_np

# Speaker diarization
def diarize_audio(audio_data, fs=16000):
    # Perform speaker diarization using pyAudioAnalysis
    segments = audioSegmentation.speaker_diarization(audio_data, fs, lda_dim=0)
    return segments

# Streaming and identifying speakers
def identify_speakers(fs=16000, chunk=1024):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    try:
        print("Recording, diarizing, and identifying speakers...")
        audio_buffer = []
        
        while True:

            # Assemble the streamed audio chunks into a buffer.
            sample_data = stream.read(chunk) # <class 'bytes'>
            audio_buffer.append(np.frombuffer(sample_data, dtype=np.int16).astype(np.float32)) # <class 'list'>
            audio_data = sc.convert_bytes_to_audio_data(sample_data)
            # print(type(audio_data)) # <class 'pyaudio.PyAudio.Stream'>

            text = sc.convert_voice_to_text(audio_data)
            if(len(text)>0):
                print(text)

            # Check buffer length (e.g., every 5 seconds)
            if len(audio_buffer) >= fs * 5 // chunk:
                
                new_speaker_embedding = process_chunk(sample_data, fs)
                identified_speaker = DataController.compare_with_stored_embeddings(new_speaker_embedding)
                if identified_speaker:
                    print(f"Speaker identified as: {identified_speaker}")
                else:
                    print(f"Speaker not identified")

                audio_buffer = []  # Reset buffer after processing
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

# Records new speaker
def record_new_speaker(sample_duration=5, fs=16000):
    import pyaudio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=fs,
                    frames_per_buffer=1024,
                    input=True)
    
    try:
        print(f"Recording {sample_duration} seconds of audio for new speaker...")
        sample_data = stream.read(sample_duration * fs)
        new_speaker_embedding = process_chunk(sample_data, fs)
        new_speaker_id = input("Enter new speaker ID: ")
        DataController.store_embedding(new_speaker_embedding, new_speaker_id)
        print("New speaker embedding stored.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def list_devices():
    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # List all audio input devices
    print("Available audio input devices:")
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            print(f"Device Index: {i}, Device Name: {dev['name']}")

    # Terminate PyAudio instance
    p.terminate()