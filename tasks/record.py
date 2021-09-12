"""
Copyright (c) 2021 Philipp Scheer
"""


from jarvis_sdk import Highway
import pyaudio


chunk          = 1024 * 64                # Each chunk will consist of 1024 * 1024 samples
sample_format  = pyaudio.paInt16     # 16 bits per sample
channels       = 4                   # Number of audio channels
fs             = 44100               # Record at 44100 samples per second
chunk_size     = chunk * 16/8 * channels # in byte -> 8kB
keep_recording = True


# Store data in chunks for 3 seconds
def start_recording(data=None):
    global keep_recording

    keep_recording = True

    p = pyaudio.PyAudio()               # Create an interface to PortAudio
    # Open a Stream with the values we just defined
    stream = p.open(format   = sample_format,
                    channels = channels,
                    rate     = fs,
                    frames_per_buffer = chunk,
                    input    = True)

    while keep_recording:
        data = stream.read(chunk, exception_on_overflow = False)
        Highway.send("mic/data", data)

    # Stop and close the Stream and PyAudio
    stream.stop_stream()
    stream.close()
    p.terminate()


def stop_recording(data=None):
    global keep_recording
    keep_recording = False
