# Failure Lab 04: Permissions, Boundaries, and Command Allowlists

## Vulnerability Focus
- **Failure Mode**: Bypassing naive regular-expression string blacklists to execute blocked commands (`curl`, `rm -rf`, `sudo`).
- **Systems Root Cause**: Shell syntax parsing allows endless permutations (quote concatenation, `$IFS`, variable interpolation, base64 pipes) that evade regex patterns.

## Files
- `regex_bypass_demo.sh`: Demonstrates 5 distinct shell evasion patterns bypassing standard regex filters.
- `ast_validator.py`: Demonstrates AST parsing to validate command semantics reliably.
