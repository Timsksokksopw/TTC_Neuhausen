# -*- coding: utf-8 -*-
"""
trainingszeiten.py — alle Trainingseinheiten der Woche.

Einzige Quelle für den Wochenplan. build.py erzeugt daraus sowohl das
Wochenraster als auch die Tabelle darunter — eine Zeitänderung wird also
an genau einer Stelle gemacht und erscheint an beiden.

Vorher standen dieselben Angaben in drei getrennten Tabellen direkt im
HTML. Wer eine Zeit änderte, musste daran denken, dass die Einheit
womöglich noch in einer zweiten Tabelle steht.

Format je Einheit:
    tag       Mo Di Mi Do Fr Sa So
    von, bis  "HH:MM", Viertelstundenschritte, innerhalb der RASTER_BAENDER
    halle     Schlüssel aus HALLEN
    angebot   Schlüssel aus ANGEBOTE — steuert auch die Filterknöpfe
    gruppe    kurz; steht im Raster auf dem Block
    trainer   ausgeschrieben; steht in der Tabelle unter dem Raster
"""

# Die Zeitachse des Rasters, in Bändern.
#
# Zwischen 10:30 und 15:00 findet kein Training statt. Über die volle
# Spanne gerechnet verbraucht dieser leere Mittag einen guten Drittel der
# Breite — und die fehlt genau dort, wo abends mehrere Angebote
# nebeneinanderliegen und die Blöcke ihren Namen tragen sollen. Die Achse
# überspringt die Lücke deshalb; im Raster ist der Sprung als Bruch
# markiert, damit niemand die Breite für Zeit hält.
#
# Zwischen dem Mittwochnachmittag (bis 16:30) und dem Abendbetrieb (ab
# 17:15) liegen nur 45 Minuten — dafür lohnt kein zweiter Bruch.
#
# Wer eine Einheit ausserhalb dieser Bänder einträgt, bekommt beim Bauen
# einen Abbruch mit Hinweis — dann gehört das Band erweitert.
RASTER_BAENDER = [
    ("08:30", "11:00"),   # Vormittag: Seniorentraining
    ("14:30", "22:00"),   # Nachmittag und Abend
]

TAGE = [
    ("Mo", "Montag"),
    ("Di", "Dienstag"),
    ("Mi", "Mittwoch"),
    ("Do", "Donnerstag"),
    ("Fr", "Freitag"),
    ("Sa", "Samstag"),
    ("So", "Sonntag"),
]

HALLEN = {
    "ebnat":   {"name": "TTZ Ebnat",    "kurz": "Ebnat",   "seite": "hallen-ttz-ebnat.html"},
    "rhyfall": {"name": "Rhyfallhalle", "kurz": "Rhyfall", "seite": "hallen-rhyfallhalle.html"},
}

# Reihenfolge bestimmt die Reihenfolge der Filterknöpfe.
ANGEBOTE = {
    "nachwuchs": {
        "name": "Nachwuchs",
        "seite": "training-nachwuchs.html",
        "notiz": 'Anmeldung beim Trainerteam: '
                 '<a href="mailto:trainer@ttc-neuhausen.ch">trainer@ttc-neuhausen.ch</a>',
    },
    "breitensport": {
        "name": "Breitensport",
        "seite": "training-breitensport.html",
        "notiz": "Jeweils eine Stunde geführt, danach freies Spiel.",
    },
    "senioren": {
        "name": "Senioren",
        "seite": "training-senioren.html",
        "notiz": 'Auskunft bei Urs Schärrer sen., '
                 '<a href="tel:+41526245265">052 624 52 65</a> oder '
                 '<a href="mailto:seniorentraining@ttc-neuhausen.ch">'
                 'seniorentraining@ttc-neuhausen.ch</a>',
    },
}

