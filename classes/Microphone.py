"""
Copyright (c) 2021 Philipp Scheer
"""


import wave
import pyaudio
from io import BytesIO


class Microphone:
    def __init__(self) -> None:
        self.chunk = 1024  # Record in chunks of 1024 samples
        self.sample_format = pyaudio.paInt16  # 16 bits per sample
        self.channels = 2
        self.fs = 44100  # Record at 44100 samples per second
        self.p = pyaudio.PyAudio()  # Create an interface to PortAudio
        self.frames = [] # Initialize array to store frames

    def record(self, callback = None, seconds: int = 5):
        self.stream = self.p.open(  format=self.sample_format,
                                    channels=self.channels,
                                    rate=self.fs,
                                    frames_per_buffer=self.chunk,
                                    input=True)
        while True:
            frames = []
            for i in range(0, int(self.fs / self.chunk * seconds)):
                data = self.stream.read(self.chunk)
                frames.append(data)
                # Save the recorded data as a WAV file
            byteswav = BytesIO()
            byteswav.close = lambda: None
            wf = wave.open(byteswav, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.sample_format))
            wf.setframerate(self.fs)
            wf.writeframes(b''.join(frames))
            wf.close()
            byteswav.seek(0)
            if callable(callback):
                callback(byteswav.read())

    def stop(self):
        self.frames = []
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
