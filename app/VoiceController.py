from pyannote.audio import Pipeline
from pyannote.core import Segment

from pyannote.audio.pipelines import VoiceActivityDetection
from diart import SpeakerDiarization
from diart.sources import MicrophoneAudioSource
from diart.inference  import StreamingInference
from diart.sinks import RTTMWriter
from tempfile import NamedTemporaryFile
import pyaudio, wave
import numpy as np
import settings
import os


# Initialize PyAudio
audio = pyaudio.PyAudio()

# Audio capture settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 10  # Adjust as needed

def capture_audio():
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
    frames = []

    print("Recording...")
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Recording finished.")

    stream.stop_stream()
    stream.close()

    # run_diarization(b''.join(frames))

    return b''.join(frames)

def save_audio(audio_data):
    # Convert byte data to numpy array
    audio_np = np.frombuffer(audio_data, dtype=np.int16)

    # Save the audio to a temporary WAV file
    with NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav_file:
        wf = wave.open(temp_wav_file, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(audio_data)
        temp_wav_file_path = temp_wav_file.name
        wf.close()
    return temp_wav_file_path

def run_diarization(temp_wav_file_path):
    try:
        # Initialize the diarization pipeline
        inference = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=Util.settings.hugging_face_token)

        # Run the pipeline on the temporary audio file
        diarization = inference(temp_wav_file_path)

        # Extract speaker IDs and their respective segments
        for segment, _, speaker in diarization.itertracks(yield_label=True):
            start_time = segment.start
            end_time = segment.end
            speaker_id = speaker
            print(f"Speaker {speaker_id} from {start_time} to {end_time}")
    except Exception as e:
          print(e)

    # Cleanup
    audio.terminate()
    os.remove(temp_wav_file_path)


