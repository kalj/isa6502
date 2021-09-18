

; This is a simple program

        NOP                     ; You can have comments trailing instructions
        NOP
        TSX
        STX $0200
        JSR init
        JSR apa
        TSX
        STX $0200
        STP
        NOP

init:
        LDA #$51
        STA $0201
        TSX
        STX $0200
        RTS
apa:
        LDA #$ab
        STA $0202
        TSX
        STX $0200
        JSR nisse
        RTS
nisse:
        LDA #$1f
        STA $0203
        TSX
        STX $0200
        RTS

        STP
        NOP
