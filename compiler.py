# vim: ai ts=4 sts=4 et sw=4
# -*- coding: utf-8 -*-
import sys
from jhvm.parser import parse_input
from jhvm.genast import generate_bytecode

def usage():
    print >> sys.stderr, 'Usage: compiler.py filename.jh'
    sys.exit(1)

def main():
    if len(sys.argv) != 2:
        usage()

    filename = sys.argv[1]
    if not filename.endswith('.jh'):
        usage()

    with open(filename) as f:
        source_code = f.read()

    ast = parse_input(source_code)
    bytecode = generate_bytecode(ast)

    outname = filename[:-len('.jh')]
    with open(outname, 'wb') as f:
        for op in bytecode:
            f.write('%s\n' % op)
    print '%s successfully compiled.' % outname

if __name__ == '__main__':
    main()


