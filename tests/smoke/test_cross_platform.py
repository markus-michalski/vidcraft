"""Smoke: Windows/POSIX MCP server launch — regression guard for Windows support."""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.parent
SOURCE_DIRS = [ROOT / "tools", ROOT / "servers"]
MCP_JSON = ROOT / ".mcp.json"
RUN_SERVER = ROOT / "bin" / "run-server"
RUN_SERVER_CMD = ROOT / "bin" / "run-server.cmd"
RUN_PY = ROOT / "servers" / "vidcraft-server" / "run.py"
REQUIREMENTS = ROOT / "requirements.txt"
REQUIREMENTS_DEV = ROOT / "requirements-dev.txt"

# Only `setup` shells out to a system-level Python interpreter to create the
# venv. `session-start`/`configure` talk to the MCP server or use the Write
# tool directly — no OS-specific interpreter path to branch on.
SKILLS_REQUIRING_OS_BRANCH = [
    ROOT / "skills" / "setup" / "SKILL.md",
]

SKILLS_REQUIRING_PY_LAUNCHER_FALLBACK = [
    ROOT / "skills" / "setup" / "SKILL.md",
]

SKILLS_WITH_MULTILINE_PYTHON = [
    ROOT / "skills" / "setup" / "SKILL.md",
]

DEV_ONLY_PACKAGES = ["pytest", "pytest-cov", "ruff", "pip-audit", "mypy"]


def test_mcp_json_is_valid_json():
    json.loads(MCP_JSON.read_text(encoding="utf-8"))


def test_mcp_json_command_has_no_hardcoded_venv_subpath():
    """command must go through the OS-agnostic bin/run-server wrapper, not hardcode
    venv/bin (POSIX) or venv\\Scripts (Windows) directly."""
    config = json.loads(MCP_JSON.read_text(encoding="utf-8"))
    command = config["mcpServers"]["vidcraft-mcp"]["command"]
    assert "venv/bin" not in command
    assert "venv\\Scripts" not in command and "venv/Scripts" not in command
    assert command.endswith("bin/run-server")


def test_mcp_json_schema():
    """A dropped/typo'd field here silently breaks the MCP server for every user."""
    config = json.loads(MCP_JSON.read_text(encoding="utf-8"))
    server = config["mcpServers"]["vidcraft-mcp"]
    assert server["type"] == "stdio"
    assert isinstance(server["args"], list) and len(server["args"]) == 1


def test_mcp_json_has_no_env_override_for_plugin_root():
    """Regression guard: run.py already self-locates CLAUDE_PLUGIN_ROOT from __file__
    and prefers an explicit env value over that fallback (os.environ.get(KEY, fallback)).
    A hardcoded ${HOME}-based env override here would silently win over the correct,
    cross-platform __file__ resolution — and ${HOME} is not a standard Windows env var,
    which would break exactly the platform this wrapper exists for."""
    config = json.loads(MCP_JSON.read_text(encoding="utf-8"))
    server = config["mcpServers"]["vidcraft-mcp"]
    assert "env" not in server or "CLAUDE_PLUGIN_ROOT" not in server.get("env", {})


def test_run_server_wrapper_exists_and_is_executable():
    assert RUN_SERVER.exists(), "bin/run-server not found"
    assert os.access(RUN_SERVER, os.X_OK), (
        "bin/run-server must have the executable bit set"
    )
    first_line = RUN_SERVER.read_text(encoding="utf-8").splitlines()[0]
    assert first_line in ("#!/bin/sh", "#!/bin/bash"), (
        f"unexpected shebang: {first_line}"
    )


def test_run_server_cmd_wrapper_targets_windows_venv():
    assert RUN_SERVER_CMD.exists(), "bin/run-server.cmd not found"
    content = RUN_SERVER_CMD.read_text(encoding="utf-8")
    assert "%USERPROFILE%" in content
    assert "Scripts\\python.exe" in content


def test_gitattributes_pins_wrapper_line_endings():
    """A corrupted shebang (CRLF) or a batch file with LF endings both fail
    silently on their respective platform."""
    gitattributes = ROOT / ".gitattributes"
    assert gitattributes.exists(), ".gitattributes not found"
    content = gitattributes.read_text(encoding="utf-8")
    assert "bin/run-server text eol=lf" in content
    assert "bin/run-server.cmd text eol=crlf" in content


def test_setup_skill_documents_both_platforms():
    """Regression guard: a file that documents only the POSIX venv path (venv/bin/python3)
    without a Windows equivalent (venv\\Scripts\\python.exe) is the root bug — check
    both markers are present together."""
    for skill_md in SKILLS_REQUIRING_OS_BRANCH:
        body = skill_md.read_text(encoding="utf-8")
        assert "venv/bin/python3" in body or "venv/bin/pip" in body, (
            f"{skill_md}: missing POSIX venv interpreter path"
        )
        assert "Scripts\\python.exe" in body or "Scripts\\pip.exe" in body, (
            f"{skill_md}: missing Windows venv interpreter path — likely not yet OS-branched"
        )


