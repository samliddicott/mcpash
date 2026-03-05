# Bash --posix Partial Implementations

Source: `docs/specs/bash-man-implementation-matrix.tsv`

Total partial rows in `mctash --posix`: **168**

## Counts by Category

- Category 1: 67
- Category 3: 15
- Category 4: 5
- Category 6: 70
- Category 10: 6
- Category 11: 5

## Rows

- `C1.OPT.SHORT.c` category=1 feature=`-c`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.SHORT.i` category=1 feature=`-i`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.SHORT.l` category=1 feature=`-l`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.SHORT.r` category=1 feature=`-r`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.SHORT.v` category=1 feature=`-v`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.SHORT.x` category=1 feature=`-x`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.SHORT.O` category=1 feature=`-O [shopt_option]`
  tests: `run_bash_invocation_option_matrix.sh,bash-man-shopt-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.SHORT.PLUSO` category=1 feature=`+O [shopt_option]`
  tests: `run_bash_invocation_option_matrix.sh,bash-man-shopt-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.SHORT.DASHDASH` category=1 feature=`--`
  tests: `run_bash_invocation_option_matrix.sh,run_startup_mode_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.SHORT.SINGLEDASH` category=1 feature=`- (as argument)`
  tests: `run_bash_invocation_option_matrix.sh,run_startup_mode_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.LONG.DEBUGGER` category=1 feature=`--debugger`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.LONG.HELP` category=1 feature=`--help`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.LONG.INIT_FILE_FILE` category=1 feature=`--init-file FILE`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.LONG.RCFILE_FILE` category=1 feature=`--rcfile FILE`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.LONG.LOGIN` category=1 feature=`--login`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.LONG.NOEDITING` category=1 feature=`--noediting`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.LONG.NOPROFILE` category=1 feature=`--noprofile`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.LONG.NORC` category=1 feature=`--norc`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.LONG.POSIX` category=1 feature=`--posix`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.LONG.RESTRICTED` category=1 feature=`--restricted`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.LONG.VERSION` category=1 feature=`--version`
  tests: `run_bash_invocation_option_matrix.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: run_bash_invocation_option_matrix.sh

- `C1.OPT.SET.a` category=1 feature=`-a`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SET.b` category=1 feature=`-b`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SET.e` category=1 feature=`-e`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SET.f` category=1 feature=`-f`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SET.h` category=1 feature=`-h`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SET.k` category=1 feature=`-k`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SET.m` category=1 feature=`-m`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SET.n` category=1 feature=`-n`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SET.p` category=1 feature=`-p`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SET.t` category=1 feature=`-t`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SET.u` category=1 feature=`-u`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SET.v` category=1 feature=`-v`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SET.x` category=1 feature=`-x`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SET.B` category=1 feature=`-B`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SET.C` category=1 feature=`-C`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SET.E` category=1 feature=`-E`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SET.H` category=1 feature=`-H`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SET.P` category=1 feature=`-P`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SET.T` category=1 feature=`-T`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.ALLEXPORT` category=1 feature=`allexport`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.BRACEEXPAND` category=1 feature=`braceexpand`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.EMACS` category=1 feature=`emacs`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.ERREXIT` category=1 feature=`errexit`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.ERRTRACE` category=1 feature=`errtrace`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.FUNCTRACE` category=1 feature=`functrace`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.HASHALL` category=1 feature=`hashall`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.HISTEXPAND` category=1 feature=`histexpand`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.HISTORY` category=1 feature=`history`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.IGNOREEOF` category=1 feature=`ignoreeof`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.INTERACTIVE_COMMENTS` category=1 feature=`interactive-comments`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.KEYWORD` category=1 feature=`keyword`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.MONITOR` category=1 feature=`monitor`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.NOCLOBBER` category=1 feature=`noclobber`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.NOEXEC` category=1 feature=`noexec`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.NOGLOB` category=1 feature=`noglob`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.NOLOG` category=1 feature=`nolog`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.NOTIFY` category=1 feature=`notify`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.NOUNSET` category=1 feature=`nounset`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.ONECMD` category=1 feature=`onecmd`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.PHYSICAL` category=1 feature=`physical`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.PIPEFAIL` category=1 feature=`pipefail`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.POSIX` category=1 feature=`posix`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.PRIVILEGED` category=1 feature=`privileged`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.VERBOSE` category=1 feature=`verbose`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.VI` category=1 feature=`vi`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

- `C1.OPT.SETO.XTRACE` category=1 feature=`xtrace`
  tests: `bash-man-seto-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-seto-surface.sh

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

