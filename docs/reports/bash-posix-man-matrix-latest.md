# Bash POSIX Man-Page Matrix

Generated: 2026-03-04 06:03:51Z

## Summary

- covered builtins: 28
- partial builtins: 12
- out-of-scope builtins: 20
- executed case files: 4
- matrix exit code: 1
- mismatch lines detected: 7

## Executed Cases

- man-bash-posix-01-core-state.sh
- man-bash-posix-02-path-command.sh
- man-bash-posix-03-io-signals.sh
- man-bash-posix-04-misc-builtins.sh

## Partial/Uncovered Builtins

- .: needs dedicated source/dot-file semantics case
- bg: interactive-only; track in jobs matrix
- break: covered indirectly in ash lane; add bash-posix case
- builtin: add dedicated builtin-dispatch case
- continue: covered indirectly in ash lane; add bash-posix case
- declare: bash-compat lane exists; add posix-lane assertion
- exit: add dedicated exit-status/handler case
- fc: tracked via temporary bash comparator policy
- fg: interactive-only; track in jobs matrix
- jobs: interactive jobs matrix handles core semantics
- return: add function return status case
- source: same as dot; add dedicated case

## Out of Scope for POSIX Parity Lane

- bind: line editor builtin; interactive/readline domain
- caller: bash extension; no mctash posix target yet
- compgen: bash completion extension
- complete: bash completion extension
- compopt: bash completion extension
- dirs: bash directory stack extension
- disown: bash jobs extension
- enable: bash builtin toggling extension
- help: bash help text surface
- history: interactive history extension
- let: bash arithmetic builtin extension
- local: bash function-local extension
- logout: login-shell session extension
- mapfile: bash extension (readarray alias)
- popd: bash directory stack extension
- pushd: bash directory stack extension
- readarray: bash extension
- shopt: bash extension; mctash has scoped variant
- suspend: interactive job control extension
- typeset: bash/ksh extension alias of declare

## Mismatch Extract

- 1:man-bash-posix-01-core-state: exit status mismatch bash=0 mctash=2
- 2:man-bash-posix-01-core-state: stdout mismatch
- 3:man-bash-posix-01-core-state: stderr mismatch
- 4:man-bash-posix-02-path-command: stdout mismatch
- 5:man-bash-posix-02-path-command: stderr mismatch
- 6:man-bash-posix-04-misc-builtins: stdout mismatch
- 7:man-bash-posix-04-misc-builtins: stderr mismatch

## Runner Output

    man-bash-posix-01-core-state: exit status mismatch bash=0 mctash=2
    man-bash-posix-01-core-state: stdout mismatch
    man-bash-posix-01-core-state: stderr mismatch
    man-bash-posix-02-path-command: stdout mismatch
    man-bash-posix-02-path-command: stderr mismatch
    man-bash-posix-04-misc-builtins: stdout mismatch
    man-bash-posix-04-misc-builtins: stderr mismatch
