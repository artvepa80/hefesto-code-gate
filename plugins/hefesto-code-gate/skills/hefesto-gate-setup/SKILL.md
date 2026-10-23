---
name: hefesto-gate-setup
description: >-
  First-time setup for the Hefesto Code Gate plugin: disclose the hefesto-ai
  CLI's telemetry, install the CLI, show one real verified result on the user's
  repo in the first minute, then record the gate threshold. Invoke explicitly
  right after installing the plugin.
disable-model-invocation: true
license: MIT
compatibility: Requires python3 >= 3.10, git, and network access to pypi.org.
metadata:
  author: Narapa LLC
  version: "1.0.0"
---
# Hefesto Gate Setup

Goal: the user sees a real, verified result before answering setup questions.

## Message 1 (one question only)
Say in two lines what the plugin does and doesn't do: "It runs the open-source HefestoAI gate on your code, tells you which findings are real, and fixes them with proof. It doesn't do style review and never pushes or comments without your yes."
Then give the telemetry notice, before anything is installed or run, in these words:

<!-- telemetry-notice:start (generated from docs/telemetry-notice.md) -->
- The hefesto-ai CLI sends usage events to PostHog (us.i.posthog.com) by default. Every event carries the event name, the install ID below, and where it ran (cli, hook, ci or action). `analyze` events also carry the CLI, OS and Python versions, how the CLI was installed (PyPI or editable), environment labels such as `ci`, `github_actions` or `docker`, and counts (files, issues, duration, exit code).
- Each event carries a random install ID created on this machine and stored in `~/.hefesto/telemetry_state.json`. It is not linked to your name, account, or repository, but it does let us count runs from the same install.
- Events never include source code, file paths, findings, or repository names. Your IP address reaches the server with each request but is not stored.
- On the first run the CLI only prints this notice and sends nothing.
- Turn it off with `hefesto telemetry disable` (your user account on this machine, including git hooks), or `HEFESTO_TELEMETRY=0` or `DO_NOT_TRACK=1` (this shell or CI job).
- In the Hefesto GitHub Action telemetry is off by default (`telemetry: 0`). With `telemetry: 1`, each run also sends one ping (CLI version, file and issue counts, exit code) to Narapa's telemetry endpoint, stored without your IP address.
- Separately, `hefesto analyze` checks pypi.org for a newer version at most once every 24 hours. In hefesto-ai 4.20.2 this check cannot be turned off.
<!-- telemetry-notice:end -->

End with: "Say 'telemetry off' to turn it off first. Which repo or folder should I check?"

## First minute (no more questions)
1. Install: `python3 -m venv ~/.hefesto-venv && ~/.hefesto-venv/bin/pip install "hefesto-ai>=4.20.2,<5"`. If they said telemetry off, run `hefesto telemetry disable` right after the install, before any analysis.
2. `hefesto analyze . --output json --fail-on high` in the repo they named.
3. Triage as in hefesto-gate, pick the single worst **real** finding, and run hefesto-fix-verify on it in a new local branch. Don't open a PR.
4. Reply with the verdict line, that one finding in two sentences, the verified diff with before/after evidence, and the count of everything else.
If nothing real is found, say so with the counts and the command. Don't invent a "worst finding".

## Then set up, one question at a time
1. "Fail the gate at critical, high or medium?" (default high). Propose `.hefesto/triage.yaml` with `threshold: <answer>` and an empty `dismissals: []`. Write it after a yes, and suggest committing it.
2. "Want the gate in CI too, with results in GitHub's Security tab?" If yes, run hefesto-gate-install.
3. "Want a trend report from time to time?" If yes, explain that hefesto-weekly-trend runs when asked, or on a schedule if their tool supports one.

## CLI output
If the CLI output contains upgrade, plan or pricing messages, do not repeat, summarize or link them. Report only the analysis results.

## Close
One line listing what's set (repo, threshold, CI yes/no, telemetry on/off) and how to change it.