def test_setup_skill_has_matching_path_counts():
    """Catches a copy-paste swap where a Windows bullet shows the POSIX path."""
    for skill_md in SKILLS_REQUIRING_OS_BRANCH:
        body = skill_md.read_text(encoding="utf-8")
        posix = len(re.findall(r"venv/bin/(?:python3|pip)", body))
        windows = len(re.findall(r"Scripts\\(?:python\.exe|pip\.exe)", body))
        assert posix == windows, (
            f"{skill_md}: POSIX/Windows path mention count mismatch ({posix} vs {windows})"
        )


def test_setup_documents_py_launcher_fallback():
    """Regression guard: on managed Windows devices, bare `python`/`python3` can resolve
    to the Microsoft Store app-execution-alias stub. `py -3` must be documented as a
    fallback, or setup silently tells a managed device user to install Python they
    already have."""
    for skill_md in SKILLS_REQUIRING_PY_LAUNCHER_FALLBACK:
        body = skill_md.read_text(encoding="utf-8")
        assert "py -3" in body, (
            f"{skill_md}: missing `py -3` fallback for Windows Store-alias detection failures"
        )


def test_setup_venv_creation_uses_resolved_interpreter_not_hardcoded():
    """Regression guard: venv creation must reuse whichever interpreter Step 0 resolved
    (<PY>), not hardcode `python`/`python3` — hardcoding breaks on Store-alias devices."""
    body = (ROOT / "skills" / "setup" / "SKILL.md").read_text(encoding="utf-8")
    step3 = body.split("### Step 3:", 1)[1].split("### Step 4:", 1)[0]
    assert "<PY> -m venv" in step3, (
        "Step 3 must invoke <PY>, not a hardcoded python/python3"
    )
    assert not re.search(
        r"^- (?:POSIX|Windows): `python3? -m venv", step3, re.MULTILINE
    ), "Step 3 still hardcodes python/python3 for venv creation"


def test_skills_use_write_then_run_for_multiline_python_not_inline_c():
    """Regression guard: a `-c "..."` argument that spans multiple lines parses
    differently across bash/PowerShell/cmd and reliably breaks under PowerShell."""
    multiline_c_pattern = re.compile(r'-c\s+"\s*\n')
    for skill_md in SKILLS_WITH_MULTILINE_PYTHON:
        body = skill_md.read_text(encoding="utf-8")
        assert not multiline_c_pattern.search(body), (
            f'{skill_md}: found a multi-line `-c "...` invocation — breaks under '
            f"PowerShell, use the write-then-run pattern instead"
        )


def test_requirements_split_runtime_from_dev_tooling():
    """Regression guard: dev/test tooling must not ship in the runtime requirements.txt
    that /vidcraft:setup installs on end users' machines."""
    assert REQUIREMENTS.exists() and REQUIREMENTS_DEV.exists()
    runtime_content = REQUIREMENTS.read_text(encoding="utf-8")
    dev_content = REQUIREMENTS_DEV.read_text(encoding="utf-8")
    for pkg in DEV_ONLY_PACKAGES:
        assert pkg not in runtime_content, (
            f"{pkg} must not be in runtime requirements.txt"
        )
        assert pkg in dev_content, f"{pkg} must be in requirements-dev.txt"
    assert "requirements.txt" in dev_content, (
        "requirements-dev.txt must reference requirements.txt (e.g. -r requirements.txt)"
    )


def test_setup_installs_runtime_requirements_not_dev():
    """Regression guard: /vidcraft:setup (Step 4) must install requirements.txt
    for end users, never requirements-dev.txt."""
    body = (ROOT / "skills" / "setup" / "SKILL.md").read_text(encoding="utf-8")
    step4 = body.split("### Step 4:", 1)[1].split("### Step 5:", 1)[0]
    assert "requirements.txt" in step4
    assert "requirements-dev.txt" not in step4


