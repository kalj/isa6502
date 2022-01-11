
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

    # ORA
    0x0d:("ORA","a"),
    0x1d:("ORA","a,x"),
    0x19:("ORA","a,y"),
    0x09:("ORA","#"),
    0x05:("ORA","zp"),
    0x01:("ORA","(zp,x)"),
    0x15:("ORA","zp,x"),
    0x12:("ORA","(zp)"),
    0x11:("ORA","(zp),y"),

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

    # BIT
    0x2c:("BIT","a"),
    0x3c:("BIT","a,x"),
    0x89:("BIT","#"),
    0x24:("BIT","zp"),
    0x34:("BIT","zp,x"),

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

    # Rotate left
    0x2e:("ROL","a"),
    0x3e:("ROL","a,x"),
    0x2A:("ROL","A"),
    0x26:("ROL","zp"),
    0x36:("ROL","zp,x"),

    # Rotate right
    0x6e:("ROR","a"),
    0x7e:("ROR","a,x"),
    0x6A:("ROR","A"),
    0x66:("ROR","zp"),
    0x76:("ROR","zp,x"),

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
