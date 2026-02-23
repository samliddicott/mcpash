**Agreement (Verbatim Transcript)**
> › Are you making use of the AST or ASDL that I referred you to?
>
> • Right now, no. This PoC uses a tiny hand-rolled AST in src/pybash/ast_nodes.py and does not use ASDL yet.
>   If you want, I can introduce an ASDL schema now and generate Python node classes from it, then refactor the parser to emit those nodes. That will align us
>   with the vision and make the tree structure explicit and evolvable.
>
> › Please get the ASDL/AST/LST and put them in a separate subdirectory along with the license file that applies to them.
>   Then consider that where bash normally forks, I would like this implemention to make threads. Make a note in the vision, strategy and general plan that we
>   need to consider per-thread CWD, per-thread file-handles (both with using unshare) and per-thread data with shared data.
>   Then continue with:
>
>   1. Add redirections for builtins/functions (and restore FDs afterward).
>
>   2. Proper here-doc capture from script source (not stdin).
>
>   3. Field splitting + pathname expansion + quote preservation.
>
> • Done. I implemented the incremental parse/execute flow and added the three requested features, plus set up the ASDL/AST/LST directory with a license note
>   and updated docs for the threading model.
>   What’s now in place
>
>   - Incremental execution: the parser yields a complete and_or unit and the runtime executes it immediately.
>
>   - Redirections + builtins: redirections apply to builtins and assignment-only lines, with FD save/restore.
>
>   - Here-docs from source: lexer captures heredoc content from the script source (not stdin) and attaches it to Redirect.
>
>   - Assignments + environment export: NAME=value before a command is applied; assignment-only persists in shell env.
>
>   - Minimal expansion: parameter expansion and $(...) command substitution.
>
>   - Field splitting + globbing + quote preservation: word expansion respects single/double quotes, splits on IFS, and does pathname expansion when unquoted.
>   ASDL/AST/LST subdirectory
>
>   - src/syntax/pybash.asdl
>
>   - src/syntax/ast.md
>
>   - src/syntax/lst.md
>
>   - src/syntax/LICENSE
>   Docs updated for thread-vs-fork note
>
>   - docs/vision.md
>
>   - docs/strategy.md
>
>   - docs/plan.md
>   ———
>   If you want the next step, I suggest:
>
>   1. Make here-doc behavior closer to POSIX (<<-, quoted delimiters, expansion rules).
>
>   2. Add proper IO-number redirections in more cases (2>, 1>&2, etc.).
>
>   3. Start adding compound commands (blocks, if, while).
>   Tell me which to do next and whether you want these changes committed now.
>
> › I notice you got pybash.asdl and others. Please add a README and explain where you got them from (project and url). Then commit what we have, and proceed
>   with:
>
>   1. Make here-doc behavior closer to POSIX (<<-, quoted delimiters, expansion rules).
>
>   2. Add proper IO-number redirections in more cases (2>, 1>&2, etc.).
>
>   3. Start adding compound commands (blocks, if, while).
>   Then I want to test what we have myself just to get excited about it

**Work Summary**
I imported OSH ASDL/LST assets into a dedicated subdirectory with the applicable license and added a provenance README. I then advanced parsing/execution support for here-docs, redirections, and compound commands to reach a more realistic ash-like subset, and committed the results for you to test.

**Post-Task Discussion (Verbatim)**
> (No additional post-task dialogue recorded in this segment.)

**Strategy/Plan Update**
The project moved from generic PoC toward ash fidelity, with OSH ASDL/LST as the structural reference and concrete shell behaviors (here-docs, redirections, blocks) in scope.
