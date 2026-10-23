# Telemetry notice (canonical text)

`scripts/gen_manifests.py` renders the block below into `hefesto-gate-setup` and
`hefesto-gate-install` between the `telemetry-notice` markers, and `--check`
fails if a copy differs. Edit the text here, never in a skill.

Placeholders, filled from `hefesto-plugin.source.json` → `telemetry`:

- `{{IP_SENTENCE}}`
  - `posthog_ip_discard: on` → "Your IP address reaches the server with each request but is not stored."
  - `off` or `pending` → "Our analytics provider (PostHog, US) receives your IP address with each request."
  - Tag builds fail while the value is `pending`.
- `{{UPDATE_CHECK_SENTENCE}}`
  - `update_check_optout: null` → "In hefesto-ai {{CLI_FLOOR}} this check cannot be turned off."
  - Set to a variable name → "Set `<NAME>=1` to skip it; `HEFESTO_TELEMETRY=0` and `DO_NOT_TRACK=1` also skip it (hefesto-ai 4.20.3 and later)."

<!-- template:start -->
- The hefesto-ai CLI sends usage events to PostHog (us.i.posthog.com) by default. Every event carries the event name, the install ID below, and where it ran (cli, hook, ci or action). `analyze` events also carry the CLI, OS and Python versions, how the CLI was installed (PyPI or editable), environment labels such as `ci`, `github_actions` or `docker`, and counts (files, issues, duration, exit code).
- Each event carries a random install ID created on this machine and stored in `~/.hefesto/telemetry_state.json`. It is not linked to your name, account, or repository, but it does let us count runs from the same install.
- Events never include source code, file paths, findings, or repository names. {{IP_SENTENCE}}
- On the first run the CLI only prints this notice and sends nothing.
- Turn it off with `hefesto telemetry disable` (your user account on this machine, including git hooks), or `HEFESTO_TELEMETRY=0` or `DO_NOT_TRACK=1` (this shell or CI job).
- In the Hefesto GitHub Action telemetry is off by default (`telemetry: 0`). With `telemetry: 1`, each run also sends one ping (CLI version, file and issue counts, exit code) to Narapa's telemetry endpoint, stored without your IP address.
- Separately, `hefesto analyze` checks pypi.org for a newer version at most once every 24 hours. {{UPDATE_CHECK_SENTENCE}}
<!-- template:end -->
