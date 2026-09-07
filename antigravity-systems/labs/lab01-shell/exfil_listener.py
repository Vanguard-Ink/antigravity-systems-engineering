#!/usr/bin/env python3
"""
Failure Lab 01 - Forensic Exfiltration Listener
Captures unauthorized HTTP exfiltration requests sent by compromised agents or subshells.
"""

import http.server
import socketserver
import urllib.parse
import sys
import datetime
import base64

PORT = 8888
HOST = "127.0.0.1"

class ForensicExfilHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        print(f"\n[ALERT - FORENSIC INTERCEPT] {timestamp}")
        print(f"  Method: GET")
        print(f"  Path:   {parsed.path}")
        print(f"  Source: {self.client_address[0]}:{self.client_address[1]}")
        print(f"  Headers:")
        for header, val in self.headers.items():
            print(f"    {header}: {val}")

        if params:
            print("  Query Parameters (Potential Staged Exfil):")
            for k, v in params.items():
                print(f"    {k} = {v}")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"received","forensic_action":"logged"}\n')

    def do_POST(self):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)

        print(f"\n[CRITICAL ALERT - DATA EXFILTRATION DETECTED] {timestamp}")
        print(f"  Target Endpoint: {parsed.path}")
        print(f"  Origin Address:  {self.client_address[0]}:{self.client_address[1]}")
        print(f"  User-Agent:      {self.headers.get('User-Agent', 'Unknown')}")
        print(f"  Payload Size:    {content_length} bytes")

        print("  Raw Captured Payload:")
        body_text = raw_body.decode("utf-8", errors="replace")
        print(f"    {body_text[:500]}{'...' if len(body_text) > 500 else ''}")

        if "env=" in body_text:
            try:
                encoded_part = body_text.split("env=")[1].split("&")[0]
                decoded = base64.b64decode(urllib.parse.unquote(encoded_part)).decode("utf-8", errors="replace")
                print("  [DECODED ENVIRONMENT PAYLOAD]:")
                for line in decoded.strip().split("\n"):
                    if any(secret in line.upper() for secret in ["KEY", "TOKEN", "SECRET", "PASS", "AUTH", "DATABASE"]):
                        print(f"    >>> [LEAKED SECRET] {line}")
                    else:
                        print(f"        {line}")
            except Exception as e:
                print(f"  [DECODE ERROR]: {e}")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"exfiltrated","action":"acknowledged"}\n')

def run_listener():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), ForensicExfilHandler) as httpd:
        print(f"================================================================================")
        print(f"[*] FORENSIC EXFILTRATION LISTENER ACTIVE ON http://{HOST}:{PORT}")
        print(f"[*] Awaiting unauthorized outbound telemetry from subshell processes...")
        print(f"[*] Press Ctrl+C to terminate listener.")
        print(f"================================================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Listener shut down cleanly.")

if __name__ == "__main__":
    run_listener()
