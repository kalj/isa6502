#define DUART_REG_MRA           $8700
#define DUART_REG_SRA_CSRA      $8701
#define DUART_REG_CRA           $8702
#define DUART_REG_FIFOA         $8703
#define DUART_REG_IPCR_ACR      $8704
#define DUART_REG_ISR_IMR       $8705
#define DUART_REG_CTU_CTPU      $8706
#define DUART_REG_CTL_CTPL      $8707
#define DUART_REG_MRB           $8708
#define DUART_REG_SRB_CSRB      $8709
#define DUART_REG_CRB           $870a
#define DUART_REG_FIFOB         $870b
#define DUART_REG_IRQVEC        $870c
#define DUART_REG_MISC          $870d
#define DUART_REG_STARTCNT_SOPR $870e
#define DUART_REG_STOPCNT_ROPR  $870f

#define DUART_STATUS_TXEMPTY  %00001000
#define DUART_STATUS_TXREADY  %00000100
#define DUART_STATUS_RXFULL   %00000010
#define DUART_STATUS_RXREADY  %00000001

duart_init:
    LDA #%10110000              ; set MRA ptr to 0
    STA DUART_REG_CRA

    LDA #%00001001              ; Set MR0A: Baud extended group I, 16-Byte FIFO, Rx and Tx interrupt when >=1 Bytes in FIFO
    STA DUART_REG_MRA

    LDA #%00010011              ; Set MR1A: No parity, char errormode, 8 char bits
    STA DUART_REG_MRA

    LDA #%00000111              ; Set MR2A: Stop bit length 1.0
    STA DUART_REG_MRA

    LDA #%00000000              ; Set ACR[7] to 1 -> 1st baud rate generator set
    STA DUART_REG_IPCR_ACR

    LDA #%11001100              ; Set CSRA: 1100 -> 230400 in Extended mode I, for 3.6864 MHz clock (115200 for 1.8432 MHz clock)
    STA DUART_REG_SRA_CSRA

    LDA #%00000101
    STA DUART_REG_CRA           ; set tx and rx enable

    RTS


duart_send_byte:
    PHA
.tx_not_ready:
    LDA DUART_REG_SRA_CSRA      ; read status register
    BIT #DUART_STATUS_TXREADY
    BEQ .tx_not_ready           ; eq/zero, i.e. NOT ready, then loop

    PLA
    STA DUART_REG_FIFOA
    RTS
