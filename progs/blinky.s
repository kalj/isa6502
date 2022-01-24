; This is a simple program
#define PORTB $8000
#define PORTA $8001
#define DDRB  $8002
#define DDRA  $8003

.org $9000
    ;; Reset stack pointer
reset:
    LDX #$ff
    TXS

    LDA #%11111111              ; Set all to output
    STA DDRB                    ; 6002 data direction b
    STA DDRA                    ; 6003 data direction a

blink_loop:
    LDA #$aa
    STA PORTA
    STA PORTB

    LDX #10
    JSR sleep10ms

    LDA #$55
    STA PORTA
    STA PORTB

    LDX #10
    JSR sleep10ms

    BRA blink_loop

the_end:
    STP
    NOP

;; Subroutines

sleep10ms:
    LDY #$ff

@inner_loop:
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
    BNE @inner_loop

    DEX
    BNE sleep10ms
    RTS
