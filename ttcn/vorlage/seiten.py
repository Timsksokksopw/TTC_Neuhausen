# -*- coding: utf-8 -*-
"""
seiten.py — Navigation und Seitenverzeichnis.

Einzige Quelle für Menü, Seitentitel und Meta-Beschreibungen.
Wer eine Seite hinzufügt, trägt sie hier ein und legt die passende
Datei unter inhalt/ ab. build.py erledigt den Rest.
"""

# --- Adresse der Website ---------------------------------------------------
# Gebraucht für canonical, die Teilen-Vorschau (og:url, og:image) und die
# Vereinsangaben für Google. Diese Angaben müssen absolut sein, relative
# Pfade funktionieren dort nicht.
#
# VOR DER AUFSCHALTUNG PRÜFEN: mit abschliessendem Schrägstrich, und genau
# die Variante eintragen, auf die der Server am Ende weiterleitet
# (mit oder ohne www, immer https).
SEITE_URL = "https://www.ttc-neuhausen.ch/"

# --- Navigation ------------------------------------------------------------
# Struktur laut Beschluss vom 10.08.2026: fünf Punkte plus Button.
NAVIGATION = [
    ("Verein", "verein.html", [
        ("Über den Verein",   "verein.html"),
        ("Vorstand",          "verein-vorstand.html"),
        ("Trainerteam",       "verein-trainerteam.html"),
        ("Jahresprogramm",    "verein-jahresprogramm.html"),
        ("Mitglied werden",   "verein-mitglied-werden.html"),
        ("Helfereinsatz",     "verein-helfereinsatz.html"),
        ("Downloads",         "verein-downloads.html"),
        ("Geschichte",        "verein-geschichte.html"),
    ]),
    ("Training", "training.html", [
        ("Trainingszeiten",             "training.html"),
        ("Nachwuchs",                   "training-nachwuchs.html"),
        ("Schnupperpass",               "training-schnupperpass.html"),
        ("Breitensport",                "training-breitensport.html"),
        ("Senioren & PingPongParkinson","training-senioren.html"),
        ("Einzeltraining",              "training-einzeltraining.html"),
        ("Stützpunkt",                  "training-stuetzpunkt.html"),
        ("Für Schulen",                 "training-schulen.html"),
    ]),
    ("Teams", "teams.html", []),
    ("Hallen", "hallen.html", [
        ("Übersicht",     "hallen.html"),
        ("TTZ Ebnat",     "hallen-ttz-ebnat.html"),
        ("Rhyfallhalle",  "hallen-rhyfallhalle.html"),
        ("Neue Halle",    "hallen-neue-halle.html"),
    ]),
    ("News", "news.html", []),
]

