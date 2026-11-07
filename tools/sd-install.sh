#!/bin/sh
# Installe la cartouche sur la SD, cree documents.d64 s'il manque, monte et lance.
# documents.d64 n'est jamais ecrase : il contient les documents de l'utilisateur.
set -eu
IP="${C64_IP:-192.168.1.128}"
SD="ftp://$IP/SD/geowrite"
BACKUP_DIR="documents/sauvegardes"
mkdir -p "$BACKUP_DIR"
LIST="$(curl -fsS -m 10 -l "$SD/")"
curl -fsS -m 15 -X PUT "http://$IP/v1/drives/a:remove" >/dev/null || true
sleep 2
if printf '%s\n' "$LIST" | grep -qx documents.d64; then
    curl -fsS -m 30 "$SD/documents.d64" -o "$BACKUP_DIR/documents-$(date +%Y%m%d-%H%M%S).d64"
else
    WORK="$(mktemp -t documents)"
    if printf '%s\n' "$LIST" | grep -qx geowrite.d64; then
        curl -fsS -m 30 "$SD/geowrite.d64" -o "$WORK"
        cp "$WORK" "$BACKUP_DIR/geowrite-avant-cartouche-$(date +%Y%m%d-%H%M%S).d64"
        python3 -I tools/d64remove.py "$WORK" GEOWRITE MPS-803
    else
        cp geowrite/build/documents.d64 "$WORK"
    fi
    curl -fsS -m 30 -T "$WORK" "$SD/documents.d64"
    rm -f "$WORK"
fi
curl -fsS -m 30 -T geowrite/build/geowrite.crt "$SD/geowrite.crt"
curl -fsS -m 15 -X PUT "http://$IP/v1/drives/a:mount?image=/SD/geowrite/documents.d64&mode=readwrite" >/dev/null
curl -fsS -m 30 -X POST --data-binary @geowrite/build/geowrite.crt \
  -H 'Content-Type: application/octet-stream' "http://$IP/v1/runners:run_crt"
