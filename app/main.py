# main.py
import VoiceController
import settings
import SpeechController as Sr
import threading

if __name__ == "__main__":
    # while True:        
        print("1. Identify speakers")
        print("2. Take commands")        
        print("3. Itentify & Take commands")
        print("===========================")
        print("4. Record new speaker")
        print("5. List devices")
        choice = input("Enter your choice: ")
        
        if choice == '4':
            print('Read one of the following sentences.')
            print('============================================')
            print('The cat sat on the mat.')
            print('The sun sets in the west.')
            print('She sells seashells by the seashore.')
            print('It rained heavily last night.')
            print('I love to read books.')
            print('The quick brown fox jumps over the lazy dog.')
            print('He drives a blue car.')
            print('The coffee is too hot.')
            print('Please close the window.')
            print('I will call you tomorrow.')
            VoiceController.record_new_speaker()
        elif choice == '1':
            VoiceController.identify_speakers()
        elif choice == '2':
            Sr.capture_voice_input("Headset Microphone (CORSAIR VOI", .5)
        elif choice == '3':
            # Create threads for PyAudio and SpeechRecognition
            pyaudio_thread = threading.Thread(target=VoiceController.identify_speakers())
            speechrec_thread = threading.Thread(target=Sr.capture_voice_input(settings.mic_name, settings.pause_threshold))

            # Start both threads
            pyaudio_thread.start()
            speechrec_thread.start()

            # Wait for both threads to complete
            pyaudio_thread.join()
            speechrec_thread.join()
        elif choice == '5':
            VoiceController.list_devices()     
        else:
            print("Invalid choice. Please try again.")