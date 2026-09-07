# Failure Lab 05: Ephemeral Environments and State Management

## Vulnerability Focus
- **Failure Mode**: An agent refactoring task accidentally deletes production dependencies (`rm -rf node_modules` or rootfs files), corrupting the workspace.
- **Systems Root Cause**: Mutating the live working tree directly without Copy-on-Write (CoW) filesystem isolation.

## Files
- `cow_workspace_manager.py`: Implements an ephemeral workspace lifecycle using OverlayFS, guaranteeing instant rollback on failure.
