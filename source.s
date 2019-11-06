; This is a simple program

        NOP                     ; You can have comments trailing instructions
        NOP
        LDA #$be
        EOR #$ff
        STA $0200
        INC A
        STA $0200
        NOP
        NOP
        STP
        NOP
