# Failure Lab 07: Indirect Prompt Injection Defense

## Vulnerability Focus
- **Failure Mode**: An automated CI bug-fixing agent reads a GitHub issue description containing hidden prompt overrides that coerce the model into running `DROP TABLE users` or exfiltrating tokens.
- **Systems Root Cause**: Conflation of the control plane (system instructions) with the untrusted data plane (user issue text).

## Files
- `issue_injection_payload.md`: Simulated GitHub issue containing indirect prompt hijacking payloads.
- `context_fencer.py`: Implementation of cryptographic and structural context fencing neutralizing prompt overrides.
