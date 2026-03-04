# mctash Grammar to OSH ASDL Mapping

Purpose:

- Make grammar productions map explicitly to OSH-shaped ASDL node families.
- Keep parser/LST evolution aligned with ASDL-native execution goals.

References:

- Grammar: `docs/specs/mctash-grammar.ebnf`
- Lexer modes: `docs/specs/mctash-lexer-modes.md`
- ASDL schema: `src/syntax/osh/syntax.asdl`
- Mapping code: `src/mctash/asdl_map.py`

## 1. Command-Level Mapping

| Grammar production | LST family | OSH ASDL family |
|---|---|---|
| `script` / `list` | `LstScript`, `LstListNode`, `LstListItem` | `command.CommandList` |
| `and_or` | `LstAndOr` | `command.AndOr` |
| `pipeline` | `LstPipeline` | `command.Pipeline` |
| `simple_command` | `LstSimpleCommand` | `command.Simple` |
| assignment-only command | `LstShAssignmentCommand` | `command.ShAssignment` |
| redirect wrapper | `LstRedirectCommand` / redirect lists | `command.Redirect` + `redir.*` |
| `group_command` | `LstGroupCommand` | `command.BraceGroup` |
| `subshell_command` | `LstSubshellCommand` | `command.Subshell` |
| `if_command` | `LstIfCommand` | `command.If` |
| `while_command` / `until_command` | `LstWhileCommand`, `LstDoGroup` | `command.WhileUntil`, `command.DoGroup` |
| `for_command` | `LstForCommand` | `command.ForEach` |
| `case_command` | `LstCaseCommand`, `LstCaseItem` | `command.Case` |
| `function_def` | `LstFunctionDef` | `command.ShFunction` |
| list background separator `&` | list-item terminator metadata | `command.Sentence` (`terminator="&"`) |

## 2. Word-Level Mapping

| Grammar production | LST node | OSH ASDL node |
|---|---|---|
| `word` | `LstWord` | `word.Compound` |
| `literal` | `LstLiteralPart` | `word_part.Literal` |
| `single_quoted` | `LstSingleQuotedPart` (via parser word parts) | `word_part.SingleQuoted` |
| `double_quoted` | `LstDoubleQuotedPart` | `word_part.DoubleQuoted` |
| `simple_var_sub` | `LstSimpleVarSubPart` | `word_part.SimpleVarSub` |
| `braced_var_sub` | `LstBracedVarSubPart` | `word_part.BracedVarSub` |
| `command_sub` | `LstCommandSubPart` | `word_part.CommandSub` |
| `arith_sub` | `LstArithSubPart` | `word_part.ArithSub` |
| `backtick_sub` | `LstCommandSubPart` (`syntax=backtick`) | `word_part.CommandSub` (`syntax=backtick`) |

Note:

- Exact class names in LST may evolve; mapping contract is semantic (part-kind to ASDL node type).
- Use `docs/osh-asdl-checklist.md` for migration status and guarded-native execution coverage.

## 3. Redirection Mapping

| Grammar redirection form | ASDL target |
|---|---|
| `<`, `>`, `>>`, `<>` | file redirection variants in `redir` family |
| `>&`, `<&` | fd duplication variants in `redir` family |
| `<<`, `<<-` | heredoc variants in `redir` family with delimiter/expand metadata |
| optional `io_number` | `fd` field on mapped `redir` node |

## 4. Position and Diagnostics Mapping

For parse/diagnostic parity and roadmap work:

- retain token position (`line`, `col`, absolute `index`) on LST nodes,
- propagate into ASDL mapping metadata where possible,
- preserve node-source spans for high-quality parse/runtime diagnostics.

## 5. Coverage Contract

Every mapping row above should be backed by:

1. parser acceptance/rejection test evidence,
2. runtime semantic evidence (ash/bash-posix differential where in scope),
3. checklist row in `docs/osh-asdl-checklist.md` and/or grammar checklist.
