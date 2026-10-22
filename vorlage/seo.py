# -*- coding: utf-8 -*-
"""SEO – alles, was Suchmaschinen über den Verein wissen sollen.

Daraus erzeugt build.py:

    site/.htaccess    Weiterleitungen der alten Adressen, https und www,
                      Fehlerseite, Zwischenspeicher, Komprimierung
    Strukturdaten     der JSON-LD-Block im <head> jeder Seite: Verein,
                      Hallen mit Adresse und Koordinaten, Brotkrumen,
                      News-Beiträge als Artikel

Seitentitel und Beschreibungen stehen weiterhin in seiten.py.

--------------------------------------------------------------------------
Warum die Weiterleitungen das Wichtigste sind
--------------------------------------------------------------------------
Die bisherige Website (WordPress) hat rund 2900 Adressen bei Google: 89
Seiten, 2577 Beiträge seit 2008, 208 Anlässe, Kategorien und Schlagworte.
Auf diese Adressen verweisen Google, andere Vereine, Verbände, Zeitungen.
Gibt es sie nach der Umstellung nicht mehr, verliert die neue Website,
was die alte in Jahren aufgebaut hat. Eine 301-Weiterleitung nimmt das
Gewicht mit auf die neue Seite.

Stand der alten Adressen: wp-sitemap.xml von ttc-neuhausen.ch, 5. Oktober 2026.
"""

# --- Der Verein -------------------------------------------------------------

VEREIN = {
    "name": "Tischtennisclub Neuhausen",
    "kurzname": ["TTC Neuhausen", "TTCN"],
    "beschreibung": "Tischtennisclub in Neuhausen am Rheinfall und Schaffhausen, gegründet 1975. "
                    "Nachwuchs, Breitensport, Senioren und Teams in der Swiss Table Tennis League.",
    "gruendung": "1975",
    "email": "info@ttc-neuhausen.ch",
    # Wie im Impressum: ohne Strasse, der Verein hat keine eigene Postadresse.
    "plz": "8200",
    "ort": "Schaffhausen",
    "kanton": "SH",
    "einzugsgebiet": ["Neuhausen am Rheinfall", "Schaffhausen", "Kanton Schaffhausen"],
    "verband": ("Swiss Table Tennis", "https://www.swisstabletennis.ch/"),
    # Quadratisch, mindestens 112 × 112: so will Google das Logo.
    "logo": "assets/img/favicon-512.png",
    # Dazu kommt von selbst die Vereinsseite bei click-tt (mannschaften.py).
    "profile": [
        "https://www.instagram.com/ttcneuhausen/",
        "https://www.facebook.com/ttcnh/",
    ],
}

# Ergänzt HALLEN aus trainingszeiten.py (Name, Seite) um das, was Google für
# die Karte braucht. Koordinaten: OpenStreetMap, 5. Oktober 2026.
HALLENORTE = {
    "ebnat": {
        "name": "Tischtenniszentrum Ebnat",
        "auch": ["TTZ Ebnat"],
        "strasse": "Ebnatstrasse 35",
        "plz": "8200",
        "ort": "Schaffhausen",
        "geo": (47.70595, 8.64120),
    },
    "rhyfall": {
        "name": "Rhyfallhalle",
        # So steht sie bei OpenStreetMap, und so wird sie auch gesucht.
        "auch": ["Rheinfallhalle"],
        "strasse": "Rheingoldstrasse 11",
        "plz": "8212",
        "ort": "Neuhausen am Rheinfall",
        "geo": (47.68055, 8.62020),
    },
}


# --- Weiterleitungen --------------------------------------------------------
#
# Links die alte Adresse ohne Domain und ohne Schrägstrich am Ende, rechts
# die neue Seite. Ein Schrägstrich am Ende der alten Adresse wird von selbst
# mit abgedeckt. Ziele mit #sprungmarke sind erlaubt.

