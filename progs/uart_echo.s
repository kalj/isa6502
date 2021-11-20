#define UART_REG_STATUS $8400
#define UART_REG_RXDATA $8401
#define UART_REG_TXDATA $8402
#define UART_STATUS_TXFULL  %00000001
#define UART_STATUS_RXEMPTY %00000010

#define PORTB $8000
#define PORTA $8001
#define DDRB  $8002
#define DDRA  $8003
#define EN    %10000000
#define RW    %01000000
#define RS    %00100000

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
