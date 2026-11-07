#!/usr/bin/env python3
"""Emballe un pilote d'imprimante brut en .cvt GEOS : mkprinter.py driver.bin sortie.cvt"""
import sys

START = 0x7900
NAME = b"MPS-803"
driver = open(sys.argv[1], "rb").read()
sectors = (len(driver) + 253) // 254

entry = bytearray(254)
entry[0] = 0x83
entry[3:19] = NAME.ljust(16, b"\xA0")
entry[21] = 0                       # structure sequentielle
entry[22] = 9                       # type GEOS : imprimante
entry[23:28] = bytes([88, 7, 6, 13, 16])
entry[28:30] = (sectors + 1).to_bytes(2, "little")
entry[30:58] = b"SEQ formatted GEOS file V1.0"

info = bytearray(254)
info[0:3] = bytes([3, 21, 0xBF])
info[3:66] = bytes([0xFF, 0xFF, 0xFF]) + bytes([0x80, 0, 1]) * 19 + bytes([0xFF, 0xFF, 0xFF])
info[66] = 0x83                     # type C64 (decalages de l'en-tete moins 2)
info[67] = 9
info[68] = 0
padded = driver + bytes(-len(driver) % 254)
end = START + len(padded) - 1       # le dernier secteur est complet
info[69:71] = START.to_bytes(2, "little")
info[71:73] = end.to_bytes(2, "little")
info[73:75] = START.to_bytes(2, "little")
info[75:95] = b"MPS-803     V1.0".ljust(20, b"\0")
info[158:] = b"Pilote MPS-803, mode graphique.\0".ljust(96, b"\0")

open(sys.argv[2], "wb").write(bytes(entry) + bytes(info) + padded)
