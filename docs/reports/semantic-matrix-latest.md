# Semantic Matrix Report

Generated: 2026-03-04 08:14:47Z

Matrix source: `tests/compat/semantic_matrix.tsv`

## Summary

- total rows: 7
- pass: 7
- fail: 0
- conflict: 0
- info: 0

## Rows

| id | class | spec | ash rc | bash --posix rc | bash rc | mctash --posix rc | mctash rc | posix refs agree | mctash-posix ok | mctash-bash ok | status | note |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|---|---|
| `set-e-andor-nonfinal` | posix-required | `POSIX-2.8.1-errexit` | 0 | 0 | 0 | 0 | 0 | yes | yes | yes | pass | - |
| `set-e-andor-final` | posix-required | `POSIX-2.8.1-errexit` | 1 | 1 | 1 | 1 | 1 | yes | yes | yes | pass | - |
| `set-e-negated-eval` | posix-required | `POSIX-2.8.1-errexit` | 0 | 0 | 0 | 0 | 0 | yes | yes | yes | pass | - |
| `param-default-forms` | posix-required | `POSIX-2.6.2-parameter-expansion` | 0 | 0 | 0 | 0 | 0 | yes | yes | yes | pass | - |
| `param-plus-forms` | posix-required | `POSIX-2.6.2-parameter-expansion` | 0 | 0 | 0 | 0 | 0 | yes | yes | yes | pass | - |
| `param-assign-forms` | posix-required | `POSIX-2.6.2-parameter-expansion` | 0 | 0 | 0 | 0 | 0 | yes | yes | yes | pass | - |
| `bash-array-basic` | extension-bash | `BASH-Arrays` | 2 | 0 | 0 | 1 | 0 | no | no | yes | pass | - |

## Policy

- `posix-required`: ash and `bash --posix` must agree, and `mctash --posix` must match.
- `extension-bash`: `mctash` default mode must match bash default mode.
- `extension-ash`: `mctash --posix` must match ash for ash-specific behavior.
- `posix-unspecified`: tracked informationally until policy is pinned.
