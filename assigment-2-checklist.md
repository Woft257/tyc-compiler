# Assignment 2 - AST Generation Checklist

## Tổng quan
Assignment 2 yêu cầu chuyển đổi parse tree thành Abstract Syntax Tree (AST) sử dụng visitor pattern.

## 1. Nghiên cứu cấu trúc AST Node

### 1.1 Đọc và hiểu nodes.py
- [x] Đọc file [src/utils/nodes.py](src/utils/nodes.py)
- [x] Hiểu class hierarchy của các node:
  - **Base**: ASTNode, Type, Stmt, Expr, Literal, Decl
  - **Program**: Program
  - **Declarations**: StructDecl, MemberDecl, FuncDecl, Param
  - **Types**: IntType, FloatType, StringType, VoidType, StructType
  - **Statements**: BlockStmt, VarDecl, IfStmt, WhileStmt, ForStmt, SwitchStmt, CaseStmt, DefaultStmt, BreakStmt, ContinueStmt, ReturnStmt, ExprStmt
  - **Expressions**: BinaryOp, PrefixOp, PostfixOp, AssignExpr, MemberAccess, FuncCall, Identifier, StructLiteral
  - **Literals**: IntLiteral, FloatLiteral, StringLiteral

### 1.2 Hiểu Visitor Pattern
- [x] Đọc [src/utils/visitor.py](src/utils/visitor.py)
- [x] Hiểu ASTVisitor interface
- [x] Hiểu BaseVisitor class

---

## 2. Grammar (Đã hoàn thành từ Assignment 1)

### 2.1 Parser Rules đã có
- [x] `program: decl* EOF;`
- [x] `decl: structDecl | funcDecl;`
- [x] `funcDecl: type? ID LPAREN paramList? RPAREN blockStmt;`
- [x] `paramList: param (COMMA param)*;`
- [x] `param: type ID;`
- [x] `structDecl: STRUCT ID LBRACE fieldDecl* RBRACE SEMI;`
- [x] `fieldDecl: type ID SEMI;`
- [x] `type: INT | FLOAT | STRING | VOID | ID;`
- [x] `blockStmt: LBRACE (varDeclStmt | stmt)* RBRACE;`
- [x] `varDeclStmt: AUTO ID (ASSIGN expr)? SEMI | type ID (ASSIGN expr)? SEMI;`
- [x] `stmt: blockStmt | ifStmt | whileStmt | forStmt | switchStmt | BREAK SEMI | CONTINUE SEMI | returnStmt | expr SEMI;`
- [x] `ifStmt: IF LPAREN expr RPAREN stmt (ELSE stmt)?;`
- [x] `whileStmt: WHILE LPAREN expr RPAREN stmt;`
- [x] `forStmt: FOR LPAREN forInit? SEMI expr? SEMI forUpdate? RPAREN stmt;`
- [x] `forInit: varDeclFor | assignmentExpr;`
- [x] `varDeclFor: AUTO ID (ASSIGN expr)? | type ID (ASSIGN expr)?;`
- [x] `forUpdate: assignmentExpr | incDecExpr;`
- [x] `switchStmt: SWITCH LPAREN expr RPAREN LBRACE switchItem* RBRACE;`
- [x] `switchItem: CASE expr COLON (varDeclStmt | stmt)* | DEFAULT COLON (varDeclStmt | stmt)*;`
- [x] `returnStmt: RETURN expr? SEMI;`

### 2.2 Expression Rules (với precedence)
- [x] `expr: assignmentExpr;`
- [x] `assignmentExpr: logicalOrExpr (ASSIGN assignmentExpr)?;`
- [x] `logicalOrExpr: logicalAndExpr (OR logicalAndExpr)*;`
- [x] `logicalAndExpr: equalityExpr (AND equalityExpr)*;`
- [x] `equalityExpr: relationalExpr ((EQ | NEQ) relationalExpr)*;`
- [x] `relationalExpr: additiveExpr ((LT | LE | GT | GE) additiveExpr)*;`
- [x] `additiveExpr: multiplicativeExpr ((PLUS | MINUS) multiplicativeExpr)*;`
- [x] `multiplicativeExpr: unaryExpr ((MUL | DIV | MOD) unaryExpr)*;`
- [x] `unaryExpr: (INC | DEC) unaryExpr | (NOT | PLUS | MINUS) unaryExpr | postfixExpr;`
- [x] `postfixExpr: primaryExpr postfixSuffix*;`
- [x] `postfixSuffix: DOT ID | INC | DEC;`
- [x] `primaryExpr: ID callSuffix? | literal | LPAREN expr RPAREN;`
- [x] `callSuffix: LPAREN argList? RPAREN;`
- [x] `argList: expr (COMMA expr)*;`
- [x] `incDecExpr: (INC | DEC) primaryLValue | primaryLValue (INC | DEC);`
- [x] `primaryLValue: ID (DOT ID)*;`
- [x] `literal: INT_LIT | FLOAT_LIT | STRING_LIT;`

