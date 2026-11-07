; Pilote d'imprimante GEOS pour Commodore MPS-803 / MPS-801 (mode graphique).
;
; Chaque passe de la tete imprime 7 rangees de points, alors que GEOS fournit
; des blocs de 8 rangees : le pilote met donc les rangees en attente.
; Tete : bit 0 en haut, bit 7 a 1, largeur 480 points (60 cartes), 9 passes/pouce.
        .setcpu "6502"

ExitTurbo  = $C232
InitForIO  = $C25C
DoneWithIO = $C25F

STATUS = $90
LISTEN = $FFB1
SECOND = $FF93
CIOUT  = $FFA8
UNLSN  = $FFAE

r0L = $02
r0H = $03
PTR_SRC = $08               ; r3
PTR_DST = $0A               ; r4
PTR_AUX = $0C               ; r5

DEVICE     = 4
SA_GRAPHIC = $60            ; canal 0 : mode graphique
CARDS      = 60
PAGE_CARDS = 88             ; 704 points, soit 11,2 pouces imprimables
PAGE_PASSES = 105           ; 11,7 pouces (A4) a 9 passes par pouce
TEAR_PASSES = 12            ; avance en fin d'impression pour pouvoir dechirer
ROWS_MAX   = 14             ; 6 rangees en attente + 8 nouvelles
DEV_NOT_FOUND = 13

; Tampon de travail que geoWrite reserve au pilote pendant l'impression
; (MEM_PRINTWORKBUF, 3*640 octets). La zone au-dessus de $75D8 sert aussi
; a sauvegarder l'ecran sous les boites de dialogue.
rowbuf     = $0400

CHR_BITIMAGE = 8
CHR_CR       = 13
CHR_TEXT     = 15

        .org $7900

        jmp InitForPrint
        jmp StartPrint
        jmp PrintBuffer
        jmp StopPrint
        jmp GetDimensions
        jmp PrintASCII
        jmp StartASCII
        jmp SetNLQ

; Adresse fixe $7918 : geoWrite la remet a 0 en mode feuille a feuille.
page_feed: .byte 0          ; passes restantes jusqu'a la page suivante
pending: .byte 0            ; rangees en attente dans rowbuf
passes:  .byte 0            ; passes deja imprimees sur la page
failed:  .byte 0            ; imprimante absente
mask:    .byte 0
card:    .byte 0
row:     .byte 0
ascii:   .byte 0

InitForPrint:
        lda #0
        sta page_feed
SetNLQ:
        ldx #0
        rts

GetDimensions:
        ldx #CARDS
        ldy #PAGE_CARDS
        lda #0
        rts

; Sort du mode rapide du lecteur et ouvre le canal. C = 1 si imprimante absente.
io_begin:
        jsr ExitTurbo
        jsr InitForIO
        lda #0
        sta STATUS
        lda #DEVICE
        jsr LISTEN
        lda #SA_GRAPHIC
        jsr SECOND
        lda STATUS
        asl
        rts

io_end:
        jsr UNLSN
        jmp DoneWithIO

StartPrint:
        lda #0
        sta pending
        sta passes
        sta failed
        sta ascii
        jsr io_begin
        bcs start_absent
        lda page_feed           ; une page suit : complete le saut de page
        beq @open
        lda #CHR_BITIMAGE
        jsr CIOUT
@feed:  lda #CHR_CR
        jsr CIOUT
        dec page_feed
        bne @feed
        lda #CHR_TEXT
        jsr CIOUT
@open:  jsr io_end
        ldx #0
        rts

start_common:
        jsr io_begin
        bcc start_ok
start_absent:
        jsr io_end
        inc failed
        ldx #DEV_NOT_FOUND
        rts
start_ok:
        jsr io_end
        ldx #0
        rts

StartASCII:
        lda #0
        sta passes
        sta failed
        lda #1
        sta ascii
        jmp start_common

; Texte brut (mode Draft) : ASCII vers PETSCII, chaine terminee par 0.
PrintASCII:
        lda failed
        bne @done
        jsr io_begin
        ldy #0
@next:  lda (r0L),y
        beq @end
        cmp #'A'
        bcc @send
        cmp #'Z'+1
        bcc @upper
        cmp #'a'
        bcc @send
        cmp #'z'+1
        bcs @send
        and #$DF                ; minuscule ASCII vers minuscule PETSCII
        bne @send
@upper: ora #$80                ; majuscule ASCII vers majuscule PETSCII
@send:  sty row
        jsr CIOUT
        ldy row
        iny
        bne @next
