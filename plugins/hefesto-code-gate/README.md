# Hefesto Code Gate

Agent skills that run the open-source [HefestoAI](https://github.com/artvepa80/Agents-Hefesto) CLI (`hefesto-ai` on PyPI) on your code, tell you which findings are real, fix them with proof, and put the gate in CI. They work in Claude Code, Codex and Cursor, and in any tool that supports Agent Skills.

## Install

- Claude Code: `/plugin marketplace add artvepa80/hefesto-code-gate`, then `/plugin install hefesto-code-gate@hefestoai`
- Codex: `codex plugin marketplace add artvepa80/hefesto-code-gate`, then install from the Plugins Directory
- Cursor: Customize → From GitHub Repository → `artvepa80/hefesto-code-gate`

## Skills

| Skill | What it does |
|---|---|
| `hefesto-gate` | Runs the gate on a PR, a diff or a repo and triages each HIGH/CRITICAL finding as real, doubtful or false positive. |
| `hefesto-fix-verify` | Fixes one real finding with the smallest patch, then re-runs the CLI and your tests to prove it. Explicit invocation only. |
| `hefesto-gate-install` | Prepares a GitHub Actions workflow (and optional local git hooks) as a reviewable change. |
| `hefesto-weekly-trend` | Compares findings with the last snapshot in `.hefesto/trend.jsonl`. |
| `hefesto-gate-setup` | First run: telemetry notice, install, one verified result, threshold. Explicit invocation only. |

## What runs, what is sent, what is written

- Installs `hefesto-ai>=4.20.3,<5` from PyPI into `~/.hefesto-venv`. Analysis runs locally; your code is not uploaded.
- The skills do not relay upgrade or pricing messages that the CLI may print.
- Telemetry from the CLI (the skills show this before the first run and before writing hooks or CI):

<!-- telemetry-notice:start (generated from docs/telemetry-notice.md) -->
- The hefesto-ai CLI sends usage events to PostHog (us.i.posthog.com) by default. Every event carries the event name, the install ID below, and where it ran (cli, hook, ci or action). `analyze` events also carry the CLI, OS and Python versions, how the CLI was installed (PyPI or editable), environment labels such as `ci`, `github_actions` or `docker`, and counts (files, issues, duration, exit code).
- Each event carries a random install ID created on this machine and stored in `~/.hefesto/telemetry_state.json`. It is not linked to your name, account, or repository, but it does let us count runs from the same install.
- Events never include source code, file paths, findings, or repository names. Your IP address reaches the server with each request but is not stored.
- On the first run the CLI only prints this notice and sends nothing.
- Turn it off with `hefesto telemetry disable` (your user account on this machine, including git hooks), or `HEFESTO_TELEMETRY=0` or `DO_NOT_TRACK=1` (this shell or CI job).
- In the Hefesto GitHub Action telemetry is off by default (`telemetry: 0`). With `telemetry: 1`, each run also sends one ping (CLI version, file and issue counts, exit code) to Narapa's telemetry endpoint, stored without your IP address.
- Separately, `hefesto analyze` checks pypi.org for a newer version at most once every 24 hours. Set `HEFESTO_NO_UPDATE_CHECK=1` to skip it; `HEFESTO_TELEMETRY=0` and `DO_NOT_TRACK=1` also skip it (hefesto-ai 4.20.3 and later).
<!-- telemetry-notice:end -->

- The skills write only after you say yes: `.hefesto/triage.yaml` (threshold and dismissals, meant to be committed), `.hefesto/trend.jsonl` (append-only snapshots), a new git branch for fixes, and `.github/workflows/hefesto.yml`.
- Nothing is pushed, no PR is opened, and nothing is posted without your explicit yes.

## Reference

`skills/hefesto-gate/references/issue_types.md` is copied (MIT) from the engine repository at the minimum CLI version; only its links to sibling docs are rewritten to point at that tag.

## Limits

No style review. No XSS detection, no package-existence ("hallucinated API") checks, no dependency vulnerability scanning (SCA), no path traversal.

## Known issues (hefesto-ai 4.20.x)

- `hefesto pr-review` hides findings inside a function whose `def` line did not change, and it does not run the narrow semantic analyzer that `analyze` runs. The skills therefore run `hefesto analyze` on the touched files for PR verdicts.
- `exclude` patterns in `.hefesto.yaml` match whole path components only. Globs (`*.py`, `tests/**`) match nothing and fail silently. Use literal names such as `tests/fixtures/`. A fix is in progress upstream; until it ships, the skills never propose glob patterns.
- If `.hefesto/triage.yaml` shows up in your own results, add `.hefesto/` (a literal name) to `exclude`.

## License

MIT, Narapa LLC.
