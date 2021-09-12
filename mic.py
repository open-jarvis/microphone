"""
Copyright (c) 2021 Philipp Scheer
"""


import time
import pyaudio
import tasks.record
import tasks.comm
from jarvis_sdk import Connection, Highway


DEVICE_ID = "ec66e636372a47f68729386a2d3c7531"
HOST = "jarvis.fipsi.at"


Highway.send("jarvis/credentials", {
    "id": DEVICE_ID,
    "host": HOST
})


def on_chunk(chunk):
    # XXX: hijack chunks here
    pass


Highway.on("mic/data", on_chunk)

tasks.record.start_recording()

while True:
    try:
        time.sleep(1)
    except Exception:
        exit()