WEITERLEITUNGEN = {
    # Verein
    "ueber-den-verein":     "verein.html",
    "mission":              "verein.html",
    "vorstand":             "verein-vorstand.html",
    "trainerteam":          "verein-trainerteam.html",
    "mitglied-werden":      "verein-mitglied-werden.html",
    "helfereinsatz":        "verein-helfereinsatz.html",
    "downloads":            "verein-downloads.html",
    "schutzkonzept-ttcn":   "verein-downloads.html",
    "events":               "verein-jahresprogramm.html",
    "calendar":             "verein-jahresprogramm.html",
    "50-jahre-ttcn":        "verein-geschichte.html",
    "meilensteine-2":       "verein-geschichte.html",
    "archivbilder":         "verein-geschichte.html#archiv",

    # Training
    "trainingszeiten":         "training.html",
    "schnupperpass":           "training-schnupperpass.html",
    "nachwuchstraining":       "training-nachwuchs.html",
    "ig-talentfoerderung":     "training-nachwuchs.html",
    "breitensporttraining":    "training-breitensport.html",
    "seniorentraining":        "training-senioren.html",
    "einzeltraining":          "training-einzeltraining.html",
    "stuetzpunkttraining":     "training-stuetzpunkt.html",
    "schulsport":              "training-schulen.html",
    "swissping":               "training-schulen.html#swissping",
    "school-trophy":           "training-schulen.html#school-trophy",
    "school-trophy-anmeldung": "training-schulen.html#school-trophy",

    # Teams – früher eine Seite je Mannschaft
    "teams":                     "teams.html",
    "mannschaften":              "teams.html",
    "swiss-table-tennis-league": "teams.html",
    "swiss-table-tennis":        "teams.html",
    "sttl-men":                  "teams.html",
    "sttl-women":                "teams.html",
    "nationalliga-a-damen":      "teams.html",
    "nationalliga-a-herren":     "teams.html",
    "nationalliga-c":            "teams.html",
    "1-liga":                    "teams.html",
    "1-liga-2":                  "teams.html",
    "1-liga-gruppe-1a":          "teams.html",
    "1-liga-gruppe-1b":          "teams.html",
    "2-liga":                    "teams.html",
    "2-liga-gruppe-2a":          "teams.html",
    "2-liga-gruppe-2b":          "teams.html",
    "3-liga":                    "teams.html",
    "6-liga-herren-6":           "teams.html",
    "senioren-o40":              "teams.html",
    "nachwuchs-1-liga":          "teams.html",
    "nachwuchs-2-liga":          "teams.html",
    "u13":                       "teams.html",
    "u15":                       "teams.html",
    "u18":                       "teams.html",
    "sportliches-palmares-mauro-schaerrer-geb-23-juli-2003": "teams.html",

    # Hallen
    "ttz-ebnat":               "hallen-ttz-ebnat.html",
    "ttz-ebnat-belegungsplan": "hallen-ttz-ebnat.html",
    "hallensportzentrum":      "hallen-neue-halle.html",
    "projekt-futuro":          "hallen-neue-halle.html",

    # News und Turniere
    "news":                 "news.html",
    "clubnews":             "news.html",
    "blog":                 "news.html",
    "superfinal2022":       "news.html",
    "top-16-montreux-2022": "news.html",
    "sm-nachwuchs":         "news.html",
    "sm-senioren":          "news.html",

    # Partner
    "sponsoren":                "partner.html",
    "marketing":                "partner.html",
    "angebote":                 "partner.html",
    "logos":                    "partner.html",
    "gutscheine-von-sponsoren": "partner.html",

    # Übriges
    "kontakt":            "kontakt.html",
    "aussichtsturm-quiz": "",
}

# Ganze Adressbereiche (regulärer Ausdruck, ohne führenden Schrägstrich).
# Reihenfolge zählt: der erste Treffer gewinnt.
MUSTER = [
    (r"^(19|20)\d\d/",            "news.html"),                  # Beiträge und Datumsarchive
    (r"^(category|tag|author)/",  "news.html"),
    (r"^page/\d+/?$",             "news.html"),
    (r"^event/",                  "verein-jahresprogramm.html"),
    (r"^calendar/",               "verein-jahresprogramm.html"),
    (r"^pdfviewer/",              "verein-downloads.html"),      # GV-Unterlagen
    (r"^wp-sitemap.*\.xml$",      "sitemap.xml"),
]

# Wer das alte News-Archiv weiter betreibt (etwa unter archiv.ttc-neuhausen.ch),
# trägt die Adresse hier ein, mit Schrägstrich am Ende. Dann führt jeder alte
# Beitrag 1:1 auf seine Kopie im Archiv statt auf news.html – so bleiben die
# 2577 Beiträge bei Google. None = alle auf news.html.
NEWS_ARCHIV = None

# Vorlagenseiten des alten WordPress-Themes («Sample Page», «Portfolio»,
# «Pricing Tables» …). Nie Vereinsinhalt – sie melden «410 Gone», damit
# Google sie schnell vergisst, statt sie auf die Startseite umzuleiten.
WEG = [
    "sample-page", "sample-page-2", "home-2", "home-3", "home-4",
    "order-tracking", "about-us", "services", "full-width", "shortcodes",
    "pricing-tables", "portfolio", "portfolio-with-content",
    "portoflio-with-slider", "scenery-portfolio", "architecture-portfolio",
    "2-columns", "3-columns", "4-columns",
    "covid-19-massnahmen-fuer-nationalliga",
]
WEG_MUSTER = [
    r"^(portfolio|testimonial|filters|kwlogos-carousel)/",
    r"^(wp-admin|wp-includes|wp-json)(/|$)",
    r"^(wp-login|xmlrpc|wp-cron|wp-signup)\.php$",
    r"(^|/)(comments/)?feed/?$",
]
