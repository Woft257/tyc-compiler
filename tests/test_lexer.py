"""
Lexer test cases for TyC compiler
TODO: Implement 100 test cases for lexer
"""

import pytest
from tests.utils import Tokenizer


def _lex(source: str) -> str:
    return Tokenizer(source).get_tokens_as_string()


def _assert_lex(source: str, expected: str):
    assert _lex(source) == expected


def test_lexer_keywords_not_id():
    _assert_lex(
        "auto break case continue default else float for if int return string struct switch void while",
        "AUTO,auto,BREAK,break,CASE,case,CONTINUE,continue,DEFAULT,default,ELSE,else,FLOAT,float,FOR,for,IF,if,INT,int,RETURN,return,STRING,string,STRUCT,struct,SWITCH,switch,VOID,void,WHILE,while,EOF",
    )


def test_lexer_keywords_vs_id_boundaries():
    _assert_lex("auto1 _auto auto_", "ID,auto1,ID,_auto,ID,auto_,EOF")


def test_lexer_whitespace_variants():
    _assert_lex("auto\t\nint\r\nstring\fvoid", "AUTO,auto,INT,int,STRING,string,VOID,void,EOF")


def test_lexer_id_basic():
    _assert_lex("_ _a9 a_b2", "ID,_,ID,_a9,ID,a_b2,EOF")


def test_lexer_ops_longer_match_first():
    _assert_lex(
        "== = <= < >= > != ++ + -- - && ||",
        "EQ,==,ASSIGN,=,LE,<=,LT,<,GE,>=,GT,>,NEQ,!=,INC,++,PLUS,+,DEC,--,MINUS,-,AND,&&,OR,||,EOF",
    )


def test_lexer_error_char_operators():
    with pytest.raises(Exception) as e:
        _lex("&")
    assert str(e.value) == "Error Token &"

    with pytest.raises(Exception) as e:
        _lex("|")
    assert str(e.value) == "Error Token |"


def test_lexer_separators():
    _assert_lex("{ } ( ) ; , :", "LBRACE,{,RBRACE,},LPAREN,(,RPAREN,),SEMI,;,COMMA,,,COLON,:,EOF")


def test_lexer_int_float_literals():
    _assert_lex(
        "0 100 1. .5 3.14 1e3 5.67E-2",
        "INT_LIT,0,INT_LIT,100,FLOAT_LIT,1.,FLOAT_LIT,.5,FLOAT_LIT,3.14,FLOAT_LIT,1e3,FLOAT_LIT,5.67E-2,EOF",
    )


def test_lexer_float_variants_more():
    _assert_lex(
        "0.0 00.1 10e0 10E+0 10E-0",
        "FLOAT_LIT,0.0,FLOAT_LIT,00.1,FLOAT_LIT,10e0,FLOAT_LIT,10E+0,FLOAT_LIT,10E-0,EOF",
    )


def test_lexer_comments_skipped():
    _assert_lex(
        "auto x = 5; // cmt\n/* block\ncomment */ int y;",
        "AUTO,auto,ID,x,ASSIGN,=,INT_LIT,5,SEMI,;,INT,int,ID,y,SEMI,;,EOF",
    )


def test_lexer_block_comment_not_nested_behavior():
    _assert_lex(
        "/* outer /* inner */ still outer */ auto x;",
        "ID,still,ID,outer,MUL,*,DIV,/,AUTO,auto,ID,x,SEMI,;,EOF",
    )


def test_lexer_string_empty():
    _assert_lex('""', "STRING_LIT,,EOF")


def test_lexer_string_valid_strips_quotes():
    _assert_lex('"abc"', 'STRING_LIT,abc,EOF')


def test_lexer_illegal_escape():
    with pytest.raises(Exception) as e:
        _lex('"Hello \\a World"')
    assert str(e.value) == "Illegal Escape In String: Hello \\a"


def test_lexer_unclose_string_newline():
    with pytest.raises(Exception) as e:
        _lex('"abc\n')
    assert str(e.value) == "Unclosed String: abc"


def test_lexer_unclose_string_carriage_return():
    with pytest.raises(Exception) as e:
        _lex('"abc\r')
    assert str(e.value) == "Unclosed String: abc"


def test_lexer_unclose_string_eof():
    with pytest.raises(Exception) as e:
        _lex('"abc')
    assert str(e.value) == "Unclosed String: abc"


