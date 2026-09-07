# Antigravity Shims: Deterministic Guardrail Proxies

This directory contains executable binary interception wrappers (shims). By prepending this directory to the agent's restricted `PATH`, the operating system enforces security policies deterministically at sub-millisecond speeds, completely eliminating the latency, cost, and probabilistic bypass vulnerabilities of "LLM-as-a-judge" prompts.

---

## Shims Catalog

- **`curl`**: Blocks unapproved WAN egress and rejects any command argument referencing local secret files (`.env`, `id_rsa`, `credentials`).
- **`git`**: Blocks `--upload-pack`, `-c core.editor=*`, and forced pushes (`--force`, `-f`).
- **`npm`**: Blocks arbitrary unpinned `npx` execution and prevents running unvetted post-install hooks.
- **`env-clean`**: Flushes the parent environment block with `/usr/bin/env -i` before running commands.
