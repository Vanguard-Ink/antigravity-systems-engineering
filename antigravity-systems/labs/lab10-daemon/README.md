# Failure Lab 10: Headless Agent Architecture & Daemon Operations

## Vulnerability Focus
- **Failure Mode**: An unattended background agent enters an infinite reasoning loop or thread deadlock, running undetected for 14 hours and burning thousands of dollars in API credits.
- **Systems Root Cause**: Lack of a hardware or supervisor watchdog dead man's switch.

## Files
- `frozen_loop_daemon.py`: Simulates a frozen background worker daemon.
- `watchdog_supervisor.py`: Implements a dead man's switch terminating frozen agents via `SIGKILL`.
