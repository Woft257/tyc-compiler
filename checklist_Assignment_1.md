# Checklist — Assignment 1 (Lexer + Parser)

## Mục tiêu
- Hoàn thành `TyC.g4` theo `tyc_specification.md` (Lexical + Syntax).
- Viết và chạy pass `test_lexer.py` + `test_parser.py`.
- Generate đủ file yêu cầu để nộp.

---

## 1) Setup & Build (1 lần)
- [x] Cài môi trường theo README (`python run.py check`, `python run.py setup`).
- [x] Build grammar để generate file: `python run.py build`.
- [x] Chạy test mẫu: `python run.py test-lexer`, `python run.py test-parser`.
### Trạng thái hiện tại
- [x] Lexer build được (đã chạy `python run.py build`).
- [x] `test_lexer.py` hiện chỉ là placeholder (1 test pass) — cần viết đủ test theo yêu cầu môn.

---

## 2) TyC.g4 — Lexer rules (theo Lexical Structure)

### 2.1 Whitespace & newline
- [x] Skip whitespace: space, tab, formfeed, carriage return, newline.

### 2.2 Comments
- [x] Line comment: `//` đến hết dòng (\n hoặc EOF) -> skip.
- [x] Block comment: `/*` ... `*/` -> skip.
- [x] Không nested (đảm bảo rule không tự ăn lồng nhau).

### 2.3 Identifiers & Keywords
- [x] `ID`: bắt đầu `[A-Za-z_]`, theo sau `[A-Za-z_0-9]*`.
- [x] Keywords tách riêng (không được lex thành `ID`):
  - [x] `auto` `break` `case` `continue` `default` `else`
  - [x] `float` `for` `if` `int` `return` `string`
  - [x] `struct` `switch` `void` `while`

### 2.4 Operators (ưu tiên token dài hơn)
- [x] `==` `!=` `<=` `>=` `++` `--` `&&` `||`
- [x] `+` `-` `*` `/` `%` `<` `>` `!` `=` `.`

### 2.5 Separators
- [x] `{` `}` `(` `)` `;` `,` `:`

### 2.6 Integer literal
- [x] Decimal digits: `0|[1-9][0-9]*` (hoặc `[0-9]+` nếu spec cho phép leading zero).
- [x] Quyết định thiết kế: dấu `-` là unary operator (khuyến nghị) hay gộp vào literal.

### 2.7 Float literal
- [x] Hỗ trợ: `0.0`, `3.14`, `1.23e4`, `5.67E-2`, `1.`, `.5`.
- [x] Quyết định thiết kế: dấu `-` là unary operator (khuyến nghị) hay gộp vào literal.

### 2.8 String literal + errors (quan trọng)
- [x] Escape hợp lệ: `\b \f \r \n \t \\\" \\\\`.
- [x] String hợp lệ: strip bỏ 2 dấu `"` ở đầu/cuối token.
- [x] Error detection order:
  - [x] `ILLEGAL_ESCAPE` (phát hiện trước)
  - [x] `UNCLOSE_STRING` (gặp \n/\r/EOF trước khi đóng `"`)
  - [x] `STRING_LIT` (hợp lệ)
- [x] Với `ILLEGAL_ESCAPE`/`UNCLOSE_STRING`: bỏ dấu `"` mở đầu trong lexeme báo lỗi.

### 2.9 Error token
- [x] `ERROR_TOKEN` cho ký tự không nhận diện (catch-all cuối lexer).

---

## 3) TyC.g4 — Parser rules (Syntax)

### 3.1 Program structure
- [x] Program gồm danh sách `struct` declarations và function declarations.

### 3.2 Declarations
- [x] Struct declaration.
- [x] Function declaration: return type + name + params + body.
- [x] Variable declaration (đặc biệt `auto`).

### 3.3 Statements
- [x] Block `{ ... }`.
- [x] If / else.
- [x] While.
- [x] For.
- [x] Switch / case / default.
- [x] Break / continue.
- [x] Return.
- [x] Expression statement / assignment statement.

### 3.4 Expressions + precedence (phải đúng)
- [x] Member access `.`
- [x] Unary: `!`, unary `+/-`, `++/--`.
- [x] `* / %`
- [x] `+ -`
- [x] `< <= > >=`
- [x] `== !=`
- [x] `&&`
- [x] `||`
- [x] Assignment `=` (thường right-assoc)

---

## 4) Tests

### 4.1 `test_lexer.py`
- [x] Keywords không bị lex thành `ID`.
- [x] `ID` edge cases: `_`, `_a9`, `a_b2`.
- [x] Operators ưu tiên token dài: `==` vs `=`; `<=` vs `<`; `++` vs `+`.
- [x] Separators.
- [x] Integer/float cases (đặc biệt `1.` và `.5`).
- [x] Comments bị skip.
- [x] Strings hợp lệ (strip quotes).
- [x] `ILLEGAL_ESCAPE` cases.
- [x] `UNCLOSE_STRING` cases (EOF, newline, carriage return).
- [x] `ERROR_TOKEN` cases.

### 4.2 `test_parser.py`
- [x] Program có struct + funcs.
- [x] Mỗi statement type có ít nhất 1 test.
- [x] Precedence tests (ví dụ `a+b*c`, `a==b||c==d`, `a.b.c`, unary chains).
- [x] Negative tests: syntax error đúng vị trí.

---

## 5) Submission checklist (bắt buộc đủ file)
- [ ] `TyC.g4`
- [ ] `test_lexer.py`
- [ ] `test_parser.py`
- [ ] `TyC.interp`
- [ ] `TyC.tokens`
- [ ] `TyCLexer.interp`
- [ ] `TyCLexer.py`
- [ ] `TyCLexer.tokens`
- [ ] `TyCParser.py`
- [ ] `TyCVisitor.py`

## Ghi nhớ khi chấm
- Hệ thống sẽ rebuild toàn bộ chỉ từ `TyC.g4`.
- Generated files nộp lên chỉ để “đủ bộ”, không phải nguồn chấm chính.

