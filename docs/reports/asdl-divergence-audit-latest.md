# ASDL Divergence Audit (Latest)

Generated: 2026-03-13

Scope:
- `src/mctash/runtime.py`
- Focus: remaining reparsing/re-escaping paths that can diverge from structured OSH ASDL execution.

## Summary

There are still meaningful non-ASDL lanes. Most are concentrated in assignment/subscript handling and in word flattening (`word -> text -> regex parse`).

Top priority to remove:
1. Legacy word reparse in expansion (`parse_legacy_word`).
2. Assignment token reparsing from flattened text.
3. Regex subscript parsing for semantic decisions where ASDL structure is already available.

## Required Boundaries (Keep)

These are expected string/regex boundaries and are not ASDL-divergence work:
- Prompt/backslash decoding and display quoting (`PS1`/formatting).
- Path/glob pattern normalization and fs-facing matching.
- Numeric parsing (`base#digits`, octal, float/int coercion).
- CLI option parsing and environment-variable normalization.

## Divergence Inventory

### A. High Priority

- `src/mctash/runtime.py:4608`
  - `parse_legacy_word(text)` in `_legacy_word_to_expansion_fields`.
  - Why: reparses strings even when ASDL word structure exists.
  - Action: route ASDL call sites to `_asdl_word_to_expansion_fields` directly; keep legacy parser only for truly legacy AST/text entrypoints.

- `src/mctash/runtime.py:3310`
  - `_expand_asdl_declare_argv`: flattens words via `_asdl_word_to_text`, then regex-splits assignment.
  - Why: loses structured quoting/subscript provenance and re-interprets.
  - Action: emit structured declare assignment IR directly from ASDL words, bypass text split.

- `src/mctash/runtime.py:11921`
  - `_argv_assignment_words`: regex-driven assignment parser over argv text.
  - Why: reparses shell syntax after expansion; fragile around embedded `=` and subscript forms.
  - Action: use ASDL assignment nodes/word parts for simple-command assignment recognition in ASDL path; keep argv regex only for non-ASDL fallback mode.

- `src/mctash/runtime.py:11870`
  - `_parse_subscripted_name` regex as semantic discriminator used broadly (`_run_unset`, `_run_declare`, `_test_var_is_set`, etc).
  - Why: string parse of syntax that should come from structured nodes in ASDL lane.
  - Action: introduce structured `VarRef`/`SubscriptRef` objects for ASDL execution; limit `_parse_subscripted_name` to fallback-only paths.

### B. Medium Priority

- `src/mctash/runtime.py:3973`
  - `_expand_asdl_rhs_assignment` currently can flatten word text then run assignment-word expansion.
  - Action: complete RHS expansion directly from ASDL word parts everywhere (including declare/local/export/readonly variants).

- `src/mctash/runtime.py:12336`
  - `_parse_assoc_compound_assignment_rhs` and sibling tokenization paths still rely on text token streams for compound RHS in some lanes.
  - Action: standardize on existing `AssignmentEntry` IR sourced from ASDL parts; demote text tokenizer to fallback-only.

- `src/mctash/runtime.py:12472`
  - `_eval_index_subscript` performs text expansion+arith parse on raw key text.
  - Action: prefer structured subscript expression where available; keep text path only when no AST/ASDL expression is present.

### C. Lower Priority

- `_asdl_word_to_text` call sites used for diagnostics/source rendering:
  - `src/mctash/runtime.py:5713`, `src/mctash/runtime.py:16959`, `src/mctash/runtime.py:16972`
  - These are mostly representational; acceptable unless used to drive semantics.

## Checklist

- [ ] Remove ASDL-path dependence on `parse_legacy_word` (`src/mctash/runtime.py:4608`).
- [ ] Replace declare assignment flatten+regex with structured ASDL assignment IR (`src/mctash/runtime.py:3310`).
- [ ] Restrict `_argv_assignment_words` regex parser to non-ASDL fallback (`src/mctash/runtime.py:11921`).
- [ ] Introduce structured subscript refs in ASDL execution and reduce `_parse_subscripted_name` semantic usage (`src/mctash/runtime.py:11870`).
- [ ] Finish ASDL-native RHS expansion in declare/local/export/readonly lanes (`src/mctash/runtime.py:3973`, `src/mctash/runtime.py:13244`).
- [ ] Consolidate compound assignment parsing onto IR from ASDL (`src/mctash/runtime.py:12336`).
- [ ] Add guard: fail-fast debug mode if ASDL lane falls back to legacy reparse in targeted paths.

## Suggested Execution Order

1. Assignment IR completion for declare/local/export/readonly.
2. Subscript ref object adoption in ASDL execution.
3. Disable ASDL-path `parse_legacy_word` usage.
4. Fence regex parsers behind fallback-only gates.

## Success Criteria

- ASDL execution no longer requires `parse_legacy_word` for semantic expansion.
- Assignment/subscript semantics in ASDL path are driven by structured nodes/IR, not text regex reparsing.
- Remaining text parsing is explicitly labeled fallback-only or display-only.
