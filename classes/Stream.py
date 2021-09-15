"""
Copyright (c) 2021 Philipp Scheer
"""


from jarvis_sdk import Connection


class Stream:
    def __init__(self, device_id: str, host: str = "jarvis.fipsi.at", port: int = 5522) -> None:
        self.id = device_id
        self.host = host
        self.port = port
        self.comm = None
        self.ready = False
        self.on_error = None
        self.on_ready = None
        self.on_close = None
        self.stream_id = None
        self.type = None

    def open(self, type: str):
        self.type = type
        self.comm = Connection(self.id, self.host, self.port, debug=True)
        def _on_comm_open():
            def _on_stream_open(msg):
                # msg looks like
                # {
                #   "success": True | False,
                #   "error": "error message if success == False"
                #   "result": {
                #       "id": "abcdef0123456789", # a unique stream id to always include in requests
                #   }
                # }
                if not msg.get("success", False):
                    if callable(self.on_error):
                        self.on_error(msg.get("error", msg.get("result", None)), orig_message=msg)
                else:
                    self.stream_id = msg.get("result", {}).get("id", None)
                    self.ready = True
                    if callable(self.on_ready):
                        self.on_ready()
            self.comm.request(f"stream/{type}/open", {}, _on_stream_open)
        self.comm.on_open = _on_comm_open

    def send(self, data: dict):
        assert isinstance(self.comm, Connection), "No communication object ready"
        assert self.ready, "Connection not ready yet"
        self.comm.request(f"stream/{self.type}/data", payload={**data, "$id": self.stream_id}, callback=None)

    def close(self):
        self.comm.request(f"stream/{self.type}/close", payload={"$id": self.stream_id}, callback=None)
        if callable(self.on_close):
            self.on_close()
