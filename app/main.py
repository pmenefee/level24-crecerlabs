import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, UJSONResponse
from fastapi.staticfiles import StaticFiles
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

def recognize_speech_from_wav(wav_io):
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_io) as source:
        audio_data = recognizer.record(source)
        print(audio_data)
        try:
            text = recognizer.recognize_google(audio_data)
            print(f"Recognized text: {text}")
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        except e:
            print(e)
    return text


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Accpets the audio input
@app.websocket("/ws/bytestream")
async def websocket_bytestream(websocket: WebSocket):
    recognizer = sr.Recognizer()
    await websocket.accept()
    
    try:
        while True:
            p = pyaudio.PyAudio()

            data = await websocket.receive_bytes()            
            wav_io = pcm_to_wav_in_memory(data, 2, 44100, 1)
            recognize_speech_from_wav(wav_io)

            # Echo bytestream
            await websocket.send_bytes(data)
    

    except WebSocketDisconnect:
        print("Client disconnected")

@app.websocket("/ws/textstream")
async def websocket_textstream(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        for i in range(100):
            await websocket.send_text(f"Message {i}")
            await asyncio.sleep(i)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)