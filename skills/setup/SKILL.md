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

**Multi-line Python scripts — write a file, don't inline them.** Never pass
multi-line content via `<PY> -c "<script>"` — a `-c` argument containing
literal newlines parses differently across bash, PowerShell, and cmd, and
reliably breaks under PowerShell. Instead, for any script longer than one
line: write the script content to a file using your own file-write
capability, then run it as `<PY> <path-to-that-file>` — a plain file-path
argument, portable across every shell. Single-line `<PY> -c "..."` commands
(Step 2, Step 6) are unaffected by this and can stay exactly as shown.

### Step 0: Detect Platform and Resolve a Working Python Interpreter

Try each of the following in order and use the **first one that actually runs**
(prints a platform string, doesn't error):

```bash
python3 -c "import sys; print(sys.platform)"
python -c "import sys; print(sys.platform)"
py -3 -c "import sys; print(sys.platform)"
```

**Do not stop at the first failure.** On Windows, `python3`/`python` frequently
fail with **exit code 49 and no output** even when Python is genuinely
installed — this is the Microsoft Store app-execution-alias stub, not a
missing-Python error. It's common on Intune/SCCM-managed devices where Python
was pushed via MSI/EXE without adding it to `PATH`. `py` (the Python Launcher
for Windows) is a separate executable that always lives in `C:\Windows\` — on
`PATH` regardless of how Python itself was installed — so try it before
concluding Python is missing.

If all three fail, check known install locations as a last resort (Windows,
PowerShell syntax): `$env:ProgramFiles\Python3*\python.exe`,
`${env:ProgramFiles(x86)}\Python3*\python.exe`,
`$env:LocalAppData\Programs\Python\Python3*\python.exe` — use the first one
that exists.

Only if *every* option above fails is Python genuinely not installed or not
locatable — see Error Handling.

Call whichever command succeeded `<PY>` — use it verbatim (not the literal
text `<PY>`) for every subsequent system-level Python invocation in this skill
(Steps 1, 2, 3, and 5 — none of these need the venv to exist yet). Steps 4 and
6 use the venv's *own* interpreter instead, resolved separately via the OS
branch below.

**Windows quoting note:** `python3`/`python`/`py -3` need no special handling.
But if `<PY>` came from the known-install-path fallback, it's a full path that
may contain spaces (e.g. `C:\Program Files\Python313\python.exe`). On
Windows, invoke it via the call operator with quotes: `& "<PY>" -c "..."`,
not bare `<PY> -c "..."` — PowerShell doesn't split unquoted paths on spaces
the way you'd want.

Output `win32` means Windows (venv layout: `venv\Scripts\python.exe`,
`venv\Scripts\pip.exe`); any other output means POSIX (Linux/macOS/WSL, venv
layout: `venv/bin/python3`, `venv/bin/pip`). Use this result for every
POSIX/Windows choice below.

### Step 1: Check Current State

This script is multi-line — follow the write-then-run pattern above: save it
to a file in the OS temp directory (resolve it with the single-line,
newline-free command `<PY> -c "import tempfile; print(tempfile.gettempdir())"`),
then run `<PY> <path-to-that-file>` (remember Step 0's Windows quoting note —
`& "<PY>" ...`, not bare `<PY>`, if `<PY>` is a space-containing full path
from the known-install fallback):

```python
from pathlib import Path
base = Path.home() / '.vidcraft'
print('venv:', 'OK' if (base / 'venv').is_dir() else 'MISSING')
print('config:', 'OK' if (base / 'config.yaml').is_file() else 'MISSING')
print('data-dir:', 'OK' if base.is_dir() else 'MISSING')
```

### Step 2: Create Data Directory (if missing)

```bash
<PY> -c "from pathlib import Path; Path.home().joinpath('.vidcraft').mkdir(parents=True, exist_ok=True)"
```

### Step 3: Create Venv (if missing)

Use `<PY>` — the same interpreter resolved in Step 0, not a hardcoded
`python`/`python3`. On a managed device where only `py -3` worked in Step 0,
hardcoding `python` here would immediately hit the same Store-alias failure
Step 0 just worked around.

- POSIX: `<PY> -m venv ~/.vidcraft/venv`
- Windows: `<PY> -m venv "$env:USERPROFILE\.vidcraft\venv"`

### Step 4: Sync Dependencies (always)

Always run this, even if venv already existed. `pip` is idempotent and fast on a warm
cache (~1s). This ensures new deps added in later releases are never silently skipped.
Install only the runtime requirements file — the dev/test/lint tooling file is not
needed at runtime and must not be installed here.

- POSIX: `~/.vidcraft/venv/bin/pip install -r ${CLAUDE_PLUGIN_ROOT}/requirements.txt -q`
- Windows: `& "$env:USERPROFILE\.vidcraft\venv\Scripts\pip.exe" install -r ${CLAUDE_PLUGIN_ROOT}/requirements.txt -q`

### Step 5: Copy Config (if missing)

Use `<PY>` (still the Step 0 interpreter — this step doesn't need the venv):

```bash
<PY> -c "import shutil; from pathlib import Path; cfg = Path.home() / '.vidcraft' / 'config.yaml'; cfg.parent.mkdir(parents=True, exist_ok=True) or None; (not cfg.exists()) and shutil.copy2(r'${CLAUDE_PLUGIN_ROOT}/config/config.example.yaml', cfg)"
```

Also create `~/.vidcraft/cache/` if it doesn't exist:

```bash
<PY> -c "from pathlib import Path; Path.home().joinpath('.vidcraft', 'cache').mkdir(parents=True, exist_ok=True)"
```

### Step 6: Verify MCP Server

Use the venv's own interpreter (not `<PY>`):

- POSIX: `~/.vidcraft/venv/bin/python3 -c "from mcp.server.fastmcp import FastMCP; print('MCP OK')"`
- Windows: `& "$env:USERPROFILE\.vidcraft\venv\Scripts\python.exe" -c "from mcp.server.fastmcp import FastMCP; print('MCP OK')"`

### Step 7: Run Configure

Run `/vidcraft:configure` for user-specific settings (content root, platform, brand).

### Step 8: Report

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

- `python3` not found (POSIX), and no other interpreter in Step 0's chain
  works either → Python is genuinely not installed. Tell user to install
  Python 3.10+.
- On Windows, `python`/`python3` exiting with code 49 and no output is
  **not** "Python not found" — it's the Microsoft Store app-execution-alias
  stub. Do not tell the user to install Python; instead fall through Step 0's
  chain (`py -3`, then known install paths).
- Only if **every** entry in Step 0's fallback chain fails is Python actually
  missing on Windows → tell the user to install Python 3.10+ from python.org
  and check "Add python.exe to PATH" during install. On a managed device
  where the user can't install software themselves, suggest contacting IT to
  confirm the Python install location or add it to `PATH`.
- `pip install` fails: Show the exact error and suggest running manually
- MCP import fails: Check `mcp[cli]` is installed
