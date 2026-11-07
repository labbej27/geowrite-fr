#!/usr/bin/env python3
"""Genere les boutons et la regle en francais : mkicons.py [--preview]

Sources : les bitmaps anglais (cadre conserve, texte redessine).
Sorties : vendor/geos/kernal/dlgbox/icons_fr_*.inc et vendor/geowrite/fr/graph*.s
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bswwidth import encode as enc_text
from geosbmp import decode, encode

V = os.path.join(HERE, "..", "vendor")
FONT = os.path.join(V, "geos", "kernal", "bswfont", "bswfont_fr.inc")
PREVIEW = "--preview" in sys.argv

f = bytes(int(x, 16) for x in re.findall(r"\$([0-9a-f]{2})", open(FONT).read()))
stride, height = f[1] | f[2] << 8, f[3]
idx, bits = f[4] | f[5] << 8, f[6] | f[7] << 8
starts = [f[idx + 2 * i] | f[idx + 2 * i + 1] << 8 for i in range((bits - idx) // 2)]


def glyph(ch):
    i = ord(ch) - 32
    return [[f[bits + r * stride + x // 8] >> (7 - x % 8) & 1 for x in range(starts[i], starts[i + 1])]
            for r in range(height)]


def draw_bold(rows, text, left, right, top):
    text = enc_text(text)
    total = sum(len(glyph(c)[0]) + 1 for c in text)
    x = left + (right - left + 1 - total) // 2
    if x < left:
        sys.exit(f"Texte trop large pour le bouton : {text} ({total})")
    for c in text:
        g = glyph(c)
        for r, line in enumerate(g):
            for k, v in enumerate(line):
                if v:
                    rows[top + r][x + k] = 1
                    rows[top + r][x + k + 1] = 1
        x += len(g[0]) + 1


def button(text):
    """Bouton de 48x16 : cadre standard de GEOS et texte en gras."""
    out = [[1] * 47 + [0]]
    out += [[1] + [0] * 45 + [1, 1] for _ in range(13)]
    out += [[1] * 48, [0] + [1] * 47]
    draw_bold(out, text, 2, 44, 3)
    return out


def preview(name, rows, size):
    if PREVIEW:
        print(f"--- {name} : {size} octets")
        for r in rows:
            print("".join("#" if v else "." for v in r))


def as_bytes(data):
    lines = []
    for i in range(0, len(data), 16):
        lines.append("\t.byte " + ",".join(f"${b:02X}" for b in data[i:i + 16]))
    return "\n".join(lines) + "\n"


# --- Noyau ---------------------------------------------------------------
KERNEL_ICONS = {"DBIcPicOK": "OK", "DBIcPicCANCEL": "Annuler", "DBIcPicYES": "Oui",
                "DBIcPicNO": "Non", "DBIcPicOPEN": "Ouvrir", "DBIcPicDISK": "Disque"}
sizes = {}
for name, text in KERNEL_ICONS.items():
    new = button(text)
    data = encode(new)
    sizes[name] = len(data)
    preview(f"{name} {text}", new, len(data))
    open(os.path.join(V, "geos", "kernal", "dlgbox", f"icons_fr_{name}.inc"), "w").write(as_bytes(data))
print("noyau, octets :", sizes)

# --- geoWrite ------------------------------------------------------------
EN = os.path.join(V, "geowrite", "en")
FR = os.path.join(V, "geowrite", "fr")


def app_icons(filename, table):
    src = open(os.path.join(EN, filename)).read()
    parts = re.split(r"(graph_\w+):", src)
    out = ""
    for i in range(1, len(parts), 2):
        name = parts[i]
        data = bytes(int(x, 16) for x in re.findall(r"\$([0-9A-Fa-f]{2})", parts[i + 1]))
        new = button(table[name]) if table.get(name) else decode(data, 6, 16)[0]
        packed = encode(new) if table.get(name) else data
        preview(f"{name} {table.get(name)}", new, len(packed))
        out += f"{name}:\n" + as_bytes(packed)
    open(os.path.join(FR, filename), "w").write(out)


app_icons("graph2.s", {"graph_create": "Créer", "graph_exit": "Quitter"})
app_icons("graph3.s", {"graph_drive": "Lecteur"})
app_icons("graph4.s", {"graph_write_protected": None})
app_icons("graph5.s", {"graph_next": "Suivant", "graph_all": "Tout"})

# --- Regle : police de 3x5 ----------------------------------------------
SMALL = {
    "A": "###|#.#|###|#.#|#.#", "C": "###|#..|#..|#..|###", "D": "##.|#.#|#.#|#.#|##.",
    "E": "###|#..|##.|#..|###", "G": "###|#..|#.#|#.#|###", "H": "#.#|#.#|###|#.#|#.#",
    "I": "###|.#.|.#.|.#.|###", "L": "#..|#..|#..|#..|###", "N": "#.#|###|###|###|#.#",
    "O": "###|#.#|#.#|#.#|###", "P": "###|#.#|###|#..|#..", "R": "###|#.#|##.|#.#|#.#",
    "T": "###|.#.|.#.|.#.|.#.", "U": "#.#|#.#|#.#|#.#|###",
}
src = open(os.path.join(EN, "graph1.s")).read()
data = bytes(int(x, 16) for x in re.findall(r"\$([0-9A-Fa-f]{2})", src))
rows, used = decode(data, 40, 7)
# Colonnes occupees par les mots anglais, cases a cocher exclues.
REPLACE = [(0, 23, "GAUCHE"), (36, 62, "CENTRE"), (70, 93, "DROITE"), (103, 121, "PLEIN")]
SPACING = (202, 250, "INTERLIGNE")


def small_text(rows, x0, x1, text):
    for y in range(5):
        for x in range(x0, x1 + 1):
            rows[y][x] = 0
    x = x0 + (x1 - x0 + 2 - (4 * len(text))) // 2
    if x < x0:
        sys.exit(f"Mot trop large pour la regle : {text}")
    for ch in text:
        for y, line in enumerate(SMALL[ch].split("|")):
            for k, c in enumerate(line):
                if c == "#":
                    rows[y][x + k] = 1
        x += 4


occupied = [any(rows[y][x] for y in range(5)) for x in range(320)]
spans, start, gap = [], None, 0
for x, v in enumerate(occupied + [False] * 4):
    if v:
        start = x if start is None else start
        last, gap = x, 0
    elif start is not None:
        gap += 1
        if gap >= 3:
            spans.append((start, last))
            start = None
print("groupes de la regle :", spans)
for x0, x1, word in REPLACE + [SPACING]:
    small_text(rows, x0, x1, word)
packed = encode(rows)
print("regle :", len(packed), "octets, origine", used)
if PREVIEW:
    for r in rows[:6]:
        print("".join("#" if v else "." for v in r))
open(os.path.join(FR, "graph1.s"), "w").write("graph_rulerbuttons:\n" + as_bytes(packed))