- `C6.VAR.CORE.HOME` category=6 feature=`HOME`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.CORE.PATH` category=6 feature=`PATH`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.CORE.IFS` category=6 feature=`IFS`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.CORE.PWD` category=6 feature=`PWD`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.CORE.OLDPWD` category=6 feature=`OLDPWD`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.CORE.OPTIND` category=6 feature=`OPTIND`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.CORE.OPTARG` category=6 feature=`OPTARG`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.CORE.PS1` category=6 feature=`PS1`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.CORE.PS2` category=6 feature=`PS2`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.CORE.MAIL` category=6 feature=`MAIL`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.CORE.MAILPATH` category=6 feature=`MAILPATH`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.CORE.LANG` category=6 feature=`LANG`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.CORE.LC_ALL` category=6 feature=`LC_ALL`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.CORE.LC_CTYPE` category=6 feature=`LC_CTYPE`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.CORE.LC_MESSAGES` category=6 feature=`LC_MESSAGES`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.CORE.LINENO` category=6 feature=`LINENO`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.CORE.ENV` category=6 feature=`ENV`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.BASH` category=6 feature=`BASH`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.BASH_VERSION` category=6 feature=`BASH_VERSION`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.BASH_VERSINFO` category=6 feature=`BASH_VERSINFO`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.BASH_SOURCE` category=6 feature=`BASH_SOURCE`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.BASH_LINENO` category=6 feature=`BASH_LINENO`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.BASH_COMMAND` category=6 feature=`BASH_COMMAND`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.BASH_SUBSHELL` category=6 feature=`BASH_SUBSHELL`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.BASHPID` category=6 feature=`BASHPID`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.BASHOPTS` category=6 feature=`BASHOPTS`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.SHELLOPTS` category=6 feature=`SHELLOPTS`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.BASH_COMPAT` category=6 feature=`BASH_COMPAT`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.BASH_ENV` category=6 feature=`BASH_ENV`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.BASH_ARGC` category=6 feature=`BASH_ARGC`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.BASH_ARGV` category=6 feature=`BASH_ARGV`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.BASH_ARGV0` category=6 feature=`BASH_ARGV0`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.BASH_CMDS` category=6 feature=`BASH_CMDS`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.BASH_REMATCH` category=6 feature=`BASH_REMATCH`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.BASH_LOADABLES_PATH` category=6 feature=`BASH_LOADABLES_PATH`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.BASH_XTRACEFD` category=6 feature=`BASH_XTRACEFD`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.EPOCHREALTIME` category=6 feature=`EPOCHREALTIME`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.EPOCHSECONDS` category=6 feature=`EPOCHSECONDS`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.RANDOM` category=6 feature=`RANDOM`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.SECONDS` category=6 feature=`SECONDS`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.SRANDOM` category=6 feature=`SRANDOM`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.EUID` category=6 feature=`EUID`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.UID` category=6 feature=`UID`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.PPID` category=6 feature=`PPID`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.GROUPS` category=6 feature=`GROUPS`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.DIRSTACK` category=6 feature=`DIRSTACK`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.FUNCNAME` category=6 feature=`FUNCNAME`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.COPROC` category=6 feature=`COPROC`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.REPLY` category=6 feature=`REPLY`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.PROMPT_COMMAND` category=6 feature=`PROMPT_COMMAND`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.PS0` category=6 feature=`PS0`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.PS3` category=6 feature=`PS3`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.PS4` category=6 feature=`PS4`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.COMP_LINE` category=6 feature=`COMP_LINE`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.COMP_POINT` category=6 feature=`COMP_POINT`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.COMP_WORDS` category=6 feature=`COMP_WORDS`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.COMP_CWORD` category=6 feature=`COMP_CWORD`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.COMP_WORDBREAKS` category=6 feature=`COMP_WORDBREAKS`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.COMP_TYPE` category=6 feature=`COMP_TYPE`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.COMP_KEY` category=6 feature=`COMP_KEY`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.COMPREPLY` category=6 feature=`COMPREPLY`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.HISTFILE` category=6 feature=`HISTFILE`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.HISTSIZE` category=6 feature=`HISTSIZE`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.HISTFILESIZE` category=6 feature=`HISTFILESIZE`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.HISTCONTROL` category=6 feature=`HISTCONTROL`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.HISTIGNORE` category=6 feature=`HISTIGNORE`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.HISTTIMEFORMAT` category=6 feature=`HISTTIMEFORMAT`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.HOSTFILE` category=6 feature=`HOSTFILE`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.FCEDIT` category=6 feature=`FCEDIT`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

- `C6.VAR.BASH.TMOUT` category=6 feature=`TMOUT`
  tests: `bash-man-variables-surface.sh`
  note: Row-level evidence mapping assigned from requirement->case rules. Evidence run has failing/timeout tests: bash-man-variables-surface.sh

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
