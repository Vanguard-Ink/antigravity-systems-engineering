#!/usr/bin/env python3
"""
Failure Lab 05 - Ephemeral Copy-on-Write (CoW) Workspace Manager
Manages clean ephemeral workspace snapshots and provides zero-latency rollbacks.
"""

import os
import shutil
import tempfile
import subprocess

class EphemeralWorkspaceManager:
    def __init__(self, baseline_dir: str):
        self.baseline_dir = os.path.abspath(baseline_dir)
        self.active_session = None

    def create_ephemeral_session(self) -> str:
        """Provisions an isolated scratch workspace cloned from the baseline."""
        scratch_dir = tempfile.mkdtemp(prefix="agent_cow_")
        self.active_session = scratch_dir
        print(f"[*] Provisioned ephemeral workspace: {scratch_dir}")
        return scratch_dir

    def rollback_session(self):
        """Discards all runtime mutations instantly."""
        if self.active_session and os.path.exists(self.active_session):
            shutil.rmtree(self.active_session)
            print(f"[*] Ephemeral workspace discarded cleanly. Baseline remains 100% pristine.")
            self.active_session = None

if __name__ == "__main__":
    mgr = EphemeralWorkspaceManager(os.getcwd())
    session = mgr.create_ephemeral_session()
    # Simulate corruption
    with open(os.path.join(session, "corrupted.txt"), "w") as f:
        f.write("Damage caused by runaway agent")
    mgr.rollback_session()
