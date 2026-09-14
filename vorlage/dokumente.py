# -*- coding: utf-8 -*-
"""
dokumente.py — Statuten, Reglemente, Tarife und Beitrittsformulare.

Einzige Quelle für die beiden Listen auf verein-downloads.html.

--------------------------------------------------------------------------
Warum die Dateien mitziehen müssen
--------------------------------------------------------------------------
Bis jetzt zeigten alle vierzehn Verweise auf die Dateien der bisherigen
Website. Das ging, solange beide Websites nebeneinander liefen — sobald
die alte abgeschaltet wird, sind es vierzehn tote Links, und zwar
ausgerechnet bei den Formularen, mit denen jemand Mitglied werden will.

Die Dateien gehören deshalb in diesen Ordner:

    site/assets/dokumente/

Geholt werden sie in einem Durchgang:

    Windows   hol-dokumente.bat doppelklicken
    sonst     python3 hol-dokumente.py

Beide arbeiten diese Liste ab. Die PowerShell-Fassung hinter der .bat
erzeugt `build.py` aus genau dieser Datei — abgetippt wären es zwei
Listen, die auseinanderlaufen können.

Wer lieber von Hand holt: `herkunft` sagt bei jedem Eintrag, wo die Datei
steht, und `datei`, wie sie nachher heissen muss.

--------------------------------------------------------------------------
Was passiert, solange eine Datei fehlt
--------------------------------------------------------------------------
Der Eintrag steht in der Liste, aber ohne Verweis und mit dem Vermerk
«folgt». Kein toter Link, kein Verweis zurück auf die alte Website.
`build.py` zählt nach jedem Lauf, welche Dateien noch fehlen, und nennt
zu jeder die Adresse, unter der sie zu finden ist.

Je Eintrag:
    name      wie er in der Liste steht
    info      eine Zeile, was drinsteht
    datei     Dateiname unter site/assets/dokumente/
    herkunft  wo die Datei auf der bisherigen Website liegt. Steht nur
              hier in der Quelldatei, kommt nie ins HTML — sie ist die
              Bezugsquelle, nicht das Ziel des Verweises.
"""

# Die Dateiendung entscheidet über das Kürzel auf der Kachel (PDF, XLSX,
# DOCX). build.py liest es aus dem Dateinamen, damit es nicht zweimal
# dasteht und auseinanderlaufen kann.

DOKUMENTE = [
    {"name": "Statuten",
     "info": "Vereinsstatuten, Ausgabe 2025/12",
     "datei": "statuten.pdf",
     "herkunft": "https://www.ttc-neuhausen.ch/wp-content/uploads/2026/01/"
                 "Statuten_Ausgabe_2025_12.pdf"},
    {"name": "Spesenreglement",
     "info": "Was der Verein vergütet und wie abgerechnet wird",
     "datei": "spesenreglement.pdf",
     "herkunft": "https://www.ttc-neuhausen.ch/_data/pdf/"
                 "ttcn_spesenreglement_2022-12.pdf"},
    {"name": "Spesenformular",
     "info": "Abrechnungsvorlage zum Ausfüllen",
     "datei": "spesenformular.xlsx",
     "herkunft": "https://www.ttc-neuhausen.ch/_data/pdf/ttcn_spesenformular.xlsx"},
    {"name": "Hallentarife",
     "info": "Miete des TTZ Ebnat für Privat-, Firmen- und Schulanlässe",
     "datei": "hallentarife-ttz-ebnat.pdf",
     "herkunft": "https://www.ttc-neuhausen.ch/wp-content/uploads/2024/05/"
                 "TTZ-Ebnat-_Hallentarife.pdf"},
    {"name": "Hallenreglement",
     "info": "Regeln für die Nutzung des TTZ Ebnat",
     "datei": "hallenreglement.pdf",
     "herkunft": "https://www.ttc-neuhausen.ch/wp-content/uploads/2026/04/"
                 "2603-TTCN-Hallenreglement.pdf"},
    {"name": "Helfereinsatzreglement",
     "info": "Wer wie viele Einsätze leistet, Stand Oktober 2025",
     "datei": "helfereinsatzreglement.docx",
     "herkunft": "https://www.ttc-neuhausen.ch/wp-content/uploads/2025/10/"
                 "Helfereinsatz_Reglement_Okt25.docx"},
    {"name": "Maturaarbeit",
     "info": "Die physikalische Beschreibung eines Tischtennisschlages, Elio Zarotti",
     "datei": "maturaarbeit-tischtennisschlag.pdf",
     "herkunft": "https://www.ttc-neuhausen.ch/wp-content/uploads/2025/03/"
                 "MA2024_DiephysikalischeBeschreibungeinesTischtennisschlages_"
                 "ElioZarotti.pdf"},
]

