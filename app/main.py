import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, UJSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
import speech_recognition as sr
import numpy as np
import io, os
import whisper
from time import sleep
from datetime import datetime, timedelta
from queue import Queue
from io import BytesIO
import pyaudio
import wave
import torch
import websockets
from transformers  import WhisperProcessor, WhisperForConditionalGeneration


class SharedState:
    def __init__(self):
        self.output_text = ""
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:            
            await connection.send_text(message)

#--------------------------+
# Model | Req VRAM | Speed |
# tiny  | ~1 GB    | ~32x  |
# base  | ~1 GB    | ~16x  |
# small | ~2 GB    | ~6x   |
#--------------------------+
# For increased accuracy select a slower model.
audio_model = whisper.load_model('tiny')
phrase_time = None  # The last time a recording was retrieved from the queue.    
    
recorder = sr.Recognizer() # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
recorder.energy_threshold = 1000    
recorder.dynamic_energy_threshold = False # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
source = sr.Microphone(sample_rate=16000)

phrase_timeout = 2  # How much empty space between recordings before we consider it a new line in the transcription.
transcription = ['']
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
manager = ConnectionManager()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "GOOGLE_APPLICATION_CREDENTIALS.json"
data_queue = Queue() # Thread safe Queue for passing data from the threaded recording callback.  
record_timeout = 1 # How real time the recording is in seconds.
recorder = sr.Recognizer()
output_text = ""
shared_state = SharedState()

# Configure CORS
origins = [
    "http://localhost",  # Allow local development
    "http://localhost:8000",  # Allow frontend served by FastAPI
    "http://127.0.0.1:8000"  # Allow frontend served by FastAPI (alternative localhost)
    "http://0.0.0.0:8000"  # Allow frontend served by FastAPI (alternative localhost)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def pcm_to_wav_in_memory(pcm_data, sample_width, frame_rate, channels):
    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(frame_rate)
        wav_file.writeframes(pcm_data)
    wav_io.seek(0)  # Important: Reset the pointer to the beginning of the BytesIO object
    return wav_io

# Save PCM data to a file
def save_pcm_to_file(pcm_data, file_path):
    print(f"Saving PCM data to {file_path}")
    with open(file_path, 'wb') as file:
        file.write(pcm_data)
        print(f"Saved PCM data to {file_path}")
        
def recognize_speech_from_wav(wav_io):
    recognizer = sr.Recognizer()   
    with sr.AudioFile(wav_io) as source:
        audio_data = recognizer.record(source)
        try:            
            text = recognizer.recognize_google(audio_data)
            print(f"Recognized text: {text}")
        except sr.UnknownValueError:
            text = "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            text = "Could not request results from Google Speech Recognition service; {e}"
        except e:
            text = e
    return text

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

processor = WhisperProcessor.from_pretrained("openai/whisper-small")

def original(websocket: WebSocket):
    # await websocket.accept() 
    # while True:
    #     try:
    #         audio_data = await websocket.receive_bytes()
    #         print(audio_data)
    #         audio_array = np.frombuffer(audio_data, dtype=np.float32)
    #         transcription_result = processor.transcribe(audio_array, sample_rate=16000)
    #         shared_state.output_text = transcription_result["text"]
            
    #     except websockets.exceptions.ConnectionClosedError:
    #         shared_state.output_text = "Connection closed"
    #         break
    #     except Exception as e:
    #         shared_state.output_text = f"Error: {e}"
    #         break
    #     await websockets.send(shared_state.output_text)
    # recognizer = sr.Recognizer()
    # await websocket.accept()

    # try:
    #     while True:
    #         p = pyaudio.PyAudio()

    #         data = await websocket.receive_bytes()            
    #         wav_io = pcm_to_wav_in_memory(data, 2, 44100, 1)
    #         shared_state.output_text = recognize_speech_from_wav(wav_io)
    #         save_pcm_to_file(data, "output.wav")

    #         # Echo bytestream
    #         await websocket.send_text(data)


    # except WebSocketDisconnect:
    #     print("Client disconnected")
    pass

# Accpets the audio input
@app.websocket("/ws/bytestream")
async def websocket_bytestream(websocket: WebSocket):
    await websocket.accept()  # Accept the WebSocket connection before entering the loop    
    shared_state.output_text = "..."
    audio_buffer = io.BytesIO()
    sample_rate = 44100  # Example sample rate
    sample_width = 2  # Example sample width (2 bytes = 16 bits)
    num_channels = 1  # Mono audio

    while True:
        try:
            # Receive audio data (assuming it's in PCM format)
            audio_data = await websocket.receive_bytes()
            audio_buffer.write(audio_data)
        except Exception as e:
            print(f"Error: {e}")
            break

    # Convert the buffered audio data to WAV format
    audio_buffer.seek(0)  # Rewind the buffer
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_buffer.read())

    # Debug: Save the WAV data to a file for listening (temporary for debugging)
    with open("debug_output.wav", "wb") as debug_file:
        debug_file.write(wav_buffer.getvalue())    

    wav_buffer.seek(0)  # Rewind the WAV buffer for reading
    
    try:
        result = audio_model.transcribe(wav_buffer)
        shared_state.output_text = result["text"]    
    except Exception as e:
        shared_state.output_text = f"Error: {e}"   
    
    await websocket.close()
    # Add header to the audio chunk.
    # 1. register speaker via web interface. 
    # 2. add header to stream.
    # 3. and give feedback.
    

@app.websocket("/ws/textstream")
async def websocket_textstream(websocket: WebSocket):
    await manager.connect(websocket)
    print(shared_state.output_text)
    try:
        for i in range(100):
            await websocket.send_text(f"Message {i}: {shared_state.output_text}")
            await asyncio.sleep(i)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)