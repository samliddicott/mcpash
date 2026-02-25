# ASDL Coverage Report

Source: `research/parser/osh_syntax/frontend.syntax.asdl`

## word_part
- `YshArrayLiteral`: missing
- `InitializerLiteral`: missing
- `Literal`: implemented
- `EscapedLiteral`: missing
- `SingleQuoted`: implemented
- `DoubleQuoted`: implemented
- `SimpleVarSub`: implemented
- `BracedVarSub`: implemented
- `ZshVarSub`: missing
- `CommandSub`: implemented
- `TildeSub`: missing
- `ArithSub`: implemented
- `BracedTuple`: missing
- `BracedRange`: missing
- `BracedRangeDigit`: missing
- `ExtGlob`: missing
- `BashRegexGroup`: missing
- `Splice`: missing
- `ExprSub`: missing

Summary: implemented `7`, missing `12`.
Checklist links:
- `docs/grammar-production-checklist.md#word-level-grammar-sub-checklist`

## command
- `NoOp`: missing
- `Redirect`: implemented
- `Simple`: implemented
- `ExpandedAlias`: missing
- `Sentence`: implemented
- `ShAssignment`: implemented
- `ControlFlow`: implemented
- `Pipeline`: implemented
- `AndOr`: implemented
- `DoGroup`: missing
- `BraceGroup`: implemented
- `Subshell`: implemented
- `DParen`: missing
- `DBracket`: missing
- `ForEach`: implemented
- `ForExpr`: missing
- `WhileUntil`: implemented
- `If`: implemented
- `Case`: implemented
- `ShFunction`: implemented
- `TimeBlock`: missing
- `CommandList`: implemented
- `VarDecl`: missing
- `BareDecl`: missing
- `Mutation`: missing
- `Expr`: missing
- `Proc`: missing
- `Func`: missing
- `Retval`: missing

Summary: implemented `15`, missing `14`.
Checklist links:
- `docs/grammar-production-checklist.md#grammar-families`

## redir_param
- `Word`: implemented
- `HereWord`: missing
- `HereDoc`: implemented

Summary: implemented `2`, missing `1`.
Checklist links:
- `docs/grammar-production-checklist.md#grammar-families`
- `docs/grammar-production-checklist.md#word-level-grammar-sub-checklist`

## redir_loc
- `Fd`: implemented

Summary: implemented `1`, missing `0`.
Checklist links:
- `docs/grammar-production-checklist.md#grammar-families`

## assign_op
- `Equal`: missing
- `PlusEqual`: missing

Summary: implemented `0`, missing `2`.
Checklist links:
- `docs/grammar-production-checklist.md#grammar-families`

## arith_expr
- `EmptyZero`: missing
- `EmptyOne`: missing
- `VarSub`: missing
- `Word`: missing
- `UnaryAssign`: missing
- `BinaryAssign`: missing
- `Unary`: missing
- `Binary`: missing
- `TernaryOp`: missing

Summary: implemented `0`, missing `9`.
Checklist links:
- `docs/grammar-production-checklist.md#word-level-grammar-sub-checklist`

## bool_expr
- `WordTest`: missing
- `Binary`: missing
- `Unary`: missing
- `LogicalNot`: missing
- `LogicalAnd`: missing
- `LogicalOr`: missing

Summary: implemented `0`, missing `6`.
Checklist links:
- `docs/grammar-production-checklist.md#grammar-families`

## condition
- `Shell`: missing
- `YshExpr`: missing

Summary: implemented `0`, missing `2`.
Checklist links:
- `docs/grammar-production-checklist.md#grammar-families`

## case_arg
- `Word`: missing
- `YshExpr`: missing

Summary: implemented `0`, missing `2`.
Checklist links:
- `docs/grammar-production-checklist.md#grammar-families`

## pat
- `Else`: missing
- `Words`: missing
- `YshExprs`: missing
- `Eggex`: missing

Summary: implemented `0`, missing `4`.
Checklist links:
- `docs/grammar-production-checklist.md#grammar-families`

## for_iter
- `Args`: missing
- `Words`: missing
- `YshExpr`: missing

Summary: implemented `0`, missing `3`.
Checklist links:
- `docs/grammar-production-checklist.md#grammar-families`

## word
- `Operator`: missing
- `Compound`: implemented
- `BracedTree`: missing
- `String`: missing
- `Redir`: missing

Summary: implemented `1`, missing `4`.
Checklist links:
- `docs/grammar-production-checklist.md#word-level-grammar-sub-checklist`
