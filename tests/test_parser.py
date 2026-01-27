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
