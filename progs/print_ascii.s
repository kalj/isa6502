; This is a simple program

        LDA #$ff
        STA $6002               ; 6002 data direction b
        STA $6003               ; 6003 data direction a

        ;;  Initialization sequence
        LDY #$00                ; E low
        STY $6001               ; Send control bits

        LDA #$30                ; Set wake-up command 30 on data bus
        STA $6000

        LDX #$03
wake_up:
        LDY #$80                ; E high
        STY $6001               ; Send control
        LDY #$00                ; E low
        STY $6001               ; Send control
        DEX
        BNE wake_up

        LDA #$38                ; Set 8-bit/2-line mode
        STA $6000

        LDY #$80                ; E high
        STY $6001               ; Send control
        LDY #$00                ; E low
        STY $6001               ; Send control

        LDA #$10                ; Set cursor shift
        STA $6000

        LDY #$80                ; E high
        STY $6001               ; Send control
        LDY #$00                ; E low
        STY $6001               ; Send control

        LDA #$0c                ; Set display ON
        STA $6000

        LDY #$80                ; E high
        STY $6001               ; Send control
        LDY #$00                ; E low
        STY $6001               ; Send control

        LDA #$06                ; Set entry mode
        STA $6000

        LDY #$80                ; E high
        STY $6001               ; Send control
        LDY #$00                ; E low
        STY $6001               ; Send control

        LDA #$01                ; Clear screen
        STA $6000

        LDY #$80                ; E high
        STY $6001               ; Send control
        LDY #$00                ; E low
        STY $6001               ; Send control

        LDA #$02                ; Return home
        STA $6000

        LDY #$80                ; E high
        STY $6001               ; Send control
        LDY #$00                ; E low
        STY $6001               ; Send control

;; Start printing characters
        LDA #$30

        LDX #$10
print_character:
        STA $6000
        LDY #$a0                ; RS high, E high
        STY $6001               ; Send control
        LDY #$20                ; RS high, E low
        STY $6001               ; Send control
        INC A
        DEX
        BNE print_character

        STP
        NOP
