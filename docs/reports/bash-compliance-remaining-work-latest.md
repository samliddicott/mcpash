# Bash Compliance Remaining Work List

Derived from: `docs/specs/bash-man-implementation-matrix.tsv`

Total remaining rows (partial or missing): 16

- Missing rows: 0
- Partial rows: 16

## Explicit Missing Features

None.

## Remaining Rows by Category

### Category 4

- `C4.REDIR.013` `redirect stdout+stderr &>word` default=`partial` posix=`partial`
  tests: `bash-man-redir-bash-ext.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-redir-bash-ext.sh
- `C4.REDIR.014` `append stdout+stderr &>>word` default=`partial` posix=`partial`
  tests: `bash-man-redir-bash-ext.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-redir-bash-ext.sh
- `C4.REDIR.016` `named-fd redirection {varname}<word and family` default=`partial` posix=`partial`
  tests: `bash-man-redir-bash-ext.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-redir-bash-ext.sh
- `C4.REDIR.019` `/dev/tcp/host/port redirection` default=`partial` posix=`partial`
  tests: `bash-man-redir-bash-ext.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-redir-bash-ext.sh
- `C4.REDIR.020` `/dev/udp/host/port redirection` default=`partial` posix=`partial`
  tests: `bash-man-redir-bash-ext.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-redir-bash-ext.sh

### Category 10

- `C10.STATE.01` `variables assignment attributes (declare/local/typeset)` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh,man-bash-posix-14-env-exec-flow.sh,bash-builtin-declare-typeset-local.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C10.STATE.02` `readonly/export attribute propagation` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh,man-bash-posix-14-env-exec-flow.sh,bash-builtin-declare-typeset-local.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C10.STATE.03` `array/indexed/assoc state model` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh,man-bash-posix-14-env-exec-flow.sh,bash-builtin-declare-typeset-local.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C10.STATE.04` `environment import/export behavior` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh,man-bash-posix-14-env-exec-flow.sh,bash-builtin-declare-typeset-local.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C10.STATE.05` `startup-time variable influences (POSIXLY_CORRECT, BASH_ENV, ENV)` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh,man-bash-posix-14-env-exec-flow.sh,bash-builtin-declare-typeset-local.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C10.STATE.06` `special variable side effects (RANDOM, LINENO, SECONDS, REPLY)` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh,man-bash-posix-14-env-exec-flow.sh,bash-builtin-declare-typeset-local.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

### Category 11

- `C11.MODE.01` `set -o option reporting format` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh,run_startup_mode_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C11.MODE.02` `shopt -p reporting format` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh,run_startup_mode_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C11.MODE.03` `diagnostic style selection (bash/ash modes)` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh,run_startup_mode_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C11.MODE.04` `mode selection by argv0 (sh/ash/dash vs bash/mctash)` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh,run_startup_mode_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C11.MODE.05` `restricted-mode enforcement matrix` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh,run_startup_mode_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
