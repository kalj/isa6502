MYVAR = (1+13)|1

    lda -1
    lda 255
    lda 65535

l:
    lda 0
.b:
    lda (.apa)
    lda $df
    lda ($df)
    lda #$df
    lda #($df)
    lda (($df))
    lda ($1 + $5)
    lda $1+$2

    lda MYVAR
    lda #3|8
    ;; lda labl+1
    ;; lda APA

.apa:
    .byte $00
