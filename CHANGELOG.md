# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.2] - 2026-11-14

### Added

- Link the privacy policy from the plugin README and the root README.
- `scripts/check_plugin_file_types.py` checks that the plugin directory only ships file types accepted by both the public pre-submission checklist and the directory portal policy for organizations that are not Verified.

### Changed

- Skill `description` fields are written as a single YAML line.
- Cursor marketplace logos point at `assets/logo.png`. The plugin package no longer includes `logo.svg`; the vector file stays at repo-root `assets/logo.svg`.
- README requirements and skill `compatibility` lines now say Python 3.11+. On Python 3.10, `hefesto-ai>=4.20.4,<5` still installs 4.20.x because 4.21.0 declares `Requires-Python: >=3.11`. Python 3.10 reached end-of-life in October 2026. The CLI floor stays `4.20.4`.
- The manifests CI job runs the full unit test suite (`python3 -m unittest discover -s tests`).

## [1.0.1] - 2026-11-05

### Changed

- Plugin keywords now include `security-gate` and `static-analysis` for discovery.
- The plugin README now uses the two-step Claude Code install (`/plugin marketplace add`, then `/plugin install hefesto-code-gate@hefestoai`), matching the root README; it works on older Claude Code versions too.
- The minimum `hefesto-ai` CLI version is raised to 4.20.4 (`hefesto-ai>=4.20.4,<5`).
- `hefesto-gate/references/issue_types.md` is now copied from the engine at v4.20.4, from its new path `skills/hefestoai/issue_types.md`.
- The plugin logo and icon (`assets/logo.png`, `assets/icon.png`, `assets/logo.svg`) now use the official HefestoAI artwork instead of the placeholder.
- CI pins `actions/setup-node` to the v7.1.0 commit SHA, and the README documents the `claude plugin validate --strict` check.

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

[Unreleased]: https://github.com/artvepa80/hefesto-code-gate/compare/v1.0.2...HEAD
[1.0.2]: https://github.com/artvepa80/hefesto-code-gate/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/artvepa80/hefesto-code-gate/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/artvepa80/hefesto-code-gate/releases/tag/v1.0.0
