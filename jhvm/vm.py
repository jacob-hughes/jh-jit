# vim: ai ts=4 sts=4 et sw=4
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from jhvm.opcodes import *
from jhvm.util import bail

from rpython.rlib.jit import JitDriver
def get_location(pc, bytecode):
    assert pc >= 0
    return "LineNo:%s Instr:%s" % (pc + 1, OP_CODES[int(bytecode[pc])])

jitdriver = JitDriver(greens = ['pc', 'bytecode'],
                      reds = ['frame', 'self'],
                      get_printable_location = get_location
                     )

def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()

class VM_Obj(object):
    pass

class Obj(VM_Obj):
    def __init__(self, fields = None):
        self.fields = fields or {}

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __neq__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '{} {}'.format(self.__class__.__name__, self.__dict__)

    def set_field(self, field, value):
        try:
            self.fields[field] = value
        except IndexError:
            for _ in range(len(self.fields) -1, field):
                self.fields.append(None)
            self.fields[field] = value

    def get_field(self, field):
        try:
            return self.fields[field]
        except IndexError:
            bail('FieldException: Field does not exist')


class Int(Obj):
    def __init__(self, value):
        self.value = value

    def add(self, other):
        return Int(self.value + other.value)

    def sub(self, other):
        return Int(self.value - other.value)

    def eq(self, other):
        return Bool(self.value == other.value)

    def neq(self, other):
        is_neq = not self.eq(other)
        return Bool(is_neq)

    def lt(self, other):
        return Bool(self.value < other.value)

class StrLiteral(Obj):
    def __init__(self, str_val):
        self.str_val = str_val

class Bool(Obj):
    def __init__(self, value):
        self.value = value

class Frame(VM_Obj):
    def __init__(self, return_address, variables, caller_frame):
        self.return_address = return_address
        self.variables = variables
        self.stack = []
        self.caller_frame = caller_frame
        self.next_frame = None

    def __repr__(self):
        return 'F: Stack{} Vars{}'.format(self.stack, self.variables)

    def pop(self):
        return self.stack.pop()

    def push(self, val):
        self.stack.append(val)

    def const_int(self, val):
        self.stack.append(Int(int(val)))

    def const_str(self, val):
        assert isinstance(val, str)
        self.stack.append(StrLiteral(val))

    def add(self):
        o2 = self.pop()
        o1 = self.pop()
        assert isinstance(o1, Obj)
        val = o1.add(o2)
        self.push(val)

    def sub(self):
        o2 = self.pop()
        o1 = self.pop()
        assert isinstance(o1, Obj)
        val = o1.sub(o2)
        self.push(val)

    def eq(self):
        o2 = self.pop()
        o1 = self.pop()
        assert isinstance(o1, Obj)
        val = o1.eq(o2)
        self.push(val)

    def lt(self):
        o2 = self.pop()
        o1 = self.pop()
        assert isinstance(o1, Obj)
        val = o1.lt(o2)
        self.push(val)

    def jump_if_true(self):
        exp = self.pop()
        return exp.value

    def jump_if_false(self):
        exp = self.pop()
        return exp.value

    def var(self):
        name = self.pop()
        value = self.variables[name.value]
        self.push(value)

    def new(self, vm):
        obj = Obj()
        vm.heap.append(obj)
        ref = Int(len(vm.heap) - 1)
        self.push(ref)

    def set_field(self, field,  vm):
        value = self.pop()
        self.var()
        ref = self.pop().value
        obj = vm.heap[ref]
        obj.set_field(field, value)

    def get_field(self, field, vm):
        self.var()
        ref = self.pop().value
        obj = vm.heap[ref]
        val = obj.get_field(field)
        self.push(val)


    def dup(self):
        val = self.stack[-1]
        self.push(val)

    def jump(self):
        pass

    def swap(self):
        first = self.pop()
        second = self.pop()
        self.push(first)
        self.push(second)

    def assign(self):
        value = self.pop()
        var = self.pop().value
        if len(self.variables) == var:
            self.variables.append(value)
        else:
            self.variables[var] = value
        self.push(value)

    def neq(self):
        o2 = self.pop()
        o1 = self.pop()
        assert isinstance(o1, Obj)
        val = o1.neq(o2)
        self.push(val)

    def ret(self):
        return (self.return_address, self.caller_frame, self.pop())

class VirtualMachine(object):

    def __init__(self, instructions, args = None):
        self.instructions = instructions
        self.stack = []
        self.heap = []

        if args:
            [self.stack.append(Int(arg)) for arg in args]



    def interp(self):
        main_frame = Frame(-1, [], None)
        self.stack.append(main_frame)
        return self._interp(self.instructions, main_frame)

    def _interp(self, bytecode, frame):
        # Begin by creating the stack frame for the main method and pushing
        # on stack.
        pc = 0

        # Begin program interpreter loop
        while True:
            jitdriver.jit_merge_point(pc=pc, bytecode=bytecode, frame=frame, self=self)
            if pc >= len(bytecode):
                break

            instr = bytecode[pc]

            if instr == CONST_INT:
                frame.const_int(bytecode[pc + 1])
            elif instr == POP:
                frame.pop()
            elif instr == JUMP_IF_TRUE:
                val = frame.jump_if_true()
                if val:
                    pc = int(bytecode[pc + 1])
                    continue # don't increment pc
            elif instr == JUMP_IF_FALSE:
                val = frame.jump_if_false()
                if not val:
                    pc = int(bytecode[pc + 1])
                    continue # don't increment pc
            elif instr == JUMP:
                pc = int(bytecode[pc + 1])
                continue
            elif instr == ADD:
                frame.add()
            elif instr == SUB:
                frame.sub()
            elif instr == EQ:
                frame.eq()
            elif instr == LT:
                frame.lt()
            elif instr == NEW:
                frame.new(self)
            elif instr == GET_FIELD:
                frame.get_field(str(bytecode[pc+1]), self)
            elif instr == SET_FIELD:
                frame.set_field(str(bytecode[pc+1]), self)
            elif instr == DUP:
                frame.dup()
            elif instr == SWAP:
                frame.swap()
            elif instr == NEQ:
                frame.neq()
            elif instr == CALL:
                frame = self.function_call(frame, pc)
                pc = int(bytecode[pc + 1])
                continue
            elif instr == RET:
                ret_address, caller_frame, ret_val = frame.ret()
                if not caller_frame: # if main function
                    return ret_val
                frame = caller_frame
                frame.pop()
                frame.push(ret_val)
                pc = ret_address
                continue
            elif instr == VAR:
                frame.var()
            elif instr == ASSIGN:
                frame.assign()
            elif instr == CONST_STR:
                frame.const_str(bytecode[pc + 1])
            elif instr == EXIT:
                break
            else:
                bail('unknown op_code: %s' % bytecode[pc])

            pc += int(HAS_ARGS[int(instr)]) + 1

        return self.stack.pop()

    def function_call(self, caller_frame, pc):
        # Invoked on the presence of the CALL opcode.
        # This method will take the values pushed on the caller's stack before
        # the CALL as arguments to the callee and place them inside the newly
        # instantiated frame. It will then push this new frame to the VMs main
        # execution stack.
        return_address = pc + 2
        variables = [None] * 5
        arg_count = caller_frame.pop().value
        for _ in range(arg_count):
            arg = caller_frame.pop()
            variables.append(arg)
        new_frame = Frame(return_address, variables, caller_frame)
        caller_frame.push(new_frame)
        return new_frame


    def pop_frame(self):
        frame = self.stack.pop()
        return_value = frame.pop()
        return (frame.return_address, return_value)