def test_run_server_wrapper_actually_launches_python():
    """Real subprocess spawn through the OS-appropriate wrapper — proves shebang
    execution / %USERPROFILE%-%*-quoting actually work, not just that the files exist."""
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp)
        if sys.platform == "win32":
            venv_scripts = home / ".vidcraft" / "venv" / "Scripts"
            venv_scripts.mkdir(parents=True)
            (venv_scripts / "python.exe").write_bytes(Path(sys.executable).read_bytes())
            env = {**os.environ, "USERPROFILE": str(home)}
            cmd = [str(RUN_SERVER_CMD), "-c", "print('OK')"]
        else:
            venv_bin = home / ".vidcraft" / "venv" / "bin"
            venv_bin.mkdir(parents=True)
            (venv_bin / "python3").symlink_to(sys.executable)
            env = {**os.environ, "HOME": str(home)}
            cmd = [str(RUN_SERVER), "-c", "print('OK')"]

        result = subprocess.run(
            cmd, env=env, capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, f"wrapper failed: {result.stderr}"
        assert "OK" in result.stdout


def _resolve_venv_python_for_platform(platform: str) -> str:
    """Run run.py's VENV_PYTHON expression under a spoofed sys.platform, in a
    fresh subprocess (not the test process itself) so the real module code
    executes rather than a copy of its logic."""
    script = (
        "import sys; sys.platform = "
        f"{platform!r}; "
        f"sys.path.insert(0, {str(RUN_PY.parent)!r}); "
        "import importlib.util; "
        f"spec = importlib.util.spec_from_file_location('run', {str(RUN_PY)!r}); "
        "mod = importlib.util.module_from_spec(spec); "
        "spec.loader.exec_module(mod); "
        "print(mod.VENV_PYTHON.as_posix())"
    )
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0, (
        f"run.py import failed for platform={platform}: {result.stderr}"
    )
    return result.stdout.strip()


def test_run_py_resolves_windows_venv_python_on_win32():
    """Regression guard for the L1 review fix: run.py's VENV_PYTHON must resolve to
    the Windows venv layout (Scripts/python.exe) when sys.platform is win32, not the
    POSIX bin/python3 it hardcoded before — that made the re-exec branch a silent
    no-op on Windows (venv_python.exists() was always False)."""
    resolved = _resolve_venv_python_for_platform("win32")
    assert resolved.endswith("Scripts/python.exe")


def test_run_py_resolves_posix_venv_python_off_windows():
    """Companion to the win32 case — must still resolve bin/python3 for every
    non-Windows platform string, so the POSIX path isn't broken by the new branch."""
    resolved = _resolve_venv_python_for_platform("linux")
    assert resolved.endswith("bin/python3")


def _load_run_module():
    """Load run.py as a fresh, real module object (not a subprocess) so
    monkeypatch can intercept its os.execv/runpy.run_path calls directly."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("run_under_test", RUN_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_run_py_main_execs_venv_python_when_it_exists_and_differs(
    monkeypatch, tmp_path
):
    """Regression guard: main()'s actual re-exec decision, not just the VENV_PYTHON
    path string, must fire os.execv when the venv interpreter exists and differs
    from the currently running interpreter."""
    mod = _load_run_module()
    fake_venv_python = tmp_path / "fake_venv_python3"
    fake_venv_python.write_text("")
    monkeypatch.setattr(mod, "VENV_PYTHON", fake_venv_python)
    monkeypatch.setattr(mod.sys, "executable", str(tmp_path / "other_python3"))

    calls = {}

    def fake_execv(path, args):
        calls["execv"] = (path, args)
        raise SystemExit(0)

    monkeypatch.setattr(mod.os, "execv", fake_execv)
    monkeypatch.setattr(
        mod.runpy, "run_path", lambda *a, **kw: calls.setdefault("run_path", True)
    )

    with pytest.raises(SystemExit):
        mod.main()

    assert calls["execv"][0] == str(fake_venv_python)
    assert "run_path" not in calls


def test_run_py_main_falls_back_to_runpy_when_venv_python_missing(
    monkeypatch, tmp_path
):
    """Companion: when the venv interpreter doesn't exist yet (pre-setup state),
    main() must fall back to runpy.run_path instead of exec-ing a nonexistent path."""
    mod = _load_run_module()
    missing_venv_python = tmp_path / "does-not-exist" / "python3"
    monkeypatch.setattr(mod, "VENV_PYTHON", missing_venv_python)

    calls = {}
    monkeypatch.setattr(mod.os, "execv", lambda *a: calls.setdefault("execv", True))
    monkeypatch.setattr(
        mod.runpy,
        "run_path",
        lambda path, run_name=None: calls.setdefault("run_path", (path, run_name)),
    )

    mod.main()

    assert "execv" not in calls
    expected_server_path = str(RUN_PY.resolve().parent / "server.py")
    assert calls["run_path"] == (expected_server_path, "__main__")


UNENCODED_FILE_IO = re.compile(r"\.(?:open|write_text|read_text)\(")


CALL_WINDOW = 4  # ruff format wraps long calls onto a few lines; look ahead this far


def test_no_unencoded_file_io_in_source():
    """Regression guard for the project-hub #75 class of bug: on a non-UTF-8-locale
    Windows host, Path.open()/write_text()/read_text() without an explicit encoding
    falls back to the locale codepage (cp1252 on German Windows), which cannot
    represent characters like -> or checkmarks and raises UnicodeEncodeError/
    UnicodeDecodeError. Every call site under tools/ and servers/ must pass
    encoding="utf-8" explicitly.

    A call and its encoding= kwarg can land on different lines once ruff format
    wraps a long line — checks a small forward window, not just the call's own
    line, to avoid flagging a wrapped-but-correct call as a violation."""
    violations = []
    for source_dir in SOURCE_DIRS:
        for path in source_dir.rglob("*.py"):
            lines = path.read_text(encoding="utf-8").splitlines()
            for lineno, line in enumerate(lines, start=1):
                if not UNENCODED_FILE_IO.search(line):
                    continue
                if ".open(" in line and "pdfplumber" in line:
                    continue  # third-party call, not our own file I/O
                window = "\n".join(lines[lineno - 1 : lineno - 1 + CALL_WINDOW])
                if "encoding=" not in window:
                    violations.append(
                        f"{path.relative_to(ROOT)}:{lineno}: {line.strip()}"
                    )
    assert not violations, 'Missing encoding="utf-8":\n' + "\n".join(violations)
