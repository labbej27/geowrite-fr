#!/usr/bin/env python3
"""Genere vendor/geowrite/fr a partir de en/ et de la table de traduction.

Chaque texte anglais doit exister (sinon erreur) et la largeur de chaque ligne
est comparee a la largeur utile d'une boite de dialogue.
"""
import os, re, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bswwidth import encode, width

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vendor", "geowrite")
EN, FR = os.path.join(ROOT, "en"), os.path.join(ROOT, "fr")

T = {
"strings1.inc": {
 "geoWrite info": "infos geoWrite", "file": "fichier", "edit": "édit", "font": "fonte",
 "options": "opt", "close": "fermer", "update": "actualiser", "preview": "aperçu",
 "recover": "récupérer", "rename": "renommer", "print": "imprimer", "quit": "quitter",
 "cut": "couper", "copy": "copier", "paste": "coller", "text": "texte", "picture": "image",
 "search": "chercher", "find next": "suivant", "change, then find": "remplacer, suivant",
 "previous page": "page préc.", "next page": "page suiv.", "goto page": "aller à page",
 "page break": "saut de page", "set first page": "1ère page",
 "  plain text": "  normal", "bold": "gras", "italic": "italique", "outline": "contour",
 "underline": "souligné", "  superscript": "  exposant", "  subscript": "  indice",
 "  xx point": "  xx pts",
},
"strings2.inc": {
 "hide pictures": "sans images", " header": " entête", " footer": " bas page",
 "select page": "choisir page", "make full page wide": "pleine largeur",
 "  title page": "  page de titre", "  NLQ spacing": "  espace NLQ",
 "swapping geoWrite": "échange geoWrite", "Error I:": "Erreur E:",
 "Insufficient disk space": "Disque plein", "Page too big": "Page trop grande",
 "reading page": "lecture page", "writing page": "écriture page",
 "No previous page": "Pas de page préc.", "HEADER": "ENTETE", "FOOTER": "BAS DE PAGE",
},
"strings3.inc": {
 "Both geoWrite and data file": "geoWrite et le document",
 "must be on the same disk": "doivent être sur le même",
 "in a one drive system.": "disque avec un seul lecteur.",
},
"strings4a.inc": {
 "show": "voir", "hide": "sans",
 "photoScrap is beyond V2.1": "photoScrap trop récent",
 "File's picture area full.": "Zone d'images pleine.",
 "No photoScrap file on disk.": "Pas de photoScrap sur disque.",
 "photoScrap too big.": "photoScrap trop grand.",
},
"strings4b.inc": {
 "Can't copy picture to scrap": "Copie d'image impossible",
 "copying photoScrap into": "copie du photoScrap dans",
 "data file.": "le document.",
 "Page too big --": "Page trop grande --",
 "Inserting page break": "Saut de page inséré",
 "WARNING!": "ATTENTION !", "Disk near full.": "Disque presque plein.",
 "Please move/delete files": "Déplacez ou supprimez des",
 "from disk to continue.": "fichiers pour continuer.",
 "There are too many pages in": "Trop de pages dans ce",
 "this file.  Text at the end": "fichier. Le texte de fin",
 "is being lost.": "est perdu.",
 "Cannot add any more pages": "Impossible d'ajouter des",
 "to this file.  Cannot insert": "pages à ce fichier. Saut",
 "page break.": "de page non inséré.",
},
"strings5.inc": {
 "geoWrite by Tony Requist": "geoWrite par Tony Requist",
 "Version 2.1 for the C64": "Version 2.1 pour C64",
 "Not enough free space on": "Pas assez de place sur le",
 "disk for desk accessory.": "disque pour l'accessoire.",
 "Please Select Option:": "Choisissez une option :",
 "new document": "nouveau document", "existing document": "document existant",
 "to deskTop": "relancer geoWrite", "Insert new disk into disk drive.": "Insérez un autre disque.",
 "File exists, choose another.": "Ce fichier existe déjà.",
 "Data file is beyond V2.1": "Document trop récent",
 "Converting earlier file to ": "Conversion vers ", "converting file.": "conversion du fichier.",
 "On disk:": "Disque :", "WARNING!": "ATTENTION !",
 "This file is write protected.": "Ce fichier est protégé.",
 "Cannot recover from file.": "Récupération impossible.",
 "Please enter new filename:": "Nouveau nom de fichier :",
 "opening file": "ouverture fichier", "creating file": "création fichier",
 "running desk accessory": "lancement accessoire",
 "Cannot run desk accessory": "Pas d'accessoire dans un",
 "while in header or footer": "entête ou un bas de page",
 "File name already exists": "Ce nom existe déjà",
},
"strings6.inc": {
 "No next page": "Dernière page", "Cannot go to page": "Page inaccessible",
 "Enter page to go to:": "Aller à la page :", "Enter page number": "Numéro de la",
 "for first page:": "première page :", "Bad value": "Valeur fausse",
 "Delete last character": "Supprimer le dernier", "of the prev page?": "signe page préc. ?",
 "String not found": "Texte non trouvé", "Search / Replace": "Chercher / Remplacer",
 "Search For": "Chercher", "Replace With": "Remplacer",
 "Whole Word": "Mot entier", "Partial Word": "Mot partiel",
 "All Pages": "Partout", "This Page Only": "Cette page",
},
"strings7.inc": {
 "Printer is inaccessable.": "Imprimante inaccessible.", " Printing...": " Impression...",
 "Previewing...": "Aperçu...", "Print...": "Imprimer...", "High": "Haute", "Draft": "Rapide",
 "From Page": "De page", "To Page": "A page", "Single Sheet": "Feuille", "Tractor Feed": "Listing",
 "Please insert the next sheet": "Insérez la feuille suivante",
 "of paper to continue printing": "pour continuer l'impression",
 "TIME": "HEURE", "January": "janvier", "February": "février", "March": "mars", "April": "avril",
 "May": "mai", "June": "juin", "July": "juillet", "August": "août", "September": "septembre",
 "October": "octobre", "November": "novembre", "December": "décembre",
},
"strings_init.inc": {
 "This file must be opened by": "Ouvrez ce fichier avec",
 "geoWrite before it can": "geoWrite avant de",
 "be printed.": "l'imprimer.",
 "Please reboot your system": "Redémarrez le système",
 "using the same GEOS disk": "avec le même disque GEOS",
 "that was first used to run": "que celui utilisé pour",
 "Cannot install geoWrite on a": "Installation impossible",
 "write protected disk.": "sur disque protégé.",
 "Error installing geoWrite": "Erreur d'installation",
 "Cannot install geoWrite on": "Installation impossible",
 "this disk.  Please refer to": "sur ce disque. Voir les",
 "installation directions in": "instructions du",
 "the manual.": "manuel.",
 "geoWrite 2.1 installed.": "geoWrite 2.1 installé.",
},
"scantextscrap_strings.inc": {
 "textScrap is beyond V2.1": "textScrap trop récent",
 "reading textScrap": "lecture du textScrap",
},
}