---

## 3. Build Project

- [ ] Chạy `python3 run.py build` để generate parser/visitor classes

---

## 4. Implement ASTGeneration Class

### 4.1 Cơ bản
- [ ] Tạo class ASTGeneration kế thừa từ TyCVisitor
- [ ] Override method `visitProgram` → return Program node
- [ ] Set line/column cho mỗi node

### 4.2 Type Nodes
- [ ] `visitType` → IntType() / FloatType() / StringType() / VoidType() / StructType(name)
  - Check token type để tạo node phù hợp

### 4.3 Declaration Nodes
- [ ] `visitDecl` → StructDecl hoặc FuncDecl (delegate)
- [ ] `visitStructDecl` → StructDecl(name, members)
- [ ] `visitFieldDecl` → MemberDecl(member_type, name)
- [ ] `visitFuncDecl` → FuncDecl(return_type, name, params, body)
  - return_type = None nếu là auto (type? trong grammar)
- [ ] `visitParamList` → List[Param]
- [ ] `visitParam` → Param(param_type, name)

### 4.4 Statement Nodes
- [ ] `visitBlockStmt` → BlockStmt(statements)
- [ ] `visitVarDeclStmt` → VarDecl(var_type, name, init_value)
  - var_type = None nếu là AUTO
- [ ] `visitIfStmt` → IfStmt(condition, then_stmt, else_stmt)
- [ ] `visitWhileStmt` → WhileStmt(condition, body)
- [ ] `visitForStmt` → ForStmt(init, condition, update, body)
- [ ] `visitForInit` → VarDecl hoặc AssignExpr
- [ ] `visitForUpdate` → AssignExpr hoặc PrefixOp/PostfixOp
- [ ] `visitSwitchStmt` → SwitchStmt(expr, cases, default_case)
- [ ] `visitSwitchItem` → CaseStmt hoặc DefaultStmt
- [ ] `visitReturnStmt` → ReturnStmt(expr)
- [ ] Xử lý `BREAK SEMI` → BreakStmt()
- [ ] Xử lý `CONTINUE SEMI` → ContinueStmt()
- [ ] `visitStmt` → delegate đến specific statement visitor

### 4.5 Expression Nodes

#### Literals
- [ ] `visitLiteral` → IntLiteral / FloatLiteral / StringLiteral
  - Parse giá trị từ token text

#### Binary Operations
- [ ] `visitLogicalOrExpr` → BinaryOp với '||'
- [ ] `visitLogicalAndExpr` → BinaryOp với '&&'
- [ ] `visitEqualityExpr` → BinaryOp với '==' hoặc '!='
- [ ] `visitRelationalExpr` → BinaryOp với '<', '>', '<=', '>='
- [ ] `visitAdditiveExpr` → BinaryOp với '+' hoặc '-'
- [ ] `visitMultiplicativeExpr` → BinaryOp với '*', '/', '%'

#### Unary Operations
- [ ] `visitUnaryExpr` → PrefixOp / PostfixOp / hoặc delegate đến postfixExpr
  - INC/DEC → PrefixOp
  - NOT/PLUS/MINUS → PrefixOp
  - postfixExpr → delegate

#### Assignment
- [ ] `visitAssignmentExpr` → AssignExpr hoặc delegate đến logicalOrExpr

#### Postfix/Function Call/Member Access
- [ ] `visitPostfixExpr` → xử lý postfixSuffix*
  - DOT ID → MemberAccess
  - INC/DEC → PostfixOp
  - callSuffix → FuncCall
