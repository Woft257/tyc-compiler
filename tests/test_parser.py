"""
Parser test cases for TyC compiler
TODO: Implement 100 test cases for parser
"""

import pytest
from tests.utils import Parser


def _parse(source: str) -> str:
    return Parser(source).parse()


def _assert_parse_ok(source: str):
    assert _parse(source) == "success"


def _assert_parse_fail(source: str):
    assert _parse(source) != "success"


def test_parser_empty_program():
    _assert_parse_ok("")


def test_parser_struct_decl():
    _assert_parse_ok("struct Point { int x; float y; }; void main() { }")


def test_parser_func_decl_typed_and_inferred_return():
    _assert_parse_ok("int add(int x, int y) { return x + y; }")
    _assert_parse_ok("add(int x, int y) { return x + y; }")


def test_parser_var_decl_auto_and_typed():
    _assert_parse_ok("void main() { auto x = 1; auto y; int a; float b = 1.0; string s = \"hi\"; }")


def test_parser_block_and_expr_stmt():
    _assert_parse_ok("void main() { { auto x = 1; } x + 1; }")


def test_parser_if_else_dangling_else_binds_inner_if():
    _assert_parse_ok("void main() { if (x) if (y) a = 1; else a = 2; }")


def test_parser_while_stmt():
    _assert_parse_ok("void main() { while (x) { ++x; } }")


def test_parser_for_stmt_variants():
    _assert_parse_ok("void main() { for (; ; ) { } }")
    _assert_parse_ok("void main() { for (auto i = 0; i < 10; ++i) { } }")
    _assert_parse_ok("void main() { for (i = 0; ; i = i + 1) { } }")


def test_parser_switch_stmt_variants():
    _assert_parse_ok("void main() { switch (x) { } }")
    _assert_parse_ok(
        "void main() { switch (x) { case 1: a = 1; break; case (2+3): a = 2; default: a = 0; } }"
    )


def test_parser_break_continue_return():
    _assert_parse_ok("void main() { while (x) { if (y) break; else continue; } return; }")
    _assert_parse_ok("int f(int x) { return x; }")


def test_parser_call_and_member_access():
    _assert_parse_ok("void main() { foo(); foo(1, 2+3); a.b.c = 1; }")


def test_parser_expr_precedence_samples():
    _assert_parse_ok("void main() { x = y = z = 10; }")
    _assert_parse_ok("void main() { a + b * c; }")
    _assert_parse_ok("void main() { a == b || c == d && e; }")
    _assert_parse_ok("void main() { ++x; x++; --x; x--; }")


def test_parser_negative_missing_semi():
    _assert_parse_fail("void main() { auto x = 1 }")


def test_parser_negative_bad_parens():
    _assert_parse_fail("void main() { if (x { } }")


def test_parser_negative_switch_missing_colon():
    _assert_parse_fail("void main() { switch (x) { case 1 a = 1; } }")


@pytest.mark.parametrize(
    "source",
    [
        # Program / decl coverage
        "void main() { }",
        "struct S { int x; }; void main() { }",
        "struct S { int x; float y; string s; }; void main() { }",
        "int f(int x) { return x; } void main() { }",
        "f(int x) { return x + 1; } void main() { }",
        "void main() { auto x; auto y = 1; int a; float b; string s; }",
        # Statement coverage
        "void main() { { { auto x = 1; } } }",
        "void main() { if (x) { } }",
        "void main() { if (x) { } else { } }",
        "void main() { while (x) { x = x + 1; } }",
        "void main() { for (; ; ) { } }",
        "void main() { for (auto i = 0; i < 10; ++i) { } }",
        "void main() { for (i = 0; i < 10; i = i + 1) { } }",
        "void main() { switch (x) { } }",
        "void main() { switch (x) { case 1: break; } }",
        "void main() { switch (x) { default: break; } }",
        "void main() { switch (x) { case 1: a = 1; break; case 2: a = 2; break; } }",
        "void main() { return; }",
        "int g(int x) { return x + 1; }",
        "void main() { foo(); foo(1,2,3); }",
    ],
)
def test_parser_ok_param(source):
    _assert_parse_ok(source)


