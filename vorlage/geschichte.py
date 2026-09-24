# -*- coding: utf-8 -*-
"""
geschichte.py — Zeitleiste und Vereinsarchiv.

Einzige Quelle für die Seite «Geschichte». build.py erzeugt daraus die
Zeitleiste, die Archivkapitel und das Jahresraster der Meistertitel.

Warum eine Datendatei und nicht einfach HTML: zwanzig Archivstücke mit
Bildtext, Alternativtext und Nachweis wären rund zweihundert Zeilen
gleichförmiges Markup. Wer hier einen Bildtext ändert, ändert eine Zeile.
Wer ein Bild dazulegt, schreibt vier.

--------------------------------------------------------------------------
Die Archivstücke sind keine gewöhnlichen Fotos
--------------------------------------------------------------------------
Was im Vereinsarchiv liegt, sind Filmstreifen, Albumblätter und ein
Matchprogramm — also Gegenstände. Die Seite zeigt sie auch so, statt sie
auf ein einheitliches Kachelmass zu beschneiden. Ein Kontaktbogen *ist*
schon eine Galerie; ihn in Einzelbilder zu zerschneiden nähme ihm genau
das, was ihn sehenswert macht: die Sprossenlöcher, die Bildnummern,
«ILFORD HP5 PLUS» am Rand, die Handschrift auf dem Albumblatt.

Deshalb kennt `art` drei Formen:

    "streifen"   Filmstreifen und Kontaktbögen. Sehr breit (bis 4.8:1).
                 Auf schmalen Schirmen in einem eigenen Scrollfenster,
                 damit die einzelnen Bilder gross genug bleiben — man
                 zieht den Streifen vorbei wie über einem Leuchttisch.

    "blatt"      Albumblätter und Einzelaufnahmen. Laufen im Raster.

    "dokument"   Papier — Programm, Plakat, Urkunde. Bekommt eine eigene
                 Spalte neben seinem Text, weil ein Dokument gelesen
                 werden will und nicht nur angeschaut.

Je Stück:
    datei     Dateiname unter site/assets/img/archiv/
    alt       Alternativtext. Beschreibt, was zu sehen ist — für alle,
              die das Bild nicht sehen.
    text      Bildlegende unter dem Stück. Darf leer bleiben.
    nachweis  Wer das Bild gemacht hat, falls bekannt. Leer = Vereinsarchiv.
    klein     True, wenn die Vorlage zu klein für eine grosse Ansicht ist.
              Das Stück läuft dann nur im Raster mit und lässt sich nicht
              vergrössern — besser als ein unscharfes Vollbild.

--------------------------------------------------------------------------
Offen, und bewusst nicht erfunden
--------------------------------------------------------------------------
Die Bildtexte beschreiben, was auf den Aufnahmen zu sehen ist. Wo das
Jahr nicht aus dem Bild hervorgeht, steht keines da.

Vom Verein beantwortet (14. September):

  · **Die Rhyfallhalle wurde 1979 eröffnet.** Sie steht jetzt als eigener
    Eintrag in der Zeitleiste, das Kapitel hängt daran.
  · **`anstossen.jpg` zeigt die Jubiläumsfeier**, nicht die Gründung. Die
    Datei hiess «Gründung_TTC», weil sie auf der alten Website an dieser
    Stelle stand — **von der Gründung 1975 gibt es kein Bild**. Die
    Aufnahme steht deshalb jetzt beim Jubiläum 2025, wo sie hingehört,
    und die Zeitleiste sagt bei 1975 nichts, was sie nicht belegen kann.

Offen bleibt:

  · Die Ebnat-Blätter tragen zwei Hinweise, die sich nicht ganz decken:
    auf einem steht handschriftlich «Glissahalle, Nov./Dez. 01», auf
    einem anderen hängt ein Banner «25 Jahre TTC Neuhausen» (also 2000).
    Die Bildtexte nennen deshalb kein genaues Datum.
"""

