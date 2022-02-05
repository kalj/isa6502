.org $9000
#include "uart.s"
#include "sleep.s"

reset:
    ;; Reset stack pointer
    LDX #$ff
    TXS

;; Start printing characters
    LDX #$00
print_loop:
    LDA hello_str,X
    CMP #$00
    BEQ the_end
    JSR uart_send_byte
    INX
    BRA print_loop

the_end:

    LDX #100
    JSR sleep10ms
    BRA reset
    STP
    NOP

hello_str:
    .asciiz "Hello World!\n"

.org $fffa
.address reset                  ; nmi
.address reset
.address reset                  ; irq
