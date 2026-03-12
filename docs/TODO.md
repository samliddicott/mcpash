# TODO

## Runtime Review Follow-Ups

These are intentionally deferred review items from the subprocess/bashiﬁcation audit:

1. Review `_seed_bash_special_vars()` surface policy (`src/mctash/runtime.py`).
   - Confirm which bash-special variables should be eagerly seeded vs lazily materialized.
   - Re-check against bash mode and `--posix` mode expectations.

2. Review parser leniency gating tied to compat mode (`lenient_unterminated_quotes` paths).
   - `src/mctash/main.py`
   - `src/mctash/runtime.py`
   - Verify current policy is intentional across bash lane vs posix/ash lane.

3. Remove host-shell dependency in pipeline failure placeholders.
   - Current use: `["sh", "-c", "exit 127"]` and `["sh", "-c", "exit 126"]`.
   - Replace with native/internal placeholder process strategy.
