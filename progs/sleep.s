
sleep10ms:
    LDY #$ff

.inner_loop:
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
    BNE .inner_loop

    DEX
    BNE sleep10ms
    RTS
