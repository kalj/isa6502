; This is a simple program

        NOP                     ; You can have comments trailing instructions
        NOP
        LDA #$be
        EOR #$ff
        STA $0200
nisse:  INC A
        STA $0200
        LDA #$11
loop:
        STA $0200
        DEC A
        CMP #$00
        BNE loop
        NOP
        NOP
        STP
        NOP
