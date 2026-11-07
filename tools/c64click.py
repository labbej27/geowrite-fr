#!/usr/bin/env python3
"""Simule un clic GEOS sur le C64 Ultimate : c64click.py X Y"""
import os, sys, time, urllib.request
IP = os.environ.get("C64_IP", "192.168.1.128")
MOUSE_X, MOUSE_Y, PRESS_FLAG, MOUSE_DATA = 0x3A, 0x3C, 0x39, 0x8505
MOUSE_BIT = 0x20


def write(addr, data):
    url = f"http://{IP}/v1/machine:writemem?address={addr:04X}&data={data.hex()}"
    urllib.request.urlopen(urllib.request.Request(url, method="PUT"), timeout=10).read()


def read(addr):
    return urllib.request.urlopen(f"http://{IP}/v1/machine:readmem?address={addr:04X}&length=1", timeout=10).read()[0]


x, y = int(sys.argv[1]), int(sys.argv[2])
write(MOUSE_X, bytes([x & 255, x >> 8]))
write(MOUSE_Y, bytes([y]))
time.sleep(0.2)
write(MOUSE_DATA, b"\x00")
write(PRESS_FLAG, bytes([read(PRESS_FLAG) | MOUSE_BIT]))
time.sleep(0.3)
write(MOUSE_DATA, b"\x80")
write(PRESS_FLAG, bytes([read(PRESS_FLAG) | MOUSE_BIT]))
