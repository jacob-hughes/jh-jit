# vim: ai ts=4 sts=4 et sw=4
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from jhvm.opcodes import *

class Node(object):
    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __neq__(self, other):
        return not self.__eq__

    def compile(self, context):
        self._compile(context)

class Program(Node):
    def __init__(self, functions):
        self.functions = functions

    def compile(self, gen):
        for function in self.functions:
            function.compile(gen)

class Function(Node):
    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self.body = body

    def _compile(self, gen):
        gen.register_function(self.name, [arg.name for arg in self.args])
        gen.emit_label(self.name + ':')
        self.body.compile(gen)

class Statement(Node):
    pass

class If(Statement):
    def __init__(self, cond, then_body):
        self.cond = cond
        self.then_body = then_body

        self._then = 'then_%s' % id(self)
        self._exit = 'exit_%s' % id(self)
        self._then_def = self._then + ':'
        self._exit_def = self._exit + ':'

    def _compile(self, gen):
        self.cond.compile(gen)
        gen.emit_bc(JUMP_IF_FALSE, self._exit)
        self.then_body.compile(gen)
        gen.emit_label(self._exit_def)

class IfElse(Statement):
    def __init__(self, cond, then_body, else_body):
        self.cond = cond
        self.then_body = then_body
        self.else_body = else_body

        self._then = 'then_%s' % id(self)
        self._else = 'else_%s' % id(self)
        self._exit = 'exit_%s' % id(self)
        self._then_def = self._then + ':'
        self._else_def = self._else + ':'
        self._exit_def = self._exit + ':'

    def _compile(self, gen):
        self.cond.compile(gen)
        gen.emit_bc(JUMP_IF_FALSE, self._else)
        self.then_body.compile(gen)
        gen.emit_bc(JUMP, self._exit)
        gen.emit_label(self._else_def)
        self.else_body.compile(gen)
        gen.emit_label(self._exit_def)

class While(Statement):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class Return(Statement):
    def __init__(self, exp):
        self.exp = exp

    def _compile(self, gen):
        self.exp.compile(gen)
        gen.emit_bc(RET)

class Block(Node):
    def __init__(self, code):
        self.code = code

    def _compile(self, gen):
        for statement in self.code:
            statement.compile(gen)

class Exp(Node):
    pass

class Call(Exp):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def _compile(self, gen):
        for arg in reversed(self.args):
            arg.compile(gen)
        gen.emit_bc(CONST_INT, len(self.args))
        gen.emit_bc(CALL, self.name)

class BinOp(Exp):
    def __init__(self, op, lhs, rhs):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def _compile(self, gen):
        self.lhs.compile(gen)
        self.rhs.compile(gen)
        gen.emit_bc(BINOP_TO_OPCODE[self.op])

class For(Node):
    def __init__(self, start, cond, step, body):
        self.start = start
        self.cond = cond
        self.step = step
        self.body = body

        self._entry = 'entry_%s' % id(self)
        self._exit = 'exit_%s' % id(self)
        self._entry_def = self._entry + ':'
        self._exit_def = self._exit + ':'

    def _compile(self, gen):
        self.start.compile(gen)
        gen.emit_label(self._entry_def)
        self.cond.compile(gen)
        gen.emit_bc(JUMP_IF_FALSE, self._exit)
        self.body.compile(gen)
        self.step.compile(gen)
        gen.emit_bc(JUMP, self._entry)
        gen.emit_label(self._exit_def)

class Var(Node):
    def __init__(self, name):
        self.name = name

    def _compile(self, gen):
        gen.emit_bc(CONST_INT, gen.register_num_for_var(self.name))
        gen.emit_bc(VAR)

class Assign(Exp):
    def __init__(self, name, exp):
        self.name = name
        self.exp = exp

    def _compile(self, gen):
        gen.emit_bc(CONST_INT, gen.register_num_for_var(self.name))
        self.exp.compile(gen)
        gen.emit_bc(ASSIGN)

class Number(Exp):
    def __init__(self, value):
        self.value = value

    def _compile(self, gen):
        gen.emit_bc(CONST_INT, self.value)

class FieldAccessor(Exp):
    def __init__(self, obj_var, field):
        self.obj_var = obj_var
        self.field = field

    def _compile(self, gen):
        gen.emit_bc(CONST_INT, gen.register_num_for_var(self.obj_var))
        gen.emit_bc(CONST_STR, self.field)
        gen.emit_bc(GET_FIELD)

class FieldSetter(Exp):
    def __init__(self, obj_var, field, exp):
        self.obj_var = obj_var
        self.field = field
        self.exp = exp

    def _compile(self, gen):
        gen.emit_bc(CONST_INT, gen.register_num_for_var(self.obj_var))
        gen.emit_bc(CONST_STR, self.field)
        self.exp.compile(gen)
        gen.emit_bc(SET_FIELD)

class Obj(Exp):
    def __init__(self, fields, values):
        self.fields = fields
        self.values = values

    def _compile(self, gen):
        gen.emit_bc(NEW)



