#!/usr/bin/env python3
"""Genere la police systeme francaise de GEOS : mkfont.py bswfont.s sortie.inc

Huit symboles rares cedent leur place aux accents francais :
{ e aigu, | e grave, } a grave, ~ c cedille, [ e circonflexe, ] u grave,
backslash o circonflexe, ^ i circonflexe.
La bande de pixels garde sa taille : le noyau ne bouge pas.
"""
import re, sys

# Base, accent (rangees 0 et 1 au-dessus de la lettre) ; None = cedille dessous.
GRAVE = ["#..", ".#."]
AIGU = [".#.", "#.."]
CIRC = [".#.", "#.#"]
ACCENTS = {
    "{": ("e", AIGU), "|": ("e", GRAVE), "}": ("a", GRAVE), "~": ("c", None),
    "[": ("e", CIRC), "]": ("u", GRAVE), "\\": ("o", CIRC), "^": ("i", CIRC),
}

src = open(sys.argv[1]).read()
start = src.index(".else", src.index("gateway_font"))
body = src[start:src.index(".endif", start)]
font = bytes(int(x, 16) for x in re.findall(r"\$([0-9a-f]{2})", body))
baseline, stride, height = font[0], font[1] | font[2] << 8, font[3]
idx_off, bits_off = font[4] | font[5] << 8, font[6] | font[7] << 8
count = (bits_off - idx_off) // 2 - 1
starts = [font[idx_off + 2 * i] | font[idx_off + 2 * i + 1] << 8 for i in range(count + 1)]
pixel = lambda row, x: font[bits_off + row * stride + x // 8] >> (7 - x % 8) & 1
glyphs = [[[pixel(r, x) for x in range(starts[i], starts[i + 1])] for r in range(height)]
          for i in range(count)]
slot = lambda ch: ord(ch) - 32


def accented(base, accent):
    g = [row[:] for row in glyphs[slot(base)]]
    w = len(g[0])
    if accent is None:                       # cedille : deux rangees sous la ligne
        mid = (w - 1) // 2
        g[baseline + 1][mid] = 1
        g[baseline + 2][mid] = 1
        g[baseline + 2][max(mid - 1, 0)] = 1
        return g
    off = 2 if w >= 6 else 1                 # la colonne 0 des lettres est vide
    if base == "i":                          # sans point, tige centree sous l'accent
        stem = [r for r in range(2, height) if g[r][1]]
        g = [[0] * 4 for _ in range(height)]
        for r in stem:
            g[r][2] = 1
        off = 1
    for r, line in enumerate(accent):
        for c, ch in enumerate(line):
            if ch == "#":
                g[r][off + c] = 1
    return g


for ch, (base, accent) in ACCENTS.items():
    glyphs[slot(ch)] = accented(base, accent)

# Un pixel de moins sur le soulignement pour rester dans la bande de pixels.
glyphs[slot("_")] = [row[:-1] for row in glyphs[slot("_")]]

widths = [len(g[0]) for g in glyphs]
if sum(widths) > stride * 8:
    sys.exit(f"Police trop large : {sum(widths)} > {stride * 8}")
strip = bytearray(stride * height)
x = 0
new_starts = []
for g in glyphs:
    new_starts.append(x)
    for r, row in enumerate(g):
        for c, v in enumerate(row):
            if v:
                strip[r * stride + (x + c) // 8] |= 0x80 >> ((x + c) % 8)
    x += len(g[0])
new_starts.append(x)
out = bytearray(font[:idx_off])
for v in new_starts:
    out += v.to_bytes(2, "little")
out += strip
if len(out) != len(font):
    sys.exit(f"Taille changee : {len(out)} au lieu de {len(font)}")
with open(sys.argv[2], "w") as f:
    f.write("; Genere par tools/mkfont.py : ne pas modifier a la main.\n")
    for i in range(0, len(out), 16):
        f.write("\t.byte " + ",".join(f"${b:02x}" for b in out[i:i + 16]) + "\n")
print(f"largeur totale {x}/{stride * 8}, {len(out)} octets")
for ch in ACCENTS:
    print(f"--- {ch!r} = {ACCENTS[ch][0]}")
    for row in glyphs[slot(ch)]:
        print("".join("#" if v else "." for v in row))
for ch in "ei":
    print(f"--- reference {ch}")
    for row in glyphs[slot(ch)]:
        print("".join("#" if v else "." for v in row))
