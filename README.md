# ANTIGRAVITY SYSTEMS ENGINEERING
## Runtime Isolation, Adversarial Containment, and Headless Agent Daemons

> **The Invariant Thesis**:  
> *"Agent autonomy is not a prompt-safety problem. It is an operating-system problem."*

---

### About This Monograph

**Antigravity Systems Engineering** is a canonical technical monograph authored for Staff/Principal Engineers, Systems Architects, DevSecOps Leads, and senior AI Platform Engineers.

While application-layer frameworks focus on prompting agents to write better code, this work focuses on the operating system, the runtime fortress, and the supervision engine: **how modern operating systems isolate, govern, contain, and supervise autonomous agent processes touching the shell and kernel.**

---

### Repository Layout

```text
.
├── MD.md                       # Master Architecture & Canonical Table of Contents
├── README.md                   # Repository Overview and Guidelines
├── research/                   # Empirical Research Corpus & Ground Truth Dossiers
│   ├── 01_linux_kernel_primitives.md
│   ├── 02_posix_process_internals.md
│   ├── 03_adversarial_cves_and_threats.md
│   ├── 04_isolation_benchmarks_and_runtimes.md
│   ├── 05_antigravity_runtime_architecture.md
│   ├── 06_ipc_supervision_specs.md
│   └── chapter_evidence_matrix.md
├── appendices/                 # Canonical Reference Appendices (RFC-Style Specs)
│   ├── appendix_a_antigravity_cli_sandbox_reference.md
│   ├── appendix_b_linux_kernel_primitives_reference.md
│   ├── appendix_c_hardened_command_allowlists.md
│   ├── appendix_d_deterministic_guardrail_shims.md
│   ├── appendix_e_unix_domain_sockets_ipc_protocol.md
│   └── appendix_f_agent_threat_modeling_blast_radius_matrix.md
├── manuscript/                 # 14 Full Chapter Manuscripts (Print / Markdown format)
│   ├── ch01_when_the_agent_holds_the_keyboard.md
│   └── ...
└── companion/                  # Executable Companion Repository
    ├── harnesses/              # Lifecycle supervisors and background daemons
    ├── sandboxes/              # Antigravity configs, bwrap wrappers, and systemd units
    ├── shims/                  # Interception wrappers (git, npm, curl, bash)
    └── labs/                   # 13 Complete Failure Labs
        ├── lab01-shell/
        ├── lab02-process/
        ├── lab03-sandbox/
        └── ...
```

---

### The Iron Trinity Architecture

1. **RUNTIME ISOLATION (The Fortress)**: Namespaces, cgroups v2, ephemeral virtualization, filesystem CoW, and process sandboxing.
2. **ADVERSARIAL CONTAINMENT (The Guardrails)**: Threat modeling, indirect prompt injection mitigation, deterministic interception shims, and secret/network isolation.
3. **AUTONOMOUS DAEMONS (The Engine)**: Headless execution, systemd supervision, state checkpoints, IPC via UNIX domain sockets, and resilient crash recovery.

---

### Authoring Editorial Board

- **The Engine (Senior Runtime Engineer)**: Kernel primitives, deterministic guardrails, zero pseudocode.
- **The Voice (Technical Writer)**: Kleppmann/Fowler clarity, mental models, trade-off focus.
- **The Critic (Editorial Reviewer)**: O'Reilly/Addison-Wesley standards, forensic failure testing.
- **The Architect of Form (Layout Auditor)**: ASCII/Mermaid systems architecture, callouts, and companion repo alignment.
