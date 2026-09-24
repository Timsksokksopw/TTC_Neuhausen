# -*- coding: utf-8 -*-
"""
sponsoren.py — Partner und Ausrüster des Vereins.

Einzige Quelle für die Sponsorenkacheln. build.py erzeugt daraus den
Abschnitt auf der Startseite und den auf partner.html — vorher stand die
Liste zweimal abgetippt im HTML, und die Zahl «21 Unternehmen» daneben
noch ein drittes Mal von Hand.

Die Zahl im Text rechnet build.py jetzt selbst aus. Wer einen Partner
einträgt oder streicht, ändert nur diese Datei.

Je Eintrag:
    name  wie er auf der Kachel steht und im Alternativtext des Logos
    url   Website, leer lassen wenn keine bekannt ist
    logo  Dateiname unter site/assets/img/partner/, leer wenn kein Logo
          da ist. Ohne Logo trägt die Kachel den Firmennamen — das Raster
          bleibt dasselbe.

--------------------------------------------------------------------------
Zu den Logodateien
--------------------------------------------------------------------------
Unter site/assets/img/partner/ liegen **aufbereitete** Fassungen, nicht
die Originale. Tims Originale bleiben unangetastet in
site/assets/img/Sponsoren/ liegen.

Der Ordner heisst «partner» und nicht «sponsoren», und das hat einen
Grund: Windows unterscheidet in Dateinamen keine Gross- und
Kleinschreibung. «sponsoren» und «Sponsoren» wären dort **derselbe
Ordner** — die aufbereiteten Dateien lägen zwischen den Originalen, und
auf einem Linux-Webserver, der sehr wohl unterscheidet, fände die Website
sie anschliessend nicht mehr. Der Fehler wäre erst nach dem Aufschalten
aufgefallen.

Aufbereitet heisst: freigestellt, auf die Marke beschnitten und auf eine
einheitliche Leinwand von 480 × 300 gesetzt — dabei nicht auf gleiche
Breite skaliert, sondern auf gleiche **Fläche**. Das ist der Unterschied
zwischen einer ruhigen und einer unruhigen Sponsorenwand: mit object-fit
allein wird ein 6:1-Wortzeichen winzig und ein quadratisches Signet
riesig, obwohl beide dieselbe Kachel füllen. Über die Fläche wiegen sie
optisch gleich viel.

Zwei Logos mussten umgekehrt werden, weil sie ausschliesslich in Weiss
vorliegen und auf der weissen Kachel unsichtbar wären: **Klingler** und
**Restaurant zum alten Schützenhaus**. Beide sind einfarbige
Strichzeichnungen, das Umkehren dreht also nur die Tintenfarbe. Trotzdem
wären dunkle Originalfassungen besser — steht auf der ToDo-Liste.
"""

# Der Ausrüster steht eigenständig über dem Raster, nicht als eine Kachel
# unter zwanzig anderen. So ist er da, wo man ihn erwartet, ohne dass er
# den Partnern die Aufmerksamkeit wegnimmt.
AUSRUESTER = {
    "rolle": "Offizieller Ausrüster",
    "name": "TT-Store.ch",
    "url": "https://www.tt-store.ch/",
    "logo": "",
    # Stand der Meldung vom 11. Mai 2026: Ausrüstung ab 2026/27, vom
    # Nachwuchs bis zu den STTL-Teams. Welches Material genau, sagt sie nicht.
    "text": "Ab der Saison 2026/27 rüstet der Schweizer JOOLA-Vertriebspartner den ganzen "
            "Verein aus – vom Nachwuchs bis zu den STTL-Teams.",
}

SPONSOREN = [
    {"name": "Klingler",
     "url": "https://www.klingler-heizung-sanitaer.ch/",
     "logo": "klingler.png"},
    {"name": "Druckwerk",
     "url": "https://druckwerk-sh.ch/",
     "logo": "druckwerk.png"},
    {"name": "Johnson & Johnson",
     "url": "",
     "logo": ""},
    {"name": "Iseli und Albrecht",
     "url": "https://www.iseli-albrecht.ch/",
     "logo": "iseli-albrecht.png"},
    {"name": "sasag",
     "url": "https://sasag.ch/",
     "logo": "sasag.png"},
    {"name": "Girsberger Sonnen- und Wetterschutz",
     "url": "https://www.girsberger-storen.ch/",
     "logo": "girsberger.png"},
    {"name": "Graf und Partner",
     "url": "https://www.immobag.ch/",
     "logo": "graf-partner.png"},
    {"name": "Wenger + Wirz",
     "url": "https://wenger-wirz.ch/",
     "logo": "wenger-wirz.png"},
    {"name": "Dux",
     "url": "http://www.duxmode.com/trio",
     "logo": "dux.png"},
    {"name": "Georg Fischer",
     "url": "https://www.georgfischer.com/de.html",
     "logo": "georg-fischer.png"},
    {"name": "Remondis",
     "url": "https://www.remondis.ch/de/startseite/",
     "logo": "remondis.png"},
    {"name": "Radio TV Sauter",
     "url": "https://www.sauterag.ch/",
     "logo": "sauter.png"},
    {"name": "Brauerei Falken",
     "url": "https://shop.falken.ch/",
     "logo": "falken.png"},
    {"name": "Volksapotheke Schaffhausen",
     "url": "https://volksapotheke.ch/",
     "logo": "volksapotheke.png"},
    {"name": "SIG",
     "url": "https://www.sigareal.ch/",
     "logo": "sig.png"},
    {"name": "Steinemann",
     "url": "https://steinemann-sh.ch/metamenu/home/",
     "logo": "steinemann.png"},
    {"name": "SH Power",
     "url": "https://www.shpower.ch/",
     "logo": "sh-power.png"},
    {"name": "Clientis BS Bank Schaffhausen",
     "url": "https://bsb.clientis.ch/de/",
     "logo": "clientis.png"},

    # Neu aufgenommen am 13. September 2026.
    {"name": "Reisebüro Sulzberger",
     "url": "https://sulzberger.com/",
     "logo": "reisebuero-sulzberger.png"},
    {"name": "Daniele Gaumenschmaus",
     "url": "https://daniele.shop/",
     "logo": "daniele.png"},
    {"name": "Restaurant zum alten Schützenhaus",
     "url": "https://schuetzenhaus.ch/",
     "logo": "schuetzenhaus.png"},
    {"name": "Wendico",
     "url": "https://wendico.ch/",
     "logo": "wendico.png"},

    # Gestrichen am 13. September 2026: GVS, IWC, Bruno Niggli.
]

# Acht Adressen waren noch offen und sind am 14. September nachgeschlagen:
# Klingler, Girsberger, Wenger + Wirz, Volksapotheke, Reisebüro Sulzberger,
# Daniele, Schützenhaus, Wendico. Gesucht über die Firmennamen aus den
# gelieferten Logos, jede Adresse an der Website selbst gegengeprüft.
#
# Offen bleibt **Johnson & Johnson** — dazu gibt es weder ein Logo noch
# einen Hinweis, welche Gesellschaft gemeint ist. In Schaffhausen sitzt
# die Cilag AG (dieselbe, die 1996 den Play-Off-Final sponserte, siehe
# Archiv). Ein Link auf den Weltkonzern wäre geraten, deshalb steht hier
# keiner.
