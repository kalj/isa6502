#!/usr/bin/python3
#
#

from isa6502 import ISA
import re
import ast
import operator as op

def u8_to_s8(u8val):
    return (u8val+128)%256-128

def s8_to_u8(s8val):
    return s8val % 256

def operand_to_str(addrmode,operand):
    if addrmode == "i":
        arg = ""
    elif addrmode == "A":
        arg = "A"
    # zero-page indexed
    elif addrmode in ["zp", "(zp,x)", "zp,x", "zp,y", "(zp)", "(zp),y"]:
        arg = addrmode.upper().replace("ZP",f"${operand:02x}")
    # absolute indexed
    elif addrmode in ["a", "(a,x)", "a,x", "a,y", "(a)"]:
        arg = addrmode.upper().replace("A",f"${operand:04x}")
    elif addrmode == "#":
        arg = f"#${operand:02x}"
    elif addrmode == "r":
        arg = str(u8_to_s8(operand))
    else:
        raise Exception("Invalid addressing mode:",addrmode)
    return arg

def operand_size(addrmode):
    # no operand
    if addrmode == "i" or addrmode == "A":
        return 0
    # 1-Byte operand
    elif addrmode in ["#", "r", "zp", "(zp,x)", "zp,x", "zp,y", "(zp)", "(zp),y"]:
        return 1
    # 2-Byte operand
    elif addrmode in ["a", "(a,x)", "a,x", "a,y", "(a)"]:
        return 2
    else:
        raise Exception("Invalid addressing mode:",addrmode)

def opcode_to_instr(op):
    if not op in ISA:
        # unknown opcode
        return "UNK"
    else:
        return ISA[op]

def identify_opcode(mnemonic,argfmt):

    mnematches = [(o,i) for o,i in ISA.items() if len(i)>0 and i[0]==mnemonic]

    if len(mnematches) == 0:
        raise SyntaxError(f"Unknown instruction mnemonic: {mnemonic}")

    # try to match address mode

    if 'lbl' in argfmt:
        # we have a label (and only a label)
        matches = [o for o,i in mnematches if i[1] in [argfmt.replace("lbl","r"), argfmt.replace("lbl","a")]]
    else:
        matches = [o for o,i in mnematches if i[1]==argfmt]

    if len(matches) == 0:
        raise SyntaxError(f"Unknown instruction: {mnemonic} {argfmt}")

    if len(matches)>1:
        raise Exception(f'Internal error, multiple instructions matched {mnemonic} {addrfmt}')
        # unknown instruction
        # return 0x00

    return matches[0]

def mnemonic_to_opcode(mnemonic):
    matches = [o for o,instr in ISA.items() if instr[0]==mnemonic]
    if len(matches) != 1:
        raise Exception(f"No unique matching instruction with mnemonic {mnemonic}: {matches}")

    return matches[0]


class Instruction:
    def __init__(self,opcode,operand,label):
        self._opcode = opcode
        self._operand = operand
        self._label = label

    def __str__(self):
        operandstr = operand_to_str(self.get_addrmode(),self._operand)
        return (self.get_mnemonic() + " " + operandstr).strip()

    def get_addrmode(self):
        myop = ISA[self._opcode]
        return myop[1]

    def get_mnemonic(self):
        myop = ISA[self._opcode]
        return myop[0]

    def size(self):
        myop = ISA[self._opcode]
        return 1+operand_size(self.get_addrmode())

    def encode(self):
        bs = [self._opcode]

        opsize = operand_size(self.get_addrmode())
        if opsize == 1:
            bs.append(self._operand)
        elif opsize == 2:
            bs.extend([self._operand & 0xff, (self._operand >>8) & 0xff])
        return bs

    def resolve_label(self,label_addresses,my_address):
        if self._label:
            if self.get_addrmode() == "r":
                # special case for program-counter-relative address mode

                # pc is incremented before jump, add size of this instruction
                pc_address = (my_address+self.size())

                if not self._label in label_addresses:
                    raise SyntaxError(f"Unknown label: {self._label}")
                branch_offset = label_addresses[self._label] - pc_address

                if branch_offset > 127 or branch_offset < -128:
                    raise SyntaxError("Out of range branch (branches are limited to -128 to +127)")

                branch_offset = (branch_offset+256) % 256 # convert to unsigned

                self._operand = branch_offset
            else:
                self._operand = label_addresses[self._label]


class Data:
    def __init__(self,bs):
        self._bytes = bs

    def __str__(self):
        return ".bytes "+str(self._bytes)

    def size(self):
        return len(self._bytes)

    def encode(self):
        return self._bytes


class SyntaxError(Exception):
    def __init__(self,message):
        super().__init__(message)
        self._linum = None

    def set_linum(self,linum):
        self._linum = linum

    def get_linum(self):
        return self._linum

#====================================================================
# Simple mathematical expression parser and evaluator
#====================================================================

# supported operators
operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.BitAnd: op.and_, ast.BitOr: op.or_, ast.Invert: op.invert,
             ast.USub: op.neg}

