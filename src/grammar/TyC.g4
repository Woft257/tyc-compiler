grammar TyC;

@lexer::header {
from lexererr import *
}

@lexer::members {
def emit(self):
    tk = self.type
    if tk == self.UNCLOSE_STRING:
        result = super().emit()
        raise UncloseString(result.text)
    elif tk == self.ILLEGAL_ESCAPE:
        result = super().emit()
        raise IllegalEscape(result.text)
    elif tk == self.ERROR_CHAR:
        result = super().emit()
        raise ErrorToken(result.text)
    else:
        return super().emit()
}

options{
	language=Python3;
}

program: EOF;

AUTO: 'auto';
BREAK: 'break';
CASE: 'case';
CONTINUE: 'continue';
DEFAULT: 'default';
ELSE: 'else';
FLOAT: 'float';
FOR: 'for';
IF: 'if';
INT: 'int';
RETURN: 'return';
STRING: 'string';
STRUCT: 'struct';
SWITCH: 'switch';
VOID: 'void';
WHILE: 'while';

EQ: '==';
NEQ: '!=';
LE: '<=';
GE: '>=';
INC: '++';
DEC: '--';
AND: '&&';
OR: '||';

PLUS: '+';
MINUS: '-';
MUL: '*';
DIV: '/';
MOD: '%';
LT: '<';
GT: '>';
NOT: '!';
ASSIGN: '=';
DOT: '.';

LBRACE: '{';
RBRACE: '}';
LPAREN: '(';
RPAREN: ')';
SEMI: ';';
COMMA: ',';
COLON: ':';

INT_LIT: [0-9]+;
FLOAT_LIT:
	[0-9]+ '.' [0-9]* ([eE] [+-]? [0-9]+)?
	| '.' [0-9]+ ([eE] [+-]? [0-9]+)?
	| [0-9]+ [eE] [+-]? [0-9]+
	;

ID: [A-Za-z_] [A-Za-z_0-9]*;

LINE_COMMENT: '//' ~[\r\n]* -> skip;
BLOCK_COMMENT: '/*' (.)*? '*/' -> skip;

WS: [ \t\f\r\n]+ -> skip;

fragment ESC: '\\' [bfrnt"\\];
fragment STR_CHAR: ~["\\\r\n] | ESC;

ILLEGAL_ESCAPE:
	'"' (STR_CHAR)* '\\' ~[bfrnt"\\\r\n]
	{self.text = self.text[1:]}
	;

UNCLOSE_STRING:
	'"' (STR_CHAR)* ( '\r'? '\n' | '\r' | EOF )
	{self.text = self.text[1:-1] if self.text.endswith('\n') or self.text.endswith('\r') else self.text[1:]}
	;

STRING_LIT:
	'"' (STR_CHAR)* '"'
	{self.text = self.text[1:-1]}
	;

ERROR_CHAR: .;
