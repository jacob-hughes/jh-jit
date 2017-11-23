# vim: ai ts=4 sts=4 et sw=4
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import unittest
from jhvm.parser import parse_input
from jhvm.genast import generate_bytecode
from jhvm.vm import VirtualMachine as VM
from jhvm.opcodes import *

from jhvm.vm import Int

class TestVirtualMachine(unittest.TestCase):

    def compile(self, source):
        ast = parse_input(source)
        print ast
        bytecode, fn_var_map = generate_bytecode(ast)
        bytecode = [str(op) for op in bytecode]
        print fn_var_map
        return bytecode, fn_var_map

    def run_prog(self, bytecode, fn_var_map):
        machine = VM(bytecode, fn_var_map)
        return machine.interp()

    def test_simple_function_call(self):
        source = """
            fn main() {
                return hello(5)
            }

            fn hello(var) {
                return 50 + var
            }

        """

        bytecode, fn_var_map = self.compile(source)
        res = self.run_prog(bytecode, fn_var_map)
        self.assertEqual(res, Int(55))

    def test_multilevel_function_call(self):
        source = """
            fn main() {
                return b(1, 2)
            }

            fn b(x, y) {
                return c(x, y, 3)
            }

            fn c(x, y, z) {
                return 10 - (x + y + z)
            }
        """

        bytecode, fn_var_map = self.compile(source)
        res = self.run_prog(bytecode, fn_var_map)
        self.assertEqual(res, Int(4))

    def test_assign_same_name(self):
        source = """
            fn main() {
                y = 5;
                z = 20;
                x = y = z + 10;
                x = x + y;
                return x
            }
        """
        bytecode, fn_var_map = self.compile(source)
        res = self.run_prog(bytecode, fn_var_map)
        self.assertEqual(res, Int(60))

    def test_for_loop(self):
        source = """
            fn main() {
                x = 10;
                for(i = 0; i < 100; i = i + 1) {
                    x = x + 1
                };
                return x
            }
        """

        bytecode, fn_var_map = self.compile(source)
        res = self.run_prog(bytecode, fn_var_map)
        self.assertEqual(res, Int(110))

    def test_simple_object(self):
        source = """
            fn main() {
                x = object();
                x.hello = 5;
                return x.hello
            }
        """
        bytecode, fn_var_map = self.compile(source)
        res = self.run_prog(bytecode, fn_var_map)
        self.assertEqual(res, Int(5))

    def test_object_across_funcs(self):
        source = """
            fn main() {
                x = object();
                return f(x)
            }

            fn f(x) {
                x.bye = 10;
                x.hello = x.bye;
                return x.hello + x.bye
            }
        """
        bytecode, fn_var_map = self.compile(source)
        res = self.run_prog(bytecode, fn_var_map)
        self.assertEqual(res, Int(20))

    def test_if_statement(self):
        source = """
            fn main() {
                if(1 == 1) {
                    x = 1
                };
                return x
            }
        """
        bytecode, fn_var_map = self.compile(source)
        res = self.run_prog(bytecode, fn_var_map)
        self.assertEqual(res, Int(1))

    def test_if_else_statement(self):
        source = """
            fn main() {
                if(1 == 2) {
                    x = 1
                }
                else {
                    x = 2
                };

                if(2 == 2) {
                    x = x + 1
                }
                else {
                    x = x + 2
                };
                return x
            }
        """
        bytecode, fn_var_map = self.compile(source)
        res = self.run_prog(bytecode, fn_var_map)
        self.assertEqual(res, Int(3))