def eval_(node):
    if isinstance(node, ast.Num): # <number>
        return node.n
    elif isinstance(node, ast.Name): # <variable>
       if not node.id in variables:
           raise SyntaxError(f"unknown variable in expression: {node.id}")
       return variables[node.id]
    elif isinstance(node, ast.BinOp): # <left> <operator> <right>
        return operators[type(node.op)](eval_(node.left), eval_(node.right))
    elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
        return operators[type(node.op)](eval_(node.operand))
    else:
        raise TypeError(node)

def evaluate_constant_expression(expr):
    # replace hexadecimal (prefix $), and binary (prefix %) literals
    # which are incompatible with expected python syntax of ast
    while m := re.search("\$[0-9ABCDEFabcdef]+",expr):
        oldlit = m.group(0)
        newlit = str(int(oldlit[1:],16))
        expr = expr.replace(oldlit, newlit)

    while m := re.search("%[01]+",expr):
        oldlit = m.group(0)
        newlit = str(int(oldlit[1:],2))
        expr = expr.replace(oldlit, newlit)

    return eval_(ast.parse(expr, mode='eval').body)

# ===================================================================
# prune
#
# remove comments and empty lines
# ===================================================================

def prune(src_in):
    src_out = []
    for i,line in enumerate(src_in):
        idx = line.find(";")
        if idx>=0:
            l = line[:idx]
        else:
            l = line

        l = l.strip()
        if len(l) == 0:
            continue

        src_out.append((l,i))
    return src_out

# ===================================================================
# preprocess
#
# gather variable definitions, and replaces references with values
# ===================================================================

class PreprocessorError(Exception):
    def __init__(self,message, linum):
        super().__init__(message)
        self._linum = linum

    def get_linum(self):
        return self._linum


def replace_variable_references(s, variables):
    for name in variables:
        val = variables[name]
        s = re.sub(r'\b'+name+r'\b', val,  s)

    return s

def preprocess(src_in):
    variables = {}
    src_out = []
    for line,linum in src_in:

        if m := re.match("^#define ([a-zA-Z_]\w*)\s+(.*)$",line):
            # variable definition
            name = m.group(1)
            if name in variables:
                raise PreprocessorError(f"Redefinition of variable '{name}'", linum)

            value = m.group(2)
            variables[name] = replace_variable_references(value, variables)
        else:
            line = replace_variable_references(line, variables)
            src_out.append((line,linum))

    return src_out


# ===================================================================
# Parse statements (instructions and data directives)
# ===================================================================

local_label_prefix='@'

def parse_parameter(param):

    label_regex = '^'+local_label_prefix+'?[a-zA-Z_]\w*$'

    if re.match(label_regex,param):
        # Found a label. Implies a 2-byte address, i.e. "a". Just
        # return the label, the address will be resolved later.
        return "lbl",param
    else:
        try:
            val = evaluate_constant_expression(param)
        except:
            raise SyntaxError(f"Failed parsing parameter expression: {param}")

        if val > 255:
            return "a",val
        else:
            return "zp",val

def parse_argument(arg):

    if len(arg)==0:
        return "i",None

    if re.match("^#",arg):
        param_type,val = parse_parameter(arg[1:])
        if param_type != "zp":
            raise SyntaxError(f"Too large literal in immediate addressing: {val}")
        return "#", val

    if arg == "A":
        return "A",None

    # match stuff like (<expr>) and (label)

    if m := re.match("^\(([^,]+)\)$",arg):
        param_type,val = parse_parameter(m.group(1))
        return f"({param_type})", val

    # match stuff like (<expr>,X) and (label,X)

    if m := re.match("^\(([^,]+),(X)\)$",arg):
        param_type,val = parse_parameter(m.group(1))
        return f"({param_type},x)",val

    # match stuff like (<expr>),Y
    if m := re.match("^\((.+)\),(Y)$",arg):
        param_type,val = parse_parameter(m.group(1))
        if param_type != "zp":
            raise SyntaxError("Invalid format of base literal for Zero Page Indirect Indexed operand string:",arg)
        return "(zp),y",val

    # match stuff like <expr>,X and label,Y
    m = re.match("^([^,]+),([XY])$",arg)
    if m:
        o1 = m.group(1)
        o2 = m.group(2)

        param_type,val = parse_parameter(o1)
        offset = o2.lower()

        return f"{param_type},{offset}",val

    # else:
    # match label or expression)
    param_type,val = parse_parameter(arg)
    return param_type,val

    # # default - Invalid addressing mode
    # raise SyntaxError(f"Invalid operand string: {arg}")


def parse_instruction(source_line, current_nonlocal_label):
    mnemonic = source_line[0:3].upper()
    arg_fmt, param = parse_argument(source_line[3:].strip())

    opcode = identify_opcode(mnemonic,arg_fmt)

    if type(param) == str:
        # param is a label
        label=param
        if label[0] == local_label_prefix:
            label = current_nonlocal_label+label

        return Instruction(opcode,None,label)
    else:
        return Instruction(opcode,param,None)


def parse_constant(s):
    try:
        if s[0] == "$":
            v = int(s[1:],16)
        elif s[0] == "%":
            v = int(s[1:],2)
        else:
            v = int(s)
    except:
        raise SyntaxError(f"Invalid constant token: {s}")

    return v


