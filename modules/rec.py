import pyaudio
import wave
import os
from threading import Thread

class AudioRecorder:
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    WAVE_OUTPUT_FILENAME = "files/recording.mp3"
    recording = False
    frames = []
    

    @classmethod
    def start_recording(cls):
        if os.path.exists(cls.WAVE_OUTPUT_FILENAME):
            os.remove(cls.WAVE_OUTPUT_FILENAME)

        cls.recording = True
        cls.frames = []
        
        cls.record_thread = Thread(target=cls._record)
        cls.record_thread.start()
        print("* recording started")
    
    @classmethod
    def stop_recording(cls):
        cls.recording = False
        if hasattr(cls, 'record_thread'):
            cls.record_thread.join()
        cls._save_recording()
        print("* recording stopped and saved")
    
    @classmethod
    def _record(cls):
        p = pyaudio.PyAudio()
        
        stream = p.open(format=cls.FORMAT,
                       channels=cls.CHANNELS,
                       rate=cls.RATE,
                       input=True,
                       frames_per_buffer=cls.CHUNK,
                       input_device_index=1)
        
        while cls.recording:
            data = stream.read(cls.CHUNK)
            cls.frames.append(data)
            
        stream.stop_stream()
        stream.close()
        p.terminate()
    
    @classmethod
    def _save_recording(cls):
        if len(cls.frames) > 0:
            p = pyaudio.PyAudio()
            wf = wave.open(cls.WAVE_OUTPUT_FILENAME, 'wb')
            wf.setnchannels(cls.CHANNELS)
            wf.setsampwidth(p.get_sample_size(cls.FORMAT))
            wf.setframerate(cls.RATE)
            wf.writeframes(b''.join(cls.frames))
            wf.close()
            p.terminate()