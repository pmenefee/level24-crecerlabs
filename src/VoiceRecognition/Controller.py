from pyannote.audio import Model
from pyannote.audio.pipelines import VoiceActivityDetection
from diart import SpeakerDiarization
from diart.sources import MicrophoneAudioSource
from diart.inference  import StreamingInference
from diart.sinks import RTTMWriter
import Util
import Util.settings

def Setup():
    model = Model.from_pretrained("pyannote/segmentation", use_auth_token="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")
    #pipeline = VoiceActivityDetection(segmentation=model)   
    try:
        pipeline = SpeakerDiarization()
        mic = MicrophoneAudioSource()
        inference = StreamingInference(pipeline, mic, do_plot=Util.settings.show_plot_gui)
        inference.attach_observers(RTTMWriter(mic.uri, "file.rttm"))
        prediction = inference()
    except Err as e:
         print(e)
    print("success")
