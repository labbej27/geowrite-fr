"""Largeur en pixels d'un texte dans la police systeme francaise."""
import re, os
INC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vendor/geos/kernal/bswfont/bswfont_fr.inc")
ENCODE = str.maketrans({"é": "{", "è": "|", "à": "}", "ç": "~", "ê": "[", "ù": "]", "ô": "\\", "î": "^"})


def _load():
    data = bytes(int(x, 16) for x in re.findall(r"\$([0-9a-f]{2})", open(INC).read()))
    idx, bits = data[4] | data[5] << 8, data[6] | data[7] << 8
    n = (bits - idx) // 2
    s = [data[idx + 2 * i] | data[idx + 2 * i + 1] << 8 for i in range(n)]
    return [s[i + 1] - s[i] for i in range(n - 1)]


WIDTHS = _load()


def encode(text):
    return text.translate(ENCODE)


def width(text, bold=False):
    plain = encode(text)
    return sum(WIDTHS[ord(c) - 32] + (1 if bold else 0) for c in plain if 32 <= ord(c) < 32 + len(WIDTHS))
