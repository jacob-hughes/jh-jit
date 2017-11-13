# vim: ai ts=4 sts=4 et sw=4
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from jhvm.parser import parse_input
from jhvm.ast import *

def generate_bytecode(ast):
    context = GeneratorContext()
    ast.compile(context)
    return context.get_bytecode()

class GeneratorContext(object):

    def __init__(self):
        self.code = []
        self.func_names = []
        self.func_vars = []
        pass

    def emit_bc(self, opcode):
        self.code.append(str(opcode))

    def emit_bc_arg_int(self, opcode, arg):
        conv_opcode = str(opcode)
        conv_arg = str(arg)
        assert isinstance(conv_opcode, str)
        assert isinstance(conv_arg, str)
        self.code.extend([conv_opcode, conv_arg])

    def emit_bc_arg_str(self, opcode, arg):
        conv_opcode = str(opcode)
        self.code.extend([conv_opcode, arg])

    def register_function(self, name, args):
        self.func_names.append(name)
        self.func_vars.append(args)

    def register_num_for_var(self, var):
        # Using a number to represent vars in bytecode makes interpreting it
        # easier, in addition to being a more efficient representation.
        #
        # As our language has no global vars or closures, we assume each var
        # number is unique to its enclosing function's scope.
        var_list = self.func_vars[-1]
        try:
            return var_list.index(var)
        except ValueError:
            var_list.append(var)
            return len(var_list) - 1

    def emit_label(self, label):
        self.code.append(label)

    def _replace_labels(self):
        # Remove statically function and loop labels from bytecode and
        # replace them with index of bytecode instr. to jump to.
        labels = {}
        for i, instr in enumerate(self.code):
            if instr.endswith(':'):
                del self.code[i]
                labels.update({instr[:-1] : str(i)})
        for i, instr in enumerate(self.code):
            try:
                self.code[i] = labels[instr]
            except KeyError: pass


    def get_bytecode(self):
        self._replace_labels()
        return self.code
