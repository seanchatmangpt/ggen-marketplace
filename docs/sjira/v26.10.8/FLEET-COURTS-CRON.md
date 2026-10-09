# FLEET-COURTS-CRON

# Fleet Courts Continuous Wiring Receipt

Schedule: every 6 hours via launchd (00:10, 06:10, 12:10, 18:10 local),
label `com.sac.fleet-courts`,
plist `/Users/sac/Library/LaunchAgents/com.sac.fleet-courts.plist`
(`plutil -lint` OK; `launchctl load -w` done; `launchctl list | grep fleet-courts`
shows `-  0  com.sac.fleet-courts`).

Log: rotating daily log
`~/Library/Logs/fleet-courts/fleet-courts-YYYYMMDD.log`
(one file per local day; append-only), plus
`~/Library/Logs/fleet-courts/launchd.err` for launchd-level stderr.
Rotation is by date in the filename; no old logs are deleted by the job.

Failure-visible rule: the job runs `scripts/run_fleet_courts.sh`, records
`=== exit <rc> ===` in the log, and propagates the runner's exit code:
launchd's last-exit-status (`launchctl list`, PID column) is non-zero iff a
court FAILED (the runner exits 0 iff every court verdict is PASS or
STYLE-ONLY). A FAIL never degrades to a silent pass; a missing court script
or missing workgraph file surfaces as MISSSING/FAIL verdict rows and exit 1.
See Also: scripts/run_fleet_courts.py (deterministic, side-effect-free:
writes only to a tempfile.TemporaryDirectory, reads sibling repos read-only,
no timestamps in output).

## First run (2026-10-09T07:37:27-0700, via `launchctl kickstart`)

```
court          verdict     violations  detail
---------------------------------------------
workgraphs     STYLE-ONLY        1047  12 workgraph repos
agent-cards    PASS                 0  69 cards across 8 repos
f5ea-graph     PASS                 0  6 graphs conform
git-trust      PASS                 0  117 rooted / 17 unrooted / 0 unresolved, 12 workgraphs
---------------------------------------------
OVERALL: PASS  (total violations: 1047)
```

launchd last-exit-status: 0.

## Prior direct run (same day, same verdicts, exit 0)

```
workgraphs     STYLE-ONLY        1047  12 workgraph repos
agent-cards     PASS                 0  69 cards across 8 repos
f5ea-graph      PASS                 0  6 graphs conform
git-trust       PASS                 0  117 rooted / 17 unrooted / 0 unresolved, 12 workgraphs
```

## Verdicts per court (first launchd run)

| court | verdict | violations |
|---|---|---|
| workgraphs | STYLE-ONLY | 1047 (all style-mismatch, 0 defects) |
| agent-cards | PASS | 0 (69 cards, 8 repos) |
| f5ea-graph | PASS | 0 (6 graphs) |
| git-trust | PASS | 0 unresolved (117 rooted / 17 unrooted) |

Commands + exits: `launchctl load -w ...` (0),
`launchctl kickstart gui/$(id -u)/com.sac.fleet-courts` (0),
`launchctl list | grep fleet-courts` -> `-  0  com.sac.fleet-courts`.
