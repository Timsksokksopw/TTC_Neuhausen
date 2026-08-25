# -*- coding: utf-8 -*-
"""
mannschaften.py — die Mannschaften des Vereins und ihre click-tt-Adressen.

Einzige Quelle für die Teams-Seite. build.py erzeugt daraus die Übersicht
mit Direktlinks auf die jeweilige Ligatabelle.

WARUM LINKS UND KEIN WIDGET
click-tt.ch läuft auf nuLiga von nu Datenautomaten. Es gibt dort weder ein
offizielles Widget noch eine öffentliche Schnittstelle — nachgeprüft bei
click-tt.ch, Swiss Table Tennis und in den einschlägigen Vereinsforen.

(Die frühere Notiz im README nannte ein «hb_api-Widget von sportred». Das
gehört zu handball.net und hat mit Tischtennis nichts zu tun. Die dort
genannte Club-ID 33244 stimmt hingegen.)

Was Vereine ersatzweise machen, ist ein iframe auf die nuLiga-Seite. Das
bringt fremdes Layout mitten in die eigene Seite, hat eine feste Höhe, ist
auf dem Handy mühsam, setzt Cookies eines Dritten — und ob nuLiga das
Einbetten überhaupt zulässt, ist nicht zugesichert und kann jederzeit
gesperrt werden. Deshalb hier der Weg, der immer funktioniert: eine
gestaltete Übersicht im Vereinsdesign, die auf die offizielle Tabelle
verweist. Die Daten dort sind immer aktuell, weil sie von dort kommen.

SAISONWECHSEL
Die Gruppennummern gelten je Saison. Zu Saisonbeginn:
1. https://www.click-tt.ch/cgi-bin/WebObjects/nuLigaTTCH.woa/wa/clubTeams?club=33244
2. Für jede Mannschaft den Link auf die Ligatabelle kopieren
3. `wettbewerb` und `gruppe_id` unten nachführen, SAISON anpassen
4. python3 build.py
"""

CLUB_ID = 33244
SAISON = "2026/27"

_BASIS = "https://www.click-tt.ch/cgi-bin/WebObjects/nuLigaTTCH.woa/wa/"

# Die drei Vereinsseiten auf click-tt, auf die wir verweisen.
VEREINSSEITEN = {
    "uebersicht": _BASIS + "clubInfoDisplay?club=%d" % CLUB_ID,
    "mannschaften": _BASIS + "clubTeams?club=%d" % CLUB_ID,
    "spielbetrieb": _BASIS + "clubMeetings?club=%d" % CLUB_ID,
}

# Reihenfolge bestimmt die Reihenfolge auf der Seite.
WETTBEWERBE = [
    ("stt",  "Nationalliga",              "Swiss Table Tennis League"),
    ("ottv", "OTTV-Mannschaftsmeisterschaft", "Ostschweizer Tischtennisverband"),
    ("cup",  "Cup",                       "Schweizer Cup und OTTV-Cup"),
]

# name         wie die Mannschaft im Verein heisst
# liga         Liga und Gruppe, ausgeschrieben
# wettbewerb   Schlüssel aus WETTBEWERBEN
# championship der championship-Parameter aus der click-tt-Adresse
# gruppe_id    der group-Parameter aus der click-tt-Adresse
MANNSCHAFTEN = [
    {"name": "STTL Men", "liga": "Swiss Table Tennis League Men",
     "wettbewerb": "stt", "championship": "STT 26/27", "gruppe_id": 219264},
    {"name": "STTL Women", "liga": "Swiss Table Tennis League Women",
     "wettbewerb": "stt", "championship": "STT 26/27", "gruppe_id": 219291},

    {"name": "Herren II", "liga": "2. Liga Herren, Gruppe 2",
     "wettbewerb": "ottv", "championship": "OTTV 26/27", "gruppe_id": 219465},
    {"name": "Herren III", "liga": "3. Liga Herren, Gruppe 2",
     "wettbewerb": "ottv", "championship": "OTTV 26/27", "gruppe_id": 219527},
    {"name": "Herren IV", "liga": "4. Liga Herren, Gruppe 3",
     "wettbewerb": "ottv", "championship": "OTTV 26/27", "gruppe_id": 219551},
    {"name": "Herren V", "liga": "5. Liga Herren, Gruppe 3",
     "wettbewerb": "ottv", "championship": "OTTV 26/27", "gruppe_id": 219566},
    {"name": "Herren VI", "liga": "6. Liga Herren, Gruppe 3",
     "wettbewerb": "ottv", "championship": "OTTV 26/27", "gruppe_id": 219590},
    {"name": "Veteranen O50", "liga": "1. Liga O50, Gruppe 1",
     "wettbewerb": "ottv", "championship": "OTTV 26/27", "gruppe_id": 219604},
    {"name": "Jugend", "liga": "Jugend 2. Liga, Gruppe 6",
     "wettbewerb": "ottv", "championship": "OTTV 26/27", "gruppe_id": 220426},
    {"name": "Jugend II", "liga": "Jugend 2. Liga, Gruppe 3",
     "wettbewerb": "ottv", "championship": "OTTV 26/27", "gruppe_id": 220424},

    {"name": "Schweizer Cup", "liga": "Herren, 3. Hauptrunde Zone 2",
     "wettbewerb": "cup", "championship": "Schweizer Cup 26/27", "gruppe_id": 219172},
    {"name": "OTTV-Cup", "liga": "Achtelfinal",
     "wettbewerb": "cup", "championship": "OTTV Cup 26/27", "gruppe_id": 219222},
]
