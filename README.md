# hefesto-code-gate

Agent skills for the Hefesto code gate, packaged as one plugin for Claude Code, OpenAI Codex and Cursor.

> **Status: Work in progress — not yet listed in any plugin directory.**

## What it is

A single plugin, [`plugins/hefesto-code-gate/`](plugins/hefesto-code-gate/), that bundles five [Agent Skills](https://agentskills.io):

| Skill | Purpose |
| --- | --- |
| `hefesto-gate` | Run the Hefesto code gate on a change, a pull request or a repo, and report which findings are real. |
| `hefesto-fix-verify` | Fix one real finding and re-run the gate and the tests to verify the fix. Explicit invocation only. |
| `hefesto-gate-install` | Prepare the gate for GitHub Actions, and optionally local git hooks, as a reviewable change. |
| `hefesto-weekly-trend` | Summarize gate results over time, on request. |
| `hefesto-gate-setup` | Getting started: telemetry notice, first run and basic configuration. Explicit invocation only. |

The skills are built on the open-source [`hefesto-ai`](https://pypi.org/project/hefesto-ai/) CLI from PyPI, developed at [github.com/artvepa80/Agents-Hefesto](https://github.com/artvepa80/Agents-Hefesto). The skills themselves do not analyze code; they tell the agent how to run the CLI and act on its output.

The OpenAI plugin package (the ZIP built by `scripts/gen_manifests.py --codex-zip`) also references a hosted analyzer at `https://hefestoai.narapallc.com/api/mcp-core`. Its `analyze` tool runs the same open-source engine on files you send (up to 20 files, 100 KB each, 256 KB total; files are deleted after the run). For a whole repository, run the CLI locally. Its `get_install_instructions` tool returns local install commands (the pinned `hefesto-ai>=4.20.4,<5` venv command) and does not install anything on the caller's machine. That remote reference is injected into the ZIP as `mcp.json` and is not kept in the plugin folder used by the Claude directory.

## Install

- Claude Code: `/plugin marketplace add artvepa80/hefesto-code-gate`, then `/plugin install hefesto-code-gate@hefestoai`
- Codex: `codex plugin marketplace add artvepa80/hefesto-code-gate`, then install from the Plugins Directory
- Cursor: Customize → From GitHub Repository → `artvepa80/hefesto-code-gate`

Then run `hefesto-gate-setup` once.

## Requirements

- Python 3.11+ and git. The skills install `hefesto-ai>=4.20.4,<5` into a virtual environment.

## Telemetry

The `hefesto-ai` CLI sends usage telemetry by default. The skills show this notice before the first run and before installing hooks or CI (see the [privacy policy](https://hefestoai.narapallc.com/privacy)):

<!-- telemetry-notice:start (generated from docs/telemetry-notice.md) -->
- The hefesto-ai CLI sends usage events to PostHog (us.i.posthog.com) by default. Every event carries the event name, the install ID below, and where it ran (cli, hook, ci or action). `analyze` events also carry the CLI, OS and Python versions, how the CLI was installed (PyPI or editable), environment labels such as `ci`, `github_actions` or `docker`, and counts (files, issues, duration, exit code).
- Each event carries a random install ID created on this machine and stored in `~/.hefesto/telemetry_state.json`. It is not linked to your name, account, or repository, but it does let us count runs from the same install.
- Events never include source code, file paths, findings, or repository names. Your IP address reaches the server with each request but is not stored.
- On the first run the CLI only prints this notice and sends nothing.
- Turn it off with `hefesto telemetry disable` (your user account on this machine, including git hooks), or `HEFESTO_TELEMETRY=0` or `DO_NOT_TRACK=1` (this shell or CI job).
- In the Hefesto GitHub Action telemetry is off by default (`telemetry: 0`). With `telemetry: 1`, each run also sends one ping (CLI version, file and issue counts, exit code) to Narapa's telemetry endpoint, stored without your IP address.
- Separately, `hefesto analyze` checks pypi.org for a newer version at most once every 24 hours. Set `HEFESTO_NO_UPDATE_CHECK=1` to skip it; `HEFESTO_TELEMETRY=0` and `DO_NOT_TRACK=1` also skip it (hefesto-ai 4.20.3 and later).
<!-- telemetry-notice:end -->

## Known issues

- **Glob excludes:** in `hefesto-ai` 4.20.3 and earlier, glob patterns in exclude settings are not applied. Exclude paths by directory, or pass only the files you want analyzed.
- **`hefesto pr-review`:** in 4.20.3 and earlier it can skip findings and report a pass. The skills run `hefesto analyze` on the files the change touches instead.
- **CLI upgrade messages:** upgrade prompts printed by the CLI are not relayed by the skills.
- **Overlapping trigger:** the engine repository ships its own skill named `hefestoai`. `hefesto-gate` does not use that word as a trigger, but both may match a request to "check code with Hefesto".

## Versioning

- The plugin uses Semantic Versioning. Every manifest takes its version from [`hefesto-plugin.source.json`](hefesto-plugin.source.json), and CI fails if a tag doesn't match.
- The minimum CLI version (`cli_floor`) is raised only when a skill needs something a newer release adds, never just to follow the latest release. When it is raised, the notice and the copied references are regenerated.

## Maintaining

- `python3 scripts/gen_manifests.py` regenerates the platform manifests, the notice copies and the Codex/OpenAI ZIP (`--codex-zip`, which injects `mcp.json`). `--check` fails on any drift.
- `--resolve-pins` resolves pinned action tags to commit SHAs (dereferencing annotated tags).
- `--sync-references` copies engine docs at the CLI floor version.
- `python3 scripts/public_audit.py` checks that nothing private is about to be published. It runs in CI and can run as a pre-push hook: `ln -s ../../scripts/public_audit.py .git/hooks/pre-push`.
- The audit also fails on any path under `docs/worklog/`, any file or folder named like a worklog or handoff, and any landing page source folder.
- `python3 scripts/check_plugin_file_types.py` checks that the plugin directory only ships file types accepted by both the [public pre-submission checklist](https://claude.com/docs/plugins/pre-submission-checklist) and the directory portal policy for organizations that are not Verified (Markdown, text, JSON, YAML, and PNG, JPEG, GIF or WebP images; `LICENSE` by exact name; no shebang files or package-manager config). `gen_manifests.py --check` runs the same check.

CI pins Claude Code 2.1.308 and runs `claude plugin validate --strict` on the plugin and on the marketplace root, with no warnings tolerated. The directory-listing fields in `.claude-plugin/plugin.json` follow the [official plugins reference](https://code.claude.com/docs/en/plugins-reference#directory-listing-fields). Passing `--strict` locally does not guarantee that a directory portal's own validation will pass. The directory also applies a file-type policy that `--strict` does not cover; `scripts/check_plugin_file_types.py` checks the shipped-file part of that policy.

## License

[MIT](LICENSE)

## Maintainer

Maintained by [Narapa LLC](https://hefestoai.narapallc.com).
