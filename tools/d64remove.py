#!/usr/bin/env python3
"""Retire des fichiers GEOS d'un .d64 et libere leurs blocs : d64remove.py image NOM [...]"""
import sys

SPT = [21] * 17 + [19] * 7 + [18] * 6 + [17] * 5


def offset(t, s):
    return (sum(SPT[:t - 1]) + s) * 256


path, *names = sys.argv[1:]
d = bytearray(open(path, "rb").read())
bam = offset(18, 0)


def release(t, s):
    d[bam + 4 * t + 1 + s // 8] |= 1 << (s % 8)
    d[bam + 4 * t] += 1


def release_chain(t, s):
    while t:
        o = offset(t, s)
        next_t, next_s = d[o], d[o + 1]
        release(t, s)
        t, s = next_t, next_s


wanted = {n.encode().ljust(16, b"\xA0") for n in names}
t, s = 18, 1
while t:
    o = offset(t, s)
    for e in range(o, o + 256, 32):
        if d[e + 2] and bytes(d[e + 5:e + 21]) in wanted:
            if d[e + 23] == 1:                      # VLIR : enregistrements puis index
                index = offset(d[e + 3], d[e + 4])
                for i in range(2, 256, 2):
                    if d[index + i]:
                        release_chain(d[index + i], d[index + i + 1])
                release(d[e + 3], d[e + 4])
            else:
                release_chain(d[e + 3], d[e + 4])
            release(d[e + 21], d[e + 22])
            d[e + 2:e + 32] = bytes(30)
    t, s = d[o], d[o + 1]
open(path, "wb").write(d)
