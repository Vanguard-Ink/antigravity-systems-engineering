# Antigravity Systems: The 13 Failure Labs

This directory contains the runnable experimental labs designed to **break the system** and prove the necessity of kernel-level runtime isolation, adversarial containment, and deterministic shims.

Every lab includes:
1. **The Vulnerable Component / Attack Payload**: Demonstrating the catastrophic failure when naive approaches are used.
2. **Forensic Log & System Traces**: Examining the kernel metrics, `/proc` tables, or network logs.
3. **The Deterministic Architectural Fix**: Applying the verified systems isolation fix.

---

## Lab Directory Index

| Lab | Corresponding Chapter | Target Failure Mode / Exploit | Deterministic Systems Fix |
| :--- | :--- | :--- | :--- |
| **`lab01-shell`** | Ch 01: The Shell Problem | Ambient `.env` exfiltration via markdown prompt injection. | Environment purge (`env -i`) & egress drop. |
| **`lab02-process`** | Ch 02: Systems Anatomy | 64KB pipe buffer deadlock & zombie PID table exhaustion. | Asynchronous stream drainers & `waitpid` loop. |
| **`lab03-sandbox`** | Ch 03: Sandbox Internals | Fork-bomb (`:(){ :\|:& };:`) & disk exhaustion. | cgroups v2 `pids.max=64`, tmpfs size caps. |
| **`lab04-permissions`** | Ch 04: Permissions & Allowlists | Regex evasion (IFS, quote splitting, base64 pipes). | Tree-sitter AST shell parser allowlisting. |
| **`lab05-ephemeral`** | Ch 05: Ephemeral Workspaces | Accidental `rm -rf /` or dependency corruption. | Copy-on-Write OverlayFS instant rollback. |
| **`lab06-threat-modeling`** | Ch 06: Threat Modeling | Hallucinated package installation / slopsquatting callback. | Pre-install package verification shim. |
| **`lab07-injection`** | Ch 07: Indirect Injection | Destructive DB commands hidden in issue descriptions. | Context fencing & JSON-RPC schema enforcement. |
| **`lab08-shims`** | Ch 08: Deterministic Shims | Obfuscated `base64 -d \| sh` execution. | Binary interception shims & PATH priority. |
| **`lab09-network`** | Ch 09: Network & Secrets | Reverse TCP shell & DNS tunneling exfiltration. | Default-drop network namespaces (`CLONE_NEWNET`).|
| **`lab10-daemon`** | Ch 10: Headless Daemons | Zombie execution freeze burning unlimited LLM tokens. | Systemd `WatchdogSec=30s` dead man's switch. |
| **`lab11-checkpoints`** | Ch 11: State Checkpoints | Hard crash (`kill -9`) midway through 3-hour refactoring. | Write-Ahead Logging (WAL) state rehydration. |
| **`lab12-ipc`** | Ch 12: Fleet Orchestration | Loopback port hijacking & lateral worker poisoning. | Abstract UNIX Domain Sockets (`SO_PEERCRED`). |
| **`lab13-sre`** | Ch 13: Autonomous SRE | Hallucinated diagnostic command during production outage.| Ephemeral replica sandbox & safety shims. |
