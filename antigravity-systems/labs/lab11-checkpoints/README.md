# Failure Lab 11: State Persistence & Agent Checkpoints

## Vulnerability Focus
- **Failure Mode**: A multi-hour autonomous refactoring task is terminated midway by an OS OOM event or power loss (`kill -9`), losing all progress and leaving Git index in an inconsistent state.
- **Systems Root Cause**: Ephemeral memory-only state management without structured Write-Ahead Logging (WAL) for conversational and filesystem mutations.

## Files
- `wal_checkpoint_engine.py`: Implements atomic state serialization and recovery routines.
- `crash_recovery_test.py`: Simulates unexpected mid-flight process termination and verifies 100% state recovery.
