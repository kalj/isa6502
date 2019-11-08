import re

ISA = {
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
    0xd0:("BNE","r"),

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


    0x00:(),
    0x01:(),
    0x02:(),
    0x03:(),
    0x04:(),
    0x05:(),
    0x06:(),
    0x07:(),
    0x08:(),
    0x09:(),
    0x0a:(),
    0x0b:(),
    0x0c:(),
    0x0d:(),
    0x0e:(),
    0x0f:(),
    0x10:(),
    0x11:(),
    0x12:(),
    0x13:(),
    0x14:(),
    0x15:(),
    0x16:(),
    0x17:(),
    0x18:(),
    0x19:(),
    0x1b:(),
    0x1c:(),
    0x1d:(),
    0x1e:(),
    0x1f:(),
    0x20:(),
    0x21:(),
    0x22:(),
    0x23:(),
    0x24:(),
    0x25:(),
    0x26:(),
    0x27:(),
    0x28:(),
    0x29:(),
    0x2a:(),
    0x2b:(),
    0x2c:(),
    0x2d:(),
    0x2e:(),
    0x2f:(),
    0x30:(),
    0x31:(),
    0x32:(),
    0x33:(),
    0x34:(),
    0x35:(),
    0x36:(),
    0x37:(),
    0x38:(),
    0x39:(),
    0x3b:(),
    0x3c:(),
    0x3d:(),
    0x3e:(),
    0x3f:(),
    0x40:(),
    0x42:(),
    0x43:(),
    0x44:(),

    0x46:(),
    0x47:(),
    0x48:(),

    0x4a:(),
    0x4b:(),
    0x4c:(),

    0x4e:(),
    0x4f:(),
    0x50:(),
    0x53:(),
    0x54:(),

    0x56:(),
    0x57:(),
    0x58:(),

    0x5a:(),
    0x5b:(),
    0x5c:(),

    0x5e:(),
    0x5f:(),
    0x60:(),
    0x61:(),
    0x62:(),
    0x63:(),
    0x64:(),
    0x65:(),
    0x66:(),
    0x67:(),
    0x68:(),
    0x69:(),
    0x6a:(),
    0x6b:(),
    0x6c:(),
    0x6d:(),
    0x6e:(),
    0x6f:(),
    0x70:(),
    0x71:(),
    0x72:(),
    0x73:(),
    0x74:(),
    0x75:(),
    0x76:(),
    0x77:(),
    0x78:(),
    0x79:(),
    0x7a:(),
    0x7b:(),
    0x7c:(),
    0x7d:(),
    0x7e:(),
    0x7f:(),
    0x80:(),
    0x82:(),
    0x83:(),
    0x84:(),
    0x86:(),
    0x87:(),
    0x88:(),
    0x89:(),
    0x8a:(),
    0x8b:(),
    0x8c:(),
    0x8e:(),
    0x8f:(),
    0x90:(),
    0x93:(),
    0x94:(),
    0x96:(),
    0x97:(),
    0x98:(),
    0x9a:(),
    0x9b:(),
    0x9c:(),
    0x9e:(),
    0x9f:(),
    0xa0:(),
    0xa2:(),
    0xa3:(),
    0xa4:(),
    0xa6:(),
    0xa7:(),
    0xa8:(),
    0xaa:(),
    0xab:(),
    0xac:(),
    0xae:(),
    0xaf:(),
    0xb0:(),
    0xb3:(),
    0xb4:(),
    0xb6:(),
    0xb7:(),
    0xb8:(),
    0xba:(),
    0xbb:(),
    0xbc:(),
    0xbe:(),
    0xbf:(),
    0xc0:(),
    0xc2:(),
    0xc3:(),
    0xc4:(),
    0xc7:(),
    0xc8:(),
    0xca:(),
    0xcb:(),
    0xcc:(),
    0xcf:(),
    0xd3:(),
    0xd4:(),
    0xd7:(),
    0xd8:(),
    0xda:(),
    0xdc:(),
    0xdf:(),
    0xe0:(),
    0xe1:(),
    0xe2:(),
    0xe3:(),
    0xe4:(),
    0xe5:(),
    0xe7:(),
    0xe8:(),
    0xe9:(),
    0xeb:(),
    0xec:(),
    0xed:(),
    0xef:(),
    0xf0:(),
    0xf1:(),
    0xf2:(),
    0xf3:(),
    0xf4:(),
    0xf5:(),
    0xf7:(),
    0xf8:(),
    0xf9:(),
    0xfa:(),
    0xfb:(),
    0xfc:(),
    0xfd:(),
    0xff:()}

class Instruction():
    def __init__(self,opcode,operand):
        self._opcode = opcode
        self._operand = operand
    def __str__(self):
        s = self.get_mnemonic()
        opsize = operand_size(self.get_addrmode())

        # TODO: remove this special case
        if type(self._operand) == str:
            s += " {}".format(self._operand)
        elif opsize == 1:
            s += " ${:x}".format(self._operand)
        elif opsize == 2:
            s += " ${:x}".format(self._operand)

        return s

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

class SyntaxError(Exception):
    pass

def parse_literal(literal):
    if literal[0] == "$":
        if len(literal) == 3:
            return "zp",int(literal[1:],16)
        elif len(literal) == 5:
            return "a",int(literal[1:],16)
        else:
            raise SyntaxError("Invalid length of literal:",literal)
    else:
        val = int(literal)
        if val > 255:
            return "a",val
        else:
            return "zp",val



