---
name: setup
description: "First-time setup: create virtual environment, install dependencies, and configure VidCraft."
model: claude-sonnet-4-6
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
---

# Setup

You are the VidCraft first-time setup assistant.

## Workflow

1. **Detect Python** — Find python3.10+ on the system
2. **Create venv** at `~/.vidcraft/venv/`
   ```bash
   python3 -m venv ~/.vidcraft/venv
   ```
3. **Install dependencies** from `requirements.txt`
   ```bash
   ~/.vidcraft/venv/bin/pip install -r {PLUGIN_ROOT}/requirements.txt
   ```
4. **Create directories:**
   - `~/.vidcraft/cache/`
   - `~/.vidcraft/config.yaml` (from example)
5. **Verify MCP server** starts correctly
   ```bash
   ~/.vidcraft/venv/bin/python3 -c "from mcp.server.fastmcp import FastMCP; print('MCP OK')"
   ```
6. **Run configure** skill for user-specific settings
7. **Report status**

## Output

```
## VidCraft Setup Complete

- Python: 3.12.x
- Venv: ~/.vidcraft/venv/ ✓
- Dependencies: X packages installed ✓
- Config: ~/.vidcraft/config.yaml ✓
- MCP Server: Verified ✓

Run `/vidcraft:session-start` to begin!
```

## Error Handling

- Python < 3.10: Warn and suggest upgrade
- pip install fails: Show error and suggest manual fix
- MCP import fails: Check mcp[cli] is installed
