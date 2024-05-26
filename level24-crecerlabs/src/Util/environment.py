import speech_recognition as sr

class Environment:
    def ListMics():
        m = None        
        with sr.Microphone() as source:        
            for i, microphone_name in enumerate(sr.Microphone.list_microphone_names()):
                print(microphone_name)
                pass