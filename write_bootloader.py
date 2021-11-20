#!/usr/bin/python3
#
#

import isa6502

outputfilename="bootloader.bin"

bootloader_size = 32
start_address = 0x9000
start_address_lsb = 0xff & start_address
start_address_msb = 0xff & (start_address >> 8)
stopcode=isa6502.mnemonic_to_opcode("STP")

## bootloader layout
#             0     1     2   ...     a     b         c      d      e    f
# ffe0      STP   STP   STP         STP   STP       STP    STP    STP  STP
# fff0      STP   STP   STP         STP   STP    sa_lsb sa_msb      0    0
bootloader = bytes(((bootloader_size-4)*[stopcode])+[start_address_lsb, start_address_msb, 0x00, 0x00])


open(outputfilename,"wb").write(bootloader)
