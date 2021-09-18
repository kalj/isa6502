    ;; Reset stack pointer
    LDX #$ff
    TXS

    LDA #$ff
    STA $6002               ; 6002 data direction b
    STA $6003               ; 6003 data direction a

    ;;  Display initialization sequence
    LDY #$00                ; E low
    STY $6001               ; Send control bits

    LDA #$30                ; Set wake-up command 30 on data bus
    STA $6000

    LDX #$03
wake_up:
    JSR send_cmd
    DEX
    BNE wake_up

    LDA #$38                ; Set 8-bit/2-line mode
    STA $6000               ; Write accumulator to I/O register
    JSR send_cmd

    LDA #$10                ; Set cursor shift
    STA $6000               ; Write accumulator to I/O register
    JSR send_cmd

    LDA #$0c                ; Set display ON
    STA $6000               ; Write accumulator to I/O register
    JSR send_cmd

    LDA #$06                ; Set entry mode
    STA $6000               ; Write accumulator to I/O register
    JSR send_cmd

    LDA #$01                ; Clear screen
    STA $6000               ; Write accumulator to I/O register
    JSR send_cmd

    LDA #$02                ; Return home
    STA $6000               ; Write accumulator to I/O register
    JSR send_cmd

;; Initialization done

    ;; print 123 == 0x7b

loop:
    LDA #$00
    JSR print_int

    LDA #$63
    JSR print_int

    LDA #$64
    JSR print_int

    LDA #$65
    JSR print_int

    BRA loop

    STP
    NOP

;;===========================================================
;; Subroutines
;;===========================================================

;;---------------------------------------------------------------
;; send command
;;---------------------------------------------------------------
send_cmd:
    LDY #$80                ; E high
    STY $6001               ; Send control
    LDY #$00                ; E low
    STY $6001               ; Send control
    RTS                     ; Return

;;---------------------------------------------------------------
;; send byte
;;---------------------------------------------------------------
send_byte:
    LDY #$a0                ; RS high, E high
    STY $6001               ; Send control
    LDY #$20                ; RS high, E low
    STY $6001               ; Send control
    RTS                     ; Return

;;-----------------------------------------------------------
;; Print an 8-bit integer to the display
;;-----------------------------------------------------------
print_int:
    PHA                     ; save A

    ; Clear screen
    LDA #$01
    STA $6000
    JSR send_cmd

    ; Set cursor position to end-3
    LDA #$8d
    STA $6000
    JSR send_cmd

    PLA                     ; restore A

    ; print 100's
    LDX #$00
pi_count_hundreds:
    CMP #$64                ; compare with 100
    BCC pi_count_hundreds_done
    INX                     ; increment hundreds
    CLC
    SBC #$64                ; subtract 100
    BRA pi_count_hundreds  ; loop
    ;; not less than
pi_count_hundreds_done:
    ;; X is hundreds
    ;; A is less than 100
    LDY #$01                ; by default, indicate that we have hundreds
    CPX #$00
    BNE pi_print_hundreds
    LDX #$ef                ; load with -16 -> add 48 below and get 32 == ' '
    LDY #$00                ; indicate that we have no hundreds

pi_print_hundreds:
    PHY                     ; save Y
    PHA                     ; save rest
    TXA
    CLC
    ADC #$30                ; convert to ascii
    STA $6000
    JSR send_byte
    PLA                     ; restore rest
    PLY                     ; load Y

    ; print 10's
    LDX #$00
pi_count_tens:
    CMP #$0a                ; compare with 10
    BCC pi_count_tens_done
    INX                     ; increment tens
    CLC
    SBC #$0a                ; subtract 10
    BRA pi_count_tens      ; loop
    ;; not less than

pi_count_tens_done:
    PHA                     ; save rest
    ;; X is tens
    ;; A is less than 10
    ;; Y indicates if we had hundreds
    ;; wanna skip if X == 0 && Y == 0 -> X+Y == 0

    CPX #$00
    BNE pi_print_tens       ; we have tens, so print unconditionally

    ;; tens == 0:
    CPY #$00
    BNE pi_print_tens       ; we had hundreds, so print zero char

    ;; tens == 0 && hundreds == 0: print space
    LDX #$ef                ; load with -16 -> add 48 below and get 32 == ' '

pi_print_tens:
    TXA
    CLC
    ADC #$30                ; convert to ascii
    STA $6000
    JSR send_byte

pi_print_ones:
    PLA                     ; restore rest
    ;;  print rest == ones
    CLC
    ADC #$30                ; convert to ascii
    STA $6000
    JSR send_byte

    RTS

;;-----------------------------------------------------------
;; sleep
;;-----------------------------------------------------------
sleep:
    ;; A is number of noops
    CMP #$00
    BEQ sleep_done
    NOP
    DEC A
    BRA sleep
sleep_done:
    RTS

;; multiply:

;;         RTS
