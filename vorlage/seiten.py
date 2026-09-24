# -*- coding: utf-8 -*-
"""Menü, Seitentitel und Beschreibungen. Neue Seite: hier eintragen und
inhalt/<datei>.html anlegen."""

# Adresse der Website, mit Schrägstrich am Ende (für canonical und Teilen-Vorschau).
SEITE_URL = "https://www.ttc-neuhausen.ch/"

NAVIGATION = [
    ("Verein", "verein.html", [
        ("Über den Verein",   "verein.html"),
        ("Vorstand",          "verein-vorstand.html"),
        ("Trainerteam",       "verein-trainerteam.html"),
        ("Geschichte",        "verein-geschichte.html"),
        ("Jahresprogramm",    "verein-jahresprogramm.html"),
        ("Mitglied werden",   "verein-mitglied-werden.html"),
        ("Helfereinsatz",     "verein-helfereinsatz.html"),
        ("Downloads",         "verein-downloads.html"),
    ]),
    ("Training", "training.html", [
        ("Trainingszeiten",              "training.html"),
        ("Schnuppern & Schnupperpass",   "training-schnupperpass.html"),
        ("Nachwuchs",                    "training-nachwuchs.html"),
        ("Breitensport",                 "training-breitensport.html"),
        ("Senioren & PingPongParkinson", "training-senioren.html"),
        ("Einzeltraining",               "training-einzeltraining.html"),
        ("Stützpunkt",                   "training-stuetzpunkt.html"),
        ("Für Schulen",                  "training-schulen.html"),
    ]),
    ("Teams", "teams.html", []),
    ("Hallen", "hallen.html", [
        ("Übersicht",                "hallen.html"),
        ("TTZ Ebnat",                "hallen-ttz-ebnat.html"),
        ("Rhyfallhalle",             "hallen-rhyfallhalle.html"),
        ("Hallensportzentrum",       "hallen-neue-halle.html"),
    ]),
    ("News", "news.html", []),
]