@pytest.mark.parametrize(
    "expr_stmt",
    [
        # Precedence: * / % over + -
        "a + b * c;",
        "a * b + c;",
        "a + b * c / d - e;",
        # Relational vs equality
        "a < b == c;",
        "a == b < c;",
        "a <= b != c >= d;",
        # Logical
        "a && b || c;",
        "a || b && c;",
        "!a && b;",
        # Assignment right assoc
        "x = y = z = 10;",
        # Member access and postfix/prefix inc-dec
        "a.b.c = 1;",
        "x++;",
        "++x;",
        "--x;",
        "x--;",
        # Mixed
        "a.b++;",
        "(a.b).c--;",
        "a.b = c.d;",
    ],
)
def test_parser_expr_stmt_precedence_param(expr_stmt):
    _assert_parse_ok(f"void main() {{ {expr_stmt} }}")


@pytest.mark.parametrize(
    "source",
    [
        # Negative syntax cases
        "void main() { if (x) { } else }",
        "void main() { for (auto i = 0 i < 10; ++i) { } }",
        "void main() { switch (x) { case 1 break; } }",
        "void main() { switch (x) { case 1 break; } }",
        "void main() { struct S { int x; } }",
        "int f(int x,) { return x; }",
    ],
)
def test_parser_negative_param(source):
    _assert_parse_fail(source)

@pytest.mark.parametrize(
    "expr_stmt",
    [
        # Extra precedence/associativity mixes
        "a + b + c;",
        "a * b * c;",
        "a / b * c;",
        "a % b % c;",
        "a < b < c;",
        "a == b == c;",
        "a && b && c;",
        "a || b || c;",
        "a && b || c && d;",
        "a || b && c || d;",
        "!(a && b) || c;",
        "(a + b) * (c - d);",
        "a.b.c.d = e.f;",
        "x = (y = 1) + 2;",
        "x = y + (z = 3);",
        "++a.b;",
        "a.b--;",
        "a.b++;",
    ],
)
def test_parser_more_expr_precedence(expr_stmt):
    _assert_parse_ok(f"void main() {{ {expr_stmt} }}")


@pytest.mark.parametrize(
    "source",
    [
        # Many statement variants (nested)
        "void main() { if (x) while (y) { for (;;){ break; } } }",
        "void main() { for (auto i = 0; ; ) { if (i) break; i = i + 1; } }",
        "void main() { switch (x) { case 1: case 2: a = 1; break; default: a = 0; } }",
        "void main() { switch (x) { default: } }",
        "void main() { { auto x; { x = 1; } } }",
        "int f(int x) { if (x) return x; return 0; }",
        "f(int x) { if (x) return x; return x + 1; }",
    ],
)
def test_parser_more_stmt_variants(source):
    _assert_parse_ok(source)


@pytest.mark.parametrize(
    "source",
    [
        # Additional negative syntax
        "void main( { }",  # missing ')'
        "void main() { for (auto i = 0; i < 10 ++i) { } }",  # missing ';'
        "void main() { switch (x) { case : break; } }",  # missing expr
        "void main() { return return; }",
        "struct S { int x; }; struct { int y; };",  # missing struct name
        "int f(int x int y) { }",  # missing comma
    ],
)
def test_parser_more_negative(source):
    _assert_parse_fail(source)
@pytest.mark.parametrize(
    "source",
    [
        # More program/decl variants
        "struct A { int x; }; struct B { float y; }; void main() { }",
        "void main() { auto x; x = 1; x = x + 2; }",
        "void main() { switch (x) { case (1+2): break; case +3: break; case -4: break; } }",
        "void main() { for (auto i = 0; i < 10; i++) { } }",
        "void main() { for (i = 0; i < 10; --i) { } }",
        "void main() { a = (b = (c = 1)); }",
        "void main() { (a + b) * c; }",
        "void main() { if (x) { if (y) { } } else { } }",
        "void main() { while (x) { for (; x; ) { x = x - 1; } } }",
        "int h(int x) { return (x = x + 1); }",
        "void main() { a = b = c = d = 1; }",
    ],
)
def test_parser_more_ok_param2(source):
    _assert_parse_ok(source)


@pytest.mark.parametrize(
    "source",
    [
        # More negatives
        "void main() { for (auto i = 0; i < 10; ) ) { } }",
        "void main() { switch (x) { case 1:: break; } }",
        "void main() { if x) { } }",
        "void main() { while ( ) { } }",
        "void main() { return 1 2; }",
        "void main() { a = ; }",
        "void main() { foo(,1); }",
        "void main() { struct S { int x; }; }",
        "struct S { int x; }; void main( { }",
        "int f( int x int y ) { }",
    ],
)
def test_parser_more_negative_param2(source):
    _assert_parse_fail(source)
