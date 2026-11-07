#!/usr/bin/env python3
"""Assemble la cartouche EasyFlash de geoWrite.

mkcrt.py banque0.bin noyau.prg sortie.crt fichier.cvt [...]
Les .cvt deviennent un petit disque virtuel (piste 36) : bloc 0 = repertoire.
"""
import struct, sys

ROM_TRACK = 36
BANK = 0x2000
bank0, kernel_prg, out, *cvts = sys.argv[1:]
kernel = open(kernel_prg, "rb").read()[2:]
blocks = [bytearray(256)]                         # repertoire
entries = []


def add_block(link, payload):
    blocks.append(bytearray(bytes(link) + payload.ljust(254, b"\0")))
    return len(blocks) - 1


def add_chain(payload, last_byte=None):
    chunks = [payload[i:i + 254] for i in range(0, len(payload), 254)]
    first = len(blocks)
    for n, chunk in enumerate(chunks):
        if n + 1 < len(chunks):
            link = (ROM_TRACK, first + n + 1)
        else:
            link = (0, last_byte if last_byte is not None else len(chunk) + 1)
        add_block(link, chunk)
    return first, len(chunks)


for path in cvts:
    cvt = open(path, "rb").read()
    entry, info, data = cvt[:254], cvt[254:508], cvt[508:]
    info_block = add_block((0, 0xFF), info)
    if cvt[30:33] == b"PRG":                      # VLIR : index puis enregistrements
        table, body = data[:254], data[254:]
        index_block = add_block((0, 0xFF), b"")
        index = bytearray(254)
        position = 0
        total = 1
        for i in range(0, 254, 2):
            count, last = table[i], table[i + 1]
            if count == 0:
                index[i:i + 2] = bytes([0, last])
                continue
            length = (count - 1) * 254 + last - 1
            first, used = add_chain(body[position:position + length], last)
            index[i:i + 2] = bytes([ROM_TRACK, first])
            position += count * 254
            total += used
        blocks[index_block][2:] = index
        first = index_block
    else:
        first, total = add_chain(data)
    entries.append(bytes([entry[0], ROM_TRACK, first]) + entry[3:19] + bytes([ROM_TRACK, info_block])
                   + entry[21:23] + entry[23:28] + (total + 1).to_bytes(2, "little"))
if len(blocks) > 256:
    sys.exit(f"Disque virtuel trop grand : {len(blocks)} blocs")
directory = blocks[0]
directory[0:2] = bytes([0, 0xFF])
for i, e in enumerate(entries):
    directory[2 + 32 * i:2 + 32 * i + len(e)] = e

raw_bank0 = open(bank0, "rb").read()
if len(raw_bank0) != 2 * BANK:
    sys.exit("Banque 0 : taille inattendue")
disk = b"".join(bytes(b) for b in blocks)
header = (b"C64 CARTRIDGE   " + struct.pack(">IHHBB", 0x40, 0x0100, 32, 1, 0) + bytes(6)
          + b"GEOWRITE FR".ljust(32, b"\0"))


def chip(bank, load, data):
    return b"CHIP" + struct.pack(">IHHHH", 0x10 + BANK, 2, bank, load, BANK) + data.ljust(BANK, b"\xFF")


rom = bytearray(header)
rom += chip(0, 0x8000, raw_bank0[:BANK])
rom += chip(0, 0xA000, raw_bank0[BANK:])
bank = 1
for image in (kernel, disk):
    for i in range(0, len(image), BANK):
        rom += chip(bank, 0x8000, image[i:i + BANK])
        bank += 1
open(out, "wb").write(rom)
print(f"{out} : {bank} banques, {len(blocks)} blocs virtuels, {len(rom)} octets")
