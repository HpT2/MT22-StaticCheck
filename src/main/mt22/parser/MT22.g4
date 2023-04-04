grammar MT22;
//2012385
@lexer::header {
from lexererr import *
}

options{
	language=Python3;
}

program:  prog EOF ;

prog				: declaration prog | declaration ;

stmtlist			: stmt stmtlist | var_declare stmtlist | stmt | var_declare ;
stmt				: block_stmt
					| ( assignment | return_stmt | do_while_stmt | BREAK | CONTINUE ) SEMI 
					| if_stmt | for_stmt | while_stmt | call_stmt;

declaration			: var_declare | func_declare ;

expr 				: expr1 DBLCOL expr1  | expr1 ;
expr1				: expr2 (EQ | NOTEQ | LESS | MORE_ | LESSOREQ | MOREOREQ) expr2 | expr2 ;
expr2				: expr2 (OR | AND) expr3 | expr3 ;
expr3				: expr3 (ADDOP | SUBOP) expr4 | expr4 ;
expr4				: expr4 (MULOP | DIVOP | MODULO) expr5 | expr5 ;
expr5				: LOGICNOT expr5 | expr6 ;
expr6 				: '-'expr6 | expr7 ;
expr7 				: indexop | exprval;
exprval				: ID | INT_TYPE | FLOAT_TYPE | STRING_TYPE | TRUE | FALSE | func_call | indexed_array
					| LP expr RP ;
exprlist			: expr COMMA exprlist | expr ;


indexop 			: ID LSB exprlist RSB ;

func_call			: ID LP argument RP ;

indexed_array 		: LCB  ( exprlist | ) RCB ;




//Type
atomic_type			: INTEGER | FLOAT | STRING | BOOLEAN ;
type_				: atomic_type | AUTO | array_type;

//Var declaration
var_declare			: id_list COLON type_ SEMI | ID recur expr SEMI;
recur				: COMMA ID recur expr COMMA | COLON type_ ASSIGN;

array_type			: ARRAY dimension OF atomic_type ;
dimension			: LSB intlist RSB ;
intlist				: INT_TYPE COMMA intlist | INT_TYPE ;
id_list				: ID COMMA id_list | ID ;


//function declarations
function_type		: type_ | VOID ;
param				: INHERIT? OUT? ID COLON type_  ;
param_list			: param COMMA param_list | param ;
func_declare		: ID COLON FUNCTION function_type LP ( param_list | ) RP (INHERIT ID)? block_stmt;

assignment			: (ID | indexop) ASSIGN expr;
return_stmt			: RETURN ( expr | ) ;
call_stmt			: ID LP argument RP SEMI;
argument			: expr COMMA argument | expr | ;
if_stmt				: IF LP expr RP ( stmt ) ( ELSE stmt | );
for_stmt			: FOR LP assignment COMMA expr COMMA expr RP stmt ;
while_stmt			: WHILE LP expr RP stmt  ;
do_while_stmt		: DO block_stmt WHILE LP expr RP;
block_stmt			: LCB (stmtlist |) RCB ;



//Keywords
AUTO				: 'auto'  ;
BREAK				: 'break' ;
BOOLEAN				: 'boolean' ;
DO					: 'do' ;
ELSE				: 'else' ;
FALSE				: 'false' ;
FLOAT				: 'float' ;
FOR 				: 'for' ;
FUNCTION			: 'function' ;
IF					: 'if' ;
INTEGER				: 'integer' ;
RETURN 				: 'return' ;
STRING 				: 'string' ;
TRUE				: 'true' ;
WHILE				: 'while' ;
VOID 				: 'void' ;
OUT					: 'out' ;
CONTINUE			: 'continue' ;
OF 					: 'of' ;
INHERIT				: 'inherit' ;
ARRAY				: 'array' ;


//Operators
ADDOP				: '+' ;
SUBOP				: '-' ;
MULOP				: '*' ;
DIVOP				: '/' ;
MODULO				: '%' ;
LOGICNOT			: '!' ;
AND					: '&&';
OR 					: '||';
EQ					: '==';
NOTEQ				: '!=';
LESS				: '<' ;
LESSOREQ			: '<=';
MORE_				: '>' ;
MOREOREQ			: '>=';
DBLCOL				: '::';

//Seperators
LP					: '(' ;
RP					: ')' ;
LSB					: '[' ;
RSB					: ']' ;
DOT					: '.' ;
COMMA				: ',' ;
SEMI				: ';' ;
COLON				: ':' ;
LCB					: '{' ;
RCB					: '}' ;
ASSIGN				: '=' ;


COMMENT 			: '/*' .*? '*/' -> skip ;
LINE_COMMENT		: '//'  (~[\r\n])* -> skip	;



ID					: [A-Za-z_][A-Za-z0-9_]* ;
INT_TYPE			: INTPART {self.text = self.text.replace('_','')} ;
FLOAT_TYPE			: ( INTPART DECIMAL? EXPONENT | INTPART DECIMAL | DECIMAL EXPONENT   ) {self.text = self.text.replace('_','')} ;
fragment INTPART 	: '0' | [1-9] ('_'? [0-9]+)*  ;
fragment DECIMAL	: '.' [0-9]* ;
fragment EXPONENT	: [eE] [-+]? [0-9]+ ;
STRING_TYPE			:  ('"''"' | '"'(~["'\n\r\\] | '\\t' | '\\r' | '\\n' | '\\b' | '\\f' | QUOTE | DBLQUOTE | BACKSLASH)*'"') {self.text=self.text[1:-1]};
fragment QUOTE 		: '\\''\u0027' ;
fragment DBLQUOTE 	: '\\''"' ;
fragment BACKSLASH 	: '\\''\\' ;


WS : [ \t\r\n]+ -> skip ; // skip spaces, tabs, newlines

ILLEGAL_ESCAPE		: '"'~["\n\r]*? ( '\\'~[trnbf'"\\] )  {raise IllegalEscape(self.text[1:])};

UNCLOSE_STRING		: '"'(~["'\n\r\\] | '\\t' | '\\r' | '\\n' | '\\b' | '\\f' | QUOTE | DBLQUOTE | BACKSLASH)* {raise UncloseString(self.text[1:])};	

ERROR_CHAR			: .  {raise ErrorToken(self.text)} ;