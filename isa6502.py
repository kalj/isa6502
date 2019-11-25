import re

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
    0x80:("BRA","r"),

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

    # DEX
    0xca:("DEX","i"),

    # ASL
    0x0e:("ASL","a"),
    0x1e:("ASL","a,x"),
    0x0A:("ASL","A"),
    0x06:("ASL","zp"),
    0x16:("ASL","zp,x"),

    # T**
    0xba:("TSX","i"),

    # Jumps
    0x20:("JSR","a"),
    0x60:("RTS","i"),

    }


def operand_to_str(addrmode,operand):
    if addrmode == "i":
        arg = ""
    elif addrmode == "A":
        arg = "A"
    # zero-page indexed
    elif addrmode in ["zp", "(zp,x)", "zp,x", "zp,y", "(zp)", "(zp),y"]:
        arg = addrmode.replace("zp","${:02x}".format(operand)).upper()
    # absolute indexed
    elif addrmode in ["a", "(a,x)", "a,x", "a,y", "(a)"]:
        arg = addrmode.replace("a","${:04x}".format(operand)).upper()
    elif addrmode == "#":
        arg = "#${:02x}".format(operand)
    elif addrmode == "r":
        arg = "${:02x}".format(operand)
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


def parse_parameter(literal):
    if re.match("^[a-zA-Z_]\w*$",literal[0]):
        # Found a label. Implies a 2-byte address, i.e. "a". Just
        # return the label, the address will be resolved later.
        return "a",literal
    elif literal[0] == "$":
        if len(literal) == 3:
            return "zp",int(literal[1:],16)
        elif len(literal) == 5:
            return "a",int(literal[1:],16)
        else:
            raise SyntaxError("Invalid length of literal: {}".format(literal))
    else:
        val = int(literal)
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

    if argfmt == "lbl":
        # we have a label (and only a label)
        matches = [o for o,i in mnematches if i[1] in ["r", "a"]]
    else:
        matches = [o for o,i in mnematches if i[1]==argfmt]

    if len(matches) == 0:
        raise SyntaxError("Unknown instruction: {} {}".format(mnemonic,addrfmt))

    if len(matches)>1:
        raise Exception('Internal error, multiple instructions matched {} {}'.format(mnemonic,addrfmt))
        # unknown instruction
        # return 0x00

    return matches[0]

def parse_argument(arg):

    if len(arg)==0:
        return "i",None

    if re.match("#",arg):
        param_type,val = parse_parameter(arg[1:])
        if param_type != "zp":
            raise SyntaxError("Too large literal in immediate addressing")
        return "#", val

    if arg == "A":
        return "A",None

    # match stuff like ($44); ($4444); (273); and (label)
    m = re.match("^\(([^,]+)\)$",arg)
    if m:
        param_type,val = parse_parameter(m.group(1))
        return "({})".format(param_type), val

    # match stuff like ($44,X); ($4444,X); (273,X); and (label,X)
    m = re.match("^\(([^,]+),(X)\)$",arg)
    if m:
        param_type,val = parse_parameter(m.group(1))
        return "({},x)".format(param_type),val

    # match stuff like ($44),Y; (123),Y
    m = re.match("^\((.+)\),(Y)$",arg)
    if m:
        param_type,val = parse_parameter(m.group(1))
        if param_type != "zp":
            raise SyntaxError("Invalid format of base literal for Zero Page Indirect Indexed operand string:",arg)
        return "(zp),y",val

    # match stuff like $44,X; $4444,Y; 273,X; and label,Y
    m = re.match("^([^,]+),([XY])$",arg)
    if m:
        o1 = m.group(1)
        o2 = m.group(2)

        param_type,val = parse_parameter(o1)
        offset = o2.lower()

        return "{},{}".format(param_type,offset),val

    # match stuff like $44; $4444; 273
    if re.match("\$?\d+",arg):
        param_type,val = parse_parameter(arg)
        # TODO: allow for explicit relative addressing
        return param_type,val

    # match a label
    if re.match("[A-Za-z_]",arg):
        return "lbl",arg

    # default - Invalid addressing mode
    raise SyntaxError("Invalid operand string: {}".format(arg))


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
    addrmode = ISA[opcode][1]
    operand_bytes = bytes_in[1:1+operand_size(addrmode)]
    operand = decode_operand(operand_bytes)
    return Instruction(opcode,operand,None)

def parse_instruction(source_line):
    mnemonic = source_line[0:3]
    arg_fmt, param = parse_argument(source_line[3:].strip())

    opcode = identify_opcode(mnemonic,arg_fmt)

    if type(param) == str:
        # param is a label
        return Instruction(opcode,None,param)
    else:
        return Instruction(opcode,param,None)
