#!/usr/bin/env python3
"""
Antigravity Systems Engineering - Chapter 12 Harness
Artifact: ipc_broker.py
Purpose: High-performance UNIX Domain Socket IPC server with length-prefixed JSON-RPC 2.0
         framing and kernel-verified peer credentials (SO_PEERCRED).
"""

import os
import sys
import socket
import struct
import json
import threading

SOCKET_PATH = "/tmp/antigravity-supervisor.sock"

class IPCBroker:
    def __init__(self, socket_path: str = SOCKET_PATH):
        self.socket_path = socket_path
        self.running = False
        self.server_sock = None

    def start(self):
        if sys.platform == "win32":
            print("[!] UNIX Domain Sockets are optimized for POSIX environments. Simulating IPC broker.")
            return

        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)

        self.server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_sock.bind(self.socket_path)
        os.chmod(self.socket_path, 0o600) # Restrict to supervisor user only
        self.server_sock.listen(16)
        self.running = True

        print(f"[*] IPC Broker listening on {self.socket_path}")

        try:
            while self.running:
                client_sock, _ = self.server_sock.accept()
                threading.Thread(target=self.handle_client, args=(client_sock,), daemon=True).start()
        except KeyboardInterrupt:
            self.stop()

    def handle_client(self, sock: socket.socket):
        # 1. Extract kernel-verified peer credentials
        peer_pid, peer_uid, peer_gid = None, None, None
        if hasattr(socket, "SO_PEERCRED"):
            creds = sock.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
            peer_pid, peer_uid, peer_gid = struct.unpack("3i", creds)
            print(f"[*] [IPC CONNECTION] Client authenticated by kernel: PID={peer_pid}, UID={peer_uid}, GID={peer_gid}")

        try:
            while True:
                # 2. Read 4-byte length prefix (big-endian uint32)
                raw_len = sock.recv(4)
                if not raw_len or len(raw_len) < 4:
                    break
                payload_len = struct.unpack(">I", raw_len)[0]

                # 3. Read JSON-RPC 2.0 payload
                data = bytearray()
                while len(data) < payload_len:
                    packet = sock.recv(payload_len - len(data))
                    if not packet:
                        break
                    data.extend(packet)

                if len(data) < payload_len:
                    break

                request = json.loads(data.decode("utf-8"))
                response = self.process_rpc(request, peer_pid)

                # 4. Emit framed response
                resp_bytes = json.dumps(response).encode("utf-8")
                sock.sendall(struct.pack(">I", len(resp_bytes)) + resp_bytes)
        except Exception as e:
            print(f"[!] IPC client error: {e}")
        finally:
            sock.close()

    def process_rpc(self, req: dict, client_pid: int) -> dict:
        req_id = req.get("id")
        method = req.get("method")

        if method == "agent.handshake":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "status": "authenticated",
                    "client_pid": client_pid,
                    "session_ttl": 3600
                }
            }
        elif method == "agent.heartbeat":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"status": "alive"}
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found"}
            }

    def stop(self):
        self.running = False
        if self.server_sock:
            self.server_sock.close()
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        print("[*] IPC Broker stopped.")

if __name__ == "__main__":
    broker = IPCBroker()
    broker.start()
