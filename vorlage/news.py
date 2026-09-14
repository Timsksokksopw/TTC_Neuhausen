# -*- coding: utf-8 -*-
"""
news.py — Beiträge aus dem Verein.

Einzige Quelle für die drei Karten auf der Startseite, die Liste auf
news.html und die Beitragsseiten selbst. Vorher stand jeder Beitrag
zweimal abgetippt im HTML — einmal als Karte, einmal als Listeneintrag —
und der eigentliche Text stand gar nicht auf dieser Website, sondern
lag auf der alten. Die Karten verwiesen dorthin.

--------------------------------------------------------------------------
Wie ein Beitrag zu einer Seite wird
--------------------------------------------------------------------------
Hat ein Beitrag Text (`absaetze` nicht leer), erzeugt build.py daraus die
Seite `news-<kennung>.html`, und Karte wie Listeneintrag verweisen darauf.

Hat er **keinen** Text, bleibt er als Meldung stehen: Datum, Titel und
Herkunftsangabe, aber ohne Verweis. Das ist Absicht. Eine Karte, die auf
eine leere Seite führt, ist schlechter als eine Karte, die nicht klickbar
ist — und ein Verweis zurück auf die alte Website ist keine Lösung,
sondern das Problem.

`build.py` zählt nach jedem Lauf, wie viele Beiträge noch ohne Text sind.

--------------------------------------------------------------------------
Je Eintrag
--------------------------------------------------------------------------
    kennung       Dateiname der Beitragsseite (Kleinbuchstaben, Bindestriche)
    datum         ISO, also JJJJ-MM-TT — daraus baut build.py die Anzeige
    titel         volle Überschrift, steht auf der Beitragsseite
    kurztitel     gekürzt für die Karte auf der Startseite; leer = titel
    text          wer den Beitrag geschrieben hat
    bildnachweis  wer die Bilder gemacht hat
    bild          Datei unter site/assets/img/fotos/
    bildalt       Alternativtext; leer, solange das Bild nur Stimmung ist
    absaetze      der Fliesstext, siehe unten

--------------------------------------------------------------------------
Der Fliesstext
--------------------------------------------------------------------------
`absaetze` ist eine Liste. Jeder Eintrag ist entweder

    "Ein gewöhnlicher Absatz."

oder eines von drei Sonderstücken:

    {"art": "titel", "text": "U13"}
    {"art": "zitat", "text": "Wir wussten früh, dass …", "wer": "Lyo Bührer"}
    {"art": "liste", "titel": "Rangliste U13", "punkte": ["ZZ-Lancy", …]}

Anführungszeichen im Fliesstext bitte als « » setzen, nicht als " " —
so steht es auf der übrigen Website auch.
"""

# --------------------------------------------------------------------------
# Hinweis zu den drei bestehenden Beiträgen
# --------------------------------------------------------------------------
# Titel, Datum, Herkunftsangabe und Bild stammen von der bisherigen
# Website und sind dort nachgeprüft. Der **Fliesstext fehlt noch** und
# steht deshalb leer: die Beiträge sind von Lyo Bührer geschrieben, und
# eine nacherzählte Fassung unter seinem Namen wäre keine Übernahme,
# sondern eine Fälschung. Den Text bitte aus dem alten Redaktionssystem
# hierher kopieren — dann bauen sich die drei Seiten von selbst.
BEITRAEGE = [
    {
        "kennung": "sttl-women-nach-dem-umbruch",
        "datum": "2026-07-09",
        "titel": "STTL Women: TTC Neuhausen stellt sich nach Umbruch neu auf",
        "kurztitel": "STTL Women: neu aufgestellt nach dem Umbruch",
        "text": "Lyo Bührer",
        "bildnachweis": "René Zwald",
        "bild": "news-1.jpg",
        "bildalt": "",
        "absaetze": [],
    },
    {
        "kennung": "finalrunde-nachwuchs",
        "datum": "2026-06-22",
        "titel": "Finalrunde Nachwuchs: Alle drei Sprachregionen holen Titel in Neuhausen",
        "kurztitel": "Finalrunde Nachwuchs: alle drei Sprachregionen holen Titel",
        "text": "Lyo Bührer",
        "bildnachweis": "Andrii Lukatskyi",
        "bild": "news-2.jpg",
        "bildalt": "",
        "absaetze": [],
    },
    {
        "kennung": "sttl-men-weichen-neu-gestellt",
        "datum": "2026-06-22",
        "titel": "STTL Men: TTC Neuhausen stellt Weichen nach schwierigem Jahr neu",
        "kurztitel": "STTL Men: Weichen nach schwierigem Jahr neu gestellt",
        "text": "Lyo Bührer",
        "bildnachweis": "Ranil Jayanetti",
        "bild": "news-3.jpg",
        "bildalt": "",
        "absaetze": [],
    },
]

# Wie viele Beiträge auf der Startseite stehen. Die Liste auf news.html
# zeigt alle.
AUF_STARTSEITE = 3
