**Agreement (Verbatim Transcript)**
> › As you suggested before the rename, please wire up a small bin/mctash entrypoint and start integrating ash-shell/test as a runnable target.
>
> • Done. I wired up the entrypoint and a runnable ash test target, and committed everything.
>   What’s added
>
>   - bin/mctash entrypoint (runs python -m mctash with PYTHONPATH=src)
>
>   - external/ash-shell-test submodule
>
>   - scripts/run-ash-test.sh to invoke the ash test harness
>
>   - docs/plan.md updated to reference the runnable target
>   Commit
>
>   - Add mctash entrypoint and ash test harness
>   How to try it
>
>   1. Initialize submodule if needed:
>      git submodule update --init --recursive
>
>   2. Run the harness:
>      ./scripts/run-ash-test.sh
>   Expect lots of failures right now; this is just wired to run against the harness so we can iterate. If you want, I can now add a quick “smoke test” script
>   so you can see some green output immediately.
>
> › I amended the commit to point to python3 but it doesn't work. Please start the "smoke test" script
>
> › yes commit those, and then run the ash test suite to show what we are missing.
>
> › yes
>
> • Done.
>
>   - Added support for script [args...] and basic positional parameters ($1, $@, $#) in mctash.
>
>   - Committed: Support script arguments and basic positional params.
>   Running the ash harness now fails with:
>   FileNotFoundError: [Errno 2] No such file or directory: '#!/bin/bash'
>   That means we’re trying to execute a script containing a shebang line as a command. We need to recognize #!/... at the start of the script and skip it (or
>   treat it as a comment), and likely add basic comment parsing (# line comments). Want me to implement shebang/comment handling next and re-run?
>
> › yes, and support reading options from the shebang as if they were passed on the command line so that as command line options are added it will
>   automatically support more shebang options too
>
> • I added shebang handling (including passing shebang options as CLI args) and comment support, then committed (Handle shebang options and comments).
>   Re-running the ash harness now fails with:
>   FileNotFoundError: [Errno 2] No such file or directory: 'Test__callable_main'
>   So we’re now parsing the script, but failing to support function definitions and the Test__callable_main function invocation. Next step is to implement
>   function definitions and function lookup/execution (including source/.).
>   If you want, I’ll implement functions and re-run the suite to show the next missing pieces.
>
> › yes, please continue to iterate to pass one test at a time, stopping to chat with me as each new test passes, to look at what was done and what needs doing
>   next
>
> › yes

**Work Summary**
I added a `bin/mctash` entrypoint, integrated the ash-shell-test harness, and wired a smoke test. I fixed the Python 3 invocation, added shebang-option parsing, and ran the ash test harness to surface missing behavior. Iteration was set up for incremental test progress.

**Post-Task Discussion (Verbatim)**
> (No additional post-task dialogue recorded in this segment.)

**Strategy/Plan Update**
This established the test-driven loop for ash compliance and made the CLI usable via both command line and shebang execution.
