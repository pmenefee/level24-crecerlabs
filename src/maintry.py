import pyaudio
import numpy as np
import wave
from pyannote.audio import Pipeline
from tempfile import NamedTemporaryFile
import Util
import Util.settings
import speechbrain as sb

# Initialize the diarization pipeline
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1", use_auth_token=Util.settings.hugging_face_token)

# Audio capture settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 10  # Adjust as needed

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Function to capture audio from the microphone
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

    return b''.join(frames)

# Capture audio
audio_data = capture_audio()

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

# Run the pipeline on the temporary audio file
diarization = pipeline(temp_wav_file_path)

# Extract speaker IDs and their respective segments
for segment, _, speaker in diarization.itertracks(yield_label=True):
    start_time = segment.start
    end_time = segment.end
    speaker_id = speaker
    print(f"Speaker {speaker_id} from {start_time} to {end_time}")

# Cleanup
audio.terminate()
