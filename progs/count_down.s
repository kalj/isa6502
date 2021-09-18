; This is a simple program

        NOP                     ; You can have comments trailing instructions
        NOP
        LDA #$ff
        STA $6002
        LDA #$be
        EOR #$ff
        STA $6000
nisse:  INC A
        STA $6000
        LDA #$11
loop:
        STA $6000
        DEC A
        CMP #$00
        BNE loop
        NOP
        NOP
        STP
        NOP
