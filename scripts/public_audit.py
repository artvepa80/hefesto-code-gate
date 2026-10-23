#!/usr/bin/env python3
"""Public-content audit: fail if a file meant for this public repo carries
private material (local or internal paths, links to private chats, names or
codewords that belong to internal projects).

Path rules (any file, text or binary): internal agent worklogs and handoffs
never go in this repo, so anything under docs/worklog/, any file or folder
named like worklog or handoff, and anything under landing-page/ fails.

Two content pattern sets:
- GENERIC, below: safe to publish.
- EXTRA: one regex per line from the PUBLIC_AUDIT_DENYLIST environment variable
  (a GitHub Actions secret) and from .git/info/public-audit-denylist (local,
  never committed). Internal names stay in those, so the denylist itself does not
  publish them.

Usage: python3 scripts/public_audit.py [--require-extra]
Run it in CI, and locally as a pre-push hook:
  ln -s ../../scripts/public_audit.py .git/hooks/pre-push
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENERIC = [
    r"/workspace/",                     # agent or container scratch paths
    r"/home/[A-Za-z0-9_.-]+/",           # absolute home paths
    r"/Users/[A-Za-z0-9_.-]+/",
    r"[A-Za-z]:\\Users\\",
    r"/cursor/stores/",
    r"claude\.ai/(chat|share|project)/",
    r"chatgpt\.com/(c|share|g)/",
    r"grok\.com/(c|chat|share)/",
    r"cursor\.com/agents/",
    r"\bagent-data\b",
    r"\bTASKS\.md\b",
    r"(?i)\b(internal only|do not publish|confidential)\b",
    r"(?i)-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"\b(ghp|gho|ghs|github_pat)_[A-Za-z0-9_]{20,}",
    r"\bphc_[A-Za-z0-9]{20,}",          # PostHog project keys
    r"(?i)\bprivate[ -](repo|repository|PRs?|pull[ -]requests?)\b",
    r"(?i)\blanding-page/",
]
PATH_RULES = [
    r"(^|/)docs/worklog/",
    r"(?i)(^|/)[^/]*(work[-_ ]?log|hand[-_ ]?offs?)[^/]*(/|$)",
    r"(?i)(^|/)landing-page/",
]
SELF = {"scripts/public_audit.py"}      # this file lists the generic patterns


def extra_patterns() -> list[str]:
    pats = [l for l in os.environ.get("PUBLIC_AUDIT_DENYLIST", "").splitlines()]
    local = ROOT / ".git" / "info" / "public-audit-denylist"
    if local.is_file():
        pats += local.read_text().splitlines()
    return [p.strip() for p in pats if p.strip() and not p.lstrip().startswith("#")]


def files() -> list[Path]:
    try:
        out = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=ROOT,
                             check=True, capture_output=True, text=True).stdout.splitlines()
        return [ROOT / f for f in out]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return [f for f in ROOT.rglob("*") if f.is_file() and ".git" not in f.parts]


def path_hits(rel: str) -> list[str]:
    return [f"{rel}: path matches {p}" for p in PATH_RULES if re.search(p, rel)]


def content_hits(rel: str, text: str, extra: list[str]) -> list[str]:
    rx = [(p, re.compile(p)) for p in GENERIC if rel not in SELF]
    rx += [(None, re.compile(p)) for p in extra]
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        # private patterns are not echoed, so CI logs don't leak them
        out += [f"{rel}:{n}: matches {shown or 'a private denylist pattern'}"
                for shown, r in rx if r.search(line)]
    return out


def read_text(f: Path) -> str | None:
    try:
        return f.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None  # binary assets: path rules only


def main() -> int:
    extra = extra_patterns()
    if "--require-extra" in sys.argv and not extra:
        print("public audit: no private denylist configured (PUBLIC_AUDIT_DENYLIST)", file=sys.stderr)
        return 2
    hits: list[str] = []
    scanned = 0
    for f in (f for f in files() if f.is_file()):
        rel = f.relative_to(ROOT).as_posix()
        hits += path_hits(rel)
        text = read_text(f)
        if text is not None:
            scanned += 1
            hits += content_hits(rel, text, extra)
    for h in hits:
        print(h)
    print(f"public audit: {scanned} text files, {len(PATH_RULES)} path rules, "
          f"{len(GENERIC)} generic + {len(extra)} private patterns, {len(hits)} hits")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
