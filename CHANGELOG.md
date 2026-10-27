# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- The plugin README now uses the two-step Claude Code install (`/plugin marketplace add`, then `/plugin install hefesto-code-gate@hefestoai`), matching the root README; it works on older Claude Code versions too.
- The minimum `hefesto-ai` CLI version is raised to 4.20.4 (`hefesto-ai>=4.20.4,<5`).
- `hefesto-gate/references/issue_types.md` is now copied from the engine at v4.20.4, from its new path `skills/hefestoai/issue_types.md`.

## [1.0.0] - 2026-10-23

### Changed

- The minimum `hefesto-ai` CLI version is raised to 4.20.3 (`hefesto-ai>=4.20.3,<5`). The telemetry notice now says the pypi.org version check can be skipped with `HEFESTO_NO_UPDATE_CHECK=1`, `HEFESTO_TELEMETRY=0` or `DO_NOT_TRACK=1`, and the known issue about that check having no off switch is removed.

### Added

- Repository created.
- Plugin `hefesto-code-gate` with five skills: `hefesto-gate`, `hefesto-fix-verify`, `hefesto-gate-install`, `hefesto-weekly-trend`, `hefesto-gate-setup`.
- Marketplace manifests for Claude Code, Codex and Cursor, generated from `hefesto-plugin.source.json`.
- Telemetry notice shown before the first run and before installing hooks or CI.
- `hefesto-gate/references/issue_types.md`, copied from the engine at v4.20.3.
- CI: manifest drift and tag check, Agent Skills and Agent Plugins validation, Claude strict validation, Codex ZIP build, public-content audit, dogfood run. Claude validation runs `claude plugin validate --strict` with Claude Code 2.1.308 pinned on Node.js 22.
- Public-content audit: path rules for worklogs, handoffs and landing page source folders, generic checks for references to non-public repositories or pull requests, and unit tests.
- README: install steps for Claude Code, Codex and Cursor, telemetry notice and known issues; plugin README includes the install line for each platform.

[Unreleased]: https://github.com/artvepa80/hefesto-code-gate/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/artvepa80/hefesto-code-gate/releases/tag/v1.0.0
