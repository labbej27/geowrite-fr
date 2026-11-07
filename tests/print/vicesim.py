#!/usr/bin/env python3
"""Banc d'essai : pilote geoWrite dans VICE par clics et frappes simules.

vicesim.py PRG_OU_CRT D64 DOSSIER_SORTIE [etape ...]
Etapes : wait:S  click:X,Y  type:TEXTE  shot:NOM
"""
import os, socket, subprocess, sys, time

prg, d64, out = map(os.path.abspath, sys.argv[1:4])
PORT = int(os.environ.get("VICE_PORT", "6510"))
cmd_line = ["x64sc", "-console", "-default", "-sounddev", "dummy", "-warp",
            "-drive8truedrive", "-8", d64,
            "-busdevice4", "-devicebackend4", "1", "-pr4drv", "mps803", "-pr4output", "graphics",
            "-pr4txtdev", "0",
            "-remotemonitor", "-remotemonitoraddress", f"ip4://127.0.0.1:{PORT}",
            *(["-cartcrt", prg] if prg.endswith(".crt") else ["-autostartprgmode", "1", "-autostart", prg])]
vice = subprocess.Popen(cmd_line, cwd=out, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def monitor(text, settle=0.1):
    """Envoie une commande et lit la reponse jusqu'au silence."""
    with socket.create_connection(("127.0.0.1", PORT), timeout=20) as s:
        s.sendall((text + "\n").encode())
        time.sleep(settle)
        s.settimeout(0.4)
        reply = b""
        try:
            while True:
                data = s.recv(16384)
                if not data:
                    break
                reply += data
        except OSError:
            pass
        return reply.decode("latin1")


def poke(addr, *values):
    monitor(f"> {addr:04x} " + " ".join(f"{v:02x}" for v in values))


def press(flag_bit):
    reply = monitor("m 0039 0039")
    parts = reply.split(">C:0039")
    flag = int(parts[1].split()[0], 16) if len(parts) > 1 else 0
    if len(parts) < 2:
        print("lecture pressFlag:", repr(reply[:120]), flush=True)
    poke(0x39, flag | flag_bit)


def click(x, y):
    poke(0x3A, x & 255, x >> 8)
    poke(0x3C, y)
    time.sleep(0.2)
    poke(0x8505, 0)
    press(0x20)
    time.sleep(0.3)
    poke(0x8505, 0x80)
    press(0x20)


def peek(addr):
    reply = monitor(f"m {addr:04x} {addr:04x}")
    return int(reply.split(f">C:{addr:04x}")[1].split()[0], 16)


def key(ch):
    """Ajoute une touche dans la file clavier de GEOS, comme le fait son scan."""
    tail = peek(0x87D8)
    poke(0x87DA + tail, ord(ch))
    poke(0x87D8, (tail + 1) % 16)
    press(0x80)
    time.sleep(0.15)


try:
    time.sleep(3)
    for step in sys.argv[4:]:
        verb, _, arg = step.partition(":")
        if verb == "wait":
            time.sleep(float(arg))
        elif verb == "click":
            click(*map(int, arg.split(",")))
        elif verb == "type":
            for ch in arg:
                key("\r" if ch == "^" else ch)
        elif verb == "mon":
            print(monitor(arg, 1.5))
        elif verb == "shot":
            monitor(f'screenshot "{out}/{arg}.png" 2', 1.0)
        print("ok", step, flush=True)
finally:
    vice.kill()