def opcode_to_instr(op):
    matches = [i for o,i in ISA.items() if op==o and len(i)>0]
    nmatches = len(matches)
    if nmatches >1:
        raise Exception('Internal error, multiple opcodes matched')
    if nmatches == 0:
        # unknown opcode
        return "UNK"
    else:
        return matches[0]

def get_opcode(mnemonic,addrmode):

    matches = [o for o,i in ISA.items() if len(i)>0 and i[0]==mnemonic and i[1]==addrmode]
    nmatches = len(matches)
    if nmatches >1:
        raise Exception('Internal error, multiple instructions matched')
    if nmatches == 0:
        raise SyntaxError("Unknown instruction: {} ({})".format(mnemonic,addrmode))
        # unknown instruction
        # return 0x00
    else:
        return matches[0]

def parse_argument(arg):
    if len(arg)==0:
        addrmode="i"
        operand=None

    elif re.match("#",arg):
        addrmode = "#"
        t,v = parse_literal(arg[1:])
        if t != "zp":
            raise SyntaxError("Too large literal in immediate addressing")
        operand=(v)

    elif arg == "A":
        addrmode = "A"
        operand = None

    # match stuff like ($44); ($4444); and (273)
    elif re.match("^\(([^,]+)\)$",arg):
        m = re.match("^\(([^,]+)\)$",arg)
        literal_type,val = parse_literal(m.group(1))
        addrmode = "({})".format(literal_type)
        operand = val

    # match stuff like ($44,X); ($4444,X); and (273,X)
    elif re.match("^\(([^,]+),([^,]+)\)$",arg):
        m = re.match("^\(([^,]+),([^,]+)\)$",arg)
        o1 = m.group(1)
        o2 = m.group(2)
        if not o2=="X":
            raise SyntaxError("Invalid offset for indexed indirect operand string:",arg)

        literal_type,val = parse_literal(o1)
        addrmode = "({},x)".format(literal_type)
        operand = val

    # match stuff like ($44),Y; (123),Y
    elif re.match("^\((.+)\),(.+)$",arg):
        m = re.match("^\((.+)\),(.+)$",arg)
        o1 = m.group(1)
        o2 = m.group(2)
        if not o2=="Y":
            raise SyntaxError("Invalid offset for Zero Page Indirect Indexed operand string:",arg)
        literal_type,val = parse_literal(o1)
        if literal_type != "zp":
            raise SyntaxError("Invalid format of base literal for Zero Page Indirect Indexed operand string:",arg)
        addrmode = "(zp),y"
        operand = val

    # match stuff like $44,X; $4444,Y; and 273,X
    elif re.match("^([^,]+),([^,]+)$",arg):
        m = re.match("^([^,]+),([^,]+)$",arg)
        o1 = m.group(1)
        o2 = m.group(2)

        literal_type,val = parse_literal(o1)

        if not o2 in ["X","Y"]:
            if literal_type=='zp':
                idxtype = "Zero Page"
            else:
                idxtype = "Absolute"
            raise SyntaxError("Invalid offset for {} Indexed operand string: {}".format(idxtype,arg))

        offset = o2.lower()

        addrmode = "{},{}".format(literal_type,o2.lower())
        operand = val

    # match stuff like $44; $4444; 273
    elif re.match("\$?\d+",arg):
        m = re.match("\$?\d+",arg)
        literal_type,val = parse_literal(m.group(0))
        # TODO: allow for explicit relative addressing
        addrmode = literal_type
        operand = val

    # match a label
    elif re.match("[A-Za-z]\d*",arg):
        addrmode = "r"
        operand = arg
        # if literal_type=='zp' and mnemonic == ":
        #     return 'zp|r'
        # else:
        #     return 'a'

    # default - Invalid addressing mode
    else:
        raise SyntaxError() #"Invalid operand string: {}".format(arg)

    return addrmode,operand

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
        raise Exception()

def decode(mnemonic,addrmode,operand_bytes):
    if addrmode == "i":
        arg = ""
    elif addrmode == "A":
        arg = "A"
    elif addrmode in ["zp,x", "zp,y"]:
        offset=addrmode[-1].upper()
        arg = "${:02x},{}".format(operand_bytes[0],offset)
    elif addrmode == "zp":
        arg = "${:02x}".format(operand_bytes[0])
    elif addrmode == "(zp)":
        arg = "(${:02x})".format(operand_bytes[0])
    elif addrmode == "(zp,x)":
        arg = "(${:02x},X)".format(operand_bytes[0])
    elif addrmode == "(zp),y":
        arg = "(${:02x}),Y".format(operand_bytes[0])
    elif addrmode == "#":
        arg = "#${:02x}".format(operand_bytes[0])
    elif addrmode in ["a,x", "a,y"]:
        offset=addrmode[-1].upper()
        arg = "${:04x},{}".format(operand_bytes[0]+(operand_bytes[1]<<8),offset)
    elif addrmode == "a":
        arg = "${:04x}".format(operand_bytes[0]+(operand_bytes[1]<<8))
    elif addrmode == "(a)":
        arg = "(${:04x})".format(operand_bytes[0]+(operand_bytes[1]<<8))
    elif addrmode == "(a,x)":
        arg = "(${:04x},X)".format(operand_bytes[0]+(operand_bytes[1]<<8))
    elif addrmode == "r":
        arg = "${:02x}".format(operand_bytes[0])
    else:
        raise Exception("Failed decoding instruction:",mnemonic,addrmode)
    return (" ".join([mnemonic,arg])).strip()
