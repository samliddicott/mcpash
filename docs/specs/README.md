# Specs Index

This directory contains first-class language specifications for mctash.

## Canonical specs

- Grammar: `docs/specs/mctash-grammar.ebnf`
- Lexer/context rules: `docs/specs/mctash-lexer-modes.md`
- Grammar-to-ASHL mapping: `docs/specs/mctash-grammar-asdl-map.md`

## Supporting coverage and migration docs

- POSIX grammar checklist: `docs/grammar-production-checklist.md`
- OSH ASDL adoption/checklist: `docs/osh-asdl-checklist.md`
- POSIX trace tables: `docs/posix-shall-trace.md`, `docs/posix-2.9-2.10-trace.md`
- Edge corpus report: `docs/reports/param-brace-quote-edge-matrix-latest.md`
- Feature index (cross-source grouped requirements + test/status links): `docs/specs/feature-index.md`, `docs/specs/feature-index.tsv`
- Feature gap board (feature-grouped non-covered backlog): `docs/specs/feature-gap-board.md`, `docs/specs/feature-gap-board.tsv`

## Update policy

For syntax-affecting changes:

1. update grammar EBNF and lexer modes spec,
2. update ASDL mapping spec if node-shape/mapping changed,
3. add/adjust test evidence and checklist links.

For requirement/matrix-affecting changes:

1. refresh the feature index via `python3 scripts/generate_feature_index.py`,
2. use the feature topic sections as the canonical cross-source implementation/design view.
