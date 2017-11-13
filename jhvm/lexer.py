# vim: ai ts=4 sts=4 et sw=4
# -*- coding: utf-8 -*-

from __future__ import absolute_import
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

token_names = []
for token, rule in token_rules:
    token_names.append(token)
    lg.add(token,rule)

lg.ignore('\s')
lexer = lg.build()

def lex(source):
    for token in lexer.lex(source):
        yield token
