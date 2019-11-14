; This is a simple program

        NOP                     ; You can have comments trailing instructions
        NOP
        LDA #$ff
        STA $6002               ; 6002 data direction b
        STA $6003               ; 6003 data direction a
        LDX #$00
reset_a:
        LDA #$01
loop:
        STX $6000               ; 6000 register b
        STA $6001               ; 6001 register a
        INX
        ASL A
        BCS reset_a
        BRA loop
        STP
        NOP
