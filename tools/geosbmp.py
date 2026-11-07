"""Bitmaps compresses GEOS (format BitmapUp) : decodage et encodage."""


def decode(data, width_cards, height):
    """Renvoie (lignes de bits, octets consommes). Largeur en cartes, hauteur en pixels."""
    need = width_cards * height
    out = bytearray()
    i = 0
    while len(out) < need:
        b = data[i]; i += 1
        if b < 128:                                   # repetition
            out += bytes([data[i]]) * b; i += 1
        elif b < 220:                                 # octets litteraux
            n = b - 128
            out += data[i:i + n]; i += n
        else:                                         # BIGCOUNT : $DC+longueur, repetitions
            length = b - 220
            count = data[i]; i += 1
            end = i + length
            pattern = bytearray()
            while i < end:
                c = data[i]; i += 1
                if c < 128:
                    pattern += bytes([data[i]]) * c; i += 1
                else:
                    k = c - 128
                    pattern += data[i:i + k]; i += k
            out += pattern * count
    rows = [[(out[y * width_cards + x // 8] >> (7 - x % 8)) & 1 for x in range(width_cards * 8)] for y in range(height)]
    return rows, i


def _pack(raw):
    """Repetitions et octets litteraux d'une suite d'octets."""
    out = bytearray()
    literal = bytearray()

    def flush():
        nonlocal literal
        while literal:
            part = literal[:91]
            out.append(128 + len(part))
            out.extend(part)
            literal = literal[91:]

    i = 0
    while i < len(raw):
        run = 1
        while i + run < len(raw) and raw[i + run] == raw[i] and run < 127:
            run += 1
        if run >= 3:
            flush()
            out += bytes([run, raw[i]])
            i += run
        else:
            literal.append(raw[i])
            i += 1
    flush()
    return bytes(out)


def encode(rows):
    """Encode des lignes de bits (largeur multiple de 8), lignes identiques en BIGCOUNT."""
    packed_rows = []
    for row in rows:
        raw = bytearray()
        for x in range(0, len(row), 8):
            v = 0
            for bit in row[x:x + 8]:
                v = v << 1 | bit
            raw.append(v)
        packed_rows.append(bytes(raw))
    out = bytearray()
    i = 0
    while i < len(packed_rows):
        n = 1
        while i + n < len(packed_rows) and packed_rows[i + n] == packed_rows[i] and n < 255:
            n += 1
        body = _pack(packed_rows[i])
        if n >= 2 and len(body) <= 35 and 2 + len(body) < n * len(body):
            out += bytes([220 + len(body), n]) + body     # $DC+longueur, repetitions
            i += n
        else:
            out += body
            i += 1
    return bytes(out)
