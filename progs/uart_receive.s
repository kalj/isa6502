#define UART_REG_STATUS $8400
#define UART_REG_RXDATA $8401
#define UART_REG_TXDATA $8402
#define UART_STATUS_TXFULL  %00000001
#define UART_STATUS_RXEMPTY %00000010

#define DPY_REG_CMD  $8200
#define DPY_REG_DATA $8201

    ;; Reset stack pointer
reset:
    LDX #$ff
    TXS

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

    LDA #%00000001              ; Clear screen
    JSR lcd_send_cmd

receive_loop:
    LDA UART_REG_STATUS
    AND #UART_STATUS_RXEMPTY
    BNE receive_loop
    ;; There is at least one received byte to read
    LDA UART_REG_RXDATA

    CMP #$0d                    ; CR
    BNE printable_test

cr_received:
    ;; switch line
    LDA DPY_REG_CMD             ; Load CMD register
    CLC
    ADC #%01000000              ; toggle msb of addr
    ORA #%10000000              ; set msb of to convert to command
    JSR lcd_send_cmd
    BRA receive_loop

printable_test:
    CMP #$20                    ; space
    BCC receive_loop            ; < space
    CMP #$7e                    ; ~
    BCS receive_loop            ; >= ~

    ;; print it
char_received:
    JSR lcd_send_byte
    ;; restart
    BRA receive_loop

    STP
    NOP

;; Subroutines

lcd_wait:
    LDY DPY_REG_CMD             ; Load CMD register
    BMI lcd_wait
    RTS

lcd_send_cmd:
    JSR lcd_wait
    STA DPY_REG_CMD             ; Write accumulator to CMD register
    RTS                         ; Return

lcd_send_byte:
    JSR lcd_wait
    STA DPY_REG_DATA            ; Write accumulator to DATA register
    RTS                         ; Return
