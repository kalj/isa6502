#define ACIA_REG_DATA    $8100
#define ACIA_REG_STATUS  $8101
#define ACIA_REG_COMMAND $8102
#define ACIA_REG_CONTROL $8103

    ;; Reset stack pointer
reset:
    LDX #$ff
    TXS

    LDA #%00001011
    STA ACIA_REG_COMMAND

    LDA #%00010000
    STA ACIA_REG_CONTROL

;; Start printing characters
    LDX #$00
print_loop:
    LDA hello_str,X
    CMP #$00
    BEQ the_end
    JSR acia_send_byte
    INX
    BRA print_loop

the_end:

    LDX #100
    JSR sleep10ms
    BRA reset
    STP
    NOP

;; Subroutines

acia_wait:
    PHY
    PHX
delay_loop:
    LDY #1
minidly:
    LDX #$68
delay_1:
    DEX
    BNE delay_1
    DEY
    BNE minidly
    PLX
    PLY
delay_done:
    RTS

acia_send_byte:
    STA ACIA_REG_DATA
    JSR acia_wait
    RTS

sleep10ms:
    LDY #$ff

sleep10ms_2:
    NOP
    NOP
    NOP
    NOP
    NOP
    NOP
    NOP
    NOP
    NOP
    NOP
    NOP
    NOP
    NOP
    NOP
    NOP
    NOP
    NOP
    DEY
    BNE sleep10ms_2

    DEX
    BNE sleep10ms
    RTS

hello_str:
    .asciiz "Hello World!\n"
