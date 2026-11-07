#!/usr/bin/env python3
"""Transforme un .d64 CBM en disque GEOS : signature et bloc frontiere."""
import sys
path = sys.argv[1]
d = bytearray(open(path, 'rb').read())
DIRHEAD = 0x16500
TRACK, SECTOR = 19, 8
offset = (17 * 21 + 19 + SECTOR) * 256
d[offset:offset + 256] = bytes([0, 0xFF]) + bytes(254)
bam = DIRHEAD + 4 * TRACK
if d[bam + 1 + SECTOR // 8] & (1 << (SECTOR % 8)):
    d[bam] -= 1
    d[bam + 1 + SECTOR // 8] &= 0xFF ^ (1 << (SECTOR % 8))
d[DIRHEAD + 0xAB] = TRACK
d[DIRHEAD + 0xAC] = SECTOR
d[DIRHEAD + 0xAD:DIRHEAD + 0xBD] = b'GEOS format V1.0'
open(path, 'wb').write(d)