def test_lexer_error_char():
    with pytest.raises(Exception) as e:
        _lex("$")
    assert str(e.value) == "Error Token $"
@pytest.mark.parametrize(
    "source,expected",
    [
        ("x", "ID,x,EOF"),
        ("_", "ID,_,EOF"),
        ("_9", "ID,_9,EOF"),
        ("a9_", "ID,a9_,EOF"),
        ("A_B_0", "ID,A_B_0,EOF"),
        ("auto", "AUTO,auto,EOF"),
        ("Auto", "ID,Auto,EOF"),
        ("while1", "ID,while1,EOF"),
    ],
)
def test_lexer_ids_and_keywords_param(source, expected):
    _assert_lex(source, expected)


@pytest.mark.parametrize(
    "source,expected",
    [
        ("1", "INT_LIT,1,EOF"),
        ("01", "INT_LIT,01,EOF"),
        ("1.", "FLOAT_LIT,1.,EOF"),
        (".1", "FLOAT_LIT,.1,EOF"),
        ("1.0", "FLOAT_LIT,1.0,EOF"),
        ("1e0", "FLOAT_LIT,1e0,EOF"),
        ("1E+0", "FLOAT_LIT,1E+0,EOF"),
        ("1E-0", "FLOAT_LIT,1E-0,EOF"),
        ("12.34e56", "FLOAT_LIT,12.34e56,EOF"),
        ("12.34E-56", "FLOAT_LIT,12.34E-56,EOF"),
    ],
)
def test_lexer_number_param(source, expected):
    _assert_lex(source, expected)


@pytest.mark.parametrize(
    "source,expected",
    [
        ("+ - * / %", "PLUS,+,MINUS,-,MUL,*,DIV,/,MOD,%,EOF"),
        ("< <= > >= == !=", "LT,<,LE,<=,GT,>,GE,>=,EQ,==,NEQ,!=,EOF"),
        ("! = .", "NOT,!,ASSIGN,=,DOT,.,EOF"),
        ("++ --", "INC,++,DEC,--,EOF"),
        ("&& ||", "AND,&&,OR,||,EOF"),
    ],
)
def test_lexer_ops_param(source, expected):
    _assert_lex(source, expected)


@pytest.mark.parametrize(
    "source,expected",
    [
        ("{}();,:", "LBRACE,{,RBRACE,},LPAREN,(,RPAREN,),SEMI,;,COMMA,,,COLON,:,EOF"),
        ("{;}()", "LBRACE,{,SEMI,;,RBRACE,},LPAREN,(,RPAREN,),EOF"),
    ],
)
def test_lexer_separators_param(source, expected):
    _assert_lex(source, expected)


@pytest.mark.parametrize(
    "source,expected",
    [
        ("//x\na", "ID,a,EOF"),
        ("/*x*/a", "ID,a,EOF"),
        ("/*x\n*/a", "ID,a,EOF"),
        ("a/*x*/b", "ID,a,ID,b,EOF"),
    ],
)
def test_lexer_comments_param(source, expected):
    _assert_lex(source, expected)


@pytest.mark.parametrize(
    "source,expected",
    [
        ('"a"', "STRING_LIT,a,EOF"),
        ('""', "STRING_LIT,,EOF"),
        ('"a b"', "STRING_LIT,a b,EOF"),
        ('"a\\t"', "STRING_LIT,a\\t,EOF"),
        ('"a\\n"', "STRING_LIT,a\\n,EOF"),
        ('"\\""', "STRING_LIT,\\\",EOF"),
        ('"\\\\"', "STRING_LIT,\\\\,EOF"),
    ],
)
def test_lexer_string_valid_param(source, expected):
    _assert_lex(source, expected)


@pytest.mark.parametrize(
    "source,err",
    [
        ('"a\\a"', "Illegal Escape In String: a\\a"),
        ('"\\q"', "Illegal Escape In String: \\q"),
    ],
)
def test_lexer_string_illegal_escape_param(source, err):
    with pytest.raises(Exception) as e:
        _lex(source)
    assert str(e.value) == err


@pytest.mark.parametrize(
    "source,err",
    [
        ('"a\n', "Unclosed String: a"),
        ('"a\r', "Unclosed String: a"),
        ('"a', "Unclosed String: a"),
    ],
)
def test_lexer_string_unclose_param(source, err):
    with pytest.raises(Exception) as e:
        _lex(source)
    assert str(e.value) == err


