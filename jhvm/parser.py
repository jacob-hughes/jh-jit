# vim: ai ts=4 sts=4 et sw=4
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from rply import ParserGenerator

from jhvm.ast import *
from jhvm.lexer import token_names, lex

pg = ParserGenerator(
    token_names,
    precedence = [
        ('right', [ 'ASSIGN']),
        ('left', ['ADD', 'SUB', 'EQ', 'LT']),
    ]
)

@pg.production('program : functions')
def program(p):
    functions = p[0]
    return Program(functions)

@pg.production('functions : functions function')
def functions_single(p):
    return p[0].extend(p[1])

@pg.production('functions : function')
def functions(p):
    return p[0]

@pg.production('function : FN ID LPAREN param_list RPAREN LBRACE block RBRACE')
def function(p):
    f = Function(p[1].getstr(), p[3], p[6] )
    return ListBox([f])

@pg.production('param_list : non_empty_param_list')
def params(p):
    return p[0]

@pg.production('param_list : empty')
def params_empty(p):
    return ListBox([])

@pg.production('non_empty_param_list : non_empty_param_list COMMA param')
def non_empty_param_list_list(p):
        return p[0].extend(p[2])

@pg.production('param : ID')
def param(p):
    return ListBox([Var(p[0].getstr())])

@pg.production('block : block_contents')
def block(p):
    return p[0]

@pg.production('block_contents : block_contents SEMICOLON inner_block')
def block_contents_multi_stm(p):
    return p[0].extend(p[2])

@pg.production('block_contents : inner_block')
def block_contents_single_stm(p):
    return p[0]

@pg.production('inner_block : statement')
def fragment_statement(p):
    return Block([p[0]])

@pg.production('inner_block : exp')
def fragment_exp(p):
    return Block([p[0]])

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
    return FieldAccessor(Var(p[0].getstr()), p[2].getstr())

@pg.production('exp : ID DOT ID ASSIGN exp')
def exp_field_setter(p):
    return FieldSetter(Var(p[0].getstr()), p[2].getstr(), p[4])

@pg.production('exp : NUMBER')
def exp_number(p):
    return Number(int(p[0].getstr()))
#
@pg.production('exp : ID')
def exp_identifier(p):
    return Var(p[0].getstr())

@pg.production('exp : LPAREN exp RPAREN')
def exp_bracket(p):
    return p[1]

@pg.production('exp : ID LPAREN arg_list RPAREN')
def exp_function_call(p):
    return Call(p[0].getstr(), p[2])

@pg.production('arg_list : non_empty_arg_list')
def args(p):
    return p[0]

@pg.production('arg_list : empty')
def args_empty(p):
    return ListBox([])

@pg.production('non_empty_arg_list : non_empty_arg_list COMMA arg')
def non_empty_arg_list(p):
        return p[0].extend(p[2])

@pg.production('arg : exp')
def arg(p):
    return ListBox([p[0]])

@pg.production('exp : OBJECT LPAREN RPAREN')
def new_obj(p):
    return Obj([],[])

@pg.production('exp : exp bin_operators exp')
def binop(p):
    return BinExp(p[1], p[0], p[2])

@pg.production('bin_operators : LT')
@pg.production('bin_operators : EQ')
@pg.production('bin_operators : ADD')
@pg.production('bin_operators : SUB')
def binop_operations(p):
    return BinOp(p[0].gettokentype())

@pg.production('exp : ID ASSIGN exp')
def exp_assign(p):
    return Assign(p[0].getstr(), p[2])

# explicit decl of empty production rule
@pg.production('empty : ')
def p_empty(p):
    return None

@pg.error
def error_handler(token):
    raise ValueError("Illegal use of  %s. Line: %s" % (token.gettokentype(), token.getsourcepos()))

parser = pg.build()

def parse_input(source):
    return parser.parse(lex(source))