# Stand: 25. August 2026, übernommen von
# https://www.ttc-neuhausen.ch/trainingszeiten/
EINHEITEN = [
    # --- Montag ---------------------------------------------------------
    {"tag": "Mo", "von": "09:00", "bis": "10:30", "halle": "ebnat",
     "angebot": "senioren", "gruppe": "Freies Spielen", "trainer": ""},
    {"tag": "Mo", "von": "18:00", "bis": "20:00", "halle": "ebnat",
     "angebot": "nachwuchs", "gruppe": "Förderkader", "trainer": "Pekka Pelz"},

    # --- Dienstag -------------------------------------------------------
    {"tag": "Di", "von": "09:00", "bis": "10:30", "halle": "ebnat",
     "angebot": "senioren", "gruppe": "Geleitetes Training", "trainer": "Pekka Pelz"},
    {"tag": "Di", "von": "17:15", "bis": "18:30", "halle": "rhyfall",
     "angebot": "nachwuchs", "gruppe": "Schnuppertraining / Anfänger",
     "kurz": "Schnuppern / Anfänger", "trainer": "Pekka Pelz"},
    {"tag": "Di", "von": "18:30", "bis": "20:30", "halle": "rhyfall",
     "angebot": "nachwuchs", "gruppe": "Nachwuchs", "trainer": "Pekka Pelz"},
    {"tag": "Di", "von": "20:00", "bis": "21:45", "halle": "rhyfall",
     "angebot": "breitensport", "gruppe": "Erwachsene / Breitensport", "trainer": "Pekka Pelz"},

    # --- Mittwoch -------------------------------------------------------
    {"tag": "Mi", "von": "15:00", "bis": "16:30", "halle": "ebnat",
     "angebot": "nachwuchs", "gruppe": "Schnuppertraining / Anfänger",
     "kurz": "Schnuppern / Anfänger", "trainer": "Pekka Pelz"},
    {"tag": "Mi", "von": "18:00", "bis": "20:30", "halle": "ebnat",
     "angebot": "nachwuchs", "gruppe": "OTTV Stützpunkt", "trainer": "Pekka Pelz, Lyo Bührer"},

    # --- Donnerstag -----------------------------------------------------
    {"tag": "Do", "von": "09:00", "bis": "10:30", "halle": "ebnat",
     "angebot": "senioren", "gruppe": "Schnuppertraining / Geleitet / PingPongParkinson",
     # Weiches Trennzeichen (U+00AD) in der Mitte: der Block im Raster ist
     # rund 120 px breit, das Wort am Stück passt nicht. So bricht es als
     # «PingPong-Parkinson» statt mitten im Wort gekappt zu werden.
     "kurz": "PingPong\u00adParkinson", "trainer": "Johann Schuler"},
    {"tag": "Do", "von": "18:30", "bis": "20:30", "halle": "ebnat",
     "angebot": "nachwuchs", "gruppe": "Nachwuchs", "trainer": "Pekka Pelz"},
    {"tag": "Do", "von": "20:00", "bis": "21:45", "halle": "ebnat",
     "angebot": "breitensport", "gruppe": "Erwachsene / Breitensport", "trainer": "Pekka Pelz"},

    # --- Freitag --------------------------------------------------------
    {"tag": "Fr", "von": "09:00", "bis": "10:30", "halle": "ebnat",
     "angebot": "senioren", "gruppe": "Geleitetes Training", "trainer": "Pekka Pelz"},
    {"tag": "Fr", "von": "18:00", "bis": "20:30", "halle": "rhyfall",
     "angebot": "nachwuchs", "gruppe": "OTTV Stützpunkt", "trainer": "Pekka Pelz, Lyo Bührer"},
    {"tag": "Fr", "von": "20:00", "bis": "21:45", "halle": "rhyfall",
     "angebot": "breitensport", "gruppe": "Erwachsene / Breitensport", "trainer": "Pekka Pelz"},

    # Samstag und Sonntag: kein angesetztes Training.
]
