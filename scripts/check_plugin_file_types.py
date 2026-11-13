#!/usr/bin/env python3
"""Check that the plugin directory ships only file types accepted by
both the public pre-submission checklist and the directory portal policy
for organizations that are not Verified.

The public checklist (https://claude.com/docs/plugins/pre-submission-checklist)
allows text files including SVG, plus PNG, JPEG, GIF and WebP, and holds
ICO and other binaries. The portal refused SVG and allowed ICO. This
checker uses the intersection: Markdown, text, JSON, YAML, and PNG, JPEG,
GIF or WebP. LICENSE is allowed by exact name. Shebang files and
package-manager config (for example pnpm-workspace.yaml) are refused.
Text files must be UTF-8 without NUL bytes.

This local check covers the shipped-file part of that intersection.
`claude plugin validate --strict` does not; the directory also runs a
safety scan and a policy review that this command does not.

Usage:
  python3 scripts/check_plugin_file_types.py
  python3 scripts/check_plugin_file_types.py plugins/hefesto-code-gate
"""
from __future__ import annotations

import sys
from pathlib import Path

ALLOWED_EXT = {
    ".md", ".txt", ".json", ".yaml", ".yml",
    ".png", ".jpeg", ".jpg", ".gif", ".webp",
}
IMAGE_EXT = {".png", ".jpeg", ".jpg", ".gif", ".webp"}
ALLOWED_NAMES = {"LICENSE"}
PACKAGE_MANAGER = {
    "pnpm-workspace.yaml", "pnpm-lock.yaml",
    "package.json", "package-lock.json", "npm-shrinkwrap.json",
    "yarn.lock", "bun.lock", "bun.lockb", "lerna.json",
    "Cargo.toml", "Cargo.lock", "go.mod", "go.sum",
    "pyproject.toml", "setup.cfg", "setup.py", "requirements.txt",
    "Pipfile", "Pipfile.lock", "poetry.lock",
    "Gemfile", "Gemfile.lock", "composer.json", "composer.lock",
}

DEFAULT_PLUGIN = Path(__file__).resolve().parent.parent / "plugins" / "hefesto-code-gate"


def collect_findings(root: Path) -> list[str]:
    """Return human-readable errors for files under *root*."""
    findings: list[str] = []
    if not root.is_dir():
        return [f"{root}: plugin directory missing"]
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        findings.extend(_check_file(root, path))
    return findings


def _type_allowed(path: Path) -> bool:
    return path.name in ALLOWED_NAMES or path.suffix.lower() in ALLOWED_EXT


def _text_encoding_findings(rel: str, path: Path, data: bytes) -> list[str]:
    if path.suffix.lower() in IMAGE_EXT:
        return []
    if b"\x00" in data:
        return [f"{rel}: text file contains NUL bytes"]
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return [f"{rel}: text file is not UTF-8"]
    return []


def _check_file(root: Path, path: Path) -> list[str]:
    rel = path.relative_to(root).as_posix()
    data = path.read_bytes()
    if path.name in PACKAGE_MANAGER:
        return [f"{rel}: package-manager config is not accepted"]
    if not _type_allowed(path):
        kind = path.suffix.lower() or "(no extension)"
        return [f"{rel}: file type {kind} is not accepted"]
    if data.startswith(b"#!"):
        return [f"{rel}: shebang files are not accepted"]
    return _text_encoding_findings(rel, path, data)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    root = Path(args[0]) if args else DEFAULT_PLUGIN
    found = collect_findings(root)
    for item in found:
        print("ERROR:", item, file=sys.stderr)
    if found:
        return 1
    print(f"OK: {root} ships only accepted file types")
    return 0


if __name__ == "__main__":
    sys.exit(main())
