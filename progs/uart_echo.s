.org $9000
#include "uart.s"

    ;; Reset stack pointer
reset:
    LDX #$ff
    TXS

;; Start printing characters
    LDX #$00
receive_loop:
    LDA UART_REG_STATUS
    AND #UART_STATUS_RXEMPTY
    BNE receive_loop
    ;; There is at least one received byte to read
    LDA UART_REG_RXDATA
    ;; print it
    JSR uart_send_byte
    ;; restart
    BRA receive_loop

    STP
    NOP


.org $fffa
.address reset                  ; nmi
.address reset
.address reset                  ; irq
