import re
import ast
import operator as op

ISA = {
    # Misc implied
    0xdb:("STP","i"),
    0xea:("NOP","i"),

    # LDA
    0xad:("LDA","a"),
    0xbd:("LDA","a,x"),
    0xb9:("LDA","a,y"),
    0xa9:("LDA","#"),
    0xa5:("LDA","zp"),
    0xa1:("LDA","(zp,x)"),
    0xb5:("LDA","zp,x"),
    0xb2:("LDA","(zp)"),
    0xb1:("LDA","(zp),y"),

    # STA
    0x8d:("STA","a"),
    0x9d:("STA","a,x"),
    0x99:("STA","a,y"),
    0x85:("STA","zp"),
    0x81:("STA","(zp,x)"),
    0x95:("STA","zp,x"),
    0x91:("STA","(zp),y"),
    0x92:("STA","(zp)"),

    # ADC
    0x6d:("ADC", "a"),
    0x7d:("ADC", "a,x"),
    0x79:("ADC", "a,y"),
    0x69:("ADC", "#"),
    0x65:("ADC", "zp"),
    0x61:("ADC", "(zp,x)"),
    0x75:("ADC", "zp,x"),
    0x72:("ADC", "(zp)"),
    0x71:("ADC", "(zp),y"),

    # SBC
    0xed:("SBC", "a"),
    0xfd:("SBC", "a,x"),
    0xf9:("SBC", "a,y"),
    0xe9:("SBC", "#"),
    0xe5:("SBC", "zp"),
    0xe1:("SBC", "(zp,x)"),
    0xf5:("SBC", "zp,x"),
    0xf2:("SBC", "(zp)"),
    0xf1:("SBC", "(zp),y"),


    # EOR
    0x4d:("EOR","a"),
    0x5d:("EOR","a,x"),
    0x59:("EOR","a,y"),
    0x49:("EOR","#"),
    0x45:("EOR","zp"),
    0x41:("EOR","(zp,x)"),
    0x55:("EOR","zp,x"),
    0x52:("EOR","(zp)"),
    0x51:("EOR","(zp),y"),

    # AND
    0x2d:("AND","a"),
    0x3d:("AND","a,x"),
    0x39:("AND","a,y"),
    0x29:("AND","#"),
    0x25:("AND","zp"),
    0x21:("AND","(zp,x)"),
    0x35:("AND","zp,x"),
    0x32:("AND","(zp)"),
    0x31:("AND","(zp),y"),

    # INC
    0x1a:("INC","A"),
    0xe6:("INC","zp"),
    0xf6:("INC","zp,x"),
    0xee:("INC","a"),
    0xfe:("INC","a,x"),

    # DEC
    0xce:("DEC","a"),
    0xde:("DEC","a,x"),
    0x3a:("DEC","A"),
    0xc6:("DEC","zp"),
    0xd6:("DEC","zp,x"),

    # Branches
    0xf0:("BEQ","r"),
    0xd0:("BNE","r"),
    0xb0:("BCS","r"),
    0x90:("BCC","r"),
    0x80:("BRA","r"),
    0x30:("BMI","r"),


    # CMP
    0xcd:("CMP","a"),
    0xdd:("CMP","a,x"),
    0xd9:("CMP","a,y"),
    0xc9:("CMP","#"),
    0xc5:("CMP","zp"),
    0xc1:("CMP","(zp,x)"),
    0xd5:("CMP","zp,x"),
    0xd2:("CMP","(zp)"),
    0xd1:("CMP","(zp),y"),

    # CPX
    0xec:("CPX","a"),
    0xe0:("CPX","#"),
    0xe4:("CPX","zp"),

    # CPY
    0xcc:("CPY","a"),
    0xc0:("CPY","#"),
    0xc4:("CPY","zp"),

    # LDX
    0xae:("LDX","a"),
    0xbe:("LDX","a,y"),
    0xa2:("LDX","#"),
    0xa6:("LDX","zp"),
    0xb6:("LDX","zp,y"),

    # STX
    0x8e:("STX","a"),
    0x86:("STX","zp"),
    0x96:("STX","zp,y"),

    # LDY
    0xac:("LDY","a"),
    0xbc:("LDY","a,x"),
    0xa0:("LDY","#"),
    0xa4:("LDY","zp"),
    0xb4:("LDY","zp,x"),

    # STY
    0x8c:("STY","a"),
    0x84:("STY","zp"),
    0x94:("STY","zp,x"),

    # INX
    0xe8:("INX","i"),

    # DEX, DEY
    0xca:("DEX","i"),
    0x88:("DEY","i"),

    # ASL
    0x0e:("ASL","a"),
    0x1e:("ASL","a,x"),
    0x0A:("ASL","A"),
    0x06:("ASL","zp"),
    0x16:("ASL","zp,x"),

    # LSR
    0x4e:("LSR","a"),
    0x5e:("LSR","a,x"),
    0x4A:("LSR","A"),
    0x46:("LSR","zp"),
    0x56:("LSR","zp,x"),

    # Transfers
    0xba:("TSX","i"),
    0x9a:("TXS","i"),
    0x8a:("TXA","i"),

    # Push & pop ("pull")
    0x48:("PHA", "i"),
    0x68:("PLA", "i"),
    0x5a:("PHY", "i"),
    0x7a:("PLY", "i"),
    0xda:("PHX", "i"),
    0xfa:("PLX", "i"),

    # Jumps
    0x20:("JSR","a"),
    0x60:("RTS","i"),

    # Clear flags
    0x18:("CLC", "i"),
    0xd8:("CLD", "i"),
    0x58:("CLI", "i"),
    0xb8:("CLV", "i"),

    # Set flags
    0x38:("SEC", "i"),
    0xf8:("SED", "i"),
    0x78:("SEI", "i"),

    }


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
        arg = addrmode.upper().replace("ZP","${:02x}".format(operand))
    # absolute indexed
    elif addrmode in ["a", "(a,x)", "a,x", "a,y", "(a)"]:
        arg = addrmode.upper().replace("A","${:04x}".format(operand))
    elif addrmode == "#":
        arg = "#${:02x}".format(operand)
    elif addrmode == "r":
        arg = "{}".format(u8_to_s8(operand))
    else:
        raise Exception("Invalid addressing mode:",addrmode)
    return arg

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
                    raise SyntaxError("Unknown label: {}".format(self._label))
                branch_offset = label_addresses[self._label] - pc_address

                if branch_offset > 127 or branch_offset < -128:
                    raise SyntaxError("Out of range branch (branches are limited to -128 to +127)")

                branch_offset = (branch_offset+256) % 256 # convert to unsigned

                self._operand = branch_offset
            else:
                self._operand = label_addresses[self._label]


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
           raise SyntaxError("unknown variable in expression: {}".format(node.id))
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

def parse_parameter(param):
    if re.match("^[a-zA-Z_]\w*$",param[0]):
        # Found a label. Implies a 2-byte address, i.e. "a". Just
        # return the label, the address will be resolved later.
        return "lbl",param
    else:
        try:
            val = evaluate_constant_expression(param)
        except:
            raise SyntaxError("Failed parsing parameter expression: {}".format(param))

        if val > 255:
            return "a",val
        else:
            return "zp",val

def opcode_to_instr(op):
    if not op in ISA:
        # unknown opcode
        return "UNK"
    else:
        return ISA[op]

def identify_opcode(mnemonic,argfmt):

    mnematches = [(o,i) for o,i in ISA.items() if len(i)>0 and i[0]==mnemonic]

    if len(mnematches) == 0:
        raise SyntaxError("Unknown instruction mnemonic: {}".format(mnemonic))

    # try to match address mode

    if 'lbl' in argfmt:
        # we have a label (and only a label)
        matches = [o for o,i in mnematches if i[1] in [argfmt.replace("lbl","r"), argfmt.replace("lbl","a")]]
    else:
        matches = [o for o,i in mnematches if i[1]==argfmt]

    if len(matches) == 0:
        raise SyntaxError("Unknown instruction: {} {}".format(mnemonic,argfmt))

    if len(matches)>1:
        raise Exception('Internal error, multiple instructions matched {} {}'.format(mnemonic,addrfmt))
        # unknown instruction
        # return 0x00

    return matches[0]

def mnemonic_to_opcode(mnemonic):
    matches = [o for o,instr in ISA.items() if instr[0]==mnemonic]
    if len(matches) != 1:
        raise Exception(f"No unique matching instruction with mnemonic {mnemonic}: {matches}")

    return matches[0]

def parse_argument(arg):

    if len(arg)==0:
        return "i",None

    if re.match("^#",arg):
        param_type,val = parse_parameter(arg[1:])
        if param_type != "zp":
            raise SyntaxError("Too large literal in immediate addressing: {}".format(val))
        return "#", val

    if arg == "A":
        return "A",None

    # match stuff like (<expr>) and (label)

    if m := re.match("^\(([^,]+)\)$",arg):
        param_type,val = parse_parameter(m.group(1))
        return "({})".format(param_type), val

    # match stuff like (<expr>,X) and (label,X)

    if m := re.match("^\(([^,]+),(X)\)$",arg):
        param_type,val = parse_parameter(m.group(1))
        return "({},x)".format(param_type),val

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

        return "{},{}".format(param_type,offset),val

    # else:
    # match label or expression)
    param_type,val = parse_parameter(arg)
    return param_type,val

    # # default - Invalid addressing mode
    # raise SyntaxError("Invalid operand string: {}".format(arg))


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
        raise Exception("Unknown opcode: 0x{:02x}".format(opcode))
    addrmode = ISA[opcode][1]
    operand_bytes = bytes_in[1:1+operand_size(addrmode)]
    operand = decode_operand(operand_bytes)
    return Instruction(opcode,operand,None)

def parse_instruction(source_line):
    mnemonic = source_line[0:3].upper()
    arg_fmt, param = parse_argument(source_line[3:].strip())

    opcode = identify_opcode(mnemonic,arg_fmt)

    if type(param) == str:
        # param is a label
        return Instruction(opcode,None,param)
    else:
        return Instruction(opcode,param,None)