# datei: (Browsertitel, Beschreibung, Rubrik im Menü)
SEITEN = {
    "index.html": (
        "TTC Neuhausen – Tischtennis von 7 bis 85, seit 1975",
        "Tischtennisclub Neuhausen: Nachwuchs, Breitensport, Senioren und Nationalliga. "
        "Training in der Rhyfallhalle und im TTZ Ebnat. Schnuppern jederzeit.",
        None),

    "verein.html": (
        "Über den Verein – TTC Neuhausen",
        "Rund 150 Mitglieder, zwei Hallen, Teams von der 6. Liga bis zur Swiss Table Tennis "
        "League: der Tischtennisclub Neuhausen im Überblick.",
        "Verein"),
    "verein-vorstand.html": (
        "Vorstand – TTC Neuhausen",
        "Wer den Tischtennisclub Neuhausen führt: Vorstand, erweiterter Vorstand und offene Ämter.",
        "Verein"),
    "verein-trainerteam.html": (
        "Trainerteam – TTC Neuhausen",
        "Cheftrainer Pekka Pelz, der Sportliche Leiter Lyo Bührer und das Trainerteam des TTC Neuhausen.",
        "Verein"),
    "verein-geschichte.html": (
        "Geschichte – TTC Neuhausen",
        "Seit 1975: Gründung in Schaffhausen, drei Meistertitel der Herren, vierzehn der Damen "
        "und eine Halle in Eigenleistung. Mit Bildern aus dem Vereinsarchiv.",
        "Verein"),
    "verein-jahresprogramm.html": (
        "Jahresprogramm – TTC Neuhausen",
        "Termine und das Vereinsjahr des TTC Neuhausen: Saison, Generalversammlung, "
        "Altpapiersammlung, School Trophy.",
        "Verein"),
    "verein-mitglied-werden.html": (
        "Mitglied werden – TTC Neuhausen",
        "Mitgliederkategorien, Beiträge und Anmeldung beim TTC Neuhausen. "
        "Mit Beitragsrechner. Zuerst schnuppern ist kostenlos.",
        "Verein"),
    "verein-helfereinsatz.html": (
        "Helfereinsatz – TTC Neuhausen",
        "Altpapiersammlung, Anlässe, Standaktionen: wo der Verein Hilfe braucht und wie man sich einträgt.",
        "Verein"),
    "verein-downloads.html": (
        "Downloads – TTC Neuhausen",
        "Statuten, Reglemente, Hallentarife und Beitrittsformulare des TTC Neuhausen.",
        "Verein"),

    "training.html": (
        "Trainingszeiten – TTC Neuhausen",
        "Der Wochenplan des TTC Neuhausen: Nachwuchs, Breitensport und Senioren "
        "in der Rhyfallhalle und im TTZ Ebnat.",
        "Training"),
    "training-schnupperpass.html": (
        "Schnuppern und Schnupperpass – TTC Neuhausen",
        "Das erste Training ist kostenlos. Danach sechs Monate mittrainieren ohne Mitgliedschaft: "
        "Schnupperpass für Nachwuchs, Breitensport und Senioren.",
        "Training"),
    "training-nachwuchs.html": (
        "Nachwuchstraining – TTC Neuhausen",
        "Geleitetes Training ab fünf Jahren, Förderkader, OTTV-Stützpunkt und SwissPing "
        "beim TTC Neuhausen.",
        "Training"),
    "training-breitensport.html": (
        "Breitensport – TTC Neuhausen",
        "Tischtennis für Erwachsene: dreimal pro Woche, erst frei einspielen, dann eine "
        "Stunde mit Trainer. Einsteigen jederzeit.",
        "Training"),
    "training-senioren.html": (
        "Senioren und PingPongParkinson – TTC Neuhausen",
        "Vormittagstraining im TTZ Ebnat für über fünfzig Seniorinnen und Senioren, "
        "dazu PingPongParkinson am Donnerstag.",
        "Training"),
    "training-einzeltraining.html": (
        "Einzeltraining – TTC Neuhausen",
        "Einzelstunden mit den Trainern des TTC Neuhausen: Preise, Abos und wie man bucht.",
        "Training"),
    "training-stuetzpunkt.html": (
        "Stützpunkttraining – TTC Neuhausen",
        "Der TTC Neuhausen ist anerkannter Stützpunkt des Ostschweizer Tischtennisverbands (OTTV).",
        "Training"),
    "training-schulen.html": (
        "Für Schulen – TTC Neuhausen",
        "Schulsport für die 1. bis 3. Klasse, SwissPing und die regionale School Trophy: "
        "Tischtennis für Schulen in Schaffhausen und Neuhausen.",
        "Training"),

    "teams.html": (
        "Teams – TTC Neuhausen",
        "Herren und Damen in der Swiss Table Tennis League, dazu die OTTV-Mannschaften. "
        "Tabellen und Resultate direkt bei click-tt.",
        "Teams"),

    "hallen.html": (
        "Hallen – TTC Neuhausen",
        "Die Rhyfallhalle in Neuhausen und das Tischtenniszentrum Ebnat in Schaffhausen.",
        "Hallen"),
    "hallen-ttz-ebnat.html": (
        "TTZ Ebnat – TTC Neuhausen",
        "Das Tischtenniszentrum Ebnat: in Eigenleistung ausgebaut, zwölf Tische, "
        "für Mitglieder rund um die Uhr offen.",
        "Hallen"),
    "hallen-rhyfallhalle.html": (
        "Rhyfallhalle Neuhausen – TTC Neuhausen",
        "Die Rhyfallhalle in Neuhausen am Rheinfall: seit 1979 Trainingsort und Bühne "
        "für grosse Turniere.",
        "Hallen"),
    "hallen-neue-halle.html": (
        "Hallensportzentrum Schaffhausen – TTC Neuhausen",
        "Stadt und Kanton sagen Ja zum Ausbau des Hallensportzentrums im Schweizersbild. "
        "Was das für den TTC Neuhausen bedeutet.",
        "Hallen"),

    "news.html": (
        "News – TTC Neuhausen",
        "Spielberichte, Resultate und Meldungen aus dem TTC Neuhausen.",
        "News"),

    "kontakt.html": (
        "Kontakt – TTC Neuhausen",
        "Wer beim TTC Neuhausen wofür zuständig ist, und wo die beiden Hallen stehen.",
        None),
    "partner.html": (
        "Für Partner – TTC Neuhausen",
        "Sponsoring, Firmenanlässe im TTZ Ebnat und die Partner des TTC Neuhausen.",
        None),
    "impressum.html": (
        "Impressum – TTC Neuhausen",
        "Impressum des Tischtennisclubs Neuhausen.",
        None),
    "datenschutz.html": (
        "Datenschutz – TTC Neuhausen",
        "Datenschutzerklärung des Tischtennisclubs Neuhausen.",
        None),
}
