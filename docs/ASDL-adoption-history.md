# OSH ASDL Adoption History

Date: 2026-03-02

## Introduction

ASDL (Abstract Syntax Description Language) is a schema language for describing the shape of syntax trees and related semantic nodes. In practice, it gives a project:

- a stable node vocabulary,
- explicit fields and variants,
- a contract between parser, mapper, and runtime,
- better change control than ad-hoc tree structures.

In this project, we started with custom shell tree structures and a custom ASDL path (`src/syntax/pybash.asdl`) while building the PoC parser/runtime. We then migrated toward OSH ASDL as the canonical syntax contract (`src/syntax/osh/*.asdl`). The expected benefits of this migration are:

- clearer long-term parser/runtime architecture,
- stronger compatibility with OSH-style syntax modeling,
- better traceability from grammar requirements to concrete node types,
- fewer semantic drifts caused by implicit or lossy intermediate structures.

This document records how that migration happened, why each stage mattered, and how ASDL is used now.

## Timeline

### 2026-02-21: Syntax schema groundwork (`3de62e8`, `e558423`)

Early syntax-schema work established the project pattern of structured syntax artifacts rather than raw token streams flowing directly into runtime logic.

Intent:

- prepare the codebase for explicit tree contracts.

Benefit:

- reduced coupling between parser details and execution behavior, making later ASDL adoption feasible.

### 2026-02-21: OSH ASDL import, licensing, and provenance (`78c9668`, `39d4263`, `8d22f09`)

OSH syntax assets and licensing/provenance documentation were added under `src/syntax/osh/` and research tracking.

Intent:

- adopt a known shell AST schema source with explicit provenance and license records.

Benefit:

- legal and technical clarity for reusing OSH schema definitions as project foundations.

### 2026-02-21: LST -> OSH-shaped ASDL mapping and coverage start (`bac469e`, `1c4eeae`, `92cb81c`)

Parser output matured into LST nodes, and mapping functions translated LST into OSH-shaped ASDL dictionaries. Coverage tracking started for mapped vs unmapped spaces.

Intent:

- put a formal boundary between parsing and execution through an ASDL-shaped intermediate.

Benefit:

- systematic visibility into what grammar/command surfaces were truly represented.

### 2026-02-23: OSH ASDL made canonical with strict mapping (`80eba87`)

ASDL mapping shifted from optional/reference to strict execution boundary enforcement.

Intent:

- prevent silent fallback behavior when mapping is incomplete.

Benefit:

- mapping defects fail early, producing safer incremental evolution.

### 2026-02-23 to 2026-02-25: Round-trip hardening and ASDL slice closure (`f8ff795`, `2712869`, `8e94e03`, `fcdadc5`, `145975a`, `12f9e8d`, `890e200`)

Word roundtrip, arithmetic node shapes, alias/glob/var behavior, and loop-body mapping (`command.DoGroup`) were tightened. Test/docs slices tracked progress.

Intent:

- make ASDL mapping behaviorally faithful for ash-relevant workloads.

Benefit:

- higher confidence that mapped nodes preserve intended shell semantics in tested paths.

### 2026-02-28: POSIX requirement trace linked to ASDL anchors (`e670b4f`, `74f37dd`)

POSIX 2.9/2.10 trace docs explicitly linked grammar/command requirements to ASDL node families and executable evidence.

Intent:

- ground ASDL adoption in normative shell behavior, not just internal structure.

Benefit:

- stronger auditability from standard requirement -> test -> mapped node.

### 2026-03-02: Runtime migration onto ASDL execution path (`b1c355c`, `5bf2009`, `038ed51`, `6e7e5e1`, `e80be0f`)

ASDL execution entry points were added and wired through main/eval paths. Core list/and-or/pipeline flow and key compound commands moved to direct ASDL-driven execution. `osh_adapter` dependency was removed from the main/runtime execution path. Regressions were added, and a real loop-control parity issue was fixed.

Intent:

- stop treating ASDL as a passive mapping artifact and execute it as the active runtime contract.

Benefit:

- major reduction of translation layers in the hot execution path, with tighter semantics control and clearer future migration to fully native OSH nodes.

## How ASDL Is Used Now

### Parse contract

- Parser produces LST (`src/mctash/lst_nodes.py`).
- LST maps to OSH-shaped ASDL dictionaries (`src/mctash/asdl_map.py`).
- Mapping is strict in execution call sites (`lst_list_item_to_asdl(..., strict=True)`), blocking unmapped `command.NoOp` from silently executing.

### Runtime usage

Runtime executes ASDL list items directly via:

- `Runtime._exec_asdl_list_item()`
- `Runtime._exec_asdl_and_or()`
- `Runtime._exec_asdl_pipeline()`
- `Runtime._exec_asdl_command()`

Primary call sites:

- `src/mctash/main.py`
- `src/mctash/runtime.py` (`_eval_source` paths)

### What is still transitional

- Internal AST dataclasses in `src/mctash/ast_nodes.py` are still used for parts of execution compatibility.
- Some ASDL command forms still convert to internal command nodes for reuse of mature executor logic.
- Word expansion is still partly text-roundtrip based, not fully native ASDL word-part evaluation end-to-end.

## ASDL Sources and Licensing

- OSH ASDL inputs:
  - `src/syntax/osh/syntax.asdl`
  - `src/syntax/osh/types.asdl`
  - `src/syntax/osh/runtime.asdl`
  - `src/syntax/osh/value.asdl`
- Licensing/provenance docs:
  - `src/syntax/osh/LICENSE.txt`
  - `src/syntax/README.md`

## Related Tracking Docs

- POSIX/ASDL alignment:
  - `docs/posix-shall-trace.md`
  - `docs/posix-2.9-2.10-trace.md`
- Grammar closure:
  - `docs/grammar-production-checklist.md`
- ASDL coverage/slices:
  - `docs/asdl-backlog-slices.md`
  - `research/parser/asdl_coverage_report.md`

## Remaining ASDL Adoption Work

1. Complete direct ASDL command execution for all command forms without compatibility fallbacks.
2. Replace text-based word reparse paths with native ASDL word-part execution.
3. Reduce/remove reliance on internal AST dataclasses where ASDL-native structures can be executed directly.
4. Continue tying POSIX + BusyBox/Oil evidence to node-level ASDL coverage as migration closes.
