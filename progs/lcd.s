#define LCD_REG_CMD  $8200
#define LCD_REG_DATA $8201

lcd_init:
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

    RTS

lcd_wait:
    LDY LCD_REG_CMD             ; Load CMD register
    BMI lcd_wait
    RTS

lcd_send_cmd:
    JSR lcd_wait
    STA LCD_REG_CMD             ; Write accumulator to CMD register
    RTS                         ; Return

lcd_send_byte:
    JSR lcd_wait
    STA LCD_REG_DATA            ; Write accumulator to DATA register
    RTS                         ; Return

lcd_read_byte:
    JSR lcd_wait
    LDA LCD_REG_DATA            ; Read into accumulator from DATA register
    RTS                         ; Return
