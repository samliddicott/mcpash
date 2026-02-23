**Agreement (Verbatim Transcript)**
> › please do it. Also use wget to do a suitable google search for people talking about ASDL AST or LST for bash or dash or posix shells. If wget google
>   doesn't work, construct search terms for me and I'll do it.
>
> • Done. I pulled the git history for each ASDL file via the GitHub API and logged the oldest commit info into src/osh_syntax/README.md, then committed it:
>
>   - Commit: Log Oil/OSH ASDL git history provenance
>   Google search via wget failed because it hit the Google consent page (no results). Here are search terms you can run manually:
>
>   1. ASDL AST POSIX shell parser
>
>   2. Lossless Syntax Tree shell parser
>
>   3. ASDL bash AST
>
>   4. shell AST lossless syntax tree
>
>   5. osh asdl syntax.asdl
>   If you want me to try a different search engine with wget (e.g. DuckDuckGo or Bing), say the word and I’ll do it.
>
> › you try those while I try google
>
> • I tried DuckDuckGo and Bing with wget. Both appear blocked or returning non‑results:
>
>   - DuckDuckGo HTML returned tiny pages (≈2916 bytes) without result titles.
>
>   - Bing pages look blocked (contain the word “blocked” and no result markup).
>   So I can’t reliably extract results from those searches via wget here.
>   Search terms you can run manually (same as I used):
>
>   1. ASDL AST POSIX shell parser
>
>   2. Lossless Syntax Tree shell parser
>
>   3. ASDL bash AST
>
>   4. shell AST lossless syntax tree
>
>   5. osh asdl syntax.asdl
>   If you want me to try another source (e.g., search.brave.com or searx), tell me which and I’ll attempt it.
>
> › Here's one to read with wget and follow some links: https://drewdevault.com/2018/12/28/Anatomy-of-a-shell.html
>
> • I’ve fetched the page and read it. It’s a solid overview of shell architecture and has several links worth following (mrsh project, POSIX shell spec, and
>   specific mrsh source files).
>   Do you want me to follow the links to:
>
>   1. mrsh (project overview and parser/AST details)
>
>   2. POSIX shell spec (command language section)
>
>   3. Specific mrsh code links (redirection, pipelines, functions)
>   Tell me which ones to pull next.
>
> › 1, 2
>
> • I pulled both links:
>   1) mrsh project page
>   I fetched https://git.sr.ht/~emersion/mrsh and scanned it. It’s a summary page, but it confirms:
>
>   - mrsh is a minimal POSIX shell
>
>   - It links to the POSIX shell spec and the repo tree/log.
>     There isn’t much parser/AST detail on the summary page itself, just project metadata.
>   If you want, I can follow the repo tree (e.g. tree/master) and read parser or AST code in mrsh next.
>   2) POSIX shell spec
>   I fetched http://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html and confirmed:
>
>   - Token recognition, shell grammar, expansions, redirections, pipelines, and compound commands are all in the page.
>
>   - It has the exact order of expansions and details for here-docs, pipelines, and compound commands.
>   Do you want me to follow the mrsh tree to inspect its parser/AST structure next?
>
> › yes
>
> • I fetched the mrsh repo tree and then pulled the raw source for key files via wget:
>
>   - parser/parser.c (lexer + recursive descent parsing)
>
>   - ast.c (AST node ownership and destruction)
>
>   - ast_print.c (AST printing, shows word/redirect node structure)
>   From parser.c, mrsh defines operators and keywords explicitly (including <<-, >&, <&, !, {, }, in, case, esac, etc.), and uses a hand-written recursive
>   descent parser. From ast_print.c, you can see their AST structure for words, redirects, and parameter expansions, which is useful as a reference.
>   If you want, I can pull more of their parser/AST or the specific files linked in the blog (e.g., redirection and pipeline tasks) and summarize the AST
>   shapes they use.
>
> › make another syntax_ directory for this stuff you are pulling and be sure to log where you got it from. Is this stuff going to be interesting and helpful
>   for our parser/lexer?
>
> › I think you need to create a "parser" research project dir to log this. You can copy their source into that dir but you must also copy and record the
>   license, and have a different dir for each project.
>
> › The osh_syntax and syntax_mrsh should be put into their folders there
>
> › I will supply you with source pages to read which you must note in a "sources" section and read with wget for research.
>   https://lobste.rs/s/fi6lax/formally_verified_interpreter_for_shell
>   https://www.irif.fr/_media/rencontres/pps2018/regis-gianas.pdf
>   https://archive.fosdem.org/2018/schedule/event/code_parsing_posix_s_hell/attachments/slides/2525/export/events/attachments/code_parsing_posix_s_hell/
>   slides/2525/morbig.pdf
>   https://pdf.sciencedirectassets.com/320563/1-s2.0-S2590118420X00025/1-s2.0-S2590118420300046/am.pdf?X-Amz-Security-
>   Token=IQoJb3JpZ2luX2VjEOz%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIBQ5cPiv0QrqQOBjANMm7riOhAG3B9EqKraMdMMwDtWnAiEAzYDsPrE4nhzEmNLRs3RssrKDlyeBd
>   88067Gtfb4LtA0qvAUItf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAFGgwwNTkwMDM1NDY4NjUiDG9j5B4IotVU3aOXyiqQBdBb%2BvdqVqDIPE9uqIIK9gvOZl1bHaI0mKvZSaE%2BSi6bJ8rN8SxuhngO
>   JTzNfPw5H%2F6SVs9pdtDLlGoiCm913Wmv6oJG%2B5fdQecDcnlK8YW%2FhaIGQ6keR1oFrFx2yKupfeJzHomq5jPAtXx%2FFecj6myyl2e0U25RzvUuMw2R%2F7J%2FdPhP2fVPjWcvwwMNBsLj%2FeYwn
>   wLGCjq4ffwUqXiLq0%2FvssmMh7ZRPyaIdvXA7lvavPzqfId4MmVwnsxLJHWGIszp8KhcyLNHvfxYN3oDAa7Vh0%2FVdAu1B74Wbdm%2Fb1f2qAbNY5wCJR6uXXRfVYSiDwagvahl%2FR7hS5pGeYqwxfeI
>   EqOl9FSL282eYcoVkO9BGVlEB2G99W98cNhc8lkv6pOT%2ByQXIqyu0GP71fuvwX%2FIuMf2wilGNhdYyL%2BnuceBhB02x%2Fv4d5mZ1j5qtJF42Hu6X4DArRs%2B1VDEQR%2B3Ee7n%2F6RuSoxiGA1DB
>   1Sh8IY5XM8Zm0tWD7WcfVHDD%2F6SzhmGwTaQ6kAOL6wLMkfdh13Oh%2BDD0qDnkueMLhCcPxE%2FWhNoK%2FlCdUNSrS%2B685cUNkLaaah7mZjZgTPPHxRBL1vOcz3MqfoX2I8TvzPzIchivUGf%2BAJO
>   puR89gx3%2BaaoBas10p62xijivHJz%2BOd2UJBtgsL0EDsmX6pNGJHYLCcrM42oa%2BD7ElAwzrncIEjLCBqCpORMuuzF%2FREtDNPkx6ryyTkFPcXKKyA9Gkh55pIR01qSXnU4cTWinv8L9wNRFyVF8y%
>   2FtZzjNpqT2XjxXjMgSFASZoHeLYVIWjnXoODMr6ygk7ZnD4ICYAORls7BOcDRHseYtazirDayRxYFUv5hututAb2i1tQda455Dlce4MKSR6MwGOrEB7UPzZRmT2lHvccuDyqZFVsxSqfcG2PgCqoRXXPt8
>   URegwvMDZ2QIUYovakqoVCofHkXSuHehE21Zv6s2kJRuEbN8ju4GSVqZp3UhqkdhZ4cjQIct7EWGUJdFN0XhZMkVW1BOV4%2Fp6W7v9r2oTGTof3pfwsBEHCPonan1Y2%2BXQDjlmYaNkheR9kmyHef2qWl
>   Xs70p9Ij5Z73KiGu7FaC4txEvRRd8oIB%2FuXSwHk8dW0DE&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20260221T205524Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-
>   Amz-Credential=ASIAQ3PHCVTY7MWZ54ZB%2F20260221%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-
>   Signature=b6d99e14fd59f2f41d194669879a749d8f5b0f563205fecdb582deccce838724&hash=1d052c6354be7ed6a8df90b4f5b52647cacdd25980b282488a2341ef38c57466&host=68042
>   c943591013ac2b2430a89b270f6af2c76d8dfd086a07176afe7c76c2c61&pii=S2590118420300046&tid=pdf-3cfc0428-a27f-4e92-8558-
>   c5bde7003bb6&sid=e1b08e795d5bb443ce4955a78695e12eb05dgxrqb&type=client
>   I think the formal parsing spec will be the major step for us that it has been for others.
>   We are looking at how to get some ASDL/AST/LST that we can use as the foundation for our parsing and lexing.
>   (Also if we go for MIT/BSD/Apache license maybe we can peel at dash ash and toysh, so put that in the vision and strategy and plan)
>
> › I saved it in the project dir, can you find it?
>
> • Context compacted
>
> › yes
>
> • Got it. What do you want me to do with 1-s2.0-S2590118420300046-am.pdf—read and summarize, extract key points into the research notes, or just log its
>   provenance in the sources section?
>
> › Move it to the research notes, log it under the original URL, and then read them all and understand and let me know your thoughts on what we can do to put
>   our parser/lexer on a firm foundation
>
> › Don't we already have an ASDL from osh?
>
> • Yes. We already have the Oil/OSH ASDL in research/parser/osh_syntax/:
>
>   - research/parser/osh_syntax/frontend.syntax.asdl
>
>   - research/parser/osh_syntax/frontend.types.asdl
>
>   - research/parser/osh_syntax/core.runtime.asdl
>
>   - research/parser/osh_syntax/core.value.asdl
>   There’s also a provenance/URL log in research/parser/osh_syntax/README.md and the Apache 2.0 license in research/parser/osh_syntax/LICENSE.txt.
>   If you want, I can start wiring our parser/lexer outputs to those ASDL definitions next.

**Work Summary**
I performed wget-based research, collected references (including Drew DeVault’s article and linked sources), and created a structured parser research area with per-project folders and licenses. The OSH syntax and mrsh sources were placed into the research tree with provenance logged.

**Post-Task Discussion (Verbatim)**
> (No additional post-task dialogue recorded in this segment.)

**Strategy/Plan Update**
Research artifacts were formalized as first-class inputs to parser/lexer design, with clear provenance, licensing, and a consistent directory structure.
