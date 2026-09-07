# Failure Lab 06: Threat Modeling for Autonomous Coding Agents

## Vulnerability Focus
- **Failure Mode**: The agent hallucinates a non-existent package (`fast-crypto-tools-py`) and installs it from public PyPI/npm, pulling down a malicious squatted package with an exfiltration preinstall hook.
- **Systems Root Cause**: Lack of an air-gapped internal package mirror or pre-install signature verification.

## Files
- `slopsquat_detector.py`: Deterministic pre-flight scanner verifying package metadata and blocking unverified outbound installation requests.
