# Failure Lab 13: Capstone Case Study — The Autonomous SRE Daemon

## Vulnerability Focus
- **Failure Mode**: High-severity production memory leak triggering 500 errors at 02:00 AM; autonomous triage agent encounters hallucinated remediation commands or risks dropping production database tables.
- **Systems Root Cause**: Uncontained autonomous operations on live production systems without sandboxed replica reproduction.

## Files
- `prometheus_alert_stub.json`: Simulated high-severity alert webhook payload.
- `leak_reproducer.py`: Memory leak reproduction script testing circular buffer leaks.
- `verify_fix.py`: Regression verification suite.
