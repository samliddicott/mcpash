# Upstream Bash Tests (Fetched Metadata)

This directory stores fetched metadata about GNU Bash upstream tests for parity planning.

Source index:

- https://git.savannah.gnu.org/cgit/bash.git/tree/tests

Fetch command:

```bash
./tests/bash/fetch_upstream_tests.sh
```

What is fetched:

- `tree-<branch>.html`: upstream tests directory index page
- `README`: upstream tests readme
- `COPYRIGHT`: upstream tests copyright notice
- `manifest-<branch>.txt`: extracted `*.tests` file list from upstream index

Current intent:

- Use this manifest as a corpus source to pick POSIX-relevant bash tests for differential runs against `mctash --posix`.
- Keep fetched artifacts out of git by default; only committed docs/scripts live in this folder.
