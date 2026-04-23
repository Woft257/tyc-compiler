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

// Parser rules (Assignment 1)

program: decl* EOF;

decl: structDecl | funcDecl;

funcDecl
	: type? ID LPAREN paramList? RPAREN blockStmt
	;

paramList: param (COMMA param)*;
param: type ID;

structDecl
	: STRUCT ID LBRACE fieldDecl* RBRACE SEMI
	;

fieldDecl: type ID SEMI;

type: INT | FLOAT | STRING | VOID | ID;

blockStmt: LBRACE (varDeclStmt | stmt)* RBRACE;

varDeclStmt
	: AUTO ID (ASSIGN expr)? SEMI
	| type ID (ASSIGN expr)? SEMI
	;

stmt
	: blockStmt
	| ifStmt
	| whileStmt
	| forStmt
	| switchStmt
	| BREAK SEMI
	| CONTINUE SEMI
	| returnStmt
	| expr SEMI
	;

ifStmt
	: IF LPAREN expr RPAREN stmt (ELSE stmt)?
	;

whileStmt
	: WHILE LPAREN expr RPAREN stmt
	;

forStmt
	: FOR LPAREN forInit? SEMI expr? SEMI forUpdate? RPAREN stmt
	;

forInit
	: varDeclFor
	| assignmentExpr
	;

varDeclFor
	: AUTO ID (ASSIGN expr)?
	| type ID (ASSIGN expr)?
	;

forUpdate
	: assignmentExpr
	| incDecExpr
	;

switchStmt
	: SWITCH LPAREN expr RPAREN LBRACE switchItem* RBRACE
	;

switchItem
	: CASE expr COLON (varDeclStmt | stmt)*
	| DEFAULT COLON (varDeclStmt | stmt)*
	;

returnStmt
	: RETURN expr? SEMI
	;

// Expressions (precedence per spec)
expr: assignmentExpr;

assignmentExpr
	: logicalOrExpr (ASSIGN assignmentExpr)?
	;

logicalOrExpr
	: logicalAndExpr (OR logicalAndExpr)*
	;

logicalAndExpr
	: equalityExpr (AND equalityExpr)*
	;

equalityExpr
	: relationalExpr ((EQ | NEQ) relationalExpr)*
	;

relationalExpr
	: additiveExpr ((LT | LE | GT | GE) additiveExpr)*
	;

additiveExpr
	: multiplicativeExpr ((PLUS | MINUS) multiplicativeExpr)*
	;

multiplicativeExpr
	: unaryExpr ((MUL | DIV | MOD) unaryExpr)*
	;

unaryExpr
	: (INC | DEC) unaryExpr
	| (NOT | PLUS | MINUS) unaryExpr
	| postfixExpr
	;

postfixExpr
	: primaryExpr postfixSuffix*
	;

postfixSuffix
	: DOT ID
	| INC
	| DEC
	;

primaryExpr
	: ID callSuffix?
	| literal
	| LPAREN expr RPAREN
	;

callSuffix: LPAREN argList? RPAREN;
argList: expr (COMMA expr)*;

incDecExpr
	: (INC | DEC) primaryLValue
	| primaryLValue (INC | DEC)
	;

primaryLValue
	: ID (DOT ID)*
	;

literal: INT_LIT | FLOAT_LIT | STRING_LIT;



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
	{
		if self.text.endswith('\r\n'):
			self.text = self.text[1:-2]
		elif self.text.endswith('\n') or self.text.endswith('\r'):
			self.text = self.text[1:-1]
		else:
			self.text = self.text[1:]
	}
	;

STRING_LIT:
	'"' (STR_CHAR)* '"'
	{self.text = self.text[1:-1]}
	;

ERROR_CHAR: .;
