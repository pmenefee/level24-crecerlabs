import VoiceRecognition.Controller  as Vr
import SpeechRecognition.Controller as Sr
import util.settings as settings
import sched
import time

global app_name

# Setup Parameters
mic_name = "Headset Microphone (CORSAIR VOI"           # Leave blank to use active mic.   
pause_threshold = .5   # seconds (float)
event_schedule = sched.scheduler(time.time, time.sleep)


# SYSTEM
print("Loading voice regocnition models.")
Vr.Setup()
print("Calibrating ambient noise.")
Sr.calibrate_ambient_noise()

# Main application loop
# 1. Listen loop
print("Listening...")
def run():        
    audio = Sr.capture_voice_input(mic_name, pause_threshold)
    event_schedule.enter(0, 1, run, ())


event_schedule.enter(0, 1, run, ())
event_schedule.run()

#====================================================================
# Helper methods
#====================================================================

#  print(ut.Environment.ListMics())   # List registered mic devices.