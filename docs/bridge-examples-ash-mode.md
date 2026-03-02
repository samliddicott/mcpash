# Bridge Examples (Ash Mode)

This file shows in-scope shell<->python bridge usage for current ash-mode behavior.

## `py` command

Execute a statement:

```sh
py 'print("ok")'
```

Evaluate expression and print result:

```sh
py -e '1 + 2'
```

Capture return value into shell variable:

```sh
py 'def add(a, b): return int(a) + int(b)'
py -r out add 2 3
echo "$out"
```

Capture Python stdout:

```sh
py -v out 'print("hello")'
printf 'X%sY\n' "$out"
```

Structured exception mode:

```sh
py -x 'raise ValueError("boom")'
echo "$PYTHON_EXCEPTION|$PYTHON_EXCEPTION_MSG|$PYTHON_EXCEPTION_LANG"
```

## `python:` pseudo-function

Callable dispatch:

```sh
py 'import math'
python: -r out math.sqrt 9
echo "$out"
```

Fallback-to-statement behavior:

```sh
python: import math
python: -r out math.pow 2 4
echo "$out"
```

## `PYTHON ... END_PYTHON` block

```sh
PYTHON
print("block")
END_PYTHON
```

No-dedent mode:

```sh
PYTHON --no-dedent
    print("requires matching indentation")
END_PYTHON
```

## Import wrappers

```sh
from math import factorial as fac
fac 5
```

## `sh` mapping APIs

Set/read shell vars from Python:

```sh
py 'sh.vars["X"] = "42"'
echo "$X"
```

Export via `sh.env`:

```sh
py 'sh.env["EXAMPLE"] = "v"'
python3 -c 'import os; print(os.getenv("EXAMPLE"))'
```

Call shell from Python:

```sh
py 'cp = sh.run("echo hi", capture_output=True); sh.vars["OUT"] = cp.stdout.strip()'
echo "$OUT"
```

## Ties (ash-mode in-scope)

Scalar tie:

```sh
py 'x = "seed"'
py -t x
x=after
py -e 'x'
```

Integer tie:

```sh
py 'n = 0; sh.tie("TN", lambda: n, lambda v: globals().__setitem__("n", v), type="integer")'
TN=12
py -e 'n'
```

## Deferred in ash mode

The following are intentionally deferred until Bash-compat mode:

- `sh.vars` list/tuple mapping
- `sh.vars` dict mapping
- `sh.tie(..., type="array")`
- `sh.tie(..., type="assoc")`

Runtime currently rejects these with explicit errors.