# --- Zeitleiste -----------------------------------------------------------
# kapitel: verweist auf ein Archivkapitel weiter unten (dessen id), damit
# der Eintrag einen Sprung dorthin anbieten kann. Leer = kein Bildmaterial.
ZEITLEISTE = [
    {
        "jahr": "1975",
        "titel": "Gründung",
        "text": "Am 20. Juni gründen Josef Mandl, Hermann Brunner, Max Muigg und Willi "
                "Borovcnik am Rosentalgässchen 15 in Schaffhausen den Verein. Trainiert wird "
                "in der Turnhalle des Schulhauses Gemeindewiesen, an höchstens fünf Tischen, "
                "mit einem Budget von 15'000 Franken.",
        "kapitel": "",
    },
    {
        "jahr": "1979",
        "titel": "Die Rhyfallhalle wird eröffnet",
        "text": "Am 31. August beginnt der Spielbetrieb in der neuen Rhyfallhalle. Der TTC "
                "wird zum Verein mit der grössten Hallenbelegung – und die Halle für gut "
                "zwanzig Jahre seine Heimat.",
        "kapitel": "rhyfallhalle",
    },
    {
        "jahr": "1981",
        "titel": "Aufstieg in die Nationalliga C",
        "text": "Mit Martin Singer, Urs Muigg und Ueli Küng. Vier Jahre später folgt die "
                "Nationalliga B.",
        "kapitel": "",
    },
    {
        "jahr": "1996",
        "titel": "Erster Meistertitel der Herren",
        "text": "Am 25. Februar gewinnen Giovanni Gentile, Ivan Jecic, Thierry Miller und "
                "Martin Singer den Final gegen CTT Meyrin 6:4, vor 350 Zuschauern in "
                "Schaffhausen. Das Hinspiel endete 5:5. Weitere Titel folgen 1998 und 2000.",
        "kapitel": "titel",
    },
    {
        "jahr": "2001",
        "titel": "Bau des TTZ Ebnat",
        "text": "In rund zwölf Monaten entsteht aus einer leeren Industriehalle das "
                "Tischtenniszentrum: 1200 Stunden Freiwilligenarbeit, 80'000 Franken "
                "Investitionen und 26'000 Franken für Material.",
        "kapitel": "ebnat",
    },
    {
        "jahr": "2002",
        "titel": "Einzug ins Tischtenniszentrum",
        "text": "Im Frühling zieht der Verein ein: 440 Quadratmeter, anfangs acht Tische, "
                "65 Stufen bis zum Eingang.",
        "kapitel": "ebnat",
    },
    {
        "jahr": "2004",
        "titel": "Die Seniorengruppe",
        "text": "Urs Schärrer senior und Edmondo Valley gründen die Seniorengruppe. Heute "
                "spielen dort über fünfzig Aktive.",
        "kapitel": "",
    },
    {
        "jahr": "2005",
        "titel": "Erster Meistertitel der Damen",
        "text": "Am 16. April schlagen Sonja Führer, Monika Führer, Laura Schärrer und "
                "Andrea Stepankova im Final Young Stars Zürich 7:3 – als jüngstes Meisterteam "
                "der Geschichte, trainiert von Pavel Rehorek. Es ist der erste von vierzehn Titeln.",
        "kapitel": "",
    },
    {
        "jahr": "2011",
        "titel": "Der Titel nach Sätzen",
        "text": "Alle drei Finalspiele gegen Wädenswil enden 5:5. Entschieden wird nach "
                "Sätzen, 18:17 für Neuhausen – nach einem dritten Spiel von über zweieinhalb "
                "Stunden. Der sechste Titel der Damen.",
        "kapitel": "",
    },
    {
        "jahr": "2015",
        "titel": "Abstieg der Herren",
        "text": "Nach vierzehn Jahren in der höchsten Spielklasse geht es in die "
                "Nationalliga B.",
        "kapitel": "",
    },
    {
        "jahr": "2019",
        "titel": "Rückkehr und neuer Boden",
        "text": "Die Herren steigen wieder auf. Im TTZ Ebnat wird ein "
                "tischtennisspezifischer Taraflex-Belag verlegt.",
        "kapitel": "",
    },
    {
        "jahr": "2025",
        "titel": "50 Jahre TTCN",
        "text": "Das Jubiläumsjahr mit Feier, Chronik und Archivbildern.",
        "kapitel": "jubilaeum",
    },
    {
        "jahr": "2026",
        "titel": "Ja zum Hallensportzentrum",
        "text": "Stadt und Kanton Schaffhausen stimmen dem Ausbau des Hallensportzentrums "
                "im Schweizersbild zu, der Kanton mit 73,9 Prozent. Dort soll der Verein "
                "ein neues Zuhause finden.",
        "kapitel": "",
    },
]