# Mots remplaces en place par le programme : meme longueur, sans PLAINTEXT.
RAW = {
"strings2.inc": [('"open",PLAINTEXT', '"ouvre"')],
"strings6.inc": [('"open",PLAINTEXT', '"ouvre"'), ('"close"', '"ferme"')],
"strings5.inc": [('"Berkeley Softworks",0',
                  '"Berkeley Softworks"\n\t.byte\tGOTOXY\n\t.word\t80\n\t.byte\t112\n\t.byte\t"'
                  + encode("Mise à jour 2026 par LABBEJ27") + '",0')],
}
# Colonnes des raccourcis clavier, adaptees aux menus francais.
COLUMNS = {
"strings1.inc": {"$52": "$63", "$92": "$9F", "$A1": "$AE", "$B8": "$B4", "$E3": "$E4",
                 "$C7": "$C3", "$C1": "$BD", "$C3": "$BF"},
"strings2.inc": {"161": "174", "$A1": "$AE"},
}
LINE_KEEP = {"strings1.inc", "strings2.inc"}   # menus : largeurs gerees a part
DIALOG_WIDTH = 170                             # texte d'une boite, depuis sa marge, en gras

shutil.rmtree(FR, ignore_errors=True)
shutil.copytree(EN, FR)
problems = []
for name, table in T.items():
    path = os.path.join(FR, name)
    src = open(path).read()
    for old, new in RAW.get(name, []):
        if old not in src:
            problems.append(f"{name}: introuvable {old}")
        src = src.replace(old, new)
    for en, fr in table.items():
        pattern = '"' + en + '"'
        if pattern not in src:
            problems.append(f"{name}: introuvable {en!r}")
        src = src.replace(pattern, '"' + encode(fr) + '"')
        if name not in LINE_KEEP and width(fr, bold=True) > DIALOG_WIDTH:
            problems.append(f"{name}: trop large {fr!r} {width(fr, bold=True)} > {DIALOG_WIDTH}")
    columns = COLUMNS.get(name)
    if columns:
        src = re.sub(r"(\.word\s+)(\$[0-9A-F]{2}|\d+)\b",
                     lambda m: m.group(1) + columns.get(m.group(2), m.group(2)), src)
    open(path, "w").write(src)
for p in problems:
    print("PROBLEME", p)
if problems:
    sys.exit(1)
print("traduction : fichiers fr/ generes")
