# Parameter Brace/Quote Edge Matrix

Generated: 2026-03-04 14:17:38Z
Comparator: `bash --posix`
Target: `mctash --posix`

This is a focused parser/expansion edge corpus for `${...}` with mixed quote/brace content.

- Full parity rows: 15/18

| Case | Intent | bash rc | mctash rc | bash stdout | mctash stdout | bash stderr | mctash stderr | Parity |
|---|---|---:|---:|---|---|---|---|---|
| `E001` | simple default expansion baseline | `0` | `0` | `<default>\n` | `<default>\n` | `` | `` | ok |
| `E002` | single quote chars in operator word | `0` | `0` | `<''z}>\n` | `<''z}>\n` | `` | `` | ok |
| `E003` | unmatched single quote inside operator word | `0` | `0` | `<'bar baz>\n` | `<'bar baz>\n` | `` | `` | ok |
| `E004` | double-quoted operator word containing escaped quote | `0` | `0` | `<"}"z>\n` | `<"}"z>\n` | `` | `` | ok |
| `E005` | exact upstream mixed quote toggles with comment tail | `0` | `2` | `28 'x ~ x''x}"x}" #\n` | `` | `` | `parse error: expected ')' at 1:61\n` | mismatch |
| `E006` | operator word with command substitution | `0` | `0` | `<hi there>\n` | `<hi there>\n` | `` | `` | ok |
| `E007` | operator word with backticks and nested ${...} | `0` | `0` | `<hi there>\n` | `<hi there>\n` | `` | `` | ok |
| `E008` | operator word with nested brace expansion | `0` | `0` | `<foo bar baz>\n` | `<foo bar baz>\n` | `` | `` | ok |
| `E009` | parameter replace with quote char in pattern | `0` | `0` | `<x'>\n` | `<x'>\n` | `` | `` | ok |
| `E010` | single quotes in unquoted expansion word | `0` | `0` | `<$key>\n` | `<$key>\n` | `` | `` | ok |
| `E011` | single quotes in quoted expansion word | `0` | `0` | `<'value'>\n` | `<'value'>\n` | `` | `` | ok |
| `E012` | line continuation inside ${...} word (single quotes) | `0` | `0` | `<foo>\n<b\\\nar>\n<baz>\n` | `<foo>\n<b\\\nar>\n<baz>\n` | `` | `` | ok |
| `E013` | line continuation inside ${...} word (double quotes) | `0` | `0` | `<foo>\n<bar>\n<baz>\n` | `<foo>\n<bar>\n<baz>\n` | `` | `` | ok |
| `E014` | braced op with escaped right brace | `0` | `0` | `<}z>\n` | `<}z>\n` | `` | `` | ok |
| `E015` | double-quoted braced op with escaped right brace | `0` | `0` | `<}z>\n` | `<}z>\n` | `` | `` | ok |
| `E016` | malformed: missing close brace | `2` | `2` | `` | `` | `bash: -c: line 1: unexpected EOF while looking for matching `"'\nbash: -c: line 2: syntax error: unexpected end of fi...` | `mctash -c: line 1: syntax error: unterminated quoted string\n` | mismatch |
| `E017` | malformed: bad parameter name | `127` | `127` | `` | `` | `bash: line 1: ${+x}: bad substitution\n` | `syntax error: bad substitution\n` | mismatch |
| `E018` | malformed: unterminated quote in braced op word | `0` | `0` | `"abc\n` | `"abc\n` | `` | `` | ok |

## Notes

- `malformed` rows are expected to error; parity requires matching error behavior class (rc+stderr), not exact wording.
- This report is a parser/expansion roadmap input; it is intentionally narrow and pathological.
