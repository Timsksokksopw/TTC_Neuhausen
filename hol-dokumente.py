#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hol-dokumente.py — holt die Vereinsdokumente von der bisherigen Website.

    python3 hol-dokumente.py           lädt, was noch fehlt
    python3 hol-dokumente.py --alle    lädt auch neu, was schon da ist

Die vierzehn Statuten, Reglemente, Tarife und Beitrittsformulare liegen
noch auf der bisherigen Website. Damit auf der neuen kein Verweis mehr
dorthin zeigt, müssen die Dateien mitziehen — dieses Skript holt sie in
einem Durchgang nach

    site/assets/dokumente/

und benennt sie dabei so, wie vorlage/dokumente.py sie erwartet. Danach
verweist verein-downloads.html von selbst auf die eigenen Dateien; ein
`python3 build.py` genügt.

Das Skript läuft **einmal**, vor dem Umzug. Es gehört nicht in den Build:
eine Website, die bei jedem Bauen fremde Server anfragt, baut irgendwann
nicht mehr.

Es lädt ausschliesslich die Adressen, die in vorlage/dokumente.py stehen —
die eigenen Dateien des Vereins, von der eigenen Website.
"""

import sys
import urllib.error
import urllib.request
from pathlib import Path

WURZEL = Path(__file__).resolve().parent
sys.path.insert(0, str(WURZEL / "vorlage"))

from dokumente import BEITRITTSFORMULARE, DOKUMENTE  # noqa: E402

ZIEL = WURZEL / "site" / "assets" / "dokumente"

# Manche Server geben ohne erkennbaren Browser einen Fehler zurück.
KOPFZEILEN = {"User-Agent": "TTCN-Website-Umzug/1.0 (+https://www.ttc-neuhausen.ch/)"}


def hole(eintrag, alle):
    ziel = ZIEL / eintrag["datei"]
    if ziel.exists() and not alle:
        print("  schon da   %s" % eintrag["datei"])
        return True

    anfrage = urllib.request.Request(eintrag["herkunft"], headers=KOPFZEILEN)
    try:
        with urllib.request.urlopen(anfrage, timeout=60) as antwort:
            daten = antwort.read()
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as fehler:
        print("  FEHLER     %s — %s" % (eintrag["datei"], fehler))
        return False

    # Eine Fehlerseite ist auch eine Antwort. Wer eine 2 kB grosse
    # «Seite nicht gefunden» als Statuten ablegt, merkt es erst, wenn
    # jemand sie öffnet.
    if daten[:5] not in (b"%PDF-", b"PK\x03\x04") and len(daten) < 4096:
        print("  VERDÄCHTIG %s — nur %d Bytes, sieht nicht nach einem "
              "Dokument aus. Nicht gespeichert." % (eintrag["datei"], len(daten)))
        return False

    ZIEL.mkdir(parents=True, exist_ok=True)
    ziel.write_bytes(daten)
    print("  geholt     %-38s %6.1f kB" % (eintrag["datei"], len(daten) / 1024))
    return True


def main():
    schalter = set(sys.argv[1:])
    if schalter & {"-h", "--hilfe", "--help"}:
        print(__doc__.strip())
        return 0
    unbekannt = schalter - {"--alle"}
    if unbekannt:
        print("Unbekannt: %s\nBekannt sind --alle und --hilfe."
              % ", ".join(sorted(unbekannt)))
        return 2

    alle = "--alle" in schalter
    eintraege = DOKUMENTE + BEITRITTSFORMULARE

    print("Vereinsdokumente nach site/assets/dokumente/")
    print("%d Dateien%s\n" % (len(eintraege), ", alle neu" if alle else ""))

    gut = sum(1 for e in eintraege if hole(e, alle))

    print("\n%d von %d bereit." % (gut, len(eintraege)))
    if gut < len(eintraege):
        print("Die fehlenden bitte von Hand holen — die Adressen stehen bei")
        print("jedem Eintrag in vorlage/dokumente.py unter «herkunft».")
        return 1
    print("Jetzt «python3 build.py» — dann verweist die Downloadseite auf "
          "die eigenen Dateien.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
