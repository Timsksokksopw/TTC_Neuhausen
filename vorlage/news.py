# -*- coding: utf-8 -*-
"""News – Startseite, news.html und die Beitragsseiten.

Je Eintrag:
    kennung       Dateiname der Beitragsseite: news-<kennung>.html
    datum         JJJJ-MM-TT
    titel         volle Überschrift
    kurztitel     kürzer für Startseite und Karten (leer = titel)
    anriss        ein Satz für Listen (optional)
    text          Autorin/Autor (optional)
    bildnachweis  Fotografin/Fotograf (optional)
    bild          Datei unter site/assets/img/fotos/ (optional)
    bildalt       Alternativtext (leer, wenn das Bild nur Stimmung ist)
    absaetze      Fliesstext. Leer = Meldung ohne eigene Seite.

Ein Absatz ist ein Text oder eines von:
    {"art": "titel", "text": "U13"}
    {"art": "zitat", "text": "…", "wer": "Lyo Bührer"}
    {"art": "liste", "titel": "Rangliste U13", "punkte": ["…", "…"]}

Die Beiträge von Lyo Bührer stehen ohne Fliesstext, bis der Originaltext
aus dem alten System hierher kopiert ist. Die Anrisse der Meldungen fassen
nur Fakten zusammen (Stand 23.9.2026, von ttc-neuhausen.ch).
"""

BEITRAEGE = [
    {
        "kennung": "sttl-saisonvorschau-2026",
        "datum": "2026-09-21",
        "titel": "Titelrennen, Playoffkampf und Abstiegssorgen: So schätzt Lyo Bührer die STTL ein",
        "kurztitel": "So schätzt Lyo Bührer die neue STTL-Saison ein",
        "anriss": "Der Sportliche Leiter über Favoriten, Playoff-Rennen und Abstiegskampf.",
        "text": "Lyo Bührer",
        "absaetze": [],
    },
    {
        "kennung": "altpapier-september-2026",
        "datum": "2026-08-24",
        "titel": "Altpapiersammlung 5. September",
        "anriss": "Treffpunkt um 7 Uhr beim TTZ Ebnat. Gesucht sind 18 Helferinnen und Helfer.",
        "absaetze": [],
    },
    {
        "kennung": "sttl-women-nach-dem-umbruch",
        "datum": "2026-07-09",
        "titel": "STTL Women: TTC Neuhausen stellt sich nach Umbruch neu auf",
        "kurztitel": "STTL Women: neu aufgestellt nach dem Umbruch",
        "text": "Lyo Bührer",
        "bildnachweis": "René Zwald",
        "bild": "news-1.jpg",
        "bildalt": "Eine Spielerin im blauen Trikot ballt nach einem Punkt die Faust.",
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
        "bildalt": "Ein Spieler streckt sich am Tisch nach dem Ball.",
        "absaetze": [],
    },
    {
        "kennung": "abstimmung-hallensportzentrum",
        "datum": "2026-06-15",
        "titel": "Schaffhausen sagt JA – Ein Sieg für den Hallensport",
        "anriss": "Alle 26 Gemeinden stimmen dem Ausbau des Hallensportzentrums zu, der Kanton mit 73,9 Prozent.",
        "text": "Lyo Bührer",
        "absaetze": [],
    },
    {
        "kennung": "bronze-o40",
        "datum": "2026-05-19",
        "titel": "Joachim Klappenecker holt Bronze im O40-Einzel",
        "anriss": "Medaille an den Schweizer Meisterschaften der Seniorinnen und Senioren in Genf.",
        "absaetze": [],
    },
    {
        "kennung": "standaktionen-hallensportzentrum",
        "datum": "2026-05-18",
        "titel": "Standaktionen für Abstimmung Hallensportzentrum Schaffhausen gestartet",
        "anriss": "Zehn Stände in der ganzen Region – mit einem kleinen Tisch zum Mitspielen.",
        "absaetze": [],
    },
    {
        "kennung": "partnerschaft-tt-store",
        "datum": "2026-05-11",
        "titel": "TTC Neuhausen geht Partnerschaft mit TT-Store.ch ein",
        "anriss": "Ab der Saison 2026/27 rüstet TT-Store.ch den ganzen Verein aus, vom Nachwuchs bis zur STTL.",
        "absaetze": [],
    },
    {
        "kennung": "altpapier-mai-2026",
        "datum": "2026-05-11",
        "titel": "Altpapiersammlung vom 9. Mai 2026",
        "anriss": "15 Helferinnen und Helfer, fünf Fahrzeuge, Sonnenschein.",
        "absaetze": [],
    },
]

# Wie viele Meldungen auf der Startseite neben dem grossen Beitrag stehen.
AUF_STARTSEITE = 4
