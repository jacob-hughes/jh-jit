# vim: ai ts=4 sts=4 et sw=4
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from jhvm.opcodes import *
from jhvm.util import bail

from rpython.rlib import jit
from rpython.rlib.debug import make_sure_not_resized
def get_location(pc, bytecode):
    assert pc >= 0
    return "LineNo:%s Instr:%s" % (pc + 1, OP_CODES[int(bytecode[pc])])

jitdriver = jit.JitDriver(greens = ['pc', 'bytecode'],
                      reds = ['frame', 'self'],
                      virtualizables=['frame'],
                      get_printable_location = get_location
                     )

def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()

class VM_Obj(object):
    pass

class VM_Objspace(VM_Obj):
    def add(self, other):
        raise NotImplementedError()

    def sub(self, other):
        raise NotImplementedError()

    def eq(self, other):
        raise NotImplementedError()

    def neq(self, other):
        raise NotImplementedError()

    def lt(self, other):
        raise NotImplementedError()

class ObjMap(object):
    _immutable_fields_ = ('field_indexes', 'other_maps')
    def __init__(self):
        self.field_indexes = {}
        self.other_maps = {}

    @jit.elidable
    def get_field_index(self, field_name):
        return self.field_indexes.get(field_name, -1)

    @jit.elidable
    def new_map_with_additional_field(self, field_name):
        if field_name not in self.other_maps:
            new_map = ObjMap()
            new_map.field_indexes.update(self.field_indexes)
            new_map.field_indexes[field_name] = len(self.field_indexes)
            self.other_maps[field_name] = new_map
        return self.other_maps[field_name]

EMPTY_MAP = ObjMap()

class Obj(VM_Obj):
    def __init__(self):
        self.field_values = []
        self.map = EMPTY_MAP


    def __repr__(self):
        return '{} {}'.format(self.__class__.__name__, self.__dict__)

    def set_field(self, field_name, value):
        _map = jit.promote(self.map)
        index = _map.get_field_index(field_name)
        if index != -1:
            self.field_values[index] = value
            return
        self.map = _map.new_map_with_additional_field(field_name)
        self.field_values.append(value)

    def get_field(self, field_name):
        _map = jit.promote(self.map)
        index = _map.get_field_index(field_name)
        if index != -1:
            return self.field_values[index]
        raise AttributeError(field_name)

class Int(VM_Objspace):
    _immutable_fields_ = ['int_val']
    def __init__(self, int_val):
        self.int_val = int_val

    def add(self, other):
        assert isinstance(other, Int)
        return Int(self.int_val + other.int_val)

    def sub(self, other):
        assert isinstance(other, Int)
        return Int(self.int_val - other.int_val)

    def eq(self, other):
        assert isinstance(other, Int)
        return Bool(self.int_val == other.int_val)

    def neq(self, other):
        assert isinstance(other, Int)
        is_neq = not self.eq(other)
        return Bool(is_neq)

    def lt(self, other):
        assert isinstance(other, Int)
        return Bool(self.int_val < other.int_val)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.int_val == other.int_val

class StrLiteral(VM_Objspace):
    _immutable_fields_ = ['str_val']
    def __init__(self, str_val):
        self.str_val = str_val

class Bool(VM_Objspace):
    _immutable_fields_ = ['bool_val']
    def __init__(self, bool_val):
        self.bool_val = bool_val

