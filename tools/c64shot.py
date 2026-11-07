#!/usr/bin/env python3
"""Capture l'ecran bitmap GEOS ($A000) du C64 Ultimate en PNG noir et blanc."""
import os, struct, sys, urllib.request, zlib

IP = os.environ.get("C64_IP", "192.168.1.128")


def chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))


url = f"http://{IP}/v1/machine:readmem?address=A000&length=8000"
bitmap = urllib.request.urlopen(url, timeout=15).read()
if len(bitmap) != 8000:
    sys.exit(f"Lecture incomplete : {len(bitmap)} octets")
rows = bytearray()
for y in range(200):
    rows.append(0)                                   # filtre PNG : aucun
    for column in range(40):
        rows.append(0xFF ^ bitmap[column * 8 + (y // 8) * 320 + y % 8])
with open(sys.argv[1], "wb") as f:
    f.write(b"\x89PNG\r\n\x1a\n")
    f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", 320, 200, 1, 0, 0, 0, 0)))
    f.write(chunk(b"IDAT", zlib.compress(bytes(rows))))
    f.write(chunk(b"IEND", b""))
