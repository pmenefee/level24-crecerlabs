from typing import Optional
from fastapi import FastAPI
from . import settings
from . import VoiceController  as Vr
import sys
import os
import debugpy  ## REQUIRED FOR REMOTE DEBUGGING

def main():
    # print("Current Working Directory:", os.getcwd())
    # print("Python Path:", sys.path)
    debugpy.listen(("0.0.0.0", 5678))

    if(settings.test_controller=="VR"):
        # Capture audio
        print("Initiating voice controller.")
        audio_data = Vr.capture_audio()
        temp_wav_file_path = Vr.save_audio(audio_data)
    else:
        print("Calibrating ambient noise.")

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    main()