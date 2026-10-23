---
name: hefesto-fix-verify
description: >-
  Fix one HefestoAI finding that hefesto-gate labeled real: write the smallest
  patch, prove with the hefesto-ai CLI and the repo's tests that the finding is
  gone and nothing new appeared, and hand over the diff. Invoke explicitly after
  a hefesto-gate report. Opens a draft PR only after the user says yes.
disable-model-invocation: true
license: MIT
compatibility: Requires python3 >= 3.10, git, and the hefesto-ai CLI.
metadata:
  author: Narapa LLC
  version: "1.0.0"
---
# Hefesto Fix & Verify

One job: turn a real HIGH or CRITICAL finding into a proven patch, then hand it over. Be bold inside a working branch and conservative at its edge: no push, PR or comment without the user's yes for that exact action.

## Before you touch code
- Only fix findings labeled **real** by hefesto-gate. If it is doubtful, ask the one question that settles it.
- Work in a new branch or git worktree off the PR head (or the default branch), never on the user's checked-out branch with uncommitted work.
- Record the baseline: `hefesto analyze <changed files> --output json`, plus the repo's own test command if one is obvious (README, Makefile, `pyproject.toml`, `package.json`). If there is none, say "no tests run"; don't guess one.

## Write the patch
- Smallest change that removes the risk and keeps behavior: parameterized query instead of string formatting, `ast.literal_eval`/`json.loads` instead of `eval`, secret moved to an environment variable with the literal removed, `subprocess` with a list and `shell=False`.
- Only call functions and parameters you have confirmed exist in this repo or its pinned dependencies. Open the definition before using it. Never add or upgrade a dependency without saying so in the first line of the report.
- A hardcoded secret is not fixed by editing code alone: it must be rotated, because it stays in git history.
- No drive-by refactors, renames or formatting outside the lines you fix.

## Verify (all three, or it isn't done)
1. Re-run the same `hefesto analyze` command: the finding is gone.
2. Compare with the baseline: no new finding at any severity in the touched files.
3. Run the tests you found: same result as before, or better.
If a check fails, read the output and fix once more (max two retries), then stop and report what failed. "Inconclusive" is not a pass.

## Hand over
- One line per fix: `file:line`, finding type, what changed.
- The unified diff.
- Evidence: before/after `hefesto` counts, and the test command with its result (or "no tests run").
- Then ask once: "Open a draft PR with this?" Only on yes: push the branch and open a **draft** PR listing the finding, the change and the evidence. Never mark it ready, merge it, or close someone else's PR.

## Limits to state, not hide
Cross-file fixes and design-level issues (auth model, trust boundaries) get a written plan instead of a patch.
