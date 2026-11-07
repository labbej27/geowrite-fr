#!/usr/bin/env python3
"""Passe le C64 Ultimate en configuration d'origine, ou restaure tes reglages.

Les changements ne sont pas ecrits en flash : un redemarrage electrique
recharge donc les reglages enregistres sur la machine.
"""
import json, os, sys, urllib.parse, urllib.request

IP = os.environ.get("C64_IP", "192.168.1.128")
HERE = os.path.dirname(os.path.abspath(__file__))
BACKUP = os.path.join(HERE, "..", "config", "reglages-sauvegarde.json")

STOCK = {
    "U64 Specific Settings": {"Turbo Control": "Off", "CPU Speed": " 1"},
    "C64 and Cartridge Settings": {
        "Kernal ROM": "", "Cartridge": "", "RAM Expansion Unit": "Disabled",
    },
    "Drive A Settings": {"ROM for 1541 mode": "1541.rom"},
    "Drive B Settings": {"ROM for 1541 mode": "1541.rom"},
}


def api(path, method="GET", body=None):
    req = urllib.request.Request(f"http://{IP}{path}", method=method, data=body)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read() or b"{}")


def read(category, item):
    path = "/v1/configs/" + urllib.parse.quote(category) + "/" + urllib.parse.quote(item)
    return api(path)[category][item]["current"]


def apply(settings):
    result = api("/v1/configs", "POST", json.dumps(settings).encode())
    if result.get("errors"):
        sys.exit(f"Erreur du C64 : {result['errors']}")
    for category, items in settings.items():
        for item, wanted in items.items():
            got = read(category, item)
            if str(got).strip() != str(wanted).strip():
                sys.exit(f"Non applique : {item} = {got!r}, attendu {wanted!r}")
    api("/v1/machine:reset", "PUT")


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action == "stock":
        if not os.path.exists(BACKUP):   # ne jamais ecraser l'original
            os.makedirs(os.path.dirname(BACKUP), exist_ok=True)
            saved = {c: {i: read(c, i) for i in items} for c, items in STOCK.items()}
            with open(BACKUP, "w") as f:
                json.dump(saved, f, indent=2, ensure_ascii=False)
            print("Reglages sauvegardes dans config/reglages-sauvegarde.json")
        apply(STOCK)
        print("C64 en configuration d'origine (1 MHz, sans REU, JiffyDOS, cartouche).")
    elif action == "restore":
        with open(BACKUP) as f:
            apply(json.load(f))
        os.remove(BACKUP)
        print("Reglages restaures.")
    else:
        sys.exit("usage: c64cfg.py stock|restore")


main()
