#!/usr/bin/python3
#
#

from isa6502 import ISA
import re
from lark import Lark, Transformer, v_args, Tree
from lark.exceptions import VisitError
import intelhex

class SyntaxError(Exception):
    def __init__(self,message, linum=None):
        super().__init__(message)
        self._linum = linum

    def set_linum(self,linum):
        self._linum = linum

    def get_linum(self):
        return self._linum

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
    possible_modes = [argfmt]

    if 'zp' in argfmt:
        possible_modes.append(argfmt.replace("zp","a"))

    if "zp" in possible_modes or "a" in possible_modes:
        possible_modes.append("r")

    matches = [o  for m in possible_modes for o,i in mnematches if i[1] == m]

    if len(matches) == 0:
        raise SyntaxError(f"Unknown instruction: {mnemonic} {argfmt}")

    return matches[0]

def mnemonic_to_opcode(mnemonic):
    matches = [o for o,instr in ISA.items() if instr[0]==mnemonic]
    if len(matches) != 1:
        raise Exception(f"No unique matching instruction with mnemonic {mnemonic}: {matches}")

    return matches[0]

def word_to_bytes(word):
    return [word & 0xff, (word >>8) & 0xff]

class Instruction:
    def __init__(self,opcode,operand, linum, current_nonlocal_label):
        self._opcode = opcode
        self._address = None
        self._linum = linum

        if isinstance(operand, Tree):
            for label_tok in operand.scan_values(lambda v: v.type == 'LABEL'):
                if label_tok.value[0] == '@':
                    label_tok.value = current_nonlocal_label+label_tok.value

        self._operand = operand

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
            bs.extend(word_to_bytes(self._operand))
        return bs

    def set_address(self, my_address):
        self._address = my_address

    def resolve_labels(self,label_addresses):
        if self._address is None:
            raise RuntimeError('resolve_labels requires address to be set')

        if isinstance(self._operand, Tree):
            try:
                self._operand = evaluate_expression(self._operand, label_addresses)
            except SyntaxError as e:
                e.set_linum(self._linum)
                raise e

        if self.get_addrmode() == "r":
            # special case for program-counter-relative address mode

            # pc is incremented before jump, add size of this instruction
            pc_address = (self._address+self.size())

            branch_offset = self._operand - pc_address

            if branch_offset > 127 or branch_offset < -128:
                raise SyntaxError("Out of range branch (branches are limited to -128 to +127)", self._linum)

            branch_offset = (branch_offset+256) % 256 # convert to unsigned

            self._operand = branch_offset


class ByteData:
    def __init__(self,bs):
        self._bytes = bs

    def __str__(self):
        return ".bytes "+str(self._bytes)

    def size(self):
        return len(self._bytes)

    def set_address(self, my_address):
        pass

    def encode(self):
        return self._bytes

    def resolve_labels(self, label_addresses):
        pass

class WordData:
    def __init__(self,ws):
        self._words = ws

    def __str__(self):
        return ".words "+', '.join(f'${w:04x}' for w in self._words)

    def size(self):
        return len(self._words) * 2

    def set_address(self, my_address):
        pass

    def encode(self):
        bs = []
        for w in self._words:
            bs.extend(word_to_bytes(w))
        return bs

    def resolve_labels(self, label_addresses):
        for i in range(len(self._words)):
            self._words[i] = evaluate_expression(self._words[i], label_addresses)


#====================================================================
# Simple mathematical expression parser and evaluator
#====================================================================

calc_grammar = """
    ?start: sum

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div
        | product "|" atom  -> or_
        | product "&" atom  -> and_
        | product "<<" atom  -> lshift
        | product ">>" atom  -> rshift

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | ">" atom         -> hi_byte
         | "<" atom         -> lo_byte
         | "~" atom         -> inv
         | LABEL            -> label
         | "(" sum ")"

    LABEL: NAME | "@" NAME
    DIGIT: "0".."9"
    HEXDIGIT: "a".."f"|"A".."F"|DIGIT
    BINDIGIT: "0".."1"
    NUMBER: DIGIT+ | "$" HEXDIGIT+ | "%" BINDIGIT+

    %import common.CNAME -> NAME
    %import common.WS_INLINE

    %ignore WS_INLINE
"""
parser  = Lark(calc_grammar, parser='lalr')

@v_args(inline=True)    # Affects the signatures of the methods
class CalculateTree(Transformer):
    from operator import add, sub, mul, floordiv as div, neg, lshift, rshift, inv, or_, and_

    def __init__(self, labels):
        self._labels = labels

    def number(self, v):
        if v[0] == '$':
            return int(v[1:],16)
        elif v[0] == '%':
            return int(v[1:],2)
        else:
            return int(v)

    def label(self, name):
        try:
            return self._labels[name.value]
        except KeyError:
            raise SyntaxError(f"label {name.value} not defined")

    def hi_byte(self, v):
        return (v >> 8) & 0xff

    def lo_byte(self, v):
        return v & 0xff

def parse_expression(expr):
    return parser.parse(expr)

def evaluate_expression(expr_tree, labels):
    evaluator = CalculateTree(labels)
    try:
        return evaluator.transform(expr_tree)
    except VisitError as e:
        raise e.orig_exc

def expression_size(expr_tree):
    try:
        value = evaluate_expression(expr_tree, {})
        if value > 255:
            return 2
        else:
            return 1
    except:
        if expr_tree.data in ['lo_byte', 'hi_byte']:
            return 1
        else:
            return 2

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

    tree = parse_expression(param)

    # check size of result
    if expression_size(tree) == 1:
        param_type = "zp"
    else:
        param_type = "a"

    return param_type, tree


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
    # match label or expression
    param_type,val = parse_parameter(arg)
    return param_type,val


