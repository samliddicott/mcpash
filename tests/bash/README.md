# Upstream Bash Tests (Fetched Metadata)

This directory stores fetched metadata about GNU Bash upstream tests for parity planning.

Source index:

- https://git.savannah.gnu.org/cgit/bash.git/tree/tests

Fetch command:

```bash
./tests/bash/fetch_upstream_tests.sh
```

Pin to a tag/branch/commit:

```bash
BASH_UPSTREAM_REF=master ./tests/bash/fetch_upstream_tests.sh
```

Force refresh (ignore cache):

```bash
./tests/bash/fetch_upstream_tests.sh --refresh
```

What is fetched:

- `upstream/<safe_ref>/tree.html`: upstream tests directory index page
- `upstream/<safe_ref>/README`: upstream tests readme
- `upstream/<safe_ref>/COPYRIGHT`: upstream tests copyright notice
- `upstream/<safe_ref>/manifest.txt`: extracted `*.tests` file list from upstream index
- `upstream/<safe_ref>/fetch-lock.json`: fetch metadata lock file
- `upstream/latest` symlink to most recently fetched ref directory

Current intent:

- Use this manifest as a corpus source to pick POSIX-relevant bash tests for differential runs against `mctash --posix`.
- Keep fetched artifacts out of git by default; only committed docs/scripts live in this folder.
