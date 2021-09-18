
; This is a simple program

        NOP                     ; You can have comments trailing instructions
        NOP
        LDA #$be
        STA $0200
        LDA #$51
        STA $0202
        TSX
        STX $0203

        LDA $0200
        NOP
        NOP
        LDA $0201
        NOP
        NOP
        LDA $0202
        NOP
        NOP
        LDA $0203

        NOP

        STP
        NOP