- [ ] `visitCallSuffix` → xử lý function call
- [ ] `visitArgList` → List[Expr]
- [ ] `visitPrimaryExpr` → Identifier / literal / hoặc delegate đến expr
- [ ] `visitIncDecExpr` → PrefixOp hoặc PostfixOp
- [ ] `visitPrimaryLValue` → Identifier hoặc MemberAccess chain

### 4.6 Program Node
- [ ] `visitProgram` → Program(decls)
  - Collect all decls (structDecl + funcDecl) vào list
  - Handle empty program (decl*)

---

## 5. Viết Test Cases

### 5.1 Test file structure
- [ ] Tạo/hoàn thiện [tests/test_ast_gen.py](tests/test_ast_gen.py)

### 5.2 Test Types
- [ ] Int type
- [ ] Float type
- [ ] String type
- [ ] Void type
- [ ] Struct type (user-defined)

### 5.3 Test Declarations
- [ ] Empty program
- [ ] Single function
- [ ] Multiple functions
- [ ] Struct declaration
- [ ] Function với parameters
- [ ] Function với no parameters
- [ ] Function với void return
- [ ] Function với auto return (không có type)

### 5.4 Test Statements
- [ ] Block statement
- [ ] Variable declaration (với/without init)
- [ ] Auto variable declaration
- [ ] If statement (without else)
- [ ] If statement (with else)
- [ ] Nested if
- [ ] While loop
- [ ] For loop (all variations)
- [ ] For loop với empty parts
- [ ] Switch với cases
- [ ] Switch với default
- [ ] Switch với cases and default
- [ ] Break statement
- [ ] Continue statement
- [ ] Return statement (với value)
- [ ] Return statement (without value)
- [ ] Expression statement
- [ ] VarDecl trong for loop

### 5.5 Test Expressions
- [ ] Integer literal
- [ ] Float literal
- [ ] String literal
- [ ] Binary operators (+, -, *, /, %)
- [ ] Comparison operators (==, !=, <, >, <=, >=)
- [ ] Logical operators (&&, ||)
- [ ] Prefix operators (++, --, +, -, !)
- [ ] Postfix operators (++, --)
- [ ] Assignment expression
- [ ] Function call (no args)
- [ ] Function call (with args)
- [ ] Member access
- [ ] Nested member access (.a.b.c)
- [ ] Complex expressions với precedence
- [ ] Parenthesized expressions

### 5.6 Test Edge Cases
- [ ] Nested structures
- [ ] Multiple statements in block
- [ ] Empty function body
- [ ] Complex nested expressions
- [ ] Empty switch cases

---

## 6. Chạy Tests

### 6.1 Build project
- [ ] Chạy `python3 run.py build` để generate parser

### 6.2 Chạy AST tests
- [ ] Chạy `python3 run.py test-ast`
- [ ] Đảm bảo tất cả tests pass

---

## Mapping Grammar Rules to AST Nodes

| Grammar Rule | AST Node |
|--------------|----------|
| program | Program |
| funcDecl | FuncDecl |
| structDecl | StructDecl |
| fieldDecl | MemberDecl |
| param | Param |
| type | IntType/FloatType/StringType/VoidType/StructType |
| blockStmt | BlockStmt |
| varDeclStmt | VarDecl |
| ifStmt | IfStmt |
| whileStmt | WhileStmt |
| forStmt | ForStmt |
| switchStmt | SwitchStmt |
| switchItem (case) | CaseStmt |
| switchItem (default) | DefaultStmt |
| returnStmt | ReturnStmt |
| BREAK | BreakStmt |
| CONTINUE | ContinueStmt |
| literal | IntLiteral/FloatLiteral/StringLiteral |
| binary ops | BinaryOp |
| unary ops | PrefixOp/PostfixOp |
| assignment | AssignExpr |
| member access | MemberAccess |
| function call | FuncCall |
| identifier | Identifier |

---

## Tham khảo

- [TyC Specification](tyc_specification.md)
- [src/utils/nodes.py](src/utils/nodes.py) - Tất cả AST node classes
- [src/grammar/TyC.g4](src/grammar/TyC.g4) - Grammar file
- [src/astgen/ast_generation.py](src/astgen/ast_generation.py) - File cần implement
- [tests/test_ast_gen.py](tests/test_ast_gen.py) - Test file
