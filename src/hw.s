; Routines materielles, appelees depuis le C (convention __fastcall__).
        .export _wait_frame, _read_joy2, _sfx_blip, _idle_count

RASTER   = $d012
CIA1_PRA = $dc00
SID      = $d400
SYNC_LINE = 250

        .bss
_idle_count:
        .res 3                  ; iterations d'attente sur la derniere image

        .code
; Attend la ligne raster SYNC_LINE et compte le temps CPU restant.
_wait_frame:
        lda #0
        sta _idle_count
        sta _idle_count+1
        sta _idle_count+2
@leave: lda RASTER              ; si on est deja sur la ligne, on la quitte
        cmp #SYNC_LINE
        beq @leave
@spin:  inc _idle_count
        bne @check
        inc _idle_count+1
        bne @check
        inc _idle_count+2
@check: lda RASTER
        cmp #SYNC_LINE
        bne @spin
        rts

; Joystick port 2. Bits a 1 = actif : 0 haut, 1 bas, 2 gauche, 3 droite, 4 feu.
_read_joy2:
        lda CIA1_PRA
        eor #$ff
        and #$1f
        ldx #0
        rts

; Bref son sur la voix 1 du SID.
_sfx_blip:
        lda #$0f
        sta SID+$18             ; volume max
        lda #$09
        sta SID+$05             ; attaque 0, declin 9
        lda #$00
        sta SID+$06             ; sustain 0, release 0
        sta SID+$00
        lda #$40
        sta SID+$01             ; frequence
        lda #$10
        sta SID+$04             ; triangle, gate off
        lda #$11
        sta SID+$04             ; triangle, gate on
        rts