def parse_byte(s):
    v = parse_constant(s)

    if v > 255 or v<-128:
        raise SyntaxError(f"Integer value of token out of 8-bit range: {s}")

    # convert to unsigned
    v = (v+256) % 256

    return v


def parse_word(s):
    v = parse_constant(s)

    if v >= (1<<16) or v<0:
        raise SyntaxError(f"Word/address token does not fit in an unsigned 16-bit value: {s}")

    return v


def parse_string(s):
   if s[0] != '"' or s[-1] != '"':
       raise SyntaxError("Not a valid ascii string")

   try:
       the_string=s[1:-1]
       the_string=the_string.replace('\\n', '\n').replace('\\t', '\t')
       return the_string.encode()
   except:
       raise SyntaxError("Failed encoding ascii string")


def parse_statement(line, current_nonlocal_label):

    if line.startswith(".byte "):
        bytez = [parse_byte(a.strip()) for a in line[5:].split(",")]
        return Data(bytes(bytez))

    elif line.startswith(".word ") or line.startswith(".address "):
        bstr=line[line.find(' '):]
        bytez = []
        for w in bstr.split(","):
            word = parse_word(w.strip())
            bytez.extend([word & 0xff, (word >>8) & 0xff])
        return Data(bytes(bytez))

    elif line.startswith(".ascii "):
        # ascii string
        bytez = parse_string(line[6:].strip())
        return Data(bytez)
    elif line.startswith(".asciiz "):
         # null-terminated ascii string
        bytez = parse_string(line[7:].strip())
        return Data(bytez+b'\0') # append null byte
    else:
        return parse_instruction(line, current_nonlocal_label)

# ===================================================================
# Assembly functions
# ===================================================================

def parse_lines(source):

    statements = []

    label_regex='^('+local_label_prefix+'?[a-zA-Z_]\w*):(.*)$'

    labels={}
    current_labels = []
    src_out = []
    current_nonlocal_label = None

    for line,linum in source:

        m = re.match(label_regex,line)
        if m:
            current_labels.append((m.group(1), linum))
            line = m.group(2).strip()

        if not line:
            # line was empty, i.e. there was nothin after the label
            continue

        if current_labels:
            for l,ln in current_labels:

                if l[0] == local_label_prefix:
                    l = current_nonlocal_label+l
                else:
                    current_nonlocal_label = l

                if l in labels:
                    label_linum=labels[l]['linum']
                    e = SyntaxError(f"Duplicate label '{l}', first label at {label_linum}")
                    e.set_linum(ln)
                    raise e
                labels[l] = {'idx':len(statements), 'linum':ln}
            current_labels = []

        try:
            s = parse_statement(line, current_nonlocal_label)
            statements.append(s)
        except SyntaxError as e:
            e.set_linum(linum)
            raise e

    if current_labels:
        e = SyntaxError("Label at end of file")
        e.set_linum(source[-1][1])
        raise e

    labels = { k:v['idx'] for k,v in labels.items() }

    return statements, labels


def resolve_labels(statements,labels,base_address):

    byte_offset = base_address
    addresses = []

    for stmt in statements:
        addresses.append(byte_offset)
        byte_offset += stmt.size()

    label_addresses = {l:addresses[idx] for l,idx in labels.items()}

    for stmt,addr in zip(statements,addresses):

        if isinstance(stmt,Instruction):
            stmt.resolve_label(label_addresses,addr)

    return statements


def assemble(raw_source, base_address):
    # prune
    source_lines = prune(raw_source)

    source_lines = preprocess(source_lines)

    # Harvest labels & parse statements
    statements, labels = parse_lines(source_lines)

    statements = resolve_labels(statements,labels,base_address)

    return statements

def encode_program(statements):
    ops = []
    for stmt in statements:
        ops.extend(stmt.encode())

    return bytes(ops)


# ===================================================================
# Disassembly (decoding) functions
# ===================================================================

def decode_operand(operand_bytes):
    if len(operand_bytes) == 2:
        return operand_bytes[0]+(operand_bytes[1]<<8)
    elif len(operand_bytes) == 1:
        return operand_bytes[0]
    else:
        return None

def decode_instruction(bytes_in):
    opcode = bytes_in[0]
    if not opcode in ISA:
        raise Exception(f"Unknown opcode: 0x{opcode:02x}")
    addrmode = ISA[opcode][1]
    operand_bytes = bytes_in[1:1+operand_size(addrmode)]
    operand = decode_operand(operand_bytes)
    return Instruction(opcode,operand,None)

def disassemble(prog):
    statements = []
    bytesize = len(prog)
    bytenum=0
    while bytenum < bytesize:
        try:
            instr = decode_instruction(prog[bytenum:])
            instr_size = instr.size()
            instr_bytes = prog[bytenum:(bytenum+instr_size)]
            statements.append((bytenum,instr_bytes,instr))
            bytenum += instr_size
        except:
            # data directive
            statements.append((bytenum, [prog[bytenum]], None))
            bytenum += 1
    return statements
