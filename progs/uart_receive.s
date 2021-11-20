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

    LDA #%11111111              ; Set all to output
    STA DDRB                    ; 6002 data direction b
    STA DDRA                    ; 6003 data direction a
    LDY #$00                    ; set port a to zeros, i.e. E low
    STY PORTA                   ; Send control bits

    LDA #%00111000              ; Set 8-bit/2-line mode
    JSR lcd_send_cmd

    LDA #%00010000              ; Set cursor shift
    JSR lcd_send_cmd

    LDA #%00001100              ; Set display ON
    JSR lcd_send_cmd

    LDA #%00000110              ; Set entry mode
    JSR lcd_send_cmd

    LDA #%00000001              ; Clear screen
    JSR lcd_send_cmd

    LDA #%00000010              ; Return home
    JSR lcd_send_cmd

;; Start printing characters
    LDX #$00
receive_loop:
    LDA UART_REG_STATUS
    AND #UART_STATUS_RXEMPTY
    BNE receive_loop
    ;; There is at least one received byte to read
    LDA UART_REG_RXDATA
    ;; print it
    JSR lcd_send_byte
    ;; restart
    BRA receive_loop

    STP
    NOP

;; Subroutines

lcd_wait:
    LDY #%00000000              ; set PORTB to input
    STY DDRB
lcd_wait_loop:
    LDY #RW
    STY PORTA
    LDY #(RW | EN)
    STY PORTA
    LDY PORTB
    BMI lcd_wait_loop
    LDY #0                      ; E low
    STY PORTA                   ; Send control
    LDY #%11111111              ; set PORTB to input
    STY DDRB
    RTS

lcd_send_cmd:
    JSR lcd_wait
    STA PORTB                   ; Write accumulator to I/O register
    LDY #0                      ; E low
    STY PORTA                   ; Send control
    LDY #EN                     ; E high
    STY PORTA                   ; Send control
    LDY #0                      ; E low
    STY PORTA                   ; Send control
    RTS                         ; Return

lcd_send_byte:
    JSR lcd_wait
    STA PORTB                   ; Write accumulator to I/O register
    LDY #RS                     ; RS high, E low
    STY PORTA                   ; Send control
    LDY #(RS|EN)                ; RS high, E high
    STY PORTA                   ; Send control
    LDY #RS                     ; RS high, E low
    STY PORTA                   ; Send control
    RTS                         ; Return
