# Bash --posix Partial Implementations

Source: `docs/specs/bash-man-implementation-matrix.tsv`

Total partial rows in `mctash --posix`: **14**

## Counts by Category

- Category 7: 10
- Category 8: 4

## Rows

- `C7.INT.01` category=7 feature=`prompt escapes in PS1/PS2/PS4 (\u, \h, \w, \!, etc.)`
  tests: `run_interactive_ux_matrix.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.

- `C7.INT.02` category=7 feature=`PROMPT_COMMAND execution before primary prompt`
  tests: `run_interactive_ux_matrix.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.

- `C7.INT.03` category=7 feature=`readline editing modes emacs/vi`
  tests: `run_interactive_ux_matrix.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.

- `C7.INT.04` category=7 feature=`bind builtin keymap/query/assignment`
  tests: `run_completion_interactive_matrix.sh,bash-builtin-completion.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.

- `C7.INT.05` category=7 feature=`history list/edit/delete/write/read`
  tests: `run_interactive_ux_matrix.sh,man-bash-posix-12-history-suspend-logout.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.

- `C7.INT.06` category=7 feature=`history expansion ! forms`
  tests: `run_interactive_ux_matrix.sh,man-bash-posix-12-history-suspend-logout.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.

- `C7.INT.07` category=7 feature=`fc editor/list/re-exec flows`
  tests: `run_interactive_ux_matrix.sh,man-bash-posix-12-history-suspend-logout.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.

- `C7.INT.08` category=7 feature=`programmable completion complete/compgen/compopt`
  tests: `run_completion_interactive_matrix.sh,bash-builtin-completion.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.

- `C7.INT.09` category=7 feature=`completion variables COMP_* and COMPREPLY`
  tests: `run_completion_interactive_matrix.sh,bash-builtin-completion.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.

- `C7.INT.10` category=7 feature=`interactive comments behavior (interactive_comments)`
  tests: `run_interactive_ux_matrix.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.

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

