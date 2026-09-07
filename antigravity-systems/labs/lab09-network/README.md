# Failure Lab 09: Network Egress & Secret Isolation

## Vulnerability Focus
- **Failure Mode**: The agent is restricted from HTTP egress, but silently exfiltrates sensitive AWS keys through DNS tunneling queries (`<base32_secret>.attacker.com`) over UDP port 53.
- **Systems Root Cause**: Failure to isolate the Linux network namespace (`CLONE_NEWNET`) or enforce strict DNS proxying.

## Files
- `dns_tunnel_exfil.py`: Demonstrates DNS exfiltration mechanics.
- `network_drop_verifier.sh`: Validates complete network boundary isolation using netfilter and `CLONE_NEWNET`.
