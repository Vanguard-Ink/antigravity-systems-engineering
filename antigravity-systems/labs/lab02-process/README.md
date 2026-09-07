# Failure Lab 02: Systems Anatomy of Agent Execution

## Vulnerability Focus
- **Failure Mode**: Linux kernel pipe buffer exhaustion (64KB default capacity) causing unrecoverable deadlock in synchronous agent subshell harnesses.
- **Systems Root Cause**: Process blocked on `write(1, ...)` waiting for buffer drain while parent process is blocked on `waitpid()` waiting for child exit.

## Files
- `pipe_deadlock_repro.py`: Reproduces the freeze by emitting 128KB of diagnostic text into an unbuffered pipe.
- `pty_stream_fix.py`: Deterministic fix utilizing non-blocking asynchronous stream readers.