@pytest.mark.parametrize(
    "ch",
    [
        "$",
        "@",
        "#",
        "^",
    ],
)
def test_lexer_error_char_param(ch):
    with pytest.raises(Exception) as e:
        _lex(ch)
    assert str(e.value) == f"Error Token {ch}"

@pytest.mark.parametrize(
    "source,expected",
    [
        # More numeric edge cases
        ("0.", "FLOAT_LIT,0.,EOF"),
        (".0", "FLOAT_LIT,.0,EOF"),
        ("0e0", "FLOAT_LIT,0e0,EOF"),
        ("0E-10", "FLOAT_LIT,0E-10,EOF"),
        ("999999.0e+1", "FLOAT_LIT,999999.0e+1,EOF"),
        ("123456789", "INT_LIT,123456789,EOF"),
        # Mixed sequences
        ("1 2.0 3e4 .5 6.", "INT_LIT,1,FLOAT_LIT,2.0,FLOAT_LIT,3e4,FLOAT_LIT,.5,FLOAT_LIT,6.,EOF"),
    ],
)
def test_lexer_more_numbers(source, expected):
    _assert_lex(source, expected)


@pytest.mark.parametrize(
    "source,expected",
    [
        # Comment interactions
        ("a//b\nc", "ID,a,ID,c,EOF"),
        ("a/*b*/c", "ID,a,ID,c,EOF"),
        ("a/*b\n//c\n*/d", "ID,a,ID,d,EOF"),
        ("//only\n", "EOF"),
        # Whitespace around tokens
        ("\n\t auto \r\n x \f = \t 1 ; ", "AUTO,auto,ID,x,ASSIGN,=,INT_LIT,1,SEMI,;,EOF"),
    ],
)
def test_lexer_more_comments_whitespace(source, expected):
    _assert_lex(source, expected)


@pytest.mark.parametrize(
    "source,expected",
    [
        # Strings with valid escapes
        ('"\\b"', "STRING_LIT,\\b,EOF"),
        ('"\\f"', "STRING_LIT,\\f,EOF"),
        ('"\\r"', "STRING_LIT,\\r,EOF"),
        ('"\\n"', "STRING_LIT,\\n,EOF"),
        ('"\\t"', "STRING_LIT,\\t,EOF"),
        ('"\\\\"', "STRING_LIT,\\\\,EOF"),
        ('"a\\tb"', "STRING_LIT,a\\tb,EOF"),
        ('"a\\nb"', "STRING_LIT,a\\nb,EOF"),
        ('"a\\rb"', "STRING_LIT,a\\rb,EOF"),
        ('"a\\bb"', "STRING_LIT,a\\bb,EOF"),
        ('"a\\fb"', "STRING_LIT,a\\fb,EOF"),
    ],
)
def test_lexer_more_valid_escapes(source, expected):
    _assert_lex(source, expected)


@pytest.mark.parametrize(
    "source,err",
    [
        # Illegal escapes
        ('"a\\c"', "Illegal Escape In String: a\\c"),
        ('"a\\0"', "Illegal Escape In String: a\\0"),
        ('"a\\x"', "Illegal Escape In String: a\\x"),
        ('"a\\u"', "Illegal Escape In String: a\\u"),
        ('"a\\/"', "Illegal Escape In String: a\\/"),
        ('"\\?"', "Illegal Escape In String: \\?"),
    ],
)
def test_lexer_more_illegal_escapes(source, err):
    with pytest.raises(Exception) as e:
        _lex(source)
    assert str(e.value) == err


@pytest.mark.parametrize(
    "source,err",
    [
        # Unclosed strings (newline, carriage return, EOF)
        ('"ab\n', "Unclosed String: ab"),
        ('"ab\r', "Unclosed String: ab"),
        ('"ab', "Unclosed String: ab"),
        ('"\\\\\n', "Unclosed String: \\\\"),
    ],
)
def test_lexer_more_unclosed_strings(source, err):
    with pytest.raises(Exception) as e:
        _lex(source)
    assert str(e.value) == err


