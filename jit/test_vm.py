# gim: ai ts=4 sts=4 et sw=4
# -*- coding: utf-8 -*-

import unittest
from vm import Obj, Int, Bool, Reference, VM
import opcodes

class MockVM(VM):

    def __init__(self, stack = None, heap = None):
        self.stack = stack if stack else []
        self.heap = heap if heap else []
        self.pc = 0

class TestVM(unittest.TestCase):
    # Test vm methods which map to opcodes. Contains only simple unit tests.
    # For a more comprehensive list of tests see integration tests.

    def assertOpcodeWorks(self,
                            op_code,
                            stack_before,
                            stack_after,
                            arg = None,
                            ret_val = None,
                            expected_pc = None,
                            heap_before = None,
                            heap_after = None):
        vm = MockVM(stack = stack_before)
        op_name = opcodes.OP_CODES[op_code].lower()
        method = getattr(vm, op_name)
        if arg:
            returned = method(arg)
        else:
            returned = method()
        if ret_val:
            self.assertEqual(returned, ret_val)

        if expected_pc:
            self.assertEqual(vm.get_pc(), expected_pc)

        self.assertEqual(vm.stack, stack_after)

    def test_push(self):
        self.assertOpcodeWorks(
            op_code = opcodes.PUSH,
            arg = Int(5),
            stack_before = [],
            stack_after = [Int(5)],
        )

    def test_pop(self):
        self.assertOpcodeWorks(
            op_code = opcodes.POP,
            stack_before = [Int(5)],
            stack_after = [],
            ret_val = Int(5)
        )

    def test_const(self):
        self.assertOpcodeWorks(
            op_code = opcodes.CONST_INT,
            arg = 5,
            stack_before = [],
            stack_after = [Int(5)],
        )

    def test_add(self):
        self.assertOpcodeWorks(
            op_code = opcodes.ADD,
            stack_before = [Int(1), Int(2)],
            stack_after = [Int(3)],
        )

    def test_sub(self):
        self.assertOpcodeWorks(
            op_code = opcodes.SUB,
            stack_before = [Int(5), Int(2)],
            stack_after = [Int(3)],
        )

    def test_eq(self):
        self.assertOpcodeWorks(
            op_code = opcodes.EQ,
            stack_before = [Int(5), Int(5)],
            stack_after = [Int(1)],
        )

        self.assertOpcodeWorks(
            op_code = opcodes.EQ,
            stack_before = [Int(5), Int(6)],
            stack_after = [Int(0)],
        )

    def test_lt(self):
        self.assertOpcodeWorks(
            op_code = opcodes.LT,
            stack_before = [Int(3), Int(5)],
            stack_after = [Int(1)],
        )

        self.assertOpcodeWorks(
            op_code = opcodes.LT,
            stack_before = [Int(7), Int(6)],
            stack_after = [Int(0)],
        )

    def test_jump_if_true(self):
        self.assertOpcodeWorks(
            op_code = opcodes.JUMP_IF_TRUE,
            arg = 5,
            stack_before = [Bool(True)],
            stack_after = [],
            ret_val = True,
            expected_pc = 5
        )

        self.assertOpcodeWorks(
            op_code = opcodes.JUMP_IF_TRUE,
            arg = 5,
            stack_before = [Bool(False)],
            stack_after = [],
            ret_val = False,
        )

    def test_new(self):
        self.assertOpcodeWorks(
            op_code = opcodes.NEW,
            stack_before = [],
            stack_after = [Reference(0)],
        )

    def test_set_field(self):
        vm = MockVM(stack = [Reference(0),Int(1),Int(5)], heap = [Obj()])
        vm.set_field()
        self.assertEqual(vm.heap[0], Obj(fields = [None, Int(5)]))
        self.assertEqual(vm.stack, [])


    def test_get_field(self):
        vm = MockVM(stack = [Reference(0),Int(1)], heap = [Obj([Int(2),Int(5)])])
        vm.get_field()
        self.assertEqual(vm.stack, [Int(5)])

    def test_dup(self):
        self.assertOpcodeWorks(
            op_code = opcodes.DUP,
            stack_before = [Int(5)],
            stack_after = [Int(5),Int(5)],
        )

if __name__ == '__main__':
    unittest.main()


