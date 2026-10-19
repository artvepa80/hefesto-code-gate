# hefesto-code-gate

Agent skills for the Hefesto code gate, packaged as one plugin for Claude Code, OpenAI Codex and Cursor.

> **Status: Work in progress — not yet listed in any plugin directory.**

## What it is

A single plugin that bundles five [Agent Skills](https://agentskills.io):

| Skill | Purpose |
| --- | --- |
| `hefesto-gate` | Run the Hefesto code gate on a change or pull request and report the findings. |
| `hefesto-fix-verify` | Fix reported findings and re-run the gate to verify the fix. |
| `hefesto-gate-install` | Install and configure the gate in a repository and its CI. |
| `hefesto-weekly-trend` | Summarize gate results over time, on request. |
| `hefesto-gate-setup` | Getting started: first run and basic configuration. |

The skills are built on the open-source [`hefesto-ai`](https://pypi.org/project/hefesto-ai/) CLI from PyPI, developed at [github.com/artvepa80/Agents-Hefesto](https://github.com/artvepa80/Agents-Hefesto). The skills themselves do not analyze code; they tell the agent how to run the CLI and act on its output.

## Requirements

- Python 3 and the `hefesto-ai` CLI (`pip install hefesto-ai`).

## Telemetry

The `hefesto-ai` CLI sends usage telemetry by default. Exactly what is sent, and how to turn it off, will be documented here before v1.

## License

[MIT](LICENSE)

## Maintainer

Maintained by [Narapa LLC](https://hefestoai.narapallc.com).
