---
name: hefesto-gate-install
description: >-
  Add the HefestoAI gate to GitHub Actions so it runs on every push and pull
  request, with results in GitHub code scanning, and optionally install local
  git hooks. Use when the user wants the gate to keep running without an agent.
  Prepares the workflow as a reviewable change and never pushes it alone.
license: MIT
compatibility: Requires git; GitHub Actions for CI; python3 >= 3.10 for local hooks.
metadata:
  author: Narapa LLC
  version: "1.0.0"
---
# Hefesto Gate Install

One job: leave a gate that keeps working when no agent is running. You prepare the change; the user decides whether it lands.

## Telemetry first
Hooks and CI jobs run the CLI with nobody watching, so before you write any hook or workflow, give the user this notice in these words:

<!-- telemetry-notice:start (generated from docs/telemetry-notice.md) -->
- The hefesto-ai CLI sends usage events to PostHog (us.i.posthog.com) by default. Every event carries the event name, the install ID below, and where it ran (cli, hook, ci or action). `analyze` events also carry the CLI, OS and Python versions, how the CLI was installed (PyPI or editable), environment labels such as `ci`, `github_actions` or `docker`, and counts (files, issues, duration, exit code).
- Each event carries a random install ID created on this machine and stored in `~/.hefesto/telemetry_state.json`. It is not linked to your name, account, or repository, but it does let us count runs from the same install.
- Events never include source code, file paths, findings, or repository names. Your IP address reaches the server with each request but is not stored.
- On the first run the CLI only prints this notice and sends nothing.
- Turn it off with `hefesto telemetry disable` (your user account on this machine, including git hooks), or `HEFESTO_TELEMETRY=0` or `DO_NOT_TRACK=1` (this shell or CI job).
- In the Hefesto GitHub Action telemetry is off by default (`telemetry: 0`). With `telemetry: 1`, each run also sends one ping (CLI version, file and issue counts, exit code) to Narapa's telemetry endpoint, stored without your IP address.
- Separately, `hefesto analyze` checks pypi.org for a newer version at most once every 24 hours. Set `HEFESTO_NO_UPDATE_CHECK=1` to skip it; `HEFESTO_TELEMETRY=0` and `DO_NOT_TRACK=1` also skip it (hefesto-ai 4.20.3 and later).
<!-- telemetry-notice:end -->

Then ask: "Turn telemetry off for these runs?" If yes:
- local hooks: run `hefesto telemetry disable` on this machine (hooks run as this user, so the choice applies to them). Each developer who installs the hooks makes the same choice on their own machine. Say so.
- CI with the HefestoAI Action: nothing to do; the Action's `telemetry` input already defaults to `0`.
- the CLI in any other CI: add `HEFESTO_TELEMETRY: "0"` to the job `env`.
Wait for the answer before writing anything.

## CI gate (GitHub Actions)
Prepare `.github/workflows/hefesto.yml` in a new branch:

```yaml
name: Hefesto
on:
  push:
    branches: [main]
  pull_request:
permissions:
  contents: read
  security-events: write   # needed to upload SARIF to code scanning
  actions: read            # needed only in private repositories
jobs:
  hefesto:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7   # or pin: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: artvepa80/Agents-Hefesto@v4
        with:
          target: .
          fail_on: HIGH          # use the threshold from .hefesto/triage.yaml
          sarif: true
          sarif_category: hefesto
```

Before proposing it, check and tell the user:
- The default branch name (replace `main`).
- Private repos need GitHub Code Security for code scanning; without it, set `upload_sarif: false` and keep the gate without the Security tab.
- Telemetry in the Action is opt-in: the `telemetry` input defaults to `0`, which sets `HEFESTO_TELEMETRY=0` for the CLI. Leave it unset unless the user asks. The pypi.org version check described in the notice still runs on each fresh runner.
- `actions/checkout@v7` and `artvepa80/Agents-Hefesto@v4` are floating major tags. If their policy requires it, offer to pin full commit SHAs. Resolve each SHA at the time you propose it with `git ls-remote https://github.com/actions/checkout 'refs/tags/v7.0.1' 'refs/tags/v7.0.1^{}'`. If a `^{}` line comes back, the tag is annotated and that dereferenced line is the commit; use it. If only the plain line comes back, the tag points straight at the commit. `uses:` needs the commit SHA, never the tag-object SHA. Keep the version in a trailing comment and never copy a SHA from memory. checkout v7 runs on node24 and needs Actions Runner v2.327.1 or later on self-hosted runners.

Show the full file, then ask: "Open a PR with this workflow?" Push and open the PR only after a yes. Never commit to the default branch directly.

After the PR's first run, report whether the job passed, how many alerts appeared under Security > Code scanning, and the category name.

## Local hooks (the user's machine)
Only after the telemetry question above is answered. In a local agent session the hooks go into the clone you are working in. Show the user the commands, and run them only after a yes:

```
pip install "hefesto-ai>=4.20.3,<5"   # in a venv, or: pipx install "hefesto-ai>=4.20.3,<5"
hefesto install-hooks
```

pre-commit checks staged files and fails on HIGH; pre-push checks the repo and fails on CRITICAL. To skip once: `SKIP_HEFESTO_HOOKS=1 git commit` (or `git push`). `hefesto install-hooks --force` overwrites existing hooks: warn first if they already use pre-commit or husky. If this session runs in a cloud sandbox and not in the user's clone, give the commands instead of running them.

## CLI output
If the CLI output contains upgrade, plan or pricing messages, do not repeat, summarize or link them.

## Anti-jobs
Don't change branch protection, required checks or repo settings. Don't enable GitHub features for the user. Don't edit other workflows.
