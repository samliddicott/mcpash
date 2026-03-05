# Bash Compliance Remaining Work List

Derived from: `docs/specs/bash-man-implementation-matrix.tsv`

Total remaining rows (partial or missing): 4

- Missing rows: 0
- Partial rows: 4

## Explicit Missing Features

None.

## Remaining Rows by Category

### Category 8

- `C8.JOB.03` `fg builtin jobspec resume in foreground` default=`covered` posix=`partial`
  tests: `man-bash-posix-10-jobs-fg-bg-interactive.sh,man-ash-jobs.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.
- `C8.JOB.07` `signal delivery to foreground jobs` default=`covered` posix=`partial`
  tests: `man-ash-trap-signal-matrix.sh,man-ash-trap-delivery.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.
- `C8.JOB.11` `set -m monitor mode behavior` default=`covered` posix=`partial`
  tests: `man-ash-set-monitor.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.
- `C8.JOB.12` `notification mode set -b/notify` default=`covered` posix=`partial`
  tests: `man-ash-set-monitor.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.
