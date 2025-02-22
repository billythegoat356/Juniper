import whisper

import functools
whisper.torch.load = functools.partial(whisper.torch.load, weights_only=True)



# Load Whisper model
model = whisper.load_model("turbo", device="cuda")
# model = whisper.load_model("large-v3-turbo", device="cuda")
# model = whisper.load_model("medium.en", device="cuda")

file_path = "files/recording.mp3"

def transcribe():
    result = model.transcribe(file_path, language="en")
    return result['text']