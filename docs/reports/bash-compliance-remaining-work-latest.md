# Bash Compliance Remaining Work List

Derived from: `docs/specs/bash-man-implementation-matrix.tsv`

Total remaining rows (partial or missing): 171

- Missing rows: 3
- Partial rows: 168

## Explicit Missing Features

- `C3.EXP.001` feature=`brace expansion {a,b}` default=`missing` posix=`missing` tests=`bash-man-expansion-brace-locale.sh`
  note: brace expansion currently literal.
- `C3.EXP.029` feature=`locale translation quoting $"..."` default=`missing` posix=`missing` tests=`bash-man-expansion-brace-locale.sh`
  note: $"..." locale translation quoting currently not implemented.
- `C4.REDIR.012` feature=`here-string <<<word` default=`missing` posix=`missing` tests=`bash-man-redir-here-string.sh`
  note: here-string <<< currently parse-error path.

## Remaining Rows by Category

### Category 1

- `C1.OPT.LONG.DEBUGGER` `--debugger` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.LONG.HELP` `--help` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.LONG.INIT_FILE_FILE` `--init-file FILE` default=`partial` posix=`partial`
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
- `C1.OPT.LONG.RCFILE_FILE` `--rcfile FILE` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.LONG.RESTRICTED` `--restricted` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.LONG.VERSION` `--version` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
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
- `C1.OPT.SHORT.DASHDASH` `--` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh,run_startup_mode_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.SHORT.O` `-O [shopt_option]` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh,bash-man-shopt-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.SHORT.PLUSO` `+O [shopt_option]` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh,bash-man-shopt-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
- `C1.OPT.SHORT.SINGLEDASH` `- (as argument)` default=`partial` posix=`partial`
  tests: `run_bash_invocation_option_matrix.sh,run_startup_mode_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh
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

### Category 3

- `C3.EXP.001` `brace expansion {a,b}` default=`missing` posix=`missing`
  tests: `bash-man-expansion-brace-locale.sh`
  note: brace expansion currently literal.
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
- `C3.EXP.029` `locale translation quoting $"..."` default=`missing` posix=`missing`
  tests: `bash-man-expansion-brace-locale.sh`
  note: $"..." locale translation quoting currently not implemented.

### Category 4

- `C4.REDIR.012` `here-string <<<word` default=`missing` posix=`missing`
  tests: `bash-man-redir-here-string.sh`
  note: here-string <<< currently parse-error path.
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

### Category 6

- `C6.VAR.BASH.BASH` `BASH` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.BASHOPTS` `BASHOPTS` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.BASHPID` `BASHPID` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.BASH_ARGC` `BASH_ARGC` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.BASH_ARGV` `BASH_ARGV` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.BASH_ARGV0` `BASH_ARGV0` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.BASH_CMDS` `BASH_CMDS` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.BASH_COMMAND` `BASH_COMMAND` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.BASH_COMPAT` `BASH_COMPAT` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.BASH_ENV` `BASH_ENV` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.BASH_LINENO` `BASH_LINENO` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.BASH_LOADABLES_PATH` `BASH_LOADABLES_PATH` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.BASH_REMATCH` `BASH_REMATCH` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.BASH_SOURCE` `BASH_SOURCE` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.BASH_SUBSHELL` `BASH_SUBSHELL` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.BASH_VERSINFO` `BASH_VERSINFO` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.BASH_VERSION` `BASH_VERSION` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.BASH_XTRACEFD` `BASH_XTRACEFD` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.COMPREPLY` `COMPREPLY` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.COMP_CWORD` `COMP_CWORD` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.COMP_KEY` `COMP_KEY` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.COMP_LINE` `COMP_LINE` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.COMP_POINT` `COMP_POINT` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.COMP_TYPE` `COMP_TYPE` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.COMP_WORDBREAKS` `COMP_WORDBREAKS` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.COMP_WORDS` `COMP_WORDS` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.COPROC` `COPROC` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.DIRSTACK` `DIRSTACK` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.EPOCHREALTIME` `EPOCHREALTIME` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.EPOCHSECONDS` `EPOCHSECONDS` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.EUID` `EUID` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.FCEDIT` `FCEDIT` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.FUNCNAME` `FUNCNAME` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.GROUPS` `GROUPS` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.HISTCONTROL` `HISTCONTROL` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.HISTFILE` `HISTFILE` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.HISTFILESIZE` `HISTFILESIZE` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.HISTIGNORE` `HISTIGNORE` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.HISTSIZE` `HISTSIZE` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.HISTTIMEFORMAT` `HISTTIMEFORMAT` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.HOSTFILE` `HOSTFILE` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.PPID` `PPID` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.PROMPT_COMMAND` `PROMPT_COMMAND` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.PS0` `PS0` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.PS3` `PS3` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.PS4` `PS4` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.RANDOM` `RANDOM` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.REPLY` `REPLY` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.SECONDS` `SECONDS` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.SHELLOPTS` `SHELLOPTS` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.SRANDOM` `SRANDOM` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.TMOUT` `TMOUT` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.BASH.UID` `UID` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.CORE.ENV` `ENV` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.CORE.HOME` `HOME` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.CORE.IFS` `IFS` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.CORE.LANG` `LANG` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.CORE.LC_ALL` `LC_ALL` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.CORE.LC_CTYPE` `LC_CTYPE` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.CORE.LC_MESSAGES` `LC_MESSAGES` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.CORE.LINENO` `LINENO` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.CORE.MAIL` `MAIL` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.CORE.MAILPATH` `MAILPATH` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.CORE.OLDPWD` `OLDPWD` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.CORE.OPTARG` `OPTARG` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.CORE.OPTIND` `OPTIND` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.CORE.PATH` `PATH` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.CORE.PS1` `PS1` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.CORE.PS2` `PS2` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh
- `C6.VAR.CORE.PWD` `PWD` default=`partial` posix=`partial`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

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

## Completion Criteria

- For each row above: convert `partial`/`missing` to `covered` (or `out_of_scope` in posix lane when justified).
- Keep row-level test IDs and evidence output reproducible.
- Regenerate this report after each tranche to show net burn-down.
