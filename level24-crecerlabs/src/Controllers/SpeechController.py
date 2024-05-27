import speech_recognition as sr
import Controllers.VoiceController  as Vr
import time, sys, os
import Util.settings as settings
import yaml
from diart import SpeakerDiarization
from diart.sources import MicrophoneAudioSource
from diart.inference  import StreamingInference

recognizer = sr.Recognizer()


def callback(recognizer, audio):
    # Voice detected
    text = convert_voice_to_text(audio)
    if(settings.output_to_concole):
        print(text)
    
    # Process Command
    # Regulate command flag.  This requires a word pair [GREETING, APP_NAME] to become active.  
    command_listen = False
    command_mode = False 

    for word in text.split(" "):
        if word in settings.greetings:
            command_listen = True
    
        if (command_listen == True):
            if (word == settings.app_name):
                command_mode = True

    if(command_mode == True):
        process_voice_command(text)   


def capture_voice_input(mic_name, pause_threshold):  
    recognizer.pause_threshold = pause_threshold  
    stop_listening = recognizer.listen_in_background(sr.Microphone() ,callback)
    time.sleep(pause_threshold) # this seems to improve detection.  Setting the value too small and nothing is detected.
        
    with sr.Microphone() as source:        
        audio = recognizer.listen(source)

    stop_listening(False)

    return audio


def convert_voice_to_text(audio):
    try:
        text = recognizer.recognize_google(audio)        

    except sr.UnknownValueError:  # Some audio came through it could not process to text
        text = ""
    except sr.RequestError as e:
        text = ""
        print("Error; {0}".format(e))
    return text

def process_voice_command(text):
    sentance = text.split(" ")
    trigger = ""    
    
    
    with open(settings.command_file, 'r') as f:
            commands = yaml.load(f, Loader=yaml.FullLoader)

    for command in commands['commands']:
        try:
            trigger = commands['commands'][command]['triggerword']  
            for word in sentance:
                if word in trigger:
                    # TODO: Do something with the command.
                    print(commands['commands'][command]["action"])
                    
        except KeyError:  # this will be tripped by greetings or any other noncommand value.
            pass

def calibrate_ambient_noise():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)