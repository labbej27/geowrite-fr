#!/usr/bin/env python3
"""Relit le repertoire d'un .d64 GEOS et verifie les fichiers : d64dump.py image [nom pilote.bin]"""
import sys

SPT = [21] * 17 + [19] * 7 + [18] * 6 + [17] * 5


def offset(t, s):
    return (sum(SPT[:t - 1]) + s) * 256


d = open(sys.argv[1], "rb").read()
sec = lambda t, s: d[offset(t, s):offset(t, s) + 256]
t, s = 18, 1
found = {}
while t:
    b = sec(t, s)
    for i in range(0, 256, 32):
        e = b[i:i + 32]
        if e[2] == 0:
            continue
        name = e[5:21].split(b"\xA0")[0].decode("latin1")
        print(f"{name:16} ctype={e[2]:02x} data={e[3]}/{e[4]} info={e[21]}/{e[22]} "
              f"struct={e[23]} gtype={e[24]} blocks={e[30] | e[31] << 8}")
        found[name.lower()] = e
    t, s = b[0], b[1]
if len(sys.argv) > 3:
    e = found[sys.argv[2].lower()]
    want = open(sys.argv[3], "rb").read()
    info = sec(e[21], e[22])
    print("info: link", info[0], info[1], "cmdr", hex(info[68]), "geos", info[69], "struct", info[70],
          "start", hex(info[71] | info[72] << 8), "end", hex(info[73] | info[74] << 8),
          "vec", hex(info[75] | info[76] << 8), "nom", info[77:93])
    t, s = e[3], e[4]
    data, chain = b"", []
    while t:
        b = sec(t, s)
        chain.append((t, s, b[0], b[1]))
        data += b[2:256] if b[0] else b[2:b[1] + 1]
        t, s = b[0], b[1] if b[0] else 0
    print("chaine", chain)
    same = data[:len(want)] == want
    print("taille lue", len(data), "attendue", len(want), "identique" if same else "DIFFERENT")
    sys.exit(0 if same else 1)
