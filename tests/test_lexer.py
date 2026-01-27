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
