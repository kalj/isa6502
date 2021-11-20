#define DPY_REG_CMD $8200
#define DPY_REG_DATA  $8201

    ;; Reset stack pointer
reset:
    LDX #$ff
    TXS

    LDA #%00111000              ; Set 8-bit/2-line mode
    JSR send_cmd

    LDA #%00010000              ; Set cursor shift
    JSR send_cmd

    LDA #%00001100              ; Set display ON
    JSR send_cmd

    LDA #%00000110              ; Set entry mode
    JSR send_cmd

    LDA #%00000001              ; Clear screen
    JSR send_cmd

    LDA #%00000010              ; Return home
    JSR send_cmd

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

;; Subroutines

lcd_wait:
    LDY DPY_REG_CMD             ; Load CMD register
    BMI lcd_wait
    RTS

send_cmd:
    JSR lcd_wait
    STA DPY_REG_CMD             ; Write accumulator to CMD register
    RTS                         ; Return

send_byte:
    JSR lcd_wait
    STA DPY_REG_DATA            ; Write accumulator to DATA register
    RTS                         ; Return

hello_str:
    .asciiz "Hello World!"