# --- Archiv ---------------------------------------------------------------
# Die Kapitel stehen chronologisch: Rhyfallhalle 1979, erster Titel 1996,
# Ebnat 2001/02, Jubiläum 2025. Die Reihenfolge hier ist die Reihenfolge auf
# der Seite — und sie soll der Zeitleiste darüber folgen, sonst läuft man
# beim Sprung aus der Zeitleiste rückwärts durchs Archiv.
ARCHIV = [
    {
        "id": "rhyfallhalle",
        "titel": "In der Rhyfallhalle",
        "lead": "1979 eröffnet, und für die nächsten gut zwanzig Jahre die "
                "Heimat des Vereins. Zwei Kontaktbögen und eine Aufnahme von "
                "der Bühne sind davon übrig.",
        "stuecke": [
            {
                "art": "streifen",
                "datei": "streifen-rhyfallhalle-1.jpg",
                "alt": "Kontaktbogen mit zwölf Aufnahmen auf Ilford "
                       "HP5-Plus-Film: Spielerinnen und Spieler am Tisch, "
                       "zwei Personen im Gespräch, zuletzt mehrere Pokale "
                       "auf einem Tisch.",
                "text": "Ein ganzer Film auf einem Bogen — vom ersten "
                        "Ballwechsel bis zum Pokaltisch.",
                "nachweis": "",
                "klein": False,
            },
            {
                "art": "streifen",
                "datei": "streifen-rhyfallhalle-2.jpg",
                "alt": "Filmstreifen auf Kodak-Safety-Film: drei Aufnahmen "
                       "einer vollen Halle mit einer Vorführung auf dem "
                       "Hallenboden, Publikum auf der Galerie.",
                "text": "Die Halle voll, der Boden frei — eine Vorführung "
                        "vor vollen Rängen.",
                "nachweis": "",
                "klein": False,
            },
            {
                "art": "blatt",
                "datei": "rhyfallhalle-buehne.jpg",
                "alt": "Schwarzweissaufnahme: eine Kinderschar singt auf "
                       "einer Bühne, dahinter die Schweizer Fahne zwischen "
                       "zwei Wappenfahnen, davor sitzendes Publikum.",
                "text": "Auf der Bühne, zwischen Schweizer Fahne und "
                        "Schaffhauser Wappen.",
                "nachweis": "",
                "klein": False,
            },
            {
                "art": "blatt",
                "datei": "frauen-erfolg.jpg",
                "alt": "Vier Spielerinnen mit Medaillen um den Hals vor "
                       "einer Werbewand.",
                "text": "Vier Spielerinnen, vier Medaillen.",
                "nachweis": "",
                "klein": True,
            },
        ],
    },
    {
        "id": "titel",
        "titel": "Der erste Titel",
        "lead": "Am 25. Februar 1996 spielte der TTC Neuhausen in der "
                "Dreifachhalle Breite gegen CTT Meyrin um den Schweizer "
                "Meistertitel. Vom Tag sind drei Filmstreifen geblieben — "
                "und der Coupon, mit dem man gratis hineinkam.",
        "stuecke": [
            {
                "art": "dokument",
                "datei": "dokument-final-1996.jpg",
                "alt": "Matchprogramm: Tischtennis-NLA-Play-Off-Final, "
                       "TTC Neuhausen gegen CTT Meyrin, Sonntag, "
                       "25. Februar 1996, 13.45 Uhr, Dreifachhalle Breite, "
                       "Schaffhausen. Darüber ein Foto aus der vollen Halle, "
                       "unten ein Eintrittscoupon des Sponsors Cilag.",
                "text": "«Besuchen Sie dieses Spiel, denn Zuschauer gehören "
                        "zu unserem Team!» — der Eintrittscoupon zum "
                        "Play-Off-Final gegen Meyrin.",
                "nachweis": "",
                "klein": False,
            },
            {
                "art": "streifen",
                "datei": "streifen-meistertitel-3.jpg",
                "alt": "Filmstreifen mit vier Aufnahmen aus dem Spiel: "
                       "Spieler am Tisch vor vollen Rängen, ringsum "
                       "Bandenwerbung von Tibhar und Joola.",
                "text": "Volle Ränge rund um den Tisch.",
                "nachweis": "",
                "klein": False,
            },
            {
                "art": "streifen",
                "datei": "streifen-meistertitel-2.jpg",
                "alt": "Filmstreifen: ein Spieler beim Ballwechsel, dann "
                       "drei Spieler Arm in Arm, dann einer mit geballten "
                       "Fäusten.",
                "text": "Der Moment danach.",
                "nachweis": "",
                "klein": False,
            },
            {
                "art": "streifen",
                "datei": "streifen-meistertitel-1.jpg",
                "alt": "Filmstreifen mit sechs Aufnahmen: Spieler und "
                       "Betreuer feiern in der Halle, Umarmungen, ein Glas "
                       "in der Hand, im Hintergrund Werbetafeln.",
                "text": "Sechs Bilder vom Feiern, aufgenommen auf einem "
                        "einzigen Film.",
                "nachweis": "",
                "klein": False,
            },
        ],
    },
    {
        "id": "ebnat",
        "titel": "Die Halle, die der Verein selbst ausgebaut hat",
        "lead": "Aus einer leeren Industriehalle im Ebnat wurde in rund "
                "zwölf Monaten das Tischtenniszentrum — grösstenteils in "
                "Eigenleistung. Die Albumblätter zeigen den Weg dahin: "
                "leerer Boden, Zementpaletten, Leitern, und am Ende Tische, "
                "auf denen gespielt wird.",
        "stuecke": [
            {
                "art": "blatt",
                "datei": "ebnat-07.jpg",
                "alt": "Albumblatt mit vier Aufnahmen einer leeren "
                       "Industriehalle mit Leitern und Werkzeug. "
                       "Handschriftlich beschriftet mit «Glissahalle» und "
                       "«Nov./Dez. 01».",
                "text": "«Glissahalle, Nov./Dez. 01» — so stand sie da, "
                        "bevor es losging.",
                "nachweis": "",
                "klein": False,
            },
            {
                "art": "blatt",
                "datei": "ebnat-03.jpg",
                "alt": "Die leere Halle, der Boden erst zur Hälfte verlegt.",
                "text": "Der Boden, halb verlegt.",
                "nachweis": "",
                "klein": False,
            },
            {
                "art": "blatt",
                "datei": "ebnat-04.jpg",
                "alt": "Zwei Aufnahmen übereinander: der Fuss einer Stütze "
                       "im frisch vergossenen Boden, darunter Stahlrahmen, "
                       "die auf einer Plane bereitliegen.",
                "text": "Stützenfuss und Stahlrahmen.",
                "nachweis": "",
                "klein": False,
            },
            {
                "art": "blatt",
                "datei": "ebnat-02.jpg",
                "alt": "Ein Mann kniet auf dem Boden und zieht mit der "
                       "Kelle Masse ab.",
                "text": "Mit der Kelle, von Hand.",
                "nachweis": "",
                "klein": False,
            },
            {
                "art": "blatt",
                "datei": "ebnat-11.jpg",
                "alt": "Albumblatt mit vier Aufnahmen: mehrere Personen "
                       "tragen gemeinsam eine grosse Platte, Paletten mit "
                       "Zementsäcken, jemand kniet beim Verlegen, zwei "
                       "Helfer mit Werkzeug am Fenster.",
                "text": "Getragen, gemischt, verlegt — vier Bilder von "
                        "einem Samstag.",
                "nachweis": "",
                "klein": False,
            },
            {
                "art": "blatt",
                "datei": "ebnat-05.jpg",
                "alt": "Der Rohbau von innen: Ständerwände, eine "
                       "Werkstattecke, Farbeimer auf dem Boden.",
                "text": "Der Rohbau von innen.",
                "nachweis": "",
                "klein": False,
            },
            {
                "art": "blatt",
                "datei": "ebnat-06.jpg",
                "alt": "Ein rundes Waschbecken mit Mehrfachbrause und ein "
                       "Heizkörper an der Wand.",
                "text": "Auch das gehört dazu: die Nasszelle.",
                "nachweis": "",
                "klein": False,
            },
            {
                "art": "blatt",
                "datei": "ebnat-01.jpg",
                "alt": "Ein junger Mann steht lachend hinter einer frisch "
                       "montierten Theke in der noch unfertigen Halle.",
                "text": "Die Theke steht.",
                "nachweis": "",
                "klein": False,
            },
            {
                "art": "blatt",
                "datei": "ebnat-09.jpg",
                "alt": "Der fertige Aufenthaltsraum mit Tischen und "
                       "Stühlen, an der Wand ein Banner mit der Aufschrift "
                       "«25 Jahre TTC Neuhausen».",
                "text": "Der Aufenthaltsraum, fertig eingerichtet.",
                "nachweis": "",
                "klein": False,
            },
            {
                "art": "blatt",
                "datei": "ebnat-08.jpg",
                "alt": "Albumblatt mit vier Aufnahmen: jemand wischt den "
                       "fertigen Hallenboden, die Tische stehen bereits, "
                       "an den Banden das Vereinssignet.",
                "text": "Aufgestellt, gewischt, bespielbar.",
                "nachweis": "",
                "klein": False,
            },
            {
                "art": "blatt",
                "datei": "ebnat-10.jpg",
                "alt": "Albumblatt mit vier Aufnahmen: Mitglieder sitzen an "
                       "Tischen im neuen Aufenthaltsraum, daneben die Halle "
                       "mit Tischen und einem Töggelikasten.",
                "text": "Die ersten Abende im neuen Haus.",
                "nachweis": "",
                "klein": False,
            },
        ],
    },
    {
        "id": "jubilaeum",
        "titel": "Fünfzig Jahre",
        "lead": "Von der Gründung 1975 ist kein Bild überliefert. Vom "
                "Jubiläum fünfzig Jahre später schon.",
        "stuecke": [
            {
                "art": "blatt",
                "datei": "anstossen.jpg",
                "alt": "Farbaufnahme: fünf Personen stossen im Freien an "
                       "einem Stehtisch mit Gläsern an, auf dem Tisch ein "
                       "Zopf und Getränke.",
                "text": "Angestossen auf fünfzig Jahre.",
                "nachweis": "",
                "klein": False,
            },
        ],
    },
]


# --- Meistertitel ---------------------------------------------------------
# Als Jahresraster statt als Kommaliste: vierzehn gegen drei sieht man,
# sobald die Jahre nebeneinander stehen.
MEISTERTITEL = [
    {
        "wer": "Damen",
        "jahre": [2005, 2006, 2007, 2009, 2010, 2011, 2012,
                  2015, 2016, 2017, 2018, 2019, 2021, 2022],
        "text": "Seit 2005 das erfolgreichste Damenteam der Schweiz.",
    },
    {
        "wer": "Herren",
        "jahre": [1996, 1998, 2000],
        "text": "Drei Titel in fünf Jahren, dazu vierzehn Jahre "
                "Nationalliga A.",
    },
]


# --- Bildnachweis ---------------------------------------------------------
NACHWEIS = (
    "Die Archivbilder stammen aus dem Vereinsarchiv. Neuere Aufnahmen sind "
    "mit freundlicher Genehmigung von Pascal Oesch, dessen Chronik "
    "ausserdem die Grundlage dieser Zeitleiste bildet."
)
