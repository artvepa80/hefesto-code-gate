---
name: hefesto-weekly-trend
description: >-
  Report how HefestoAI findings by severity moved since the last snapshot of
  this repo: new HIGH/CRITICAL findings, the file that got worse and the one that
  improved. Use when the user asks how the repo's code health or security trend
  moved this week or since the last check.
license: MIT
compatibility: Requires python3 >= 3.10, git, and the hefesto-ai CLI.
metadata:
  author: Narapa LLC
  version: "1.0.0"
---
# Hefesto Weekly Trend

One job: tell the user, in under ten lines, whether the repo got safer or riskier since the last snapshot.

## Run
1. Make sure you are on the latest default branch (ask before pulling if there is uncommitted work).
2. `hefesto analyze . --output json --quiet` with `.hefesto.yaml` if present. Note the CLI version.
3. Read the last line of `.hefesto/trend.jsonl` (one JSON object per line: date, commit SHA, CLI version, counts by severity, counts by type, top 5 files by HIGH+CRITICAL).
4. Propose appending today's snapshot as one new line, and append it after a yes. Never rewrite earlier lines. Suggest committing the file, or ignoring it in git if the user prefers local-only history.

## Report
- No change in counts and no new HIGH/CRITICAL: one line, "Hefesto trend: no change (C critical, H high) at <short sha>, v<version>".
- Otherwise: counts now vs last snapshot with the delta; new HIGH/CRITICAL findings (file:line, type), worst first, max 5, triaged as in hefesto-gate, with dismissals from `.hefesto/triage.yaml` excluded and counted; the file that got worse and the one that improved most; one next step (usually "fix X with hefesto-fix-verify").
- If the CLI version changed since the last snapshot, say so: new rules can move counts without code changes.
- No earlier snapshot: report the counts and say the trend starts with the next run.

## Scheduling
This skill runs when asked. If your tool supports scheduled runs, the user can schedule it weekly there.

## Failure policy
If the analysis fails, report the failure and the error line. Never reuse an old snapshot as the current one.

## Anti-jobs
No PR comments, issues or emails.
