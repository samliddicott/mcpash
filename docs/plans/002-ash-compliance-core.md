# 002: Ash Compliance Core Checklist

Goal: implement core ash semantics before resuming full `ash-shell/test`.

## 1. Word Model + Expansion Pipeline
- [ ] Represent words as parts (literal, parameter, command, arithmetic).
- [ ] Proper quoting rules (single, double, escapes).
- [ ] Expansion order: tilde → parameter → command → arithmetic → field split → glob → quote removal.
- [ ] `$@` vs `$*` semantics (quoted vs unquoted).
- [ ] Here-doc expansion rules (quoted delimiter disables expansion).

## 2. Grammar Coverage
- [ ] Reserved words recognition in correct parser contexts.
- [ ] Compound lists with `;` and newlines.
- [ ] Subshell `(...)`.
- [ ] `for`, `case`.
- [ ] Function definitions (`name() { ...; }`), local scopes.

## 3. Execution Semantics
- [ ] Builtins: `set`, `export`, `unset`, `shift`, `trap`, `read`, `printf`.
- [ ] `set -e` / `set -u` basics.
- [ ] Pipeline return codes and `!` negation.
- [ ] Assignment-only commands and environment export rules.

## 4. IO and Redirection
- [ ] IO-number coverage for `n>`, `n>>`, `n<`, `n>&m`, `n<&m`, `n>&-`, `n<&-`.
- [ ] `<<-` tab-stripping and delimiters.
- [ ] Redirection restore for builtins and functions.

## 5. Test Ramp
- [ ] Add mctash-only smoke script (ash syntax only).
- [ ] Add small internal test scripts for expansions and quoting.
- [ ] Re-enable `ash-shell/test` when 1–4 are minimally complete.
