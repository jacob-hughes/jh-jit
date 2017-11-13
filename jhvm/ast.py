# vim: ai ts=4 sts=4 et sw=4
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from jhvm.opcodes import *

from rply.token import BaseBox

_label_counter = 0

def next_label():
    return _label_counter + 1

class Node(BaseBox):

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

    def _compile(self, gen):
        self.functions.compile(gen)

class Function(Node):
    def __init__(self, name, arg_list, body):
        self.name = name
        self.arg_list = arg_list
        self.body = body

    def append_arg(self, arg):
        self.args.append(arg)

    def _compile(self, gen):
        gen.register_function(self.name, [])
        gen.emit_label(self.name + ':')
        self.body.compile(gen)

class ListBox(Node):
    def __init__(self, items):
        self.items = items

    def extend(self, other):
        assert isinstance(other, ListBox)
        self.items.extend(other.items)
        return self

    def _compile(self, gen):
        for item in self.items:
            item.compile(gen)

    def _compile_reversed(self, gen):
        for item in reversed(self.items):
            item.compile(gen)

    def get_length(self):
        return len(self.items)


class Statement(Node):
    pass

class If(Statement):
    def __init__(self, cond, then_body):
        self.cond = cond
        self.then_body = then_body

        label_no = next_label()
        self._then = 'then_%s' % label_no
        self._exit = 'exit_%s' % label_no
        self._then_def = self._then + ':'
        self._exit_def = self._exit + ':'

    def _compile(self, gen):
        self.cond.compile(gen)
        gen.emit_bc_arg_str(JUMP_IF_FALSE, self._exit)
        self.then_body.compile(gen)
        gen.emit_label(self._exit_def)

class IfElse(Statement):
    def __init__(self, cond, then_body, else_body):
        self.cond = cond
        self.then_body = then_body
        self.else_body = else_body

        label_no = next_label()
        self._then = 'then_%s' % label_no
        self._else = 'else_%s' % label_no
        self._exit = 'exit_%s' % label_no
        self._then_def = self._then + ':'
        self._else_def = self._else + ':'
        self._exit_def = self._exit + ':'

    def _compile(self, gen):
        self.cond.compile(gen)
        gen.emit_bc_arg_str(JUMP_IF_FALSE, self._else)
        self.then_body.compile(gen)
        gen.emit_bc_arg_str(JUMP, self._exit)
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

class Block(ListBox):
    pass




class Exp(Node):
    pass

class Call(Exp):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def _compile(self, gen):
        self.args._compile_reversed(gen)
        gen.emit_bc_arg_int(CONST_INT, self.args.get_length())
        gen.emit_bc_arg_str(CALL, self.name)

class BinOp(Node):
    def __init__(self, op_name):
        self.op_code = BINOP_TO_OPCODE[op_name]

    def _compile(self, gen):
        gen.emit_bc(self.op_code)

class BinExp(Exp):
    def __init__(self, op, lhs, rhs):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def _compile(self, gen):
        self.lhs.compile(gen)
        self.rhs.compile(gen)
        self.op.compile(gen)

class For(Node):
    def __init__(self, start, cond, step, body):
        self.start = start
        self.cond = cond
        self.step = step
        self.body = body

        label_no = next_label()
        self._entry = 'entry_%s' % label_no
        self._exit = 'exit_%s' % label_no
        self._entry_def = self._entry + ':'
        self._exit_def = self._exit + ':'

    def _compile(self, gen):
        self.start.compile(gen)
        gen.emit_label(self._entry_def)
        self.cond.compile(gen)
        gen.emit_bc_arg_str(JUMP_IF_FALSE, self._exit)
        self.body.compile(gen)
        self.step.compile(gen)
        gen.emit_bc_arg_str(JUMP, self._entry)
        gen.emit_label(self._exit_def)

class Var(Node):
    def __init__(self, name):
        self.name = name

    def _compile(self, gen):
        gen.emit_bc_arg_int(VAR, gen.register_num_for_var(self.name))

class Assign(Exp):
    def __init__(self, name, exp):
        self.name = name
        self.exp = exp

    def _compile(self, gen):
        gen.emit_bc_arg_int(CONST_INT, gen.register_num_for_var(self.name))
        self.exp.compile(gen)
        gen.emit_bc(ASSIGN)

class Number(Exp):
    def __init__(self, value):
        self.value = value

    def _compile(self, gen):
        gen.emit_bc_arg_int(CONST_INT, self.value)

class FieldAccessor(Exp):
    def __init__(self, obj_var, field):
        self.obj_var = obj_var
        self.field = field

    def _compile(self, gen):
        self.obj_var.compile(gen)
        gen.emit_bc_arg_str(GET_FIELD, self.field)

class FieldSetter(Exp):
    def __init__(self, obj_var, field, exp):
        self.obj_var = obj_var
        self.field = field
        self.exp = exp

    def _compile(self, gen):
        self.obj_var.compile(gen)
        self.exp.compile(gen)
        gen.emit_bc_arg_str(SET_FIELD, self.field)

class Obj(Exp):
    def __init__(self, fields, values):
        self.fields = fields
        self.values = values

    def _compile(self, gen):
        gen.emit_bc(NEW)

