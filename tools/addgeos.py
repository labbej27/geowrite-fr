#!/usr/bin/env python3
"""Ajoute ou remplace un fichier GEOS (.cvt) dans un .d64 : addgeos.py image.d64 fichier.cvt

Les autres fichiers du disque ne sont pas modifies.
"""
import sys

SPT = [21] * 17 + [19] * 7 + [18] * 6 + [17] * 5
BAM = (18, 0)
INTERLEAVE = 8


def offset(t, s):
    return (sum(SPT[:t - 1]) + s) * 256


path, cvt_path = sys.argv[1:3]
d = bytearray(open(path, "rb").read())
cvt = open(cvt_path, "rb").read()
entry, info, data = cvt[:254], cvt[254:508], cvt[508:]
if entry[30:33] not in (b"SEQ", b"PRG"):
    sys.exit("Fichier .cvt non reconnu")
is_vlir = entry[30:33] == b"PRG"
bam = offset(*BAM)


def is_free(t, s):
    return d[bam + 4 * t + 1 + s // 8] >> (s % 8) & 1


def set_used(t, s, used):
    byte = bam + 4 * t + 1 + s // 8
    if used:
        d[byte] &= 0xFF ^ (1 << (s % 8))
        d[bam + 4 * t] -= 1
    else:
        d[byte] |= 1 << (s % 8)
        d[bam + 4 * t] += 1


def directory():
    t, s = 18, 1
    while t:
        o = offset(t, s)
        for i in range(0, 256, 32):
            yield o + i
        t, s = d[o], d[o + 1]


def free_chain(t, s):
    while t:
        o = offset(t, s)
        set_used(t, s, False)
        t, s = d[o], d[o + 1]


name = entry[3:19]
slot = None
for o in directory():
    if d[o + 2] and d[o + 5:o + 21] == name:
        if d[o + 23] == 1:              # VLIR : chaque enregistrement, puis l'index
            index = offset(d[o + 3], d[o + 4])
            for i in range(2, 256, 2):
                if d[index + i]:
                    free_chain(d[index + i], d[index + i + 1])
            set_used(d[o + 3], d[o + 4], False)
        else:
            free_chain(d[o + 3], d[o + 4])
        set_used(d[o + 21], d[o + 22], False)
        d[o + 2:o + 32] = bytes(30)
    if slot is None and d[o + 2] == 0:
        slot = o
if slot is None:
    sys.exit("Repertoire plein")

cursor = [17, 0]


def allocate():
    t, s = cursor
    while t <= 35:
        if t != 18:
            for k in range(SPT[t - 1]):
                candidate = (s + k * INTERLEAVE) % SPT[t - 1]
                if is_free(t, candidate):
                    set_used(t, candidate, True)
                    cursor[:] = [t, (candidate + INTERLEAVE) % SPT[t - 1]]
                    return t, candidate
        t, s = t + 1, 0
    sys.exit("Disque plein")


info_ts = allocate()
o = offset(*info_ts)
d[o:o + 2] = bytes([0, 0xFF])
d[o + 2:o + 256] = info



def write_chain(payload, last_byte=None):
    """Ecrit une chaine de secteurs et renvoie son premier secteur et sa longueur."""
    chunks = [payload[i:i + 254] for i in range(0, len(payload), 254)]
    places = [allocate() for _ in chunks]
    for n, (chunk, (t, s)) in enumerate(zip(chunks, places)):
        o = offset(t, s)
        if n + 1 < len(places):
            d[o:o + 2] = bytes(places[n + 1])
        else:
            d[o:o + 2] = bytes([0, last_byte if last_byte is not None else len(chunk) + 1])
        d[o + 2:o + 256] = chunk.ljust(254, b"\0")
    return places[0], len(chunks)


if is_vlir:
    table, body = data[:254], data[254:]
    index_ts = allocate()
    index = bytearray(256)
    index[0:2] = bytes([0, 0xFF])
    blocks = 1
    position = 0
    for i in range(0, 254, 2):
        count, last = table[i], table[i + 1]
        if count == 0:
            index[i + 2:i + 4] = bytes([0, last])
            continue
        length = (count - 1) * 254 + last - 1
        first, used = write_chain(body[position:position + length], last)
        index[i + 2:i + 4] = bytes(first)
        position += count * 254
        blocks += used
    d[offset(*index_ts):offset(*index_ts) + 256] = index
    first_ts = index_ts
else:
    first_ts, blocks = write_chain(data)

d[slot + 2] = entry[0]
d[slot + 3:slot + 5] = bytes(first_ts)
d[slot + 5:slot + 21] = name
d[slot + 21:slot + 23] = bytes(info_ts)
d[slot + 23] = entry[21]
d[slot + 24] = entry[22]
d[slot + 25:slot + 30] = entry[23:28]
d[slot + 30:slot + 32] = (blocks + 1).to_bytes(2, "little")
open(path, "wb").write(d)