@end:   jsr io_end
@done:  ldx #0
        rts

; r0 : 640 octets, 80 cartes de 8 octets. Seules 60 cartes sont imprimees.
PrintBuffer:
        lda failed
        bne @done
        lda #0
        sta row
@rows:  clc                     ; source : r0 + rangee
        lda r0L
        adc row
        sta PTR_SRC
        lda r0H
        adc #0
        sta PTR_SRC+1
        lda pending
        clc
        adc row
        tax
        lda row_lo,x
        sta PTR_DST
        lda row_hi,x
        sta PTR_DST+1
        ldy #0
@cards: sty card
        ldy #0
        lda (PTR_SRC),y
        ldy card
        sta (PTR_DST),y
        clc
        lda PTR_SRC
        adc #8
        sta PTR_SRC
        bcc :+
        inc PTR_SRC+1
:       iny
        cpy #CARDS
        bne @cards
        inc row
        lda row
        cmp #8
        bne @rows
        clc
        lda pending
        adc #8
        sta pending
        jsr io_begin
@emit:  lda pending
        cmp #7
        bcc @end
        jsr emit_pass
        jmp @emit
@end:   jsr io_end
@done:  ldx #0
        rts

; Imprime les 7 premieres rangees et decale les rangees restantes.
emit_pass:
        lda #CHR_BITIMAGE
        jsr CIOUT
        lda #0
        sta card
@card:  lda #$80
        sta mask
@dot:   ldx #6
        ldy card
        lda #0
        sta PTR_AUX             ; octet de points en construction
@head:  lda row_lo,x
        sta PTR_DST
        lda row_hi,x
        sta PTR_DST+1
        lda (PTR_DST),y
        and mask
        cmp #1                  ; C = point present
        rol PTR_AUX
        dex
        bpl @head
        lda PTR_AUX
        ora #$80
        jsr CIOUT
        lsr mask
        bne @dot
        inc card
        lda card
        cmp #CARDS
        bne @card
        lda #CHR_CR
        jsr CIOUT
        inc passes
        sec
        lda pending
        sbc #7
        sta pending
        tax
        beq @rts
        lda #<(rowbuf + 7*CARDS)
        sta PTR_SRC
        lda #>(rowbuf + 7*CARDS)
        sta PTR_SRC+1
        lda #<rowbuf
        sta PTR_DST
        lda #>rowbuf
        sta PTR_DST+1
@shift: ldy #CARDS-1
@byte:  lda (PTR_SRC),y
        sta (PTR_DST),y
        dey
        bpl @byte
        clc
        lda PTR_SRC
        adc #CARDS
        sta PTR_SRC
        bcc :+
        inc PTR_SRC+1
:       clc
        lda PTR_DST
        adc #CARDS
        sta PTR_DST
        bcc :+
        inc PTR_DST+1
:       dex
        bne @shift
@rts:   rts

; Vide les rangees restantes et avance jusqu'a la page suivante.
StopPrint:
        lda failed
        bne @done
        jsr io_begin
        lda ascii
        bne @text
        ldx pending
        beq @feed
@blank: cpx #7                  ; complete la passe avec des rangees vides
        bcs @flush
        lda row_lo,x
        sta PTR_DST
        lda row_hi,x
        sta PTR_DST+1
        ldy #CARDS-1
        lda #0
@zero:  sta (PTR_DST),y
        dey
        bpl @zero
        inx
        bne @blank
@flush: stx pending
        jsr emit_pass
@feed:  lda #CHR_BITIMAGE        ; meme interligne que pendant l'impression
        jsr CIOUT
        lda #TEAR_PASSES
        sta row
@tear:  lda passes
        cmp #PAGE_PASSES
        bcs @rest
        lda #CHR_CR
        jsr CIOUT
        inc passes
        dec row
        bne @tear
@rest:  sec                     ; le reste de la page attend la page suivante
        lda #PAGE_PASSES
        sbc passes
        sta page_feed
@text:  lda #CHR_TEXT
        jsr CIOUT
        jsr io_end
@done:  ldx #0
        rts

row_lo:
        .repeat ROWS_MAX, I
        .byte <(rowbuf + I*CARDS)
        .endrepeat
row_hi:
        .repeat ROWS_MAX, I
        .byte >(rowbuf + I*CARDS)
        .endrepeat

.assert * <= $7F40, error, "le pilote deborde de sa zone memoire"
