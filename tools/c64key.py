#!/usr/bin/env python3
"""Ajoute du texte dans la file clavier de GEOS sur le C64 Ultimate : c64key.py TEXTE (^ = Entree)"""
import os, sys, time, urllib.request
IP = os.environ.get("C64_IP", "192.168.1.128")
TAIL, QUEUE, PRESS_FLAG, KEYPRESS = 0x87D8, 0x87DA, 0x39, 0x80


def write(addr, data):
    url = f"http://{IP}/v1/machine:writemem?address={addr:04X}&data={data.hex()}"
    urllib.request.urlopen(urllib.request.Request(url, method="PUT"), timeout=10).read()


def read(addr):
    return urllib.request.urlopen(f"http://{IP}/v1/machine:readmem?address={addr:04X}&length=1", timeout=10).read()[0]


for ch in sys.argv[1]:
    tail = read(TAIL)
    write(QUEUE + tail, bytes([13 if ch == "^" else ord(ch)]))
    write(TAIL, bytes([(tail + 1) % 16]))
    write(PRESS_FLAG, bytes([read(PRESS_FLAG) | KEYPRESS]))
    time.sleep(0.25)
