.orig $9000
#include "lcd.s"

    ;; Reset stack pointer
reset:
    LDX #$ff
    TXS

    JSR lcd_init

;; Start printing characters
    LDX #$00
print_loop:
    LDA hello_str,X
    CMP #$00
    BEQ the_end
    JSR send_byte
    INX
    BRA print_loop

the_end:
    STP
    NOP

hello_str:
    .asciiz "Hello World!"

.org $fffa
.address $0000
.address reset
.address $0000
