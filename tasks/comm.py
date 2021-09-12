"""
Copyright (c) 2021 Philipp Scheer
"""


import time
import zlib
import base64
from jarvis_sdk import Connection, Highway


con = None
streaming_callback = None

def get_credentials(credentials):
    global con, streaming_callback

    id   = credentials.get("id", "")
    host = credentials.get("host", "")
    con = Connection(id, host)
    def get_streaming_callback():
        global streaming_callback, con
        con.request("status", {}, print)
        # streaming_callback = con.stream("stream/audio")
    con.on_open = get_streaming_callback


def send_chunk(chunk):
    global streaming_callback
    if streaming_callback is None: return

    start = time.time()

    chunk_compressed = zlib.compress(chunk)

    compression_time = time.time() - start
    compression_rate = (1 - (len(chunk_compressed) / len(chunk)))

    streaming_callback({
        "$meta": {
            "timestamp": start,
            "compression": {
                "time": compression_time,
                "rate": compression_rate
            }
        },
        "data": base64.b64encode(chunk_compressed).decode("utf-8")
    })


Highway.on("mic/data", send_chunk)
Highway.on("jarvis/credentials", get_credentials)
