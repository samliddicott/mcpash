# Bash POSIX Man-Page Matrix

Generated: 2026-03-05 09:00:48Z

## Summary

- covered builtins: 53
- partial builtins: 1
- out-of-scope builtins: 6
- executed case files: 18
- matrix exit code: 0
- mismatch lines detected: 0

## Executed Cases

- bash-builtin-completion.sh
- bash-builtin-declare-typeset-local.sh
- bash-builtin-dirstack.sh
- bash-builtin-disown.sh
- bash-builtin-enable.sh
- bash-builtin-help.sh
- bash-compat-mapfile-readarray.sh
- man-ash-fc.sh
- man-bash-posix-01-core-state.sh
- man-bash-posix-02-path-command.sh
- man-bash-posix-03-io-signals.sh
- man-bash-posix-04-misc-builtins.sh
- man-bash-posix-05-dot-source.sh
- man-bash-posix-06-loop-control.sh
- man-bash-posix-07-builtin-dispatch.sh
- man-bash-posix-08-declare-posix-policy.sh
- man-bash-posix-09-return-exit.sh
- man-bash-posix-10-jobs-fg-bg-interactive.sh

## Partial/Uncovered Builtins

- bind: interactive/readline semantics partially covered; strict PTY matrix in `run_completion_interactive_matrix.sh`

## Out of Scope for POSIX Parity Lane

- caller: bash extension; no mctash posix target yet
- history: interactive history extension
- let: bash arithmetic builtin extension
- logout: login-shell session extension
- shopt: bash extension; mctash has scoped variant
- suspend: interactive job control extension

## Mismatch Extract

- none
