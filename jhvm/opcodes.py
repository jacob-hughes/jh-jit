# vim: ai ts=4 sts=4 et sw=4
# -*- coding: utf-8 -*-

# =============================================================================
# OP_CODES
#
# Description of opcode, followed by [before] -> [after] of stack in order
# args are left to right where rightmost is most recent stack value
# =============================================================================

OP_CODES = []
HAS_ARGS = []

# load onto stack an integer constant
# -> int obj
CONST_INT = "0"
OP_CODES.append('CONST_INT')
HAS_ARGS.append(True)

# pushes argument onto stack
# -> val
PUSH = "1"
OP_CODES.append('PUSH')
HAS_ARGS.append(True)

# Returns and removes the item at the top of the stack
# val ->
POP = "2"
OP_CODES.append('POP')
HAS_ARGS.append(False)

# Pops the item at the top, evaluates it, if true will jump to label given as arg.
# val ->
JUMP_IF_TRUE = "3"
OP_CODES.append('JUMP_IF_TRUE')
HAS_ARGS.append(True)

# Pops top 2 elements from stack, pushes result of their addition
# val, val - > val
ADD = "4"
OP_CODES.append('ADD')
HAS_ARGS.append(False)

# Pops top 2 elements from stack, pushes result of last - first
# val, val  -> val
SUB = "5"
OP_CODES.append('SUB')
HAS_ARGS.append(False)

# Compares top 2 elements from stack, pushes result of equality comparison
# val, val -> val, val, val
EQ = "6"
OP_CODES.append('EQ')
HAS_ARGS.append(False)

# Compares top 2 elements from stack, pushes result of last value greater than first
# val, val -> val, val, val
LT = "7"
OP_CODES.append('LT')
HAS_ARGS.append(False)

# Instantiates new object, pushes heap reference on stack.
# -> objectref
NEW = "8"
OP_CODES.append('NEW')
HAS_ARGS.append(False)

# Assigns value to object's field identified by value, field index and object ref on the stack
# objectref, index, val ->
SET_FIELD = "9"
OP_CODES.append('SET_FIELD')
HAS_ARGS.append(True)

# Pops field index and objectref and returns object's field value
# index, objectref -> val
GET_FIELD = "10"
OP_CODES.append('GET_FIELD')
HAS_ARGS.append(True)

# Duplicates the value on the top of the stack
# val -> val, val
DUP = "11"
OP_CODES.append('DUP')
HAS_ARGS.append(False)

EXIT = "12"
OP_CODES.append('EXIT')
HAS_ARGS.append(False)

JUMP = "13"
OP_CODES.append('JUMP')
HAS_ARGS.append(True)

SWAP = "14"
OP_CODES.append('SWAP')
HAS_ARGS.append(False)

NEQ = "15"
OP_CODES.append('NEQ')
HAS_ARGS.append(False)

CALL = "16"
OP_CODES.append('CALL')
HAS_ARGS.append(True)

RET = "17"
OP_CODES.append('RET')
HAS_ARGS.append(False)

ASSIGN = "18"
OP_CODES.append('ASSIGN')
HAS_ARGS.append(False)

VAR = "19"
OP_CODES.append('VAR')
HAS_ARGS.append(True)

CONST_STR = "20"
OP_CODES.append('CONST_STR')
HAS_ARGS.append(True)

JUMP_IF_FALSE = "21"
OP_CODES.append('JUMP_IF_FALSE')
HAS_ARGS.append(True)

START_ITER = "22"
OP_CODES.append('START_ITER')
HAS_ARGS.append(False)

BINOP_TO_OPCODE = {
    'ADD' : ADD,
    'SUB' : SUB,
    'EQ' : EQ,
    'LT' : LT
}

EOB = ':__EOB__:'
