# vim: ai ts=4 sts=4 et sw=4
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from bytecode.ast import *
from rply import ParserGenerator
from rply import LexerGenerator

lg = LexerGenerator()

token_rules = [
    ('ADD', '\+'),
    ('SUB', '\-'),
    ('LPAREN', '\('),
    ('RPAREN', '\)'),
    ('LBRACE', '\{'),
    ('RBRACE', '\}'),
    ('LSQUARE', '\['),
    ('RSQUARE', '\]'),
    ('DOT', '\.'),
    ('COMMA', ','),
    ('SEMICOLON', ';'),
    ('EQ', '=='),
    ('ASSIGN', '='),
    ('LT', '<'),
    ('TO', 'to(?!\w)'),
    ('FOR', 'for(?!\w)'),
    ('IF', 'if(?!\w)'),
    ('ELSE', 'else(?!\w)'),
    ('WHILE', 'while(?!\w)'),
    ('FN', 'fn(?!\w)'),
    ('OBJECT', 'object(?!\w)'),
    ('RETURN', 'return(?!\w)'),
    ('ID', '[a-zA-Z_][a-zA-Z_0-9]*'),
    ('NUMBER', '\d+'),
]

for token, rule in token_rules:
    lg.add(token,rule)

lg.ignore('\s')

def get_lexer():
    lexer = lg.build()

pg = ParserGenerator(
    [token for token, _ in token_rules],
    precedence = [
        ('right', [ 'ASSIGN']),
        ('left', ['ADD', 'SUB', 'EQ', 'LT']),
    ]
)

@pg.production('program : functions')
def program(p):
    return Program(p[0])


@pg.production('functions : functions function')
@pg.production('functions : function')
def functions_single(p):
    if len(p) == 2:
        return p[0] + [p[1]]
    else:
        return [p[0]]

@pg.production('function : FN ID LPAREN params RPAREN LBRACE block RBRACE')
def function(p):
    return Function(p[1].getstr(), p[3], p[6])

@pg.production('params : one_or_more_params')
def params(p):
    return p[0]

@pg.production('params : empty')
def params_empty(p):
    return []

@pg.production('one_or_more_params : one_or_more_params COMMA ID')
def one_or_more_params(p):
        return p[0] + [Var(p[2].getstr())]

@pg.production('one_or_more_params : ID')
def one_or_more_params_id(p):
    return [Var(p[0].getstr())]

@pg.production('block : block_contents')
def block(p):
    return Block(p[0])

@pg.production('block_contents : block_contents SEMICOLON fragment')
@pg.production('block_contents : fragment')
def block_contents(p):
    if len(p) == 3:
        return p[0] + [p[2]]
    else:
        return [p[0]]

@pg.production('fragment : statement')
def fragment_statement(p):
    return p[0]

@pg.production('fragment : exp')
def fragment_exp(p):
    return p[0]

@pg.production('statement : RETURN exp')
def statement_return(p):
    return Return(p[1])

@pg.production('statement : IF LPAREN exp RPAREN LBRACE block RBRACE')
def statement_if(p):
    return If(p[2], p[5])

@pg.production('statement : IF LPAREN exp RPAREN LBRACE block RBRACE ELSE LBRACE block RBRACE')
def statement_if_else(p):
    return IfElse(p[2], p[5], p[9])

@pg.production('statement : FOR LPAREN exp SEMICOLON exp SEMICOLON exp RPAREN LBRACE block RBRACE')
def statement_for(p):
    return For(p[2], p[4], p[6], p[9])

@pg.production('exp : ID DOT ID')
def exp_field_accessor(p):
    return FieldAccessor(p[0].getstr(), p[2].getstr())

@pg.production('exp : ID DOT ID ASSIGN exp')
def exp_field_setter(p):
    return FieldSetter(p[0].getstr(), p[2].getstr(), p[4])

@pg.production('exp : ID LSQUARE exp RSQUARE ASSIGN exp')
def exp_set_field(p):
    return ObjSetter(p[0].getstr(), p[2], p[5])


@pg.production('exp : NUMBER')
def exp_number(p):
    return Number(int(p[0].getstr()))

@pg.production('exp : ID')
def exp_identifier(p):
    return Var(p[0].getstr())

@pg.production('exp : LPAREN exp RPAREN')
def exp_bracket(p):
    return p[1]

@pg.production('fields : one_or_more_fields')
def fields(p):
    return p[0]

@pg.production('fields : empty')
def fields_empty(p):
    return ([],[])

@pg.production('one_or_more_fields : one_or_more_fields COMMA ID ASSIGN exp')
def one_or_more_fields(p):
        return ([p[0][0]] + [p[2].getstr()], [p[0][1]] + [p[4]] )

@pg.production('one_or_more_fields : ID ASSIGN exp')
def one_or_more_fields_with_val(p):
    return (p[0].getstr(), p[2])

@pg.production('exp : ID LPAREN args RPAREN')
def exp_function_call(p):
    return Call(p[0].getstr(), p[2])

@pg.production('args : one_or_more_args')
def args(p):
    return p[0]

@pg.production('args : empty')
def args_empty(p):
    return []

@pg.production('one_or_more_args : one_or_more_args COMMA exp')
def one_or_more_args(p):
        return p[0] + [p[2]]

@pg.production('one_or_more_args : exp')
def one_or_more_args_exp(p):
    return [p[0]]

@pg.production('exp : exp binop exp')
def binop(p):
    return BinOp(p[1], p[0], p[2])

@pg.production('exp : OBJECT LPAREN RPAREN')
def new_obj(p):
    return Obj([],[])

@pg.production('binop : LT')
@pg.production('binop : EQ')
@pg.production('binop : ADD')
@pg.production('binop : SUB')
def binop_operations(p):
    return p[0].gettokentype()

@pg.production('exp : ID ASSIGN exp')
def exp_assign(p):
    return Assign(p[0].getstr(), p[2])

# explicit decl of empty production rule
@pg.production('empty : ')
def p_empty(p):
    pass

@pg.error
def error_handler(token):
    raise ValueError("Illegal use of  %s. Line: %s" % (token.gettokentype(), token.getsourcepos()))

def parse_input(source):
    lexer = lg.build()
    parser = pg.build()
    return parser.parse(lexer.lex(source))
