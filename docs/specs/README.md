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

## Update policy

For syntax-affecting changes:

1. update grammar EBNF and lexer modes spec,
2. update ASDL mapping spec if node-shape/mapping changed,
3. add/adjust test evidence and checklist links.
