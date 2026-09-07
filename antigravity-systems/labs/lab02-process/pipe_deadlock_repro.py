#!/usr/bin/env python3
"""
Failure Lab 02 - Linux Pipe Buffer Deadlock Reproduction
Demonstrates how emitting > 64KB of output without concurrent stream draining
hangs an agent subshell indefinitely in the Linux kernel.
"""

import sys
import subprocess
import time

def trigger_deadlock():
    print("[*] Spawning child process that emits 128KB of stdout...")
    
    # Child script that emits 128KB (exceeding standard 64KB pipe capacity)
    child_cmd = [
        sys.executable,
        "-c",
        "import sys; sys.stdout.write('A' * 131072); sys.stdout.flush(); sys.exit(0)"
    ]

    # VULNERABLE PATTERN: Using subprocess.PIPE synchronously without concurrent drain
    proc = subprocess.Popen(child_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    print("[*] Child process spawned (PID: %d). Calling proc.wait()..." % proc.pid)
    print("[!] IF DEADLOCK OCCURS: The script will hang indefinitely here!")

    start = time.time()
    try:
        # This will block forever on POSIX systems because the child cannot finish writing
        # its 128KB while the pipe buffer (64KB) is full and unread.
        proc.wait(timeout=5)
        print("[*] Completed without deadlock.")
    except subprocess.TimeoutExpired:
        print("\n[CRITICAL FAILURE - DEADLOCK CONFIRMED]")
        print("  Child process PID %d is frozen in kernel write(1, ...) state." % proc.pid)
        print("  Kernel pipe buffer is completely saturated at 65,536 bytes.")
        proc.kill()
        print("  Child killed by watchdog.")

if __name__ == "__main__":
    trigger_deadlock()
