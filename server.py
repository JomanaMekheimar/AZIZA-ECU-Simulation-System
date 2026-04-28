# ============================================================
# AZIZA - Distributed Automotive ECU Simulation
# server.py — Built-in HTTP + WebSocket server (no dependencies)
# ============================================================

import json
import threading
import time
import socket
import hashlib
import base64
import struct
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler


class AZIZAServer:
    def __init__(self, engine_ecu=None):
        self.engine_ecu = engine_ecu
        self._clients = []
        self._lock = threading.Lock()
        self._latest_payload = None

        self._server = HTTPServer(("0.0.0.0", 8765), self._make_handler())

    def _make_handler(self):
        server_ref = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, fmt, *args):
                pass  # Silence access logs

            def do_GET(self):
                if self.path == "/" or self.path == "/index.html":
                    dashboard_path = Path(__file__).parent / "dashboard.html"
                    if dashboard_path.exists():
                        content = dashboard_path.read_bytes()
                        self.send_response(200)
                        self.send_header("Content-Type", "text/html; charset=utf-8")
                        self.send_header("Content-Length", str(len(content)))
                        self.end_headers()
                        self.wfile.write(content)
                    else:
                        self.send_response(404)
                        self.end_headers()
                        self.wfile.write(b"dashboard.html not found")

                elif self.path == "/ws":
                    # WebSocket handshake
                    key = self.headers.get("Sec-WebSocket-Key", "")
                    accept = base64.b64encode(
                        hashlib.sha1(
                            (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()
                        ).digest()
                    ).decode()

                    self.send_response(101)
                    self.send_header("Upgrade", "websocket")
                    self.send_header("Connection", "Upgrade")
                    self.send_header("Sec-WebSocket-Accept", accept)
                    self.end_headers()

                    # Register this client
                    with server_ref._lock:
                        server_ref._clients.append(self)

                    # Send latest state immediately if available
                    if server_ref._latest_payload:
                        self._ws_send(server_ref._latest_payload)

                    # Keep alive — read incoming frames (commands from browser)
                    try:
                        while True:
                            data = self._ws_recv()
                            if data is None:
                                break
                            try:
                                cmd = json.loads(data)
                                server_ref._handle_command(cmd)
                            except Exception:
                                pass
                    except Exception:
                        pass
                    finally:
                        with server_ref._lock:
                            if self in server_ref._clients:
                                server_ref._clients.remove(self)

                else:
                    self.send_response(404)
                    self.end_headers()

            def _ws_send(self, text):
                payload = text.encode("utf-8")
                length = len(payload)
                if length <= 125:
                    header = bytes([0x81, length])
                elif length <= 65535:
                    header = bytes([0x81, 126]) + struct.pack(">H", length)
                else:
                    header = bytes([0x81, 127]) + struct.pack(">Q", length)
                self.wfile.write(header + payload)
                self.wfile.flush()

            def _ws_recv(self):
                try:
                    self.connection.settimeout(60)
                    b1, b2 = self.rfile.read(2)
                    opcode = b1 & 0x0F
                    if opcode == 8:  # Close frame
                        return None
                    masked = b2 & 0x80
                    length = b2 & 0x7F
                    if length == 126:
                        length = struct.unpack(">H", self.rfile.read(2))[0]
                    elif length == 127:
                        length = struct.unpack(">Q", self.rfile.read(8))[0]
                    mask = self.rfile.read(4) if masked else b"\x00\x00\x00\x00"
                    data = bytearray(self.rfile.read(length))
                    if masked:
                        for i in range(len(data)):
                            data[i] ^= mask[i % 4]
                    return data.decode("utf-8")
                except Exception:
                    return None

        return Handler

    def _handle_command(self, cmd):
        if self.engine_ecu is None:
            return
        action = cmd.get("action")
        if action == "cruise_on":
            self.engine_ecu.enable_cruise(float(cmd.get("target_speed", 80.0)))
        elif action == "cruise_off":
            self.engine_ecu.disable_cruise()
        elif action == "set_target_speed":
            self.engine_ecu.target_speed = float(cmd.get("value", 80.0))

    def push_state(self, state: dict, log_lines: list):
        payload = json.dumps({"state": state, "log": log_lines})
        self._latest_payload = payload
        dead = []
        with self._lock:
            clients = list(self._clients)
        for client in clients:
            try:
                client._ws_send(payload)
            except Exception:
                dead.append(client)
        if dead:
            with self._lock:
                for c in dead:
                    if c in self._clients:
                        self._clients.remove(c)

    def start(self):
        t = threading.Thread(
            target=self._server.serve_forever,
            daemon=True
        )
        t.start()
        time.sleep(0.5)
        print("[SERVER] Dashboard running at http://localhost:8765")