def parse_instruction(source_line, linum, current_nonlocal_label):
    mnemonic = source_line.split()[0].upper()
    mnemonic_len = len(mnemonic)
    arg_fmt, param = parse_argument(source_line[mnemonic_len:].strip())

    opcode = identify_opcode(mnemonic,arg_fmt)

    return Instruction(opcode, param, linum, current_nonlocal_label)


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

    return parse_expression(s)


def parse_string(s):
   if s[0] != '"' or s[-1] != '"':
       raise SyntaxError("Not a valid ascii string")

   try:
       the_string=s[1:-1]
       the_string=the_string.replace('\\n', '\n').replace('\\t', '\t')
       return the_string.encode()
   except:
       raise SyntaxError("Failed encoding ascii string")


# ===================================================================
# Assembly functions
# ===================================================================

def parse_lines(source):

    global_statement_count = 0
    sections = []
    statements = []
    base_address = 0;

    label_regex='^('+local_label_prefix+'?[a-zA-Z_]\w*):(.*)$'

    labels={}
    current_labels = []
    src_out = []
    current_nonlocal_label = None

    for line,linum in source:

        m = re.match(label_regex,line)
        if m:
            lbl = m.group(1)

            if lbl[0] == local_label_prefix:
                if current_nonlocal_label is None:
                    raise SyntaxError(f"Local label '{lbl}' with no preceeding non-local label", linum)
                lbl = current_nonlocal_label+lbl
            else:
                current_nonlocal_label = lbl

            current_labels.append((lbl, linum))
            line = m.group(2).strip()

        if not line:
            # line was empty, i.e. there was nothin after the label
            continue

        try:
            # Parse statement

            if line.startswith(".org "):
                arg = line[4:].strip()
                expr = parse_expression(arg)
                org_address = evaluate_expression(expr,{})

                if len(statements) > 0:
                    # save previous section
                    sections.append({'base_address':base_address, 'statements':statements})

                base_address = org_address
                statements = []

                s = None # no "statement"

            elif line.startswith(".byte "):
                bytez = [parse_byte(a.strip()) for a in line[5:].split(",")]
                s = ByteData(bytes(bytez))

            elif line.startswith(".word ") or line.startswith(".address "):
                wstr=line[line.find(' '):]
                words = []
                for w in wstr.split(","):
                    words.append(parse_word(w.strip()))
                s = WordData(words)

            elif line.startswith(".ascii "):
                # ascii string
                bytez = parse_string(line[6:].strip())
                s = ByteData(bytez)
            elif line.startswith(".asciiz "):
                # null-terminated ascii string
                bytez = parse_string(line[7:].strip())
                s = ByteData(bytez+b'\0') # append null byte
            else:
                s = parse_instruction(line, linum, current_nonlocal_label)

        except SyntaxError as e:
            e.set_linum(linum)
            raise e

        if not s is None:
            statements.append(s)

            if current_labels:
                for l,ln in current_labels:
                    if l in labels:
                        label_linum=labels[l]['linum']
                        raise SyntaxError(f"Duplicate label '{l}', first label at {label_linum}",ln)

                    labels[l] = {'global_statement_idx':global_statement_count, 'linum':ln}
                current_labels = []

            global_statement_count += 1

    if len(statements) > 0:
        # save last section if non-empty
        sections.append({'base_address':base_address, 'statements':statements})

    if current_labels:
        label_linum = source[-1][1]
        raise SyntaxError("Label at end of file", label_linum)

    # remove line numbers used for debugging
    labels = { k:v['global_statement_idx'] for k,v in labels.items() }

    return sections, labels


def resolve_labels(sections,labels):

    addresses = []

    for section in sections:
        byte_offset = section['base_address']

        for stmt in section['statements']:
            addresses.append(byte_offset)
            stmt.set_address(byte_offset)
            byte_offset += stmt.size()

    label_addresses = {l:addresses[idx] for l,idx in labels.items()}

    for section in sections:
        for stmt in section['statements']:
            stmt.resolve_labels(label_addresses)

    return sections


def assemble(raw_source):
    # prune
    source_lines = prune(raw_source)

    source_lines = preprocess(source_lines)

    # Harvest labels & parse statements
    sections, labels = parse_lines(source_lines)

    sections = resolve_labels(sections,labels)

    return sections

def encode_program(sections):
    prog_sections = []
    for section in sections:
        prog_bytes = []
        for stmt in section['statements']:
            prog_bytes.extend(stmt.encode())

        prog_sections.append({'bytes':prog_bytes, 'base_address':section['base_address']})

    prog_sections.sort(key=lambda s: s['base_address'])

    for i in range(1,len(prog_sections)):
        cur_sect = prog_sections[i]
        prev_sect = prog_sections[i-1]

        section_start = cur_sect['base_address']
        prev_section_end = prev_sect['base_address']+len(prev_sect['bytes'])-1

        if section_start <= prev_section_end:
            raise Exception(f"Section starting at {section_start:x} overlaps with previous section ending at {prev_section_end:x}!")

    return prog_sections


def program_sections_to_binary(prog_sections, binary_start_address, fillbyte=0):
    binary = []

    prev_section_end = binary_start_address
    for section in prog_sections:
        section_start=section['base_address']
        gap_size = section_start - prev_section_end

        # Fill any gap
        binary.extend([fillbyte]*gap_size)

        binary.extend(section['bytes'])
        prev_section_end = section_start + len(section['bytes'])

    return bytes(binary)


def program_sections_to_hex(prog_sections, hex_start_address):

    ih = intelhex.IntelHex()

    for section in prog_sections:
        ih.puts(section['base_address']-hex_start_address, bytes(section['bytes']))

    return ih


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
    return Instruction(opcode,operand,None,None)

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
