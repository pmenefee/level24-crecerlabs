from pyannote.audio import Model
from pyannote.audio.pipelines import VoiceActivityDetection
from diart import SpeakerDiarization
from diart.sources import MicrophoneAudioSource
from diart.inference  import StreamingInference
from diart.sinks import RTTMWriter
import Util
import Util.settings

def Setup():
    
     
    try:
        model = Model.from_pretrained("pyannote/segmentation", token=Util.settings.hugging_face_token)
        pipeline = VoiceActivityDetection(segmentation=model)  
        pipeline = SpeakerDiarization()
        # mic = MicrophoneAudioSource()
        # inference = StreamingInference(pipeline, mic, do_plot=Util.settings.show_plot_gui)
        # inference.attach_observers(RTTMWriter(mic.uri, "file.rttm"))
        # prediction = inference()
    except Exception as e:
         print(e)
    print("success")
