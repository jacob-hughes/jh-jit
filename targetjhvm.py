# vim: ai ts=4 sts=4 et sw=4
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import sys
from jhvm.vm import VirtualMachine
from jhvm.opcodes import EOB
from rpython.rlib.streamio import open_file_as_stream
def usage():
    print 'Usage: target-vm compiled-bytecode'
    return 1

def entry_point(argv):
    if len(argv) < 1:
        usage()

    filename = argv[1]
    lines = open_file_as_stream(argv[1]).readall().splitlines()
    bytecode = []
    break_line = 0
    for i, line in enumerate(lines):
        if line == EOB:
            break_line = i
            break
        bytecode.append(line)

    var_count = {}
    for line in lines[break_line + 1:]:
        k,v = line.split(',')
        var_count.update({int(k):int(v)})

    machine = VirtualMachine(bytecode, var_count)
    res = machine.interp(bytecode)
    print res
    return 0

def target(*args):
    return entry_point

if __name__ == '__main__':
    entry_point(sys.argv)