@pytest.mark.parametrize(
    "src,err",
    [
        ("`", "Error Token `"),
        ("~", "Error Token ~"),
        ("?", "Error Token ?"),
        ("'", "Error Token '"),
        ("\\", "Error Token \\"),
        ("\u0007", "Error Token \u0007"),
    ],
)
def test_lexer_more_error_chars(src, err):
    with pytest.raises(Exception) as e:
        _lex(src)
    assert str(e.value) == err


@pytest.mark.parametrize(
    "source,expected",
    [
        # Complex token mix
        (
            "struct S { int x; }; void main() { auto a = 1; a = a + 2 * 3; }",
            "STRUCT,struct,ID,S,LBRACE,{,INT,int,ID,x,SEMI,;,RBRACE,},SEMI,;,VOID,void,ID,main,LPAREN,(,RPAREN,),LBRACE,{,AUTO,auto,ID,a,ASSIGN,=,INT_LIT,1,SEMI,;,ID,a,ASSIGN,=,ID,a,PLUS,+,INT_LIT,2,MUL,*,INT_LIT,3,SEMI,;,RBRACE,},EOF",
        ),
        (
            "for (auto i = 0; i < 10; ++i) { }",
            "FOR,for,LPAREN,(,AUTO,auto,ID,i,ASSIGN,=,INT_LIT,0,SEMI,;,ID,i,LT,<,INT_LIT,10,SEMI,;,INC,++,ID,i,RPAREN,),LBRACE,{,RBRACE,},EOF",
        ),
    ],
)
def test_lexer_complex_mix(source, expected):
    _assert_lex(source, expected)



def _lex(source: str) -> str:
    return Tokenizer(source).get_tokens_as_string()


def _assert_lex(source: str, expected: str):
    assert _lex(source) == expected


def test_lexer_keywords_not_id():
    _assert_lex(
        "auto break case continue default else float for if int return string struct switch void while",
        "AUTO,auto,BREAK,break,CASE,case,CONTINUE,continue,DEFAULT,default,ELSE,else,FLOAT,float,FOR,for,IF,if,INT,int,RETURN,return,STRING,string,STRUCT,struct,SWITCH,switch,VOID,void,WHILE,while,EOF",
    )


def test_lexer_id_basic():
    _assert_lex("_ _a9 a_b2", "ID,_,ID,_a9,ID,a_b2,EOF")


def test_lexer_ops_longer_match_first():
    _assert_lex(
        "== = <= < >= > != ++ + -- - && ||",
        "EQ,==,ASSIGN,=,LE,<=,LT,<,GE,>=,GT,>,NEQ,!=,INC,++,PLUS,+,DEC,--,MINUS,-,AND,&&,OR,||,EOF",
    )


def test_lexer_error_char_operators():
    with pytest.raises(Exception) as e:
        _lex("&")
    assert str(e.value) == "Error Token &"

    with pytest.raises(Exception) as e:
        _lex("|")
    assert str(e.value) == "Error Token |"


def test_lexer_separators():
    _assert_lex("{ } ( ) ; , :", "LBRACE,{,RBRACE,},LPAREN,(,RPAREN,),SEMI,;,COMMA,,,COLON,:,EOF")


def test_lexer_int_float_literals():
    _assert_lex(
        "0 100 1. .5 3.14 1e3 5.67E-2",
        "INT_LIT,0,INT_LIT,100,FLOAT_LIT,1.,FLOAT_LIT,.5,FLOAT_LIT,3.14,FLOAT_LIT,1e3,FLOAT_LIT,5.67E-2,EOF",
    )


def test_lexer_comments_skipped():
    _assert_lex(
        "auto x = 5; // cmt\n/* block\ncomment */ int y;",
        "AUTO,auto,ID,x,ASSIGN,=,INT_LIT,5,SEMI,;,INT,int,ID,y,SEMI,;,EOF",
    )


def test_lexer_string_valid_strips_quotes():
    _assert_lex('"abc"', 'STRING_LIT,abc,EOF')


def test_lexer_illegal_escape():
    with pytest.raises(Exception) as e:
        _lex('"Hello \\a World"')
    assert str(e.value) == "Illegal Escape In String: Hello \\a"


def test_lexer_unclose_string_newline():
    with pytest.raises(Exception) as e:
        _lex('"abc\n')
    assert str(e.value) == "Unclosed String: abc"


def test_lexer_error_char():
    with pytest.raises(Exception) as e:
        _lex("$")
    assert str(e.value) == "Error Token $"
