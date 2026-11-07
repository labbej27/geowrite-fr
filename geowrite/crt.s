; Demarrage de la cartouche EasyFlash de geoWrite.
;
; Banque 0 : ROMH contient le demarrage Ultimax, ROML l'autostart CBM80.
; Banques suivantes : noyau GEOS, puis disque virtuel (voir tools/mkcrt.py).
; KERNEL_PAGES, KERNEL_BANK et DISK_BANK viennent de la ligne de commande.
        .setcpu "6502"

EF_BANK    = $DE00
EF_CONTROL = $DE02
MODE_16K   = $07
MODE_OFF   = $04
BUFFER     = $0800               ; libre au demarrage ; $0200-$02FF contient des variables de la ROM
RAM_CODE   = $0340
KERNEL_RUN = $C003
BOOT_DEVICE = 8
DRIVE_WAIT_FRAMES = 150       ; laisse le lecteur finir son propre demarrage

r4L = $0A
PTR = $FB

        .segment "ROML"
        .word cold, cold
        .byte $C3, $C2, $CD, $38, $30   ; signature CBM80
cold:   sei
        stx $D016
        jsr $FDA3               ; IOINIT
        jsr $FD50               ; RAMTAS
        jsr $FD15               ; RESTOR
        jsr $FF5B               ; CINT
        ldx #ram_end - ram_start - 1
@copy:  lda ram_image,x
        sta RAM_CODE,x
        dex
        cpx #$FF
        bne @copy
        jmp boot

ram_image:
        .org RAM_CODE
ram_start:

; Doit rester en $0340 : le pilote disque appelle cette adresse.
; Lit le secteur r1H de la piste virtuelle vers (r4). Renvoie X = 0, Y = 0.
ROMRead:
        php
        sei
        lda $01
        pha
        lda #$37
        sta $01
        lda $05                 ; r1H : numero de bloc
        pha
        lsr
        lsr
        lsr
        lsr
        lsr
        clc
        adc #DISK_BANK
        sta EF_BANK
        lda #MODE_16K
        sta EF_CONTROL
        pla
        and #$1F
        ora #$80
        sta @src+2
        ldy #0
@src:   lda $8000,y
        sta (r4L),y
        iny
        bne @src
        lda #MODE_OFF
        sta EF_CONTROL
        pla
        sta $01
        plp
        ldx #0
        ldy #0
        rts

; Recopie le noyau de la ROM vers $5000-$FFFF, RAM sous les E/S comprise.
boot:   lda #0
        sta PTR                 ; numero de page copiee
@page:  lda #$37
        sta $01
        lda PTR
        lsr
        lsr
        lsr
        lsr
        lsr
        clc
        adc #KERNEL_BANK
        sta EF_BANK
        lda PTR
        and #$1F
        ora #$80
        sta @from+2
        ldy #0
@from:  lda $8000,y
        sta BUFFER,y
        iny
        bne @from
        lda #$30                ; tout en RAM
        sta $01
        clc
        lda PTR
        adc #$50
        sta @to+2
@copy:  lda BUFFER,y
@to:    sta $5000,y
        iny
        bne @copy
        inc PTR
        lda PTR
        cmp #KERNEL_PAGES
        bne @page
        lda #$37
        sta $01
        lda #MODE_OFF
        sta EF_CONTROL
        ldx #DRIVE_WAIT_FRAMES
@wait:  bit $D011
        bpl @wait
@vbl:   bit $D011
        bmi @vbl
        dex
        bne @wait
        lda #BOOT_DEVICE
        sta $BA
        jmp KERNEL_RUN

ram_end:
.assert ram_end <= $03FC, error, "code residant trop grand"
        .reloc

        .segment "ROMH"
; Ultimax au demarrage : seule cette ROM et 4 Ko de RAM sont visibles.
ultimax:
        sei
        ldx #$FF
        txs
        cld
        ldx #stub_end - stub - 1
@copy:  lda stub,x
        sta $0100,x
        dex
        bpl @copy
        jmp $0100
stub:   lda #MODE_16K           ; KERNAL visible et CBM80 en $8000
        sta EF_CONTROL
        jmp $FCE2
stub_end:

        .segment "VECTORS"
        .word ultimax, ultimax, ultimax
