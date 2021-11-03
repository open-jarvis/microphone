"""
Copyright (c) 2021 Philipp Scheer
"""


import os
import sys
import zlib
import time
import base64
import signal
import threading
from classes.Microphone import Microphone
from classes.Stream import Stream
from jarvis_sdk import Connection, Storage


Storage.PATH = os.path.dirname(os.path.abspath(__file__))
DEVICE_ID = Storage.get("dev-id", None)
HOST = Storage.get("host", "jarvis.fipsi.at")


stream = None
mic = None


def start_stream():
    global stream, mic, DEVICE_ID

    if DEVICE_ID is None:
        DEVICE_ID = Storage.get("dev-id", None)
    if DEVICE_ID is None:
        print(f"+ No device ID found")
        exit(1)

    print(f"+ Connecting to {HOST} with device {DEVICE_ID}")

    stream  = Stream(DEVICE_ID, host=HOST)

    def hj(x):
        # print(x)
        return x
    stream.hijack = hj

    mic     = Microphone()
    seconds = 0.5

    def _stream_ready():
        print(f"+ Stream {stream.stream_id} sending")
        def _on_chunk(chunk):
            start = time.time()
            chunk_compressed = zlib.compress(chunk)
            compression_time = time.time() - start
            full_length = len(chunk)
            compressed_length = len(chunk_compressed)
            compression_rate = (1 - compressed_length / full_length)
            stream.send({
                "$meta": {
                    "$id": stream.stream_id,
                    "format": "wave",
                    "seconds": seconds,
                    "chunks": int(mic.fs / mic.chunk * seconds),
                    "channels": mic.channels,
                    "framerate": mic.fs
                },
                "$internals": {
                    "timestamp": start,
                    "compression": {
                        "enabled": False,
                        "time": compression_time,
                        "length": {
                            "full": full_length,
                            "compressed": compressed_length
                        },
                        "ratio": compression_rate
                    }
                },
                "data": base64.b64encode(chunk).decode("utf-8"),
            })
        mic.record(_on_chunk, seconds=seconds)

    def _stream_close():
        print("+ Stream closing")
        mic.stop()

    def _stream_error(er, orig_message):
        print("+ Stream error", er, orig_message)

    stream.on_ready = _stream_ready
    stream.on_close = _stream_close
    stream.on_error = _stream_error

    stream.open("audio")


def start_mic_stream():
    global DEVICE_ID
    print(f"+ Device ID is {DEVICE_ID}")
    if DEVICE_ID is None:
        def _on_open():
            def _on_device_id(msg):
                if msg.get("success"):
                    print("< Here you are:", msg.get("result", {}).get("id"))
                    DEVICE_ID = msg.get("result", {}).get("id")
                    Storage.set("dev-id", DEVICE_ID)
                    start_stream()
                else:
                    print("< No!")
                    print("\nError: Failed to get ID", msg)
                    exit(1)
            print("> Can you give me an anonymous ID?")
            con.request("device/anonymous", payload={"type": "microphone"}, callback=_on_device_id)
        con = Connection(None)
        con.on_open = _on_open
    else:
        start_stream()

def stop_mic_stream():
    if mic:
        mic.stop()
    if stream:
        stream.close()


start_mic_stream()


while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        stop_mic_stream()


        exit_ts = time.time() + 5

        while time.time() < exit_ts:
            print("============================================")
            for thread in threading.enumerate(): 
                print(thread.name, thread.is_alive())
            time.sleep(0.9)

        try:
            os._exit()
        except Exception:
            try:
                os.kill(os.getpid(), signal.SIGINT)
            except Exception:
                pass