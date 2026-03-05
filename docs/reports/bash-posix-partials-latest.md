# Bash --posix Partial Implementations

Source: `docs/specs/bash-man-implementation-matrix.tsv`

Total partial rows in `mctash --posix`: **16**

## Counts by Category

- Category 4: 5
- Category 10: 6
- Category 11: 5

## Rows

- `C4.REDIR.013` category=4 feature=`redirect stdout+stderr &>word`
  tests: `bash-man-redir-bash-ext.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-redir-bash-ext.sh

- `C4.REDIR.014` category=4 feature=`append stdout+stderr &>>word`
  tests: `bash-man-redir-bash-ext.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-redir-bash-ext.sh

- `C4.REDIR.016` category=4 feature=`named-fd redirection {varname}<word and family`
  tests: `bash-man-redir-bash-ext.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-redir-bash-ext.sh

- `C4.REDIR.019` category=4 feature=`/dev/tcp/host/port redirection`
  tests: `bash-man-redir-bash-ext.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-redir-bash-ext.sh

- `C4.REDIR.020` category=4 feature=`/dev/udp/host/port redirection`
  tests: `bash-man-redir-bash-ext.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-redir-bash-ext.sh

- `C10.STATE.01` category=10 feature=`variables assignment attributes (declare/local/typeset)`
  tests: `bash-man-variables-surface.sh,man-bash-posix-14-env-exec-flow.sh,bash-builtin-declare-typeset-local.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C10.STATE.02` category=10 feature=`readonly/export attribute propagation`
  tests: `bash-man-variables-surface.sh,man-bash-posix-14-env-exec-flow.sh,bash-builtin-declare-typeset-local.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C10.STATE.03` category=10 feature=`array/indexed/assoc state model`
  tests: `bash-man-variables-surface.sh,man-bash-posix-14-env-exec-flow.sh,bash-builtin-declare-typeset-local.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C10.STATE.04` category=10 feature=`environment import/export behavior`
  tests: `bash-man-variables-surface.sh,man-bash-posix-14-env-exec-flow.sh,bash-builtin-declare-typeset-local.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C10.STATE.05` category=10 feature=`startup-time variable influences (POSIXLY_CORRECT, BASH_ENV, ENV)`
  tests: `bash-man-variables-surface.sh,man-bash-posix-14-env-exec-flow.sh,bash-builtin-declare-typeset-local.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C10.STATE.06` category=10 feature=`special variable side effects (RANDOM, LINENO, SECONDS, REPLY)`
  tests: `bash-man-variables-surface.sh,man-bash-posix-14-env-exec-flow.sh,bash-builtin-declare-typeset-local.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C11.MODE.01` category=11 feature=`set -o option reporting format`
  tests: `bash-man-seto-surface.sh,run_startup_mode_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C11.MODE.02` category=11 feature=`shopt -p reporting format`
  tests: `bash-man-seto-surface.sh,run_startup_mode_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C11.MODE.03` category=11 feature=`diagnostic style selection (bash/ash modes)`
  tests: `bash-man-seto-surface.sh,run_startup_mode_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C11.MODE.04` category=11 feature=`mode selection by argv0 (sh/ash/dash vs bash/mctash)`
  tests: `bash-man-seto-surface.sh,run_startup_mode_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C11.MODE.05` category=11 feature=`restricted-mode enforcement matrix`
  tests: `bash-man-seto-surface.sh,run_startup_mode_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
