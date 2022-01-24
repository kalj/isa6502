#define UART_REG_STATUS $8400
#define UART_REG_RXDATA $8401
#define UART_REG_TXDATA $8402
#define UART_STATUS_TXFULL  %00000001
#define UART_STATUS_RXEMPTY %00000010

#define DPY_REG_CMD  $8200
#define DPY_REG_DATA $8201

.org $9000
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

    ;; BS/DEL received?
    CMP #$08
    BEQ bsdel_case
    CMP #$7f
    BEQ bsdel_case

    ;; CR received?
    CMP #$0d
    BEQ cr_case

    ;; test for printable
    CMP #$20                    ; space
    BCC receive_loop            ; < space
    CMP #$7e                    ; ~
    BCS receive_loop            ; >= ~
    BRA printable_case

bsdel_case:
    ;; determine if on beginning of line
    LDA DPY_REG_CMD             ; Load CMD register
    BIT #%00111111
    BEQ receive_loop            ; beginning of line -> done

    ;; Decrement address
    LDA #%00010000
    JSR lcd_send_cmd

    ;; Write space
    LDA #$20
    JSR lcd_send_byte

    ;; Decrement address
    LDA #%00010000
    JSR lcd_send_cmd

    BRA receive_loop            ; done

cr_case:
    ;; Determine if first line or not
    LDA DPY_REG_CMD             ; Load CMD register
    AND #%01000000
    BEQ not_on_line2

    ;; copy line2 to line1, clear line2, and go to beginning of second line

    ;; First read line2, read happens backward since DDRAM addr is decreased when reading

    ;; start at position 15, second line
    LDA #%11000000
    JSR lcd_send_cmd
    LDX #16                      ; start loop index at 16, decrement until 0

read_loop:
    JSR lcd_read_byte           ; increments address
    STA 0,X                     ; store read value in zero-page with x as index
    DEX                         ; decrement X, setting Z flag if 0 is hit
    BNE read_loop               ; loop if not 0

    ;; Now pop from stack and write to row 1, now forwards

    ;; start at position 0, first line
    LDA #%10000000
    JSR lcd_send_cmd
    LDX #16                      ; start loop index at 16, decrement until 0
write_loop:
    LDA 0,X                      ; read value from zero-page with x as index
    JSR lcd_send_byte            ; write and increment address
    DEX                          ; decrement X, setting Z flag if 0 is hit
    BNE write_loop               ; loop if not 0

    ;; Last clear out second line
    ;; start at position 0, second line
    LDA #%11000000
    JSR lcd_send_cmd
    LDX #16                      ; start loop index at 16, decrement until 0
    LDA #$20                     ; load a space char

clear_loop:
    JSR lcd_send_byte            ; write and increment address
    DEX                          ; decrement X, setting Z flag if 0 is hit
    BNE clear_loop               ; loop if not 0
    ;; Fall through to other case to get back to beginning of second line

not_on_line2:
    ;; go to beginning of second line
    LDA #%11000000
    JSR lcd_send_cmd
    BRA receive_loop            ; done

printable_case:
    JSR lcd_send_byte
    ;; restart
    BRA receive_loop            ; done

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

lcd_read_byte:
    JSR lcd_wait
    LDA DPY_REG_DATA            ; Read into accumulator from DATA register
    RTS                         ; Return
