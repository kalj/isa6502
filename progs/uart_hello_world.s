#define UART_REG_STATUS $8400
#define UART_REG_RXDATA $8401
#define UART_REG_TXDATA $8402
#define UART_STATUS_TXFULL  %00000001
#define UART_STATUS_RXEMPTY %00000010

    ;; Reset stack pointer
reset:
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

;; Subroutines

uart_send_byte:
    PHA
tx_full:
    LDA UART_REG_STATUS
    AND #UART_STATUS_TXFULL
    BNE tx_full

    PLA
    STA UART_REG_TXDATA
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