BEITRITTSFORMULARE = [
    {"name": "AktivPlus",
     "info": "Training, Spielbetrieb, Lizenz möglich",
     "datei": "beitritt-aktivplus.pdf",
     "herkunft": "https://www.ttc-neuhausen.ch/wp-content/uploads/2025/10/"
                 "Beitrittserklaerungen-AktivPlus.pdf"},
    {"name": "AktivPlus Nachwuchs",
     "info": "Volles Nachwuchsprogramm mit Trainerbetreuung",
     "datei": "beitritt-aktivplus-nachwuchs.pdf",
     "herkunft": "https://www.ttc-neuhausen.ch/wp-content/uploads/2025/10/"
                 "Beitrittserklaerungen-AktivPlus-Nachwuchs.pdf"},
    {"name": "AktivPlus Studenten und Lehrlinge",
     "info": "Gleiche Leistungen, reduzierter Beitrag",
     "datei": "beitritt-aktivplus-studenten.pdf",
     "herkunft": "https://www.ttc-neuhausen.ch/wp-content/uploads/2025/10/"
                 "Beitrittserklaerungen-AktivPlus-Studenten-und-Lehrling.pdf"},
    {"name": "AktivPlus Senioren",
     "info": "Geführtes Seniorentraining inklusive",
     "datei": "beitritt-aktivplus-senioren.pdf",
     "herkunft": "https://www.ttc-neuhausen.ch/wp-content/uploads/2025/10/"
                 "Beitrittserklaerungen-AktivPlus-Senioren.pdf"},
    {"name": "Aktiv",
     "info": "Spielberechtigung ohne geführtes Training",
     "datei": "beitritt-aktiv.pdf",
     "herkunft": "https://www.ttc-neuhausen.ch/wp-content/uploads/2025/10/"
                 "Beitrittserklaerungen-Aktiv.pdf"},
    {"name": "Damenverein",
     "info": "Mitgliedschaft ohne Spielbetrieb",
     "datei": "beitritt-damenverein.pdf",
     "herkunft": "https://www.ttc-neuhausen.ch/wp-content/uploads/2025/10/"
                 "Beitrittserklaerungen-Damenverein.pdf"},
    {"name": "Passive",
     "info": "Unterstützung ohne Spielbetrieb",
     "datei": "beitritt-passive.pdf",
     "herkunft": "https://www.ttc-neuhausen.ch/wp-content/uploads/2025/10/"
                 "Beitrittserklaerungen-Passive.pdf"},
]

# --------------------------------------------------------------------------
# Das Anmeldeformular
# --------------------------------------------------------------------------
# Auf der bisherigen Website ist ein Microsoft-Forms-Formular in die Seite
# «Mitglied werden» eingebettet. Der Knopf auf verein-mitglied-werden.html
# zeigte bis jetzt auf jene Seite — also auf die alte Website.
#
# Jetzt zeigt er direkt auf das Formular. Kein iframe: aus demselben
# Grund, aus dem die Ligatabellen nicht eingebettet sind — fremdes
# Layout, feste Höhe, Cookies Dritter. Das `&embed=true` der
# Einbettungsfassung ist dafür entfernt.
#
# ZU PRÜFEN: einmal anklicken und schauen, ob das richtige Formular
# aufgeht. Die Adresse stammt aus der Einbettung der bisherigen Seite.
ANMELDEFORMULAR = (
    "https://forms.cloud.microsoft/Pages/ResponsePage.aspx"
    "?id=6V37WvpsZEegkDvLYeU-pSaeXtPZeXVBn0ykXpGPbhlUMURBTU0zV1ZMMEZTS0tRMjlJOU9PT1FPSy4u"
)
