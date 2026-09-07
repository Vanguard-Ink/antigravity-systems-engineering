# Antigravity Harnesses: Daemon & Supervisor Runtime

This directory contains the production-grade host harnesses responsible for process lifecycle supervision, resource ceilings, IPC arbitration, and crash recovery.

---

## Files

- **`supervisor.py`**: Robust POSIX subshell supervisor. Sets process groups (`setpgrp`), prevents zombie process accumulation, drains stdout/stderr asynchronously to avoid pipe buffer deadlocks, and enforces hard timeouts.
- **`ipc_broker.py`**: UNIX Domain Socket broker providing low-latency, framed JSON-RPC 2.0 streaming, peer credential verification (`SO_PEERCRED`), and file descriptor transmission (`SCM_RIGHTS`).
