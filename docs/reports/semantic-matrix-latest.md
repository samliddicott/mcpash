# Semantic Matrix Report

Generated: 2026-03-04 10:08:12Z

Matrix source: `tests/compat/semantic_matrix.tsv`

## Summary

- total rows: 27
- pass: 16
- fail: 0
- conflict: 0
- info: 11

## Rows

| id | class | spec | ash rc | bash --posix rc | bash rc | mctash --posix rc | mctash rc | posix refs agree | mctash-posix ok | mctash-bash ok | status | note |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|---|---|
| `set-e-andor-nonfinal` | posix-required | `POSIX-2.8.1-errexit` | 0 | 0 | 0 | 0 | 0 | yes | yes | yes | pass | - |
| `set-e-andor-final` | posix-required | `POSIX-2.8.1-errexit` | 0 | 0 | 0 | 0 | 0 | yes | yes | yes | pass | - |
| `set-e-negated-eval` | posix-required | `POSIX-2.8.1-errexit` | 0 | 0 | 0 | 0 | 0 | yes | yes | yes | pass | - |
| `set-e-cmdsub-posix-abort` | posix-required | `POSIX-2.8.1-errexit` | 0 | 0 | 0 | 0 | 0 | yes | yes | yes | pass | - |
| `set-e-cmdsub-bash-nonposix` | extension-bash | `BASH-set-e-cmdsub` | 0 | 0 | 0 | 0 | 0 | yes | yes | yes | pass | - |
| `set-e-andor-subshell-left` | posix-required | `POSIX-2.8.1-errexit` | 0 | 0 | 0 | 0 | 0 | yes | yes | yes | pass | - |
| `set-e-andor-func-subshell-left` | posix-required | `POSIX-2.8.1-errexit` | 0 | 0 | 0 | 0 | 0 | yes | yes | yes | pass | - |
| `set-e-negated-brace-pipeline` | posix-required | `POSIX-2.8.1-errexit` | 0 | 0 | 0 | 0 | 0 | yes | yes | yes | pass | - |
| `set-e-negation-true-continues` | posix-required | `POSIX-2.8.1-errexit` | 0 | 0 | 0 | 0 | 0 | yes | yes | yes | pass | - |
| `startup-grouped-ce-posix` | posix-required | `POSIX-shell-invocation` | 0 | 0 | 0 | 0 | 0 | yes | yes | yes | pass | - |
| `comsub-commented-close-paren` | posix-unspecified | `BASH-UPSTREAM-comsub` | 0 | 0 | 0 | 0 | 0 | no | no | no | info | unspecified/extension behavior |
| `comsub-heredoc-close-paren` | posix-required | `POSIX-2.6.3-command-substitution` | 0 | 0 | 0 | 0 | 0 | yes | yes | yes | pass | - |
| `comsub-heredoc-quoted-delim` | posix-required | `POSIX-2.6.3-command-substitution` | 0 | 0 | 0 | 0 | 0 | yes | yes | yes | pass | - |
| `comsub-double-lparen-command-sub` | posix-unspecified | `BASH-UPSTREAM-comsub` | 0 | 0 | 0 | 0 | 0 | no | yes | yes | info | unspecified/extension behavior |
| `posixpipe-lone-bang` | posix-unspecified | `BASH-UPSTREAM-posixpipe` | 0 | 0 | 0 | 0 | 0 | no | yes | yes | info | unspecified/extension behavior |
| `param-default-forms` | posix-required | `POSIX-2.6.2-parameter-expansion` | 0 | 0 | 0 | 0 | 0 | yes | yes | yes | pass | - |
| `param-plus-forms` | posix-required | `POSIX-2.6.2-parameter-expansion` | 0 | 0 | 0 | 0 | 0 | yes | yes | yes | pass | - |
| `param-assign-forms` | posix-required | `POSIX-2.6.2-parameter-expansion` | 0 | 0 | 0 | 0 | 0 | yes | yes | yes | pass | - |
| `bash-array-basic` | extension-bash | `BASH-Arrays` | 0 | 0 | 0 | 0 | 0 | no | no | yes | pass | - |
| `upstream-posix2` | posix-unspecified | `BASH-UPSTREAM-posix2` | -1 | -1 | -1 | -1 | -1 | no | no | no | info | upstream row skipped (set RUN_UPSTREAM_ROWS=1 to execute) |
| `upstream-posixexp` | posix-unspecified | `BASH-UPSTREAM-posixexp` | -1 | -1 | -1 | -1 | -1 | no | no | no | info | upstream row skipped (set RUN_UPSTREAM_ROWS=1 to execute) |
| `upstream-posixexp2` | posix-unspecified | `BASH-UPSTREAM-posixexp2` | -1 | -1 | -1 | -1 | -1 | no | no | no | info | upstream row skipped (set RUN_UPSTREAM_ROWS=1 to execute) |
| `upstream-posixpat` | posix-unspecified | `BASH-UPSTREAM-posixpat` | -1 | -1 | -1 | -1 | -1 | no | no | no | info | upstream row skipped (set RUN_UPSTREAM_ROWS=1 to execute) |
| `upstream-posixpipe` | posix-unspecified | `BASH-UPSTREAM-posixpipe` | -1 | -1 | -1 | -1 | -1 | no | no | no | info | upstream row skipped (set RUN_UPSTREAM_ROWS=1 to execute) |
| `upstream-ifs-posix` | posix-unspecified | `BASH-UPSTREAM-ifs-posix` | -1 | -1 | -1 | -1 | -1 | no | no | no | info | upstream row skipped (set RUN_UPSTREAM_ROWS=1 to execute) |
| `upstream-comsub-posix` | posix-unspecified | `BASH-UPSTREAM-comsub-posix` | -1 | -1 | -1 | -1 | -1 | no | no | no | info | upstream row skipped (set RUN_UPSTREAM_ROWS=1 to execute) |
| `upstream-set-e` | posix-unspecified | `BASH-UPSTREAM-set-e` | -1 | -1 | -1 | -1 | -1 | no | no | no | info | upstream row skipped (set RUN_UPSTREAM_ROWS=1 to execute) |

## Policy

- `posix-required`: ash and `bash --posix` must agree, and `mctash --posix` must match.
- `extension-bash`: `mctash` default mode must match bash default mode.
- `extension-ash`: `mctash --posix` must match ash for ash-specific behavior.
- `posix-unspecified`: tracked informationally until policy is pinned.
