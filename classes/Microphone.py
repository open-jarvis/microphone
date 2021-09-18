"""
Copyright (c) 2021 Philipp Scheer
"""


import pyaudio


class Microphone:
    def __init__(self, chunks: int = 1024 * 20, sample_format = pyaudio.paInt16, channels: int = 4, sample_rate: int = 44100) -> None:
        self.on_chunk = None
        self.config = {
            "frames_per_buffer": chunks,
            "format": sample_format,
            "channels": channels,
            "rate": sample_rate
        }
        self.interface = None
        self.stream = None
        self.recording = False

    def start(self):
        self.interface = pyaudio.PyAudio()
        self.stream = self.interface.open(input = True, **self.config)
        self.recording = True
        while self.recording:
            data = self.stream.read(self.config.get("frames_per_buffer", 1024 * 64), exception_on_overflow = False)
            if callable(self.on_chunk):
                self.on_chunk(data)

    def stop(self):
        if not self.recording: return
        self.recording = False
        print(self.stream, self.interface)
        if hasattr(self.stream, "stop_stream"):
            self.stream.stop_stream()
            self.stream.close()
        if hasattr(self.interface, "terminate"):
            self.interface.terminate()

