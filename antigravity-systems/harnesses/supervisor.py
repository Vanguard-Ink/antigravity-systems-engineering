#!/usr/bin/env python3
"""
Antigravity Systems Engineering - Chapter 2 & 10 Harness
Artifact: supervisor.py
Purpose: Production-grade process supervisor for executing autonomous agent subshells.
         Enforces process group isolation, asynchronous stream draining (deadlock prevention),
         hard timeouts, signal forwarding, and zombie reaping.
"""

import os
import sys
import time
import signal
import subprocess
import threading
import queue

class ProcessSupervisor:
    def __init__(self, timeout_seconds: int = 60, max_output_bytes: int = 1048576):
        self.timeout_seconds = timeout_seconds
        self.max_output_bytes = max_output_bytes
        self.process = None
        self.pgid = None

    def execute(self, cmd: list[str], env: dict = None, cwd: str = None) -> tuple[int, str, str]:
        """
        Executes a command under strict supervision.
        - Spawns process in a new process group (os.setpgrp).
        - Spawns background threads to drain stdout/stderr to prevent 64KB pipe buffer deadlock.
        - Sends SIGKILL to the entire process group if timeout is exceeded.
        """
        # Ensure minimal clean environment if none provided
        if env is None:
            env = {
                "PATH": "/usr/local/bin:/usr/bin:/bin",
                "LANG": "C.UTF-8",
                "LC_ALL": "C.UTF-8",
                "TERM": "xterm-256color"
            }

        stdout_chunks = []
        stderr_chunks = []
        stdout_bytes_collected = 0
        stderr_bytes_collected = 0

        def preexec_fn():
            # Create a new process group so that child subshells share the PGID.
            # This allows killing the entire process tree atomically.
            if hasattr(os, "setpgrp"):
                os.setpgrp()

        # Spawn subshell process
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE, # Disallow interactive stdin blocking
            env=env,
            cwd=cwd,
            preexec_fn=preexec_fn if sys.platform != "win32" else None,
            close_fds=True,
            text=False
        )

        try:
            self.pgid = os.getpgid(self.process.pid) if sys.platform != "win32" else None
        except ProcessLookupError:
            self.pgid = None

        # Asynchronous stream drainers
        def reader(stream, chunk_list, is_stderr=False):
            nonlocal stdout_bytes_collected, stderr_bytes_collected
            while True:
                chunk = stream.read(4096)
                if not chunk:
                    break
                chunk_list.append(chunk)
                if is_stderr:
                    stderr_bytes_collected += len(chunk)
                else:
                    stdout_bytes_collected += len(chunk)
                
                # Check buffer ceiling to prevent memory exhaustion
                if (stdout_bytes_collected + stderr_bytes_collected) > self.max_output_bytes:
                    break
            stream.close()

        t_out = threading.Thread(target=reader, args=(self.process.stdout, stdout_chunks, False))
        t_err = threading.Thread(target=reader, args=(self.process.stderr, stderr_chunks, True))
        t_out.daemon = True
        t_err.daemon = True
        t_out.start()
        t_err.start()

        # Wait with timeout
        start_time = time.time()
        timed_out = False

        while True:
            ret = self.process.poll()
            if ret is not None:
                break
            if time.time() - start_time > self.timeout_seconds:
                timed_out = True
                self.terminate_process_group()
                break
            time.sleep(0.05)

        t_out.join(timeout=1.0)
        t_err.join(timeout=1.0)

        raw_stdout = b"".join(stdout_chunks).decode("utf-8", errors="replace")
        raw_stderr = b"".join(stderr_chunks).decode("utf-8", errors="replace")

        if timed_out:
            raw_stderr += f"\n[SUPERVISOR TIMEOUT] Execution exceeded hard limit of {self.timeout_seconds}s. Process group killed."
            return 124, raw_stdout, raw_stderr

        return self.process.returncode, raw_stdout, raw_stderr

    def terminate_process_group(self):
        """Sends SIGTERM followed by SIGKILL to the entire process group."""
        if not self.process:
            return

        if sys.platform != "win32" and self.pgid:
            try:
                os.killpg(self.pgid, signal.SIGTERM)
                time.sleep(0.1)
                os.killpg(self.pgid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
        else:
            try:
                self.process.kill()
            except ProcessLookupError:
                pass

if __name__ == "__main__":
    supervisor = ProcessSupervisor(timeout_seconds=5)
    test_cmd = ["python", "-c", "import sys; print('Supervisor test execution output'); sys.exit(0)"]
    code, out, err = supervisor.execute(test_cmd)
    print(f"Exit Code: {code}")
    print(f"Output: {out.strip()}")
