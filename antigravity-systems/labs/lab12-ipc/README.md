# Failure Lab 12: Inter-Process Communication & Fleet Orchestration

## Vulnerability Focus
- **Failure Mode**: Coordinating worker agents over local TCP ports allows rogue unprivileged local processes to connect to open loopback ports and inject forged commands.
- **Systems Root Cause**: Lack of kernel-enforced peer credential authentication (`SO_PEERCRED`) on generic TCP loopback sockets.

## Files
- `unix_socket_dispatcher.py`: Implements secure multi-agent coordination using local abstract UNIX Domain Sockets.
- `rogue_hijack_simulation.py`: Demonstrates TCP port hijacking vs. UNIX domain socket rejection.
