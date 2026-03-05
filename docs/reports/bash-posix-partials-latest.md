# Bash --posix Partial Implementations

Source: `docs/specs/bash-man-implementation-matrix.tsv`

Total partial rows in `mctash --posix`: **31**

## Counts by Category

- Category 3: 15
- Category 4: 5
- Category 10: 6
- Category 11: 5

## Rows

- `C3.EXP.003` category=3 feature=`parameter expansion $name ${name}`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh

- `C3.EXP.004` category=3 feature=`special parameters $* $@ $# $? $- $$ $! $0`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh

- `C3.EXP.005` category=3 feature=`positional parameters $1..${N}`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh

- `C3.EXP.006` category=3 feature=`parameter default operators ${v-word} ${v:-word}`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh

- `C3.EXP.007` category=3 feature=`parameter assign operators ${v=word} ${v:=word}`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh

- `C3.EXP.008` category=3 feature=`parameter error operators ${v?word} ${v:?word}`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh

- `C3.EXP.009` category=3 feature=`parameter alternate operators ${v+word} ${v:+word}`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh

- `C3.EXP.015` category=3 feature=`case modification ${v^} ${v^^} ${v,} ${v,,}`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh

- `C3.EXP.016` category=3 feature=`transformation operator ${v@op}`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh

- `C3.EXP.017` category=3 feature=`indirection ${!name}`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh

- `C3.EXP.018` category=3 feature=`name expansion ${!prefix*} ${!prefix@}`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh

- `C3.EXP.019` category=3 feature=`array subscript expansion ${a[i]} ${a[@]} ${a[*]}`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh

- `C3.EXP.020` category=3 feature=`array slicing ${a[@]:o:l}`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh

- `C3.EXP.024` category=3 feature=`process substitution <(cmd) >(cmd)`
  tests: `bash-man-expansion-process-subst.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-expansion-process-subst.sh

- `C3.EXP.026` category=3 feature=`pathname expansion (globbing)`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh

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
