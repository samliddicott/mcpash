**Agreement (Verbatim Transcript)**
> › Please begin as you see best, writing this poc code in the src dir
>
> • I started the PoC code in src/pybash/ with a minimal lexer, parser, AST, and runtime to execute simple commands and pipelines.
>   What’s in place
>
>   - src/pybash/lexer.py: minimal tokenization with basic quotes and operators.
>
>   - src/pybash/parser.py: parses simple commands, pipelines, and &&/|| lists.
>
>   - src/pybash/runtime.py: executes builtins (cd, exit, :) and external commands.
>
>   - src/pybash/main.py: CLI entry that reads a file or stdin.
>   If you want, I can extend this next with:
>
>   1. Redirections + here-doc handling
>
>   2. Assignments + environment export
>
>   3. Minimal expansion (parameter + command substitution)
>   Tell me where to focus first.
>
> › Do you parse until you have a complete "statement" (is that the right word? Or "Block") and then execute it?
>
> • Right now it parses the entire input into a ListNode (a sequence of AndOr items separated by ; or newlines) and then executes them in order. It does not
>   incrementally parse/exe “one statement at a time.”
>   In shell terms, the closest unit is a command list item (an and_or pipeline group). I’m not doing “blocks” yet (no { ...; }, if, loops, or functions).
>   If you want incremental parse-and-execute per complete command (for interactive or streaming), I can refactor the parser/runner to do that next.
>
> › Yes, do that. Then progress with:
>
>   1. Redirections + here-doc handling
>
>   2. Assignments + environment export
>
>   3. Minimal expansion (parameter + command substitution)

**Work Summary**
I implemented the initial Python 3 shell PoC in `src/`, using a parse-next-statement loop that parses a complete command/list item before execution. This established the interpreter structure for incremental parsing and execution.

**Post-Task Discussion (Verbatim)**
> • Done. I switched to incremental parse/execute and added the first three requested steps.
>   What changed
>
>   - Incremental execution: parser now returns one complete and_or at a time, and the runtime executes it immediately.
>
>   - Redirections + here-docs: basic <, >, >>, << handled in the executor (here-doc reads from stdin).
>
>   - Assignments + environment export: NAME=value before a command is applied; assignment-only lines persist in shell env.
>
>   - Minimal expansion: $VAR, ${VAR}, and $(...) command substitution (executes via /bin/sh -c for now).
>   Key files
>
>   - src/pybash/parser.py (incremental parsing, assignments, redirections)
>
>   - src/pybash/runtime.py (redir, here-doc, assignments, expansion)
>
>   - src/pybash/main.py (incremental loop)
>
>   - src/pybash/ast_nodes.py (assignments, redirects)
>   If you want, I can now:
>
>   1. Add redirections for builtins/functions (and restore FDs afterward).
>
>   2. Proper here-doc capture from script source (not stdin).
>
>   3. Field splitting + pathname expansion + quote preservation.
>   Tell me which to do next.

**Strategy/Plan Update**
The interpreter loop was confirmed to be statement-based, enabling later expansion to redirections, assignments, and command lists while preserving a simple execution model.