# --- Seitenverzeichnis -----------------------------------------------------
# datei: (Browsertitel, Meta-Beschreibung, Rubrik für die Menümarkierung)
SEITEN = {
    "index.html": (
        "TTC Neuhausen – Tischtennis für alle, seit 1975",
        "Tischtennisclub Neuhausen am Rheinfall: Nachwuchsförderung, Breitensport und "
        "Seniorentraining in der Rhyfallhalle und im TTZ Ebnat. Schnuppern jederzeit möglich.",
        None),

    "verein.html": (
        "Über den Verein – TTC Neuhausen",
        "Rund 150 Mitglieder, drei Trainer, 35 Trainingsstunden pro Woche. "
        "Der TTC Neuhausen bietet Tischtennis vom Anfänger bis zur Nationalliga.",
        "Verein"),
    "verein-vorstand.html": (
        "Vorstand – TTC Neuhausen",
        "Der Vorstand des TTC Neuhausen mit Zuständigkeiten und Kontaktadressen.",
        "Verein"),
    "verein-trainerteam.html": (
        "Trainerteam – TTC Neuhausen",
        "Cheftrainer, sportlicher Leiter und Trainerteam des TTC Neuhausen.",
        "Verein"),
    "verein-jahresprogramm.html": (
        "Jahresprogramm – TTC Neuhausen",
        "Termine, Anlässe und Turniere des TTC Neuhausen im Vereinsjahr.",
        "Verein"),
    "verein-mitglied-werden.html": (
        "Mitglied werden – TTC Neuhausen",
        "Mitgliederkategorien und Beiträge des TTC Neuhausen. Schnuppertraining ist "
        "kostenlos, Schläger können ausgeliehen werden.",
        "Verein"),
    "verein-helfereinsatz.html": (
        "Helfereinsatz – TTC Neuhausen",
        "Der Vereinsbetrieb lebt von Freiwilligen. Einsätze bei Anlässen, im Training "
        "und im Hintergrund.",
        "Verein"),
    "verein-downloads.html": (
        "Downloads – TTC Neuhausen",
        "Hallenreglement, Hallentarife und weitere Dokumente des TTC Neuhausen.",
        "Verein"),
    "verein-geschichte.html": (
        "Geschichte – TTC Neuhausen",
        "Seit 1975: 14 Jahre Nationalliga A, drei Meistertitel bei den Herren, "
        "14 bei den Damen, eine eigene Halle.",
        "Verein"),

    "training.html": (
        "Trainingszeiten – TTC Neuhausen",
        "Alle Trainingszeiten des TTC Neuhausen für Nachwuchs, Breitensport und "
        "Senioren, mit Halle und Trainer.",
        "Training"),
    "training-nachwuchs.html": (
        "Nachwuchstraining – TTC Neuhausen",
        "Geleitetes Nachwuchstraining ab 5 Jahren, Förderkader und OTTV-Stützpunkt.",
        "Training"),
    "training-schnupperpass.html": (
        "Schnupperpass – TTC Neuhausen",
        "Sechs Monate Tischtennis ohne Mitgliedschaft: der Schnupperpass für Kinder.",
        "Training"),
    "training-breitensport.html": (
        "Breitensport – TTC Neuhausen",
        "Erwachsenentraining mit einer geführten Stunde, danach freies Spiel.",
        "Training"),
    "training-senioren.html": (
        "Senioren und PingPongParkinson – TTC Neuhausen",
        "Vormittagstraining für Seniorinnen und Senioren, dazu das Angebot "
        "PingPongParkinson.",
        "Training"),
    "training-einzeltraining.html": (
        "Einzeltraining – TTC Neuhausen",
        "Individuelle Einzeltrainings mit den professionellen Trainern des TTCN.",
        "Training"),
    "training-stuetzpunkt.html": (
        "Stützpunkttraining – TTC Neuhausen",
        "Der TTC Neuhausen ist anerkannter Stützpunkt von Swiss Table Tennis.",
        "Training"),
    "training-schulen.html": (
        "Für Schulen – TTC Neuhausen",
        "Schulsport, SwissPing und School Trophy: Tischtennisangebote für Schulklassen "
        "in Neuhausen und Schaffhausen.",
        "Training"),

    "teams.html": (
        "Teams – TTC Neuhausen",
        "Herren und Damen in der Swiss Table Tennis League, dazu Regional- und "
        "Jugendmannschaften. Tabellen direkt aus click-tt.",
        "Teams"),

    "hallen.html": (
        "Hallen – TTC Neuhausen",
        "Zwei Hallen: die Rhyfallhalle Neuhausen und das clubeigene TTZ Ebnat. "
        "Dazu das Projekt für eine neue Halle.",
        "Hallen"),
    "hallen-ttz-ebnat.html": (
        "TTZ Ebnat – TTC Neuhausen",
        "400 m², zwölf Tische, rund um die Uhr geöffnet: das clubeigene "
        "Tischtenniszentrum Ebnat in Schaffhausen.",
        "Hallen"),
    "hallen-rhyfallhalle.html": (
        "Rhyfallhalle Neuhausen – TTC Neuhausen",
        "Die Rhyfallhalle in Neuhausen am Rheinfall: Trainingsort für Nachwuchs und "
        "Breitensport, Austragungsort grosser Turniere.",
        "Hallen"),
    "hallen-neue-halle.html": (
        "Neue Halle – TTC Neuhausen",
        "Projekt Futuro und der Ausbau der BBC-Arena Schaffhausen: der TTC Neuhausen "
        "sucht ein neues Trainings- und Spiellokal.",
        "Hallen"),

    "news.html": (
        "News – TTC Neuhausen",
        "Aktuelles aus dem TTC Neuhausen: Spielberichte, Clubnews und Anlässe.",
        "News"),

    "kontakt.html": (
        "Kontakt – TTC Neuhausen",
        "Kontaktadressen des TTC Neuhausen und Anfahrt zu beiden Hallen.",
        None),
    "partner.html": (
        "Für Partner – TTC Neuhausen",
        "Sponsoring, Firmenevents und Hallenmiete beim TTC Neuhausen. "
        "Unsere Partner und was sie ermöglichen.",
        None),
    "impressum.html": (
        "Impressum – TTC Neuhausen",
        "Impressum des Tischtennisclubs Neuhausen am Rheinfall.",
        None),
    "datenschutz.html": (
        "Datenschutzerklärung – TTC Neuhausen",
        "Datenschutzerklärung des Tischtennisclubs Neuhausen am Rheinfall.",
        None),
}
