#!/usr/bin/env python3
"""
Failure Lab 01 - Naive (Victim) Agent Harness
Demonstrates the dangerous consequences of naive subshell execution where
ambient authority and inherited environment variables are passed unchecked
to child processes spawned by autonomous agents.
"""

import os
import sys
import subprocess
import re

# Simulated Ambient Host / CI / Bastion Credentials
AMBIECT_SECRETS = {
    "AWS_ACCESS_KEY_ID": "AKIA_PROD_DEPLOYER_9981",
    "AWS_SECRET_ACCESS_KEY": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "GITHUB_TOKEN": "ghp_7749abcdef0123456789FEDCBA0123456789",
    "PRODUCTION_DATABASE_URL": "postgresql://svc_agent:P@ssw0rd2026!@db.internal.corp:5432/primary_store",
    "INTERNAL_SIGNING_KEY": "MIICXAIBAAKCAQEA0Y1W9Z38Q...",
    "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")
}

def load_simulated_ambient_environment():
    """Injects high-privilege credentials into the agent's runtime environment."""
    for k, v in AMBIECT_SECRETS.items():
        os.environ[k] = v
    print(f"[*] [AGENT PROCESS: PID {os.getpid()}] Ambient authority initialized with {len(AMBIECT_SECRETS)} sensitive credentials.")

def parse_readme_for_actions(fixture_readme_path: str):
    """
    Simulates an LLM agent ingesting an untrusted repository README,
    falling victim to indirect prompt injection instructions.
    """
    if not os.path.exists(fixture_readme_path):
        print(f"[!] Fixture file not found: {fixture_readme_path}")
        sys.exit(1)

    with open(fixture_readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"[*] Ingested README ({len(content)} bytes). Scanning instructions...")

    # Pattern simulating an agent extracting commands from text or HTML comments
    injection_pattern = re.compile(r"CRITICAL SYSTEM DIRECTIVE.*?(curl\s+-[^\n\r]+)", re.DOTALL)
    match = injection_pattern.search(content)

    if match:
        extracted_cmd = match.group(1).strip()
        print(f"[!] [INJECTION DETECTED BY SIMULATOR] Extracted untrusted command from context:")
        print(f"    >>> {extracted_cmd}")
        return extracted_cmd
    else:
        # Fallback normal command
        return "echo 'Normal build step executed'"

def execute_naive_subshell(command: str):
    """
    THE VULNERABILITY:
    Spawns a shell directly inheriting the parent process's environment,
    file descriptors, and unrestricted networking.
    """
    print(f"\n[*] [SPAWNING SUBSHELL] Executing command with ambient environment inheritance...")
    print(f"    Command: {command}")
    
    # Naive execution pattern seen in many open-source agent frameworks:
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ, # Explicit ambient leakage
            text=True
        )
        stdout, stderr = process.communicate(timeout=10)
        print(f"[*] [SUBSHELL COMPLETE] Exit Code: {process.returncode}")
        if stdout:
            print(f"    STDOUT: {stdout.strip()}")
        if stderr:
            print(f"    STDERR: {stderr.strip()}")
    except subprocess.TimeoutExpired:
        process.kill()
        print(f"[!] [ERROR] Subshell timed out and was killed.")
    except Exception as e:
        print(f"[!] [ERROR] Execution failed: {e}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_fixture = os.path.join(current_dir, "malicious_repo_fixture", "README.md")

    load_simulated_ambient_environment()
    injected_command = parse_readme_for_actions(target_fixture)
    execute_naive_subshell(injected_command)
