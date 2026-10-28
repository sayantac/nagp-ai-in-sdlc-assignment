#!/usr/bin/env python3
"""One-time setup for the assignment scaffold. Run from the repo root:  python3 scripts/setup_scaffold.py

Checks prerequisites, installs the commit-trailer git hook, makes scripts
executable, and prints the one command you still need to run yourself (the
Mermaid MCP install, because it changes your global npm packages).
"""
import os
import shutil
import stat
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def have(cmd):
    return shutil.which(cmd) is not None


def main():
    print("Prerequisites")
    for cmd, why in [("git", "version control"), ("claude", "Claude Code CLI"),
                     ("dotnet", ".NET 8 SDK for the architecture test"), ("node", "Mermaid MCP + e2e"),
                     ("npm", "Mermaid MCP install"), ("claude-mermaid", "Mermaid MCP server")]:
        print(f"  [{'ok' if have(cmd) else 'MISSING'}] {cmd:15} {why}")

    hook_src = ROOT / "scripts" / "git-hooks" / "prepare-commit-msg"
    hook_dst = ROOT / ".git" / "hooks" / "prepare-commit-msg"
    if (ROOT / ".git").exists():
        hook_dst.parent.mkdir(exist_ok=True)
        shutil.copyfile(hook_src, hook_dst)
        print(f"\nInstalled git hook -> {hook_dst.relative_to(ROOT)} (adds AI-Log-Id trailers)")
    for path in list((ROOT / "scripts").glob("*.py")) + list((ROOT / ".claude" / "hooks").glob("*.py")) + [hook_dst]:
        if path.exists():
            path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    (ROOT / "ai-logs" / "transcripts").mkdir(parents=True, exist_ok=True)
    (ROOT / "ai-logs" / "raw.jsonl").touch()

    user_memory = Path.home() / ".claude" / "CLAUDE.md"
    if user_memory.exists() and user_memory.read_text(encoding="utf-8").strip():
        print(f"\nNOTE: {user_memory} is not empty. Move it aside before running the Task 4 evals.")

    mcp = subprocess.run(["claude", "mcp", "list"], capture_output=True, text=True) if have("claude") else None
    if not mcp or "mermaid" not in (mcp.stdout or ""):
        print("\nStill to do (once):")
        print("  npm install -g claude-mermaid")
        print("  claude mcp add --scope project mermaid claude-mermaid    # writes .mcp.json, commit it")
    print("\nThen start Claude Code in the repo root and approve the project hooks when asked "
          "(/hooks shows them). Check that ai-logs/raw.jsonl grows after your first prompt.")


if __name__ == "__main__":
    main()
