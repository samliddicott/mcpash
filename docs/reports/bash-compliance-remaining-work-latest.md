# Bash Compliance Remaining Work List

Derived from: `docs/specs/bash-man-implementation-matrix.tsv`

Total remaining rows (partial or missing): 98

- Missing rows: 0
- Partial rows: 98

## Explicit Missing Features

None.

## Remaining Rows by Category

### Category 1

- `C1.OPT.SHORT.c` `-c` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.SHORT.i` `-i` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.SHORT.l` `-l` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.SHORT.r` `-r` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.SHORT.v` `-v` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.SHORT.x` `-x` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.SHORT.O` `-O [shopt_option]` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh,bash-man-shopt-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.SHORT.PLUSO` `+O [shopt_option]` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh,bash-man-shopt-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.SHORT.DASHDASH` `--` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh,run_startup_mode_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.SHORT.SINGLEDASH` `- (as argument)` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh,run_startup_mode_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.LONG.DEBUGGER` `--debugger` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.LONG.HELP` `--help` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.LONG.INIT_FILE_FILE` `--init-file FILE` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.LONG.RCFILE_FILE` `--rcfile FILE` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.LONG.LOGIN` `--login` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.LONG.NOEDITING` `--noediting` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.LONG.NOPROFILE` `--noprofile` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.LONG.NORC` `--norc` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.LONG.POSIX` `--posix` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.LONG.RESTRICTED` `--restricted` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.LONG.VERSION` `--version` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.SET.a` `-a` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SET.b` `-b` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SET.e` `-e` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SET.f` `-f` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SET.h` `-h` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SET.k` `-k` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SET.m` `-m` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SET.n` `-n` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SET.p` `-p` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SET.t` `-t` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SET.u` `-u` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SET.v` `-v` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SET.x` `-x` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SET.B` `-B` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SET.C` `-C` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SET.E` `-E` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SET.H` `-H` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SET.P` `-P` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SET.T` `-T` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.ALLEXPORT` `allexport` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.BRACEEXPAND` `braceexpand` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.EMACS` `emacs` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.ERREXIT` `errexit` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.ERRTRACE` `errtrace` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.FUNCTRACE` `functrace` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.HASHALL` `hashall` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.HISTEXPAND` `histexpand` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.HISTORY` `history` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.IGNOREEOF` `ignoreeof` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.INTERACTIVE_COMMENTS` `interactive-comments` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.KEYWORD` `keyword` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.MONITOR` `monitor` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.NOCLOBBER` `noclobber` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.NOEXEC` `noexec` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.NOGLOB` `noglob` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.NOLOG` `nolog` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.NOTIFY` `notify` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.NOUNSET` `nounset` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.ONECMD` `onecmd` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.PHYSICAL` `physical` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.PIPEFAIL` `pipefail` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.POSIX` `posix` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.PRIVILEGED` `privileged` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.VERBOSE` `verbose` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.VI` `vi` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh
- `C1.OPT.SETO.XTRACE` `xtrace` default=`partial` posix=`partial`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

### Category 3

- `C3.EXP.003` `parameter expansion $name ${name}` default=`partial` posix=`partial`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh
- `C3.EXP.004` `special parameters $* $@ $# $? $- $$ $! $0` default=`partial` posix=`partial`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh
- `C3.EXP.005` `positional parameters $1..${N}` default=`partial` posix=`partial`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh
- `C3.EXP.006` `parameter default operators ${v-word} ${v:-word}` default=`partial` posix=`partial`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh
- `C3.EXP.007` `parameter assign operators ${v=word} ${v:=word}` default=`partial` posix=`partial`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh
- `C3.EXP.008` `parameter error operators ${v?word} ${v:?word}` default=`partial` posix=`partial`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh
- `C3.EXP.009` `parameter alternate operators ${v+word} ${v:+word}` default=`partial` posix=`partial`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh
- `C3.EXP.015` `case modification ${v^} ${v^^} ${v,} ${v,,}` default=`partial` posix=`partial`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh
- `C3.EXP.016` `transformation operator ${v@op}` default=`partial` posix=`partial`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh
- `C3.EXP.017` `indirection ${!name}` default=`partial` posix=`partial`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh
- `C3.EXP.018` `name expansion ${!prefix*} ${!prefix@}` default=`partial` posix=`partial`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh
- `C3.EXP.019` `array subscript expansion ${a[i]} ${a[@]} ${a[*]}` default=`partial` posix=`partial`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh
- `C3.EXP.020` `array slicing ${a[@]:o:l}` default=`partial` posix=`partial`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh
- `C3.EXP.024` `process substitution <(cmd) >(cmd)` default=`partial` posix=`partial`
  tests: `bash-man-expansion-process-subst.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-expansion-process-subst.sh
- `C3.EXP.026` `pathname expansion (globbing)` default=`partial` posix=`partial`
  tests: `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-compat-param-array-hash-extended.sh

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
