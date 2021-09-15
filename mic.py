"""
Copyright (c) 2021 Philipp Scheer
"""


import os
import zlib
import time
import signal
import base64
from classes.Microphone import Microphone
from classes.Stream import Stream
from jarvis_sdk import Connection, Highway, Storage


DEVICE_ID = Storage.get("dev-id", None)
HOST = Storage.get("host", "jarvis.fipsi.at")

stream = None
mic = None


def start_stream():
    global stream, mic

    print(f"+ Connecting to {HOST} with device {DEVICE_ID}")

    stream = Stream(DEVICE_ID, host=HOST)
    mic = Microphone()

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
                    **mic.config
                },
                "$internals": {
                    "timestamp": start,
                    "compression": {
                        "enabled": True,
                        "time": compression_time,
                        "length": {
                            "full": full_length,
                            "compressed": compression_time
                        },
                        "ratio": compression_rate
                    }
                },
                "data": base64.b64encode(chunk_compressed).decode("utf-8")
            })
        mic.on_chunk = _on_chunk
        mic.start()

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
    if DEVICE_ID is None:
        def _on_open():
            def _on_device_id(msg):
                if msg.get("success"):
                    DEVICE_ID = msg.get("result", {}).get("id")
                    Storage.set("dev-id", DEVICE_ID)
                    start_stream()
                else:
                    print("Error: Failed to get ID", msg)
            con.request("device/anonymous", payload={}, callback=_on_device_id)
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

        try:
            os._exit()
        except Exception:
            try:
                os.kill(os.getpid(), signal.SIGINT)
            except Exception:
                pass
