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

## command
- `NoOp`: missing
- `Redirect`: implemented
- `Simple`: implemented
- `ExpandedAlias`: missing
- `Sentence`: missing
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

## redir_param
- `Word`: implemented
- `HereWord`: missing
- `HereDoc`: implemented

## redir_loc
- `Fd`: implemented

## assign_op
- `Equal`: missing
- `PlusEqual`: missing

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

## bool_expr
- `WordTest`: missing
- `Binary`: missing
- `Unary`: missing
- `LogicalNot`: missing
- `LogicalAnd`: missing
- `LogicalOr`: missing

## condition
- `Shell`: missing
- `YshExpr`: missing

## case_arg
- `Word`: missing
- `YshExpr`: missing

## pat
- `Else`: missing
- `Words`: missing
- `YshExprs`: missing
- `Eggex`: missing

## for_iter
- `Args`: missing
- `Words`: missing
- `YshExpr`: missing

## word
- `Operator`: missing
- `Compound`: implemented
- `BracedTree`: missing
- `String`: missing
- `Redir`: missing
