# Failure Lab 08: Deterministic Guardrails & Interception Shims

## Vulnerability Focus
- **Failure Mode**: The agent is manipulated into executing obfuscated bash one-liners (`echo ... | base64 -d | sh`) to bypass LLM-as-a-judge prompt inspectors.
- **Systems Root Cause**: Relying on slow, probabilistic LLM evaluations instead of deterministic kernel/binary wrappers.

## Files
- `obfuscated_eval_attack.sh`: Simulates evasion payloads.
- `shim_tester.py`: Tests interception efficiency of POSIX shims in `/shims`.
