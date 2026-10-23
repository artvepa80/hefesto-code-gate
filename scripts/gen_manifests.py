#!/usr/bin/env python3
"""Generate every platform manifest from hefesto-plugin.source.json.

Usage:
  python3 scripts/gen_manifests.py           # write files
  python3 scripts/gen_manifests.py --check   # exit 1 if any file differs, or a rule fails
  python3 scripts/gen_manifests.py --check --tag v1.0.0   # also require version == tag
                                                          # and no pending telemetry choice
  python3 scripts/gen_manifests.py --resolve-pins      # network: resolve action tags to commits
  python3 scripts/gen_manifests.py --sync-references   # network: copy engine docs at the CLI floor
  python3 scripts/gen_manifests.py --codex-zip dist/x.zip  # build the OpenAI upload ZIP

Rules checked: skill name == folder name and matches the Agent Skills pattern,
description 1..1024 chars, metadata.version == source version, README in the
plugin folder has >= 40 words outside code blocks, LICENSE present there,
every interface limit OpenAI documents for submission, the CLI pin text
in each SKILL.md equals cli_requirement, the telemetry notice copies match
docs/telemetry-notice.md, copied references carry the CLI floor version, and
every pinned action SHA in skills and workflows is the recorded commit.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^(?!.*--)[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
AP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"


def dump(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise ValueError("missing frontmatter")
    fm, out, key = m.group(1), {}, None
    for line in fm.splitlines():
        top = re.match(r"^([a-zA-Z_-]+):\s*(.*)$", line)
        if top:
            key, val = top.group(1), top.group(2).strip()
            out[key] = "" if val in (">-", "|", ">") else val.strip('"')
        elif key and line.startswith("  "):
            sub = re.match(r"^\s+([a-zA-Z_-]+):\s*(.*)$", line)
            if key == "metadata" and sub:
                out.setdefault("_meta", {})[sub.group(1)] = sub.group(2).strip('"')
            else:
                out[key] = (out[key] + " " + line.strip()).strip()
    return out


NOTICE_START = "<!-- telemetry-notice:start (generated from docs/telemetry-notice.md) -->"
NOTICE_END = "<!-- telemetry-notice:end -->"
NOTICE_SKILLS = ("hefesto-gate-setup", "hefesto-gate-install")
IP_TEXT = {
    "on": "Your IP address reaches the server with each request but is not stored.",
    "off": "Our analytics provider (PostHog, US) receives your IP address with each request.",
}
IP_TEXT["pending"] = IP_TEXT["off"]  # the conservative wording until the setting is checked


def notice(src: dict) -> str:
    t = src["telemetry"]
    tpl = (ROOT / "docs" / "telemetry-notice.md").read_text()
    body = re.search(r"<!-- template:start -->\n(.*?)<!-- template:end -->", tpl, re.S).group(1)
    if t["update_check_optout"]:
        upd = (f"Set `{t['update_check_optout']}=1` to skip it; "
               "`HEFESTO_TELEMETRY=0` and `DO_NOT_TRACK=1` also skip it (hefesto-ai 4.20.3 and later).")
    else:
        upd = f"In hefesto-ai {src['cli_floor']} this check cannot be turned off."
    return (body.replace("{{IP_SENTENCE}}", IP_TEXT[t["posthog_ip_discard"]])
                .replace("{{UPDATE_CHECK_SENTENCE}}", upd))


def render_notice(text: str, block: str) -> str:
    pat = re.compile(re.escape(NOTICE_START) + r".*?" + re.escape(NOTICE_END), re.S)
    if not pat.search(text):
        raise ValueError("telemetry-notice markers missing")
    return pat.sub(lambda _m: NOTICE_START + "\n" + block + NOTICE_END, text)


def build(src: dict) -> dict[str, str]:
    v, m, p = src["version"], src["marketplace"], src["plugin"]
    pdir = p["dir"]
    rel = "./" + pdir
    files: dict[str, str] = {}
    files[".claude-plugin/marketplace.json"] = dump({
        "name": m["name"], "description": m["description"], "owner": {"name": m["owner"]},
        "plugins": [{"name": p["name"], "source": rel, "description": p["description"]}],
    })
    files[".agents/plugins/marketplace.json"] = dump({
        "name": m["name"], "interface": {"displayName": m["display_name"]},
        "plugins": [{"name": p["name"], "source": {"source": "local", "path": rel},
                     "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                     "category": p["category"]}],
    })
    # cursor.directory takes the listing name/description/logo from this file
    # (it does not open the sub-plugin manifest when this one has a name).
    files[".cursor-plugin/marketplace.json"] = dump({
        "name": m["cursor_name"], "owner": {"name": m["owner"]},
        "description": p["description"], "version": v,
        "logo": pdir + "/assets/logo.svg",
        "metadata": {"description": m["description"], "version": v},
        "plugins": [{"name": p["name"], "source": pdir, "description": p["description"],
                     "version": v, "logo": "assets/logo.svg", "category": p["category"]}],
    })
    common = {"name": p["name"], "version": v, "description": p["description"],
              "author": p["author"], "homepage": p["repository"], "repository": p["repository"],
              "license": p["license"], "keywords": p["keywords"]}
    files[pdir + "/.claude-plugin/plugin.json"] = dump({
        **{k: common[k] for k in ("name",)}, "displayName": p["display_name"],
        **{k: common[k] for k in ("version", "description", "author", "homepage", "repository", "license", "keywords")},
        "icon": "./assets/logo.png",
        "documentationUrl": p["repository"] + "#readme",
        "supportUrl": p["repository"] + "/issues",
        "privacyPolicyUrl": p["privacy_policy_url"],
    })
    files[pdir + "/plugin.json"] = dump({
        "$schema": AP_SCHEMA, **common,
        "extensions": {"com.openai": {
            "interface": {
                "displayName": p["display_name"], "shortDescription": p["short_description"],
                "longDescription": p["long_description"], "developerName": p["author"]["name"],
                "category": p["category"], "capabilities": [],
                "websiteURL": p["repository"], "supportURL": p["repository"] + "/issues",
                "privacyPolicyURL": p["privacy_policy_url"], "defaultPrompt": p["default_prompts"],
                "brandColor": p["brand_color"], "composerIcon": "./assets/icon.png", "logo": "./assets/logo.png",
            },
            "onboardingSkill": f"./skills/{p['onboarding_skill']}/SKILL.md",
            "publication": {"release_notes": f"v{v}"},
        }},
    })
    block = notice(src)
    targets = [f"{pdir}/skills/{sk}/SKILL.md" for sk in NOTICE_SKILLS] + ["README.md", f"{pdir}/README.md"]
    for rel_s in targets:
        files[rel_s] = render_notice((ROOT / rel_s).read_text(), block)
    return files


def _check_interface(src: dict, tag: str | None) -> list[str]:
    v, p = src["version"], src["plugin"]
    errs = [f"version {v} != tag {tag}"] if tag is not None and tag.lstrip("v") != v else []
    if not NAME_RE.match(p["name"]):
        errs.append(f"plugin name {p['name']!r} invalid")
    limits = {"displayName": (p["display_name"], 30), "shortDescription": (p["short_description"], 30),
              "longDescription": (p["long_description"], 4000)}
    errs += [f"{k} length {len(val)} > {lim}" for k, (val, lim) in limits.items() if not 0 < len(val) <= lim]
    errs += [f"defaultPrompt too long: {d}" for d in p["default_prompts"] if len(d) > 128]
    if len(p["default_prompts"]) > 3:
        errs.append("more than 3 defaultPrompt")
    return errs


def _check_plugin_files(pdir: Path) -> list[str]:
    readme = pdir / "README.md"
    if not readme.is_file():
        errs = ["plugin README.md missing (Anthropic reads the plugin folder)"]
    else:
        words = len(re.sub(r"```.*?```", "", readme.read_text(), flags=re.S).split())
        errs = [f"plugin README has {words} words outside code (< 40)"] if words < 40 else []
    if not (pdir / "LICENSE").is_file():
        errs.append("plugin LICENSE missing")
    errs += [f"assets/{k} missing" for k in ("logo.png", "logo.svg", "icon.png")
             if not (pdir / "assets" / k).is_file()]
    return errs


def _check_skill(path: Path, version: str, cli_req: str) -> list[str]:
    body = path.read_text()
    fm, folder = frontmatter(body), path.parent.name
    name, desc = fm.get("name", ""), fm.get("description", "")
    errs = []
    if name != folder or not NAME_RE.match(name):
        errs.append(f"{folder}: name {name!r} must equal folder and match pattern")
    if not 0 < len(desc) <= 1024:
        errs.append(f"{folder}: description length {len(desc)}")
    if fm.get("_meta", {}).get("version") != version:
        errs.append(f"{folder}: metadata.version != {version}")
    if "pip install" in body and cli_req not in body:
        errs.append(f"{folder}: pip install without {cli_req!r}")
    return errs


def _check_release_inputs(src: dict, tag: str | None) -> list[str]:
    ip = src["telemetry"]["posthog_ip_discard"]
    errs = [] if ip in IP_TEXT else ["telemetry.posthog_ip_discard must be on, off or pending"]
    if tag is not None and ip == "pending":
        errs.append("telemetry.posthog_ip_discard is pending: check the PostHog setting before a release")
    if src["cli_requirement"] != f"hefesto-ai>={src['cli_floor']},<5":
        errs.append("cli_requirement does not start at cli_floor")
    return errs


def _check_refs_and_pins(src: dict) -> list[str]:
    floor, errs = src["cli_floor"], []
    for upstream, local in src["references"]["files"].items():
        f = ROOT / local
        if not f.is_file() or f"blob/v{floor}/{upstream}" not in f.read_text().split("\n", 1)[0]:
            errs.append(f"{local}: missing or not copied at v{floor} (run --sync-references)")
    pinned_in = (f"{src['plugin']['dir']}/skills/hefesto-gate-install/SKILL.md", ".github/workflows/validate.yml")
    for action, pin in src["pins"].items():
        line = f"{action}@{pin['commit']} # {pin['tag']}"
        errs += [f"{r}: expected pin '{line}'" for r in pinned_in if line not in (ROOT / r).read_text()]
    return errs


def checks(src: dict, tag: str | None) -> list[str]:
    pdir = ROOT / src["plugin"]["dir"]
    skills = sorted((pdir / "skills").glob("*/SKILL.md"))
    errs = _check_interface(src, tag) + _check_plugin_files(pdir) + ([] if skills else ["no skills found"])
    for s in skills:
        errs += _check_skill(s, src["version"], src["cli_requirement"])
    return errs + _check_release_inputs(src, tag) + _check_refs_and_pins(src)


def resolve_pins(src: dict) -> None:
    """Resolve each pinned action tag to the commit it points at.

    `git ls-remote` on an annotated tag returns the tag-object SHA; the commit is
    on the `^{}` line. A lightweight tag has no `^{}` line and already names the
    commit. `uses:` needs the commit.
    """
    for action, pin in src["pins"].items():
        ref = f"refs/tags/{pin['tag']}"
        out = subprocess.run(["git", "ls-remote", f"https://github.com/{action}", ref, ref + "^{}"],
                             check=True, capture_output=True, text=True).stdout
        refs = {r: sha for sha, r in (l.split("\t") for l in out.splitlines() if l)}
        commit = refs.get(ref + "^{}") or refs.get(ref)
        if not commit:
            raise SystemExit(f"{action}: tag {pin['tag']} not found")
        kind = "annotated, dereferenced" if ref + "^{}" in refs else "lightweight, direct commit"
        print(f"{action} {pin['tag']}: {commit} ({kind})")
        pin["commit"] = commit


def sync_references(src: dict) -> None:
    repo, ver = src["references"]["engine_repo"], src["cli_floor"]
    for upstream, local in src["references"]["files"].items():
        url = f"https://raw.githubusercontent.com/{repo}/v{ver}/{upstream}"
        text = urllib.request.urlopen(url, timeout=30).read().decode()
        base = f"https://github.com/{repo}/blob/v{ver}/{Path(upstream).parent.as_posix()}/"
        # sibling links would break once copied; point them at the upstream tag
        text = re.sub(r"\]\((?!https?://|#)([^)]+\.md)\)", lambda m: f"]({base}{m.group(1)})", text)
        head = (f"<!-- Copied from https://github.com/{repo}/blob/v{ver}/{upstream} "
                f"(MIT, Copyright (c) Narapa LLC). Do not edit here; run "
                f"scripts/gen_manifests.py --sync-references after raising cli_floor. -->\n")
        (ROOT / local).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / local).write_text(head + text)
        print(f"copied {url} -> {local}")


def codex_zip(src: dict, out: Path) -> None:
    """ZIP of the plugin folder for the OpenAI upload, without the Claude/Cursor-only
    `disable-model-invocation` key (Codex reads agents/openai.yaml instead)."""
    pdir = ROOT / src["plugin"]["dir"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(pdir.rglob("*")):
            if not f.is_file():
                continue
            info = zipfile.ZipInfo(f.relative_to(pdir).as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            data = f.read_bytes()
            if f.name == "SKILL.md":
                text = data.decode()
                m = re.match(r"^---\n(.*?\n)---\n", text, re.S)
                fm = re.sub(r"(?m)^disable-model-invocation:.*\n", "", m.group(1))
                data = ("---\n" + fm + "---\n" + text[m.end():]).encode()
            z.writestr(info, data)
    print(f"wrote {out}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--tag")
    ap.add_argument("--resolve-pins", action="store_true")
    ap.add_argument("--sync-references", action="store_true")
    ap.add_argument("--codex-zip", type=Path)
    a = ap.parse_args()
    src_path = ROOT / "hefesto-plugin.source.json"
    src = json.loads(src_path.read_text())
    if a.resolve_pins:
        resolve_pins(src)
        src_path.write_text(json.dumps(src, indent=2, ensure_ascii=False) + "\n")
        return 0
    if a.sync_references:
        sync_references(src)
        return 0
    if a.codex_zip:
        codex_zip(src, a.codex_zip)
        return 0
    files = build(src)
    if not a.check:
        for rel, text in files.items():
            path = ROOT / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    drift = [rel for rel, text in files.items()
             if not (ROOT / rel).is_file() or (ROOT / rel).read_text() != text]
    errs = [f"out of date: {r} (run scripts/gen_manifests.py)" for r in drift] + checks(src, a.tag)
    for e in errs:
        print("ERROR:", e, file=sys.stderr)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
