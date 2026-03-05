# Bash --posix Partial Implementations

Source: `docs/specs/bash-man-implementation-matrix.tsv`

Total partial rows in `mctash --posix`: **4**

## Counts by Category

- Category 8: 4

## Rows

- `C8.JOB.03` category=8 feature=`fg builtin jobspec resume in foreground`
  tests: `man-bash-posix-10-jobs-fg-bg-interactive.sh,man-ash-jobs.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.

- `C8.JOB.07` category=8 feature=`signal delivery to foreground jobs`
  tests: `man-ash-trap-signal-matrix.sh,man-ash-trap-delivery.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.

- `C8.JOB.11` category=8 feature=`set -m monitor mode behavior`
  tests: `man-ash-set-monitor.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.

- `C8.JOB.12` category=8 feature=`notification mode set -b/notify`
  tests: `man-ash-set-monitor.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.

