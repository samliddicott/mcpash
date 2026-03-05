# Bash Compliance Remaining Work List

Derived from: `docs/specs/bash-man-implementation-matrix.tsv`

Total remaining rows (partial or missing): 14

- Missing rows: 0
- Partial rows: 14

## Explicit Missing Features

None.

## Remaining Rows by Category

### Category 7

- `C7.INT.01` `prompt escapes in PS1/PS2/PS4 (\u, \h, \w, \!, etc.)` default=`covered` posix=`partial`
  tests: `run_interactive_ux_matrix.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.
- `C7.INT.02` `PROMPT_COMMAND execution before primary prompt` default=`covered` posix=`partial`
  tests: `run_interactive_ux_matrix.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.
- `C7.INT.03` `readline editing modes emacs/vi` default=`covered` posix=`partial`
  tests: `run_interactive_ux_matrix.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.
- `C7.INT.04` `bind builtin keymap/query/assignment` default=`covered` posix=`partial`
  tests: `run_completion_interactive_matrix.sh,bash-builtin-completion.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.
- `C7.INT.05` `history list/edit/delete/write/read` default=`covered` posix=`partial`
  tests: `run_interactive_ux_matrix.sh,man-bash-posix-12-history-suspend-logout.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.
- `C7.INT.06` `history expansion ! forms` default=`covered` posix=`partial`
  tests: `run_interactive_ux_matrix.sh,man-bash-posix-12-history-suspend-logout.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.
- `C7.INT.07` `fc editor/list/re-exec flows` default=`covered` posix=`partial`
  tests: `run_interactive_ux_matrix.sh,man-bash-posix-12-history-suspend-logout.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.
- `C7.INT.08` `programmable completion complete/compgen/compopt` default=`covered` posix=`partial`
  tests: `run_completion_interactive_matrix.sh,bash-builtin-completion.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.
- `C7.INT.09` `completion variables COMP_* and COMPREPLY` default=`covered` posix=`partial`
  tests: `run_completion_interactive_matrix.sh,bash-builtin-completion.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.
- `C7.INT.10` `interactive comments behavior (interactive_comments)` default=`covered` posix=`partial`
  tests: `run_interactive_ux_matrix.sh`
  note: In scope for POSIX lane closure: requires strict interactive PTY/job-control comparator evidence under --posix.
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