class Frame(VM_Obj):
    _immutable_fields_ = ['stack', 'return_address', 'caller_frame', 'variables' ]
    _virtualizable_ = ['return_address', 'sp', 'caller_frame', 'stack[*]', 'variables[*]' ]

    def __init__(self, return_address, variables, caller_frame):
        self = jit.hint(self, access_directly=True, fresh_virtualizable=True)
        self.return_address = return_address
        self.variables = variables
        self.stack = [None] * 128
        self.sp = 0
        self.caller_frame = caller_frame
        self.next_frame = None

        # make_sure_not_resized(self.stack)


    # def __repr__(self):
    #     return 'F: Stack{} Vars{}'.format(self.stack, self.variables)

    def pop(self):
        index = self.sp - 1
        assert index >= 0
        val = self.stack[index]
        self.stack[index] = None
        self.sp = index
        return val

    def push(self, obj):
        assert isinstance(obj, VM_Obj)
        self.stack[self.sp] = obj
        self.sp += 1

    def add(self):
        o2 = self.pop()
        o1 = self.pop()
        assert isinstance(o1, VM_Objspace)
        val = o1.add(o2)
        self.push(val)

    def sub(self):
        o2 = self.pop()
        o1 = self.pop()
        assert isinstance(o1, VM_Objspace)
        val = o1.sub(o2)
        self.push(val)

    def eq(self):
        o2 = self.pop()
        o1 = self.pop()
        assert isinstance(o1, VM_Objspace)
        val = o1.eq(o2)
        self.push(val)

    def lt(self):
        o2 = self.pop()
        o1 = self.pop()
        assert isinstance(o1, VM_Objspace)
        val = o1.lt(o2)
        self.push(val)

    def jump_if_true(self):
        exp = self.pop()
        if isinstance(exp, Bool):
            return exp.bool_val
        else:
            raise NotImplementedError()

    def jump_if_false(self):
        exp = self.pop()
        if isinstance(exp, Bool):
            return exp.bool_val
        else:
            raise NotImplementedError()

    def var(self, index):
        assert index >= 0
        obj = self.variables[index]
        self.push(obj)

    def new(self, vm):
        obj = Obj()
        vm.heap.append(obj)
        ref = Int(len(vm.heap) - 1)
        self.push(ref)

    def set_field(self, field,  vm):
        value = self.pop()
        obj_ref = self.pop()
        if isinstance(obj_ref, Int):
            obj = vm.heap[obj_ref.int_val]
            obj.set_field(field, value)
        else:
            raise NotImplementedError()

    def get_field(self, field, vm):
        obj_ref = self.pop()
        if isinstance(obj_ref, Int):
            obj = vm.heap[obj_ref.int_val]
            val = obj.get_field(field)
            self.push(val)
        else:
            raise NotImplementedError()

    def jump(self):
        pass

    def swap(self):
        first = self.pop()
        second = self.pop()
        self.push(first)
        self.push(second)

    def assign(self):
        value = self.pop()
        var = self.pop()
        if isinstance(var, Int):
            index = var.int_val
            assert index > 0
            self.variables[index] = value
        else:
            raise NotImplementedError()

    def neq(self):
        o2 = self.pop()
        o1 = self.pop()
        assert isinstance(o1, VM_Objspace)
        val = o1.neq(o2)
        self.push(val)

    def ret(self):
        return (self.return_address, self.caller_frame, self.pop())

class VirtualMachine(object):

    def __init__(self, instructions, fn_var_map, args = None):
        self.instructions = instructions
        self.stack = []
        self.fn_var_map = fn_var_map
        self.heap = []

        if args:
            [self.stack.append(Int(arg)) for arg in args]

    def interp(self, bytecode):
        main_fn_size = self.fn_var_map[0] # FIXME: VERY HACKY
        main_vars = [None] * main_fn_size
        frame = Frame(len(bytecode) + 1, main_vars, None)
        self.stack.append(frame)
        pc = 0

        # Begin program interpreter loop
        while True:
            jitdriver.jit_merge_point(pc=pc, bytecode=bytecode, frame=frame, self=self)
            if pc >= len(bytecode):
                break

            instr = bytecode[pc]

            if instr == CONST_INT:
                frame.push(Int(int(bytecode[pc + 1])))
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
            elif instr == SWAP:
                frame.swap()
            elif instr == NEQ:
                frame.neq()
            elif instr == CALL:
                caller_address = int(bytecode[pc + 1])
                var_size = self.fn_var_map[caller_address]
                frame = self.function_call(frame, pc, var_size)
                pc = caller_address
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
                frame.var(int(bytecode[pc + 1]))
            elif instr == ASSIGN:
                frame.assign()
            elif instr == CONST_STR:
                frame.push(StrLiteral(bytecode[pc + 1]))
            elif instr == EXIT:
                break
            else:
                bail('unknown op_code: %s' % bytecode[pc])

            pc += int(HAS_ARGS[int(instr)]) + 1

        return self.stack.pop()

    def function_call(self, caller_frame, pc, var_size):
        # Invoked on the presence of the CALL opcode.
        # This method will take the values pushed on the caller's stack before
        # the CALL as arguments to the callee and place them inside the newly
        # instantiated frame. It will then push this new frame to the VMs main
        # execution stack.
        return_address = pc + 2
        variables = [None] * var_size
        arg_count = caller_frame.pop()
        if isinstance(arg_count, Int):
            for i in range(arg_count.int_val):
                arg = caller_frame.pop()
                variables[i] = arg
            new_frame = Frame(return_address, variables, caller_frame)
            caller_frame.push(new_frame)
            return new_frame
        else:
            raise NotImplementedError()


    def pop_frame(self):
        frame = self.stack.pop()
        return_value = frame.pop()
        return (frame.return_address, return_value)



