#!/usr/bin/env python3
"""Baut die Website: vorlage/layout.html + inhalt/*.html + Daten aus vorlage/*.py → site/

    python3 build.py                      echte Website
    python3 build.py --vorschau <Adresse> Vorschau (noindex, robots gesperrt)
    python3 build.py --bilder-verkleinern dazu News-Fotos verkleinern und Teilbilder
                                          rechnen (braucht Pillow; GitHub Actions)

Bearbeitet werden inhalt/ und vorlage/. Die News liegen in einem eigenen
Repository, das als Ordner redaktion/ daneben gehört (news/, bilder/,
dokumente/); nur dorthin schreibt die Redaktion unter /admin.

site/*.html und site/admin/config.yml werden bei jedem Lauf neu geschrieben,
ebenso site/assets/img/news/ und site/assets/dokumente/news/ (Abbild von
redaktion/bilder/ und redaktion/dokumente/). Die übrigen Bilder, Schriften
und Dokumente unter site/assets/ nicht.
"""

import html
import io
import json
import os
import re
import sys
import urllib.parse
from datetime import date
from pathlib import Path

WURZEL = Path(__file__).resolve().parent
sys.path.insert(0, str(WURZEL / "vorlage"))

from seiten import NAVIGATION, SEITEN, SEITE_URL  # noqa: E402
from trainingszeiten import ANGEBOTE, EINHEITEN, HALLEN, RASTER_BAENDER, TAGE  # noqa: E402
from mannschaften import MANNSCHAFTEN, SAISON, VEREINSSEITEN, WETTBEWERBE  # noqa: E402
from sponsoren import AUSRUESTER, SPONSOREN  # noqa: E402
from geschichte import ARCHIV, MEISTERTITEL, NACHWEIS, ZEITLEISTE  # noqa: E402
from news import AUF_STARTSEITE  # noqa: E402
from dokumente import ANMELDEFORMULAR, BEITRITTSFORMULARE, DOKUMENTE, HALLENPROJEKT  # noqa: E402
from termine import TERMINE  # noqa: E402
from seo import (HALLENORTE, MUSTER, NEWS_ARCHIV, VEREIN, WEG, WEG_MUSTER,  # noqa: E402
                 WEITERLEITUNGEN)

ALLE_DOKUMENTE = DOKUMENTE + BEITRITTSFORMULARE + HALLENPROJEKT
INHALT = WURZEL / "inhalt"
VORLAGE = WURZEL / "vorlage"
ZIEL = WURZEL / "site"
DOKUMENTORDNER = "assets/dokumente"
e = html.escape


def _vorschau_adresse():
    if "--vorschau" not in sys.argv:
        return None
    i = sys.argv.index("--vorschau")
    if i + 1 >= len(sys.argv) or sys.argv[i + 1].startswith("-"):
        sys.exit("--vorschau braucht eine Adresse, z. B. https://name.github.io/repo/")
    adresse = sys.argv[i + 1]
    return adresse if adresse.endswith("/") else adresse + "/"


VORSCHAU_URL = _vorschau_adresse()
BASIS_URL = VORSCHAU_URL or SEITE_URL
WURZELPFAD = urllib.parse.urlsplit(BASIS_URL).path   # "/" – auf der Vorschau "/repo/"
OG_BILD = BASIS_URL + "assets/img/og-standard.jpg"
# Grosse Bildvorschau und volle Textauszüge in der Google-Suche erlauben.
ROBOTS_META = ('\n<meta name="robots" content="noindex, nofollow">' if VORSCHAU_URL else
               '\n<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">')
ROBOTS_NOINDEX = '\n<meta name="robots" content="noindex, follow">'
# Seiten, die gebaut, aber nicht gefunden werden sollen: kein Eintrag in der
# Sitemap, noindex. Die Fehlerseite wird unter jeder Adresse ausgeliefert und
# setzt ihre Verweise deshalb ab der Wurzel.
FEHLERSEITE = "404.html"


# --- Hilfen -----------------------------------------------------------------

MONATE = ("Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember")
MONATE_KURZ = ("Jan", "Feb", "März", "Apr", "Mai", "Juni", "Juli",
               "Aug", "Sept", "Okt", "Nov", "Dez")
ZAHLWORTE = {2: "zwei", 3: "drei", 4: "vier", 5: "fünf", 6: "sechs", 7: "sieben",
             8: "acht", 9: "neun", 10: "zehn", 11: "elf", 12: "zwölf"}


def minuten(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def datum_lang(iso):
    j, m, t = (int(x) for x in iso.split("-"))
    return "%d. %s %d" % (t, MONATE[m - 1], j)


def bildmass(pfad):
    """(Breite, Höhe) eines JPEG, PNG oder WebP, ohne Pillow – so, wie der
    Browser es zeigt: ein Handyfoto, das nur im EXIF als hochkant markiert
    ist, ist hochkant."""
    with open(pfad, "rb") as f:
        kopf = f.read(30)
        if kopf[:8] == b"\x89PNG\r\n\x1a\n":
            return int.from_bytes(kopf[16:20], "big"), int.from_bytes(kopf[20:24], "big")
        if kopf[:4] == b"RIFF" and kopf[8:12] == b"WEBP":
            art = kopf[12:16]
            if art == b"VP8 ":
                return (int.from_bytes(kopf[26:28], "little") & 0x3FFF,
                        int.from_bytes(kopf[28:30], "little") & 0x3FFF)
            if art == b"VP8L":
                bits = int.from_bytes(kopf[21:25], "little")
                return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
            if art == b"VP8X":
                return int.from_bytes(kopf[24:27], "little") + 1, int.from_bytes(kopf[27:30], "little") + 1
            raise ValueError("Unbekannte WebP-Art %r in %s" % (art, pfad))
        if kopf[:2] != b"\xff\xd8":
            raise ValueError("Weder JPEG noch PNG noch WebP: %s" % pfad)
        f.seek(2)
        drehung = 1
        while True:
            b = f.read(1)
            while b and b != b"\xff":
                b = f.read(1)
            while b == b"\xff":
                b = f.read(1)
            if not b:
                raise ValueError("Kein SOF-Segment in %s" % pfad)
            marker = b[0]
            laenge = int.from_bytes(f.read(2), "big")
            if marker == 0xE1:
                drehung = _exif_drehung(f.read(laenge - 2)) or drehung
                continue
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                f.read(1)
                hoehe = int.from_bytes(f.read(2), "big")
                breite = int.from_bytes(f.read(2), "big")
                return (hoehe, breite) if drehung in (5, 6, 7, 8) else (breite, hoehe)
            f.seek(laenge - 2, 1)


def _exif_drehung(daten):
    """Orientierung 1–8 aus einem APP1-Segment, None ohne EXIF."""
    if daten[:6] != b"Exif\0\0":
        return None
    tiff = daten[6:]
    ordnung = {b"II": "little", b"MM": "big"}.get(tiff[:2])
    if not ordnung:
        return None

    def zahl(von, n):
        return int.from_bytes(tiff[von:von + n], ordnung)
    ifd = zahl(4, 4)
    for i in range(zahl(ifd, 2)):
        eintrag = ifd + 2 + 12 * i
        if zahl(eintrag, 2) == 0x0112:
            return zahl(eintrag + 8, 2)
    return None


def groesse(pfad):
    kb = pfad.stat().st_size / 1024
    return "%d kB" % round(kb) if kb < 1000 else ("%.1f MB" % (kb / 1024)).replace(".", ",")


PFEIL = '<span class="pfeil" aria-hidden="true"></span>'


# --- Navigation -------------------------------------------------------------

def navigation_html(datei, rubrik):
    z = []
    for titel, ziel, unter in NAVIGATION:
        klasse = "nav__punkt" + (" ist-aktiv" if rubrik == titel else "")
        aktuell = ' aria-current="page"' if ziel == datei else ""
        z.append('        <li class="%s">' % klasse)
        z.append('          <a class="nav__link" href="%s"%s>%s</a>' % (ziel, aktuell, e(titel)))
        if unter:
            z.append('          <ul class="nav__unter">')
            for u_titel, u_ziel in unter:
                u_aktuell = ' aria-current="page"' if u_ziel == datei else ""
                z.append('            <li><a href="%s"%s>%s</a></li>' % (u_ziel, u_aktuell, e(u_titel)))
            z.append('          </ul>')
        z.append('        </li>')
    return "\n".join(z)


# --- Training ---------------------------------------------------------------

def _achse():
    """Viertelstunden-Zeilen über alle Bänder, mit einer Bruchzeile dazwischen."""
    zeile, marken, brueche, n = {}, [], [], 1
    for i, (von, bis) in enumerate(RASTER_BAENDER):
        if i:
            brueche.append(n)
            n += 1
        viertel = (minuten(bis) - minuten(von)) // 15
        for k in range(viertel + 1):
            m = minuten(von) + k * 15
            zeile[m] = n + k
            if m % 60 == 0 and k < viertel:
                marken.append((n + k, "%02d:00" % (m // 60)))
        n += viertel
    return zeile, marken, brueche, n - 1


ACHSE, ACHSE_MARKEN, ACHSE_BRUECHE, ACHSE_ZEILEN = _achse()


def _zeile(hhmm):
    m = minuten(hhmm)
    if m not in ACHSE:
        sys.exit("Trainingszeit %s liegt ausserhalb von RASTER_BAENDER "
                 "(trainingszeiten.py) oder nicht auf einer Viertelstunde." % hhmm)
    return ACHSE[m]


def _bahnen(einheiten):
    frei_ab = []
    for x in sorted(einheiten, key=lambda x: (minuten(x["von"]), minuten(x["bis"]))):
        for i, f in enumerate(frei_ab):
            if f <= minuten(x["von"]):
                x["bahn"], frei_ab[i] = i + 1, minuten(x["bis"])
                break
        else:
            frei_ab.append(minuten(x["bis"]))
            x["bahn"] = len(frei_ab)
    return max(len(frei_ab), 1)


def _einheiten_sortiert(filter_fn=lambda x: True):
    rang = {k: i for i, (k, _) in enumerate(TAGE)}
    return sorted((x for x in EINHEITEN if filter_fn(x)),
                  key=lambda x: (rang[x["tag"]], minuten(x["von"])))


def wochenplan_html():
    z = ['<div class="plan" data-plan data-filter="alle">',
         '  <div class="plan__steuerung">',
         '    <div class="plan__filter" role="group" aria-label="Nach Angebot hervorheben">',
         '      <button type="button" data-zeigt="alle" aria-pressed="true">Alle</button>']
    for k, a in ANGEBOTE.items():
        z.append('      <button type="button" data-zeigt="%s" aria-pressed="false">%s</button>'
                 % (k, e(a["name"])))
    z.append('    </div>')
    z.append('    <ul class="plan__legende">')
    for k, h in HALLEN.items():
        z.append('      <li><i class="halle-marke halle-marke--%s"></i>%s</li>' % (k, e(h["name"])))
    z.append('    </ul>')
    z.append('  </div>')
    z.append('  <div class="plan__raster" style="--zeilen:%d">' % ACHSE_ZEILEN)
    z.append('    <div class="plan__achse" aria-hidden="true">')
    for zeile, text in ACHSE_MARKEN:
        z.append('      <span style="--z:%d">%s</span>' % (zeile, text))
    for zeile in ACHSE_BRUECHE:
        z.append('      <span class="plan__bruch" style="--z:%d">Mittag</span>' % zeile)
    z.append('    </div>')
    for kurz, lang in TAGE:
        einheiten = [dict(x) for x in EINHEITEN if x["tag"] == kurz]
        if not einheiten:
            continue
        bahnen = _bahnen(einheiten)
        z.append('    <section class="plan__tag" data-tag="%s" style="--bahnen:%d">' % (kurz, bahnen))
        z.append('      <h3 class="plan__tagname">%s<span class="plan__heute">Heute</span></h3>' % e(lang))
        z.append('      <div class="plan__spalte">')
        for zeile in ACHSE_BRUECHE:
            z.append('        <i class="plan__bruchlinie" style="--z:%d" aria-hidden="true"></i>' % zeile)
        for x in sorted(einheiten, key=lambda x: minuten(x["von"])):
            a = ANGEBOTE[x["angebot"]]
            z.append('        <a class="einheit einheit--%s" href="%s" data-angebot="%s" '
                     'style="--von:%d;--bis:%d;--bahn:%d">'
                     % (x["halle"], a["seite"], x["angebot"],
                        _zeile(x["von"]), _zeile(x["bis"]), x["bahn"]))
            z.append('          <span class="einheit__zeit">%s–%s</span>' % (x["von"], x["bis"]))
            z.append('          <span class="einheit__gruppe">%s</span>' % e(x.get("kurz") or x["gruppe"]))
            z.append('          <span class="einheit__halle">%s</span>' % e(HALLEN[x["halle"]]["kurz"]))
            z.append('        </a>')
        z.append('      </div>')
        z.append('    </section>')
    z.append('  </div>')
    frei = [lang for kurz, lang in TAGE if not any(x["tag"] == kurz for x in EINHEITEN)]
    if frei:
        z.append('  <p class="plan__frei">%s: kein angesetztes Training. Mitglieder mit '
                 'Hallenbeitrag spielen im TTZ Ebnat trotzdem – die Halle ist rund um die Uhr offen.</p>'
                 % " und ".join(frei))
    z.append('  <p class="sr-only" data-plan-stand role="status" aria-live="polite"></p>')
    z.append('  <details class="plan__tabelle">')
    z.append('    <summary>Alle Einheiten als Liste, mit Trainerinnen und Trainern</summary>')
    z.append(zeiten_html(None, trainer=True))
    z.append('  </details>')
    z.append('</div>')
    return "\n".join(z)


def _filter(spec):
    """«nachwuchs», «nachwuchs+Stützpunkt|Förderkader» oder «halle=rhyfall»."""
    if spec is None:
        return lambda x: True
    if spec.startswith("halle="):
        halle = spec[6:]
        return lambda x: x["halle"] == halle
    angebot, _, begriffe = spec.partition("+")
    begriffe = [b for b in begriffe.split("|") if b]
    return lambda x: (x["angebot"] == angebot or angebot == "alle") and \
        (not begriffe or any(b in x["gruppe"] for b in begriffe))


def zeiten_html(spec, trainer=False):
    """Tabelle der Einheiten, gefiltert nach _filter()."""
    tage = dict(TAGE)
    auswahl = _einheiten_sortiert(_filter(spec))
    if not auswahl:
        sys.exit("{{zeiten:%s}} findet keine Einheit in trainingszeiten.py" % spec)
    kopf = '<th>Tag</th><th>Zeit</th><th>Gruppe</th><th>Halle</th>' + ('<th>Leitung</th>' if trainer else "")
    z = ['<div class="tabelle"><table>', '  <thead><tr>%s</tr></thead>' % kopf, '  <tbody>']
    voriger = None
    for x in auswahl:
        tag = "" if x["tag"] == voriger else e(tage[x["tag"]])
        voriger = x["tag"]
        halle = HALLEN[x["halle"]]
        z.append('    <tr data-tag="%s"><th scope="row">%s</th><td class="zahl">%s–%s</td><td>%s</td>'
                 '<td><a href="%s"><i class="halle-marke halle-marke--%s"></i>%s</a></td>%s</tr>'
                 % (x["tag"], tag, x["von"], x["bis"], e(x["gruppe"]), halle["seite"], x["halle"],
                    e(halle["name"]), ("<td>%s</td>" % (e(x["trainer"]) or "–")) if trainer else ""))
    z += ['  </tbody>', '</table></div>']
    return "\n".join(z)


def kurzzeiten_html(spec):
    """Kurzform für Randspalten: gleiche Zeiten werden zusammengefasst."""
    tage = [k for k, _ in TAGE]
    gruppen = {}
    for x in _einheiten_sortiert(_filter(spec)):
        schluessel = (x["von"], x["bis"], x["halle"])
        gruppen.setdefault(schluessel, []).append(x["tag"])
    if not gruppen:
        sys.exit("{{kurzzeiten:%s}} findet keine Einheit" % spec)
    zeilen = sorted(gruppen.items(), key=lambda kv: (tage.index(kv[1][0]), minuten(kv[0][0])))
    mit_halle = not spec.startswith("halle=")
    return "<br>".join("%s %s–%s%s" % (", ".join(t), von, bis, (", " + e(HALLEN[h]["kurz"])) if mit_halle else "")
                       for (von, bis, h), t in zeilen)


def trainer_zeiten_html(name):
    """Die Einheiten, die eine Person leitet – für das Trainerteam."""
    tage = dict(TAGE)
    auswahl = _einheiten_sortiert(lambda x: name in x["trainer"])
    if not auswahl:
        return ""
    z = ['<ul class="trainerwoche">']
    for x in auswahl:
        z.append('  <li><b>%s</b> %s–%s <span>%s, %s</span></li>'
                 % (e(tage[x["tag"]][:2]), x["von"], x["bis"], e(x["gruppe"]), e(HALLEN[x["halle"]]["kurz"])))
    z.append('</ul>')
    return "\n".join(z)


def woche_kurz_html():
    """Die Woche kompakt für die Startseite, ein Tag je Spalte."""
    z = ['<ol class="woche">']
    for kurz, lang in TAGE:
        einheiten = _einheiten_sortiert(lambda x: x["tag"] == kurz)
        if not einheiten:
            continue
        z.append('  <li class="woche__tag" data-tag="%s">' % kurz)
        z.append('    <h3>%s<span class="woche__heute">Heute</span></h3>' % e(lang))
        z.append('    <ul>')
        for x in einheiten:
            a = ANGEBOTE[x["angebot"]]
            z.append('      <li><a href="%s"><b class="zahl">%s</b> %s <span>%s · %s</span></a></li>'
                     % (a["seite"], x["von"], e(a["name"]), e(x.get("kurz") or x["gruppe"]),
                        e(HALLEN[x["halle"]]["kurz"])))
        z.append('    </ul>')
        z.append('  </li>')
    z.append('</ol>')
    return "\n".join(z)


def trainingsdaten_json():
    """Die Woche als JSON für «Heute im Training» (main.js)."""
    daten = [{"tag": x["tag"], "von": x["von"], "bis": x["bis"], "gruppe": x.get("kurz", x["gruppe"]).replace("­", ""),
              "halle": HALLEN[x["halle"]]["name"], "seite": ANGEBOTE[x["angebot"]]["seite"]}
             for x in _einheiten_sortiert()]
    return ('<script type="application/json" id="trainingsdaten">%s</script>'
            % json.dumps(daten, ensure_ascii=False))


def trainingsumfang():
    stunden = sum(minuten(x["bis"]) - minuten(x["von"]) for x in EINHEITEN) / 60
    return len(EINHEITEN), len({x["tag"] for x in EINHEITEN}), stunden


# --- Partner ----------------------------------------------------------------

def sponsoren_html():
    z = ['<ul class="partnerwand">']
    for s in SPONSOREN:
        if s["logo"]:
            inhalt = ('<img src="assets/img/partner/%s" alt="%s" width="480" height="300" '
                      'loading="lazy" decoding="async">' % (s["logo"], e(s["name"], quote=True)))
        else:
            inhalt = '<span class="partnerwand__name">%s</span>' % e(s["name"])
        if s["url"]:
            z.append('  <li><a href="%s" rel="noopener">%s</a></li>' % (e(s["url"], quote=True), inhalt))
        else:
            z.append('  <li><span>%s</span></li>' % inhalt)
    z.append('</ul>')
    return "\n".join(z)


def ausruester_html():
    a = AUSRUESTER
    z = ['<div class="ausruester">',
         '  <p class="rubrik">%s</p>' % e(a["rolle"]),
         '  <p class="ausruester__name">%s</p>' % e(a["name"]),
         '  <p class="ausruester__text">%s</p>' % e(a["text"])]
    if a["url"]:
        z.append('  <a class="pfeil-link" href="%s" rel="noopener">Zum Shop%s</a>' % (e(a["url"], quote=True), PFEIL))
    z.append('</div>')
    return "\n".join(z)


# --- News -------------------------------------------------------------------
#
# Je Beitrag eine Datei redaktion/news/<kennung>.json, geschrieben in der
# Redaktion unter /admin oder von Hand. Das Format steht in vorlage/news.py.
#
# redaktion/ ist ein eigenes Repository (die «News-Ablage»): Nur dorthin darf
# der Schlüssel schreiben, den die Redaktion nach der Anmeldung bekommt. Was
# von dort kommt, ist deshalb nie Programm, nur Daten – Texte, die build.py
# maskiert, und Dateien, die es nach Name, Art und Inhalt prüft, bevor sie in
# zwei eigene Ordner von site/ kommen. Diese Ordner gehören ganz der
# Redaktion; im Haupt-Repository liegt dort nichts.

REDAKTION = WURZEL / "redaktion"
NEWSORDNER = REDAKTION / "news"
# Ordner in redaktion/ → Ordner in site/, erlaubte Dateiarten
ABLAGEN = (("bilder", "assets/img/news", (".jpg", ".jpeg", ".png", ".webp")),
           ("dokumente", "assets/dokumente/news", (".pdf",)))
DATEINAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
# Darf in keinem Dateinamen als Endung vorkommen, auch nicht in der Mitte
# («bild.php.jpg»): Apache wertet unter Umständen jede Endung aus.
AUSFUEHRBAR = {"php", "php3", "php4", "php5", "php7", "php8", "phtml", "phar", "pht", "phps", "cgi", "pl", "py",
               "sh", "shtml", "asp", "aspx", "jsp", "htaccess", "htpasswd", "ini", "exe", "html", "htm", "js", "svg"}
GROESSTE_DATEI = 30 * 1024 * 1024
BLOCKARTEN = ("absatz", "titel", "zitat", "bild", "liste")
# «Wichtiger Bildteil»: wie object-position der Klassen .ausschnitt--* (komponenten.css)
AUSSCHNITT = {"oben": .25, "mitte": .5, "unten": .75}
TEILBILDER = "assets/img/teilen"
OG_STANDARD = (OG_BILD, 1200, 630, "Komm an den Tisch. Tischtennisclub Neuhausen, seit 1975")


def _zeichen(wert):
    return wert.strip() if isinstance(wert, str) else ""


def _warnung(text):
    """Ins Protokoll – in GitHub Actions als gelbe Warnung auf der Übersicht."""
    print(("::warning::" if "GITHUB_ACTIONS" in os.environ else "ACHTUNG: ") + text)


def hole_redaktion():
    """Spiegelt die Bilder und Dokumente der Redaktion nach site/.

    Nach jedem Lauf liegt in den beiden Zielordnern genau das, was in
    redaktion/ liegt und die Prüfung besteht. Verknüpfungen (Symlinks),
    Unterordner, fremde Dateiarten und Dateien, deren Inhalt nicht zur Endung
    passt, bleiben draussen."""
    if not NEWSORDNER.is_dir() or REDAKTION.is_symlink() or NEWSORDNER.is_symlink():
        sys.exit("redaktion/news/ fehlt. Die News liegen in einem eigenen Repository, das als Ordner "
                 "redaktion/ neben build.py gehört:\n"
                 "    git clone https://github.com/<Konto>/<Repository>-News.git redaktion\n"
                 "In GitHub Actions holt es der Workflow (Secret REDAKTION_SCHLUESSEL).")
    abgelehnt, zahl = [], {}
    for quelle, ziel, arten in ABLAGEN:
        ordner, zielordner = REDAKTION / quelle, ZIEL / ziel
        zielordner.mkdir(parents=True, exist_ok=True)
        soll = {}
        for datei in (sorted(ordner.iterdir()) if ordner.is_dir() and not ordner.is_symlink() else []):
            name = datei.name
            if name == ".gitkeep":
                continue
            teile = name.lower().split(".")[1:]
            if datei.is_symlink() or not datei.is_file():
                grund = "keine gewöhnliche Datei"
            elif not DATEINAME.match(name) or not teile or AUSFUEHRBAR.intersection(teile):
                grund = "Dateiname"
            elif "." + teile[-1] not in arten:
                grund = "Dateiart"
            elif datei.stat().st_size > GROESSTE_DATEI:
                grund = "grösser als %d MB" % (GROESSTE_DATEI // 1024 // 1024)
            else:
                daten = datei.read_bytes()
                try:
                    if teile[-1] == "pdf":
                        if not daten.startswith(b"%PDF-"):
                            raise ValueError
                    else:
                        bildmass(datei)
                    grund = ""
                except (ValueError, OSError):
                    grund = "Inhalt passt nicht zur Endung"
            if grund:
                abgelehnt.append("%s/%s (%s)" % (quelle, name, grund))
            else:
                soll[name] = daten
        for name, daten in soll.items():
            fertig = zielordner / name
            if not fertig.is_file() or fertig.is_symlink() or fertig.read_bytes() != daten:
                if fertig.is_symlink():
                    fertig.unlink()
                fertig.write_bytes(daten)
        for alt in zielordner.iterdir():
            if alt.name not in soll and (alt.is_file() or alt.is_symlink()):
                alt.unlink()
        zahl[quelle] = len(soll)
    if abgelehnt:
        _warnung("Aus der Redaktion nicht übernommen: " + ", ".join(abgelehnt))
    return zahl


def _site_pfad(wert, quelle, ordner):
    """«/assets/img/news/x.webp» aus der Redaktion → «assets/img/news/x.webp»:
    relativ, damit es auch in der Vorschau unter /repo/ stimmt. Der Pfad muss
    in ordner liegen – ein Beitrag kann auf nichts anderes zeigen."""
    pfad = urllib.parse.unquote(_zeichen(wert)).lstrip("/")
    if pfad.startswith("site/"):
        pfad = pfad[len("site/"):]
    if not pfad:
        return ""
    if not pfad.startswith(ordner) or ".." in pfad.split("/") or "\\" in pfad:
        sys.exit("%s: «%s» liegt nicht unter /%s" % (quelle, wert, ordner))
    if not (ZIEL / pfad).is_file():
        sys.exit("%s: «%s» fehlt unter site/%s" % (quelle, wert, pfad))
    return pfad


def _bildpfad(wert, quelle):
    """Wie _site_pfad, dazu muss es ein Bild sein, dessen Masse build.py lesen kann."""
    pfad = _site_pfad(wert, quelle, "assets/img/")
    if pfad:
        try:
            bildmass(ZIEL / pfad)
        except (ValueError, OSError):
            sys.exit("%s: «%s» ist kein JPEG, PNG oder WebP – bitte als Foto hochladen" % (quelle, wert))
    return pfad


def _url(pfad):
    return e(urllib.parse.quote(pfad), quote=True)


def _bloecke(roh, quelle):
    """Die Blöcke aus der Datei; aus einem Absatz-Block wird jede Zeile ein Absatz."""
    absaetze = []
    for block in roh or []:
        if isinstance(block, str):
            block = {"art": "absatz", "text": block}
        art = block.get("art") or "absatz"
        text = _zeichen(block.get("text"))
        if art not in BLOCKARTEN:
            sys.exit("%s: unbekannte Blockart «%s» (erlaubt: %s)" % (quelle, art, ", ".join(BLOCKARTEN)))
        if art == "absatz":
            absaetze += [zeile.strip() for zeile in text.splitlines() if zeile.strip()]
        elif art in ("titel", "zitat") and text:
            absaetze.append({"art": art, "text": text, "wer": _zeichen(block.get("wer"))})
        elif art == "bild" and _zeichen(block.get("bild")):
            absaetze.append({"art": "bild", "bild": _bildpfad(block["bild"], quelle),
                             "beschreibung": _zeichen(block.get("beschreibung"))})
        elif art == "liste":
            punkte = [_zeichen(p if isinstance(p, str) else (p or {}).get("punkt"))
                      for p in block.get("punkte") or []]
            if any(punkte):
                absaetze.append({"art": "liste", "titel": _zeichen(block.get("titel")),
                                 "punkte": [p for p in punkte if p]})
    return absaetze


def lade_news():
    beitraege = []
    for datei in sorted(NEWSORDNER.glob("*.json")):
        quelle = "redaktion/news/" + datei.name
        # Der Dateiname wird zur Adresse news-<kennung>.html.
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", datei.stem):
            sys.exit("%s: Dateiname nur aus Buchstaben, Ziffern und Bindestrichen" % quelle)
        if datei.is_symlink() or not datei.is_file() or datei.stat().st_size > 2 * 1024 * 1024:
            sys.exit("%s: keine gewöhnliche Datei oder grösser als 2 MB" % quelle)
        try:
            roh = json.loads(datei.read_text(encoding="utf-8-sig"))
        except ValueError as fehler:
            sys.exit("%s: kein gültiges JSON (%s)" % (quelle, fehler))
        if not isinstance(roh, dict):
            sys.exit("%s: kein Beitrag (erwartet: Felder in geschweiften Klammern)" % quelle)
        datum = _zeichen(roh.get("datum"))[:10]
        try:
            date.fromisoformat(datum)
        except ValueError:
            sys.exit("%s: Datum «%s» ist nicht JJJJ-MM-TT" % (quelle, roh.get("datum")))
        if not _zeichen(roh.get("titel")):
            sys.exit("%s: Titel fehlt" % quelle)
        ausschnitt = _zeichen(roh.get("ausschnitt")) or "mitte"
        if ausschnitt not in AUSSCHNITT:
            sys.exit("%s: Ausschnitt «%s» (erlaubt: %s)" % (quelle, ausschnitt, ", ".join(AUSSCHNITT)))
        galerie = [_bildpfad(p if isinstance(p, str) else (p or {}).get("bild"), quelle)
                   for p in roh.get("galerie") or []]
        beitraege.append({
            "kennung": datei.stem,
            "datum": datum,
            "titel": _zeichen(roh["titel"]),
            "kurztitel": _zeichen(roh.get("kurztitel")),
            "anriss": _zeichen(roh.get("anriss")),
            "autor": _zeichen(roh.get("autor")),
            "bildnachweis": _zeichen(roh.get("bildnachweis")),
            "bild": _bildpfad(roh.get("bild"), quelle),
            "bildalt": _zeichen(roh.get("bildalt")),
            "ausschnitt": ausschnitt,
            "absaetze": _bloecke(roh.get("absaetze"), quelle),
            "galerie": [p for p in galerie if p],
            "pdf": _site_pfad(roh.get("pdf"), quelle, "assets/dokumente/"),
            "pdf_titel": _zeichen(roh.get("pdf_titel")),
        })
    if not beitraege:
        sys.exit("Keine News unter redaktion/news/ – die Startseite braucht mindestens eine.")
    return beitraege


ABLAGE_ZAHL = hole_redaktion()
BEITRAEGE = lade_news()


def news_datei(b):
    return "news-%s.html" % b["kennung"]


def _hat_seite(b):
    """Mit Text, Bildern oder PDF eine eigene Seite, sonst nur eine Meldung."""
    return bool(b["absaetze"] or b["galerie"] or b["pdf"])


def _herkunft(b):
    teile = []
    if b["autor"]:
        teile.append("Text: " + b["autor"])
    if b["bildnachweis"]:
        teile.append("Bild: " + b["bildnachweis"])
    return " · ".join(teile)


def _news_neueste():
    return sorted(BEITRAEGE, key=lambda b: b["datum"], reverse=True)


def _img(pfad, alt, klasse="", faul=True):
    breite, hoehe = bildmass(ZIEL / pfad)
    return ('<img src="%s" alt="%s"%s width="%d" height="%d"%s>'
            % (_url(pfad), e(alt, quote=True), ' class="%s"' % klasse if klasse else "", breite, hoehe,
               ' loading="lazy" decoding="async"' if faul else ""))


def _ausschnitt(b):
    return "" if b["ausschnitt"] == "mitte" else "ausschnitt--" + b["ausschnitt"]


def _newseintrag(b, klasse="meldung", kurz=True, mit_bild=False):
    titel = b["kurztitel"] if kurz and b["kurztitel"] else b["titel"]
    tag_a = ('<a class="%s" href="%s">' % (klasse, news_datei(b))) if _hat_seite(b) \
        else '<article class="%s">' % klasse
    z = [tag_a]
    if mit_bild and b["bild"]:
        z.append('  <div class="%s__bild">%s</div>' % (klasse, _img(b["bild"], b["bildalt"], _ausschnitt(b))))
    z.append('  <time datetime="%s">%s</time>' % (b["datum"], datum_lang(b["datum"])))
    z.append('  <h3>%s</h3>' % e(titel))
    if b["anriss"]:
        z.append('  <p>%s</p>' % e(b["anriss"]))
    herkunft = _herkunft(b)
    if b["galerie"]:
        n = len(b["galerie"])
        herkunft += (" · " if herkunft else "") + ("Galerie: %d %s" % (n, "Bild" if n == 1 else "Bilder"))
    if herkunft:
        z.append('  <p class="%s__herkunft">%s</p>' % (klasse, e(herkunft)))
    if _hat_seite(b):
        z.append('  <span class="pfeil-link">Weiterlesen%s</span>' % PFEIL)
    z.append('</a>' if _hat_seite(b) else '</article>')
    return "\n".join(z)


def news_start_html():
    """Startseite: der neueste Beitrag mit Bild gross, daneben die Liste."""
    neu = _news_neueste()
    gross = next((b for b in neu if b["bild"]), neu[0])
    rest = [b for b in neu if b is not gross][:AUF_STARTSEITE]
    z = ['<div class="newsblock">', '  <div class="newsblock__gross">',
         _newseintrag(gross, "newskarte", mit_bild=True), '  </div>',
         '  <div class="newsblock__liste">']
    z += [_newseintrag(b) for b in rest]
    z += ['  </div>', '</div>']
    return "\n".join(z)


def aktuell_html():
    """Die Zeile «Aktuell» im Auftakt: neuester Beitrag."""
    b = _news_neueste()[0]
    ziel = news_datei(b) if _hat_seite(b) else "news.html"
    return ('<a class="aktuell__news" href="%s"><span class="aktuell__marke">Aktuell</span>'
            '<time datetime="%s">%s</time><span class="aktuell__titel">%s</span>%s</a>'
            % (ziel, b["datum"], datum_lang(b["datum"]), e(b["kurztitel"] or b["titel"]), PFEIL))


def newsliste_html():
    neu = _news_neueste()
    z = ['<div class="newsliste">']
    jahr = None
    for b in neu:
        j = b["datum"][:4]
        if j != jahr:
            z.append('<h2 class="newsliste__jahr">%s</h2>' % j)
            jahr = j
        z.append(_newseintrag(b, "newseintrag", kurz=False, mit_bild=bool(b["bild"])))
    z.append('</div>')
    return "\n".join(z)


def _absatz_html(s):
    if isinstance(s, str):
        return '<p>%s</p>' % e(s)
    art = s["art"]
    if art == "titel":
        return '<h2>%s</h2>' % e(s["text"])
    if art == "zitat":
        wer = '<cite>%s</cite>' % e(s["wer"]) if s["wer"] else ""
        return '<blockquote class="zitat"><p>%s</p>%s</blockquote>' % (e(s["text"]), wer)
    if art == "bild":
        legende = '<figcaption>%s</figcaption>' % e(s["beschreibung"]) if s["beschreibung"] else ""
        return ('<figure class="bild bild--im-text"><a href="%s" data-lupe>%s</a>%s</figure>'
                % (_url(s["bild"]), _img(s["bild"], s["beschreibung"]), legende))
    punkte = "".join("<li>%s</li>" % e(p) for p in s["punkte"])
    titel = '<h3>%s</h3>' % e(s["titel"]) if s["titel"] else ""
    return '<div class="rangliste">%s<ol>%s</ol></div>' % (titel, punkte)


def galerie_html(b):
    """Die weiteren Bilder unter dem Text: Zeilen gleicher Höhe, jedes Bild in
    seinem Format (--r = Breite/Höhe). Ein Klick öffnet die Lupe (main.js)."""
    n = len(b["galerie"])
    titel = b["kurztitel"] or b["titel"]
    z = ['<section class="galerie" aria-labelledby="galerie">',
         '  <h2 class="galerie__titel" id="galerie">Bilder <span>%d</span></h2>' % n,
         '  <ul class="galerie__raster">']
    for i, pfad in enumerate(b["galerie"], 1):
        breite, hoehe = bildmass(ZIEL / pfad)
        z.append('    <li style="--r:%.3f"><figure><a href="%s" data-lupe>%s</a></figure></li>'
                 % (breite / hoehe, _url(pfad), _img(pfad, "Bild %d von %d: %s" % (i, n, titel))))
    z += ['  </ul>', '</section>']
    return "\n".join(z)


def beitrag_html(b):
    bild = ""
    if b["bild"]:
        legende = ('<figcaption><span class="nachweis">%s</span></figcaption>' % e(_herkunft(b))
                   if _herkunft(b) else "")
        bild = ('<figure class="bild bild--breit"><a href="%s" data-lupe>%s</a>%s</figure>'
                % (_url(b["bild"]), _img(b["bild"], b["bildalt"], _ausschnitt(b), faul=False), legende))
    # Der Anriss steht als Vorspann unter dem Titel.
    vorspann = '\n    <p class="lead">%s</p>' % e(b["anriss"]) if b["anriss"] else ""
    absaetze = "\n".join(_absatz_html(s) for s in b["absaetze"])
    if b["pdf"]:
        absaetze += ('\n<p><a class="pfeil-link" href="%s">%s%s</a></p>'
                     % (_url(b["pdf"]), e(b["pdf_titel"] or "Dokument als PDF"), PFEIL))
    galerie = "\n" + galerie_html(b) if b["galerie"] else ""
    return """<header class="aufmacher aufmacher--schmal">
  <div class="wrap">
    <nav class="brotkrumen" aria-label="Brotkrumen"><a href="index.html">Start</a><a href="news.html">News</a><span aria-current="page">Beitrag</span></nav>
    <p class="rubrik"><time datetime="%s">%s</time></p>
    <h1 class="h1--mittel">%s</h1>%s
  </div>
</header>
<section class="flaeche--papier eng">
  <div class="wrap">%s
    <div class="text beitrag">
%s
    </div>%s
    <p><a class="pfeil-link" href="news.html">Alle Beiträge%s</a></p>
  </div>
</section>""" % (b["datum"], datum_lang(b["datum"]), e(b["titel"]), vorspann, bild, absaetze, galerie, PFEIL)


def teilbild(b):
    """Bild für die Vorschau beim Teilen (WhatsApp, Facebook): das Titelbild
    des Beitrags, mit --bilder-verkleinern auf 1200 × 630 gerechnet. Ohne das
    das Titelbild selbst – ausser WebP, das nicht jede App zeigt."""
    if not b or not b["bild"]:
        return OG_STANDARD
    pfad = "%s/%s.jpg" % (TEILBILDER, b["kennung"])
    if not (ZIEL / pfad).is_file():
        if b["bild"].lower().endswith(".webp"):
            return OG_STANDARD
        pfad = b["bild"]
    breite, hoehe = bildmass(ZIEL / pfad)
    return BASIS_URL + urllib.parse.quote(pfad), breite, hoehe, b["bildalt"] or b["titel"]


# --- Bilder für den Server (nur mit --bilder-verkleinern) -------------------

GROESSTE_KANTE = 2000


def _news_bilder():
    pfade = set()
    for b in BEITRAEGE:
        pfade.update([b["bild"]] + b["galerie"] +
                     [s["bild"] for s in b["absaetze"] if isinstance(s, dict) and s["art"] == "bild"])
    pfade.discard("")
    return sorted(pfade)


def bilder_aufbereiten():
    """Für GitHub Actions: Fotos der News auf höchstens 2000 Pixel verkleinern
    und ohne EXIF (Kamera, Aufnahmeort) speichern, dazu je Beitrag ein
    Teilbild. Geändert wird nur, was auf den Server geht – im Repository
    bleiben die Dateien, wie die Redaktion sie hochgeladen hat."""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        sys.exit("--bilder-verkleinern braucht Pillow: pip install pillow")
    verkleinert = 0
    for pfad in _news_bilder():
        datei = ZIEL / pfad
        with Image.open(datei) as bild:
            art = bild.format
            if art not in ("JPEG", "PNG", "WEBP") or (
                    max(bild.size) <= GROESSTE_KANTE and not bild.getexif() and datei.stat().st_size <= 900_000):
                continue
            profil = bild.info.get("icc_profile")
            neu = ImageOps.exif_transpose(bild)
            neu.thumbnail((GROESSTE_KANTE, GROESSTE_KANTE), Image.Resampling.LANCZOS)
            puffer = io.BytesIO()
            if art == "JPEG":
                neu.convert("RGB").save(puffer, "JPEG", quality=82, optimize=True, progressive=True,
                                        icc_profile=profil)
            elif art == "WEBP":
                neu.save(puffer, "WEBP", quality=82, method=6, icc_profile=profil)
            else:
                neu.save(puffer, "PNG", optimize=True, icc_profile=profil)
        datei.write_bytes(puffer.getvalue())
        verkleinert += 1
    ordner = ZIEL / TEILBILDER
    ordner.mkdir(parents=True, exist_ok=True)
    for alt in ordner.glob("*.jpg"):
        alt.unlink()
    teilbilder = 0
    for b in BEITRAEGE:
        if not b["bild"] or not _hat_seite(b):
            continue
        with Image.open(ZIEL / b["bild"]) as bild:
            profil = bild.info.get("icc_profile")
            teil = ImageOps.fit(ImageOps.exif_transpose(bild).convert("RGB"), (1200, 630),
                                Image.Resampling.LANCZOS, centering=(.5, AUSSCHNITT[b["ausschnitt"]]))
        teil.save(ordner / ("%s.jpg" % b["kennung"]), "JPEG", quality=84, optimize=True, progressive=True,
                  icc_profile=profil)
        teilbilder += 1
    print("Bilder: %d verkleinert, %d Teilbilder für WhatsApp und Facebook." % (verkleinert, teilbilder))


# --- Termine ----------------------------------------------------------------

def termine_html(anzahl=None):
    """Kommende Termine. main.js blendet Vergangenes auch ohne neuen Build aus."""
    heute = date.today().isoformat()
    kommend = [t for t in sorted(TERMINE, key=lambda t: t["datum"]) if t["datum"] >= heute]
    if anzahl:
        kommend = kommend[:anzahl]
    z = ['<div class="termine" data-termine>']
    for t in kommend:
        j, m, d = (int(x) for x in t["datum"].split("-"))
        z.append('  <article class="termin" data-datum="%s">' % t["datum"])
        z.append('    <p class="termin__datum"><b>%d</b> %s</p>' % (d, MONATE_KURZ[m - 1]))
        z.append('    <div><h3>%s</h3><p>%s</p></div>' % (e(t["titel"]), e(t["info"])))
        z.append('  </article>')
    z.append('  <p class="termine__leer"%s>Zurzeit sind keine weiteren Termine eingetragen. '
             'Neue Anlässe stehen zuerst in den <a href="news.html">News</a> und auf '
             '<a href="https://www.instagram.com/ttcneuhausen/" rel="noopener">Instagram</a>.</p>'
             % ("" if not kommend else " hidden"))
    z.append('</div>')
    return "\n".join(z)


# --- Teams ------------------------------------------------------------------

def _tabellen_url(m):
    # nuLiga will das Leerzeichen als «+» (quote_plus), mit %20 öffnet sich eine andere Liga.
    return ("https://www.click-tt.ch/cgi-bin/WebObjects/nuLigaTTCH.woa/wa/groupPage"
            "?championship=%s&amp;group=%d" % (urllib.parse.quote_plus(m["championship"]), m["gruppe_id"]))


def mannschaften_html():
    z = ['<div class="ligen">']
    for schluessel, titel, unter in WETTBEWERBE:
        gruppe = [m for m in MANNSCHAFTEN if m["wettbewerb"] == schluessel]
        if not gruppe:
            continue
        z.append('  <section class="liga">')
        z.append('    <h3 class="liga__titel">%s <span>%s</span></h3>' % (e(titel), e(unter)))
        z.append('    <ol class="liga__liste">')
        for m in gruppe:
            z.append('      <li><a href="%s" rel="noopener"><b>%s</b><span>%s</span>'
                     '<em>Tabelle%s</em></a></li>' % (_tabellen_url(m), e(m["name"]), e(m["liga"]), PFEIL))
        z.append('    </ol>')
        z.append('  </section>')
    z.append('</div>')
    return "\n".join(z)


def mannschaftszahl():
    return sum(1 for m in MANNSCHAFTEN if m["wettbewerb"] != "cup")


# --- Geschichte -------------------------------------------------------------

def zeitleiste_html():
    umfang = {k["id"]: len(k["stuecke"]) for k in ARCHIV}
    z = ['<ol class="zeitleiste">']
    for x in ZEITLEISTE:
        z.append('  <li class="zeitleiste__eintrag">')
        z.append('    <p class="zeitleiste__jahr">%s</p>' % e(x["jahr"]))
        z.append('    <div class="zeitleiste__text">')
        z.append('      <h3>%s</h3>' % e(x["titel"]))
        z.append('      <p>%s</p>' % e(x["text"]))
        kap = x.get("kapitel")
        if kap in umfang:
            n = umfang[kap]
            z.append('      <a class="pfeil-link pfeil-link--klein" href="#archiv-%s">%s im Archiv%s</a>'
                     % (kap, "Ein Bild" if n == 1 else "%d Bilder" % n, PFEIL))
        z.append('    </div>')
        z.append('  </li>')
    z.append('</ol>')
    return "\n".join(z)


def _artefakt_html(s):
    datei = s["datei"]
    breite, hoehe = bildmass(ZIEL / "assets/img/archiv" / datei)
    bild = ('<img src="assets/img/archiv/%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async">'
            % (datei, e(s["alt"], quote=True), breite, hoehe))
    kern = bild if s.get("klein") else '<a href="assets/img/archiv/%s" data-lupe>%s</a>' % (datei, bild)
    if s["art"] == "streifen":
        kern = ('<div class="streifen" tabindex="0" role="group" aria-label="Filmstreifen, seitlich scrollbar">'
                '%s</div>' % kern)
    legende = e(s["text"]) if s["text"] else ""
    if s.get("nachweis"):
        legende += ' <span class="nachweis">Bild: %s</span>' % e(s["nachweis"])
    return ('<figure class="artefakt artefakt--%s%s">%s%s</figure>'
            % (s["art"], " ist-klein" if s.get("klein") else "", kern,
               "<figcaption>%s</figcaption>" % legende if legende else ""))


def archiv_html():
    z = []
    for k in ARCHIV:
        z.append('<section class="archivkapitel" id="archiv-%s">' % k["id"])
        z.append('  <header class="archivkapitel__kopf"><h3>%s</h3><p>%s</p></header>'
                 % (e(k["titel"]), e(k["lead"])))
        z.append('  <div class="archivkapitel__stuecke">')
        z += ['    ' + _artefakt_html(s) for s in k["stuecke"]]
        z.append('  </div>')
        z.append('</section>')
    return "\n".join(z)


def meistertitel_html():
    z = ['<div class="titel">']
    for r in MEISTERTITEL:
        jahre = "".join('<li>%d</li>' % j for j in r["jahre"])
        z.append('  <div class="titel__reihe"><p class="titel__zahl">%d</p><div><h3>%s</h3><p>%s</p>'
                 '<ul class="titel__jahre">%s</ul></div></div>'
                 % (len(r["jahre"]), e(r["wer"]), e(r["text"]), jahre))
    z.append('</div>')
    return "\n".join(z)


# --- Dokumente --------------------------------------------------------------

def _dokument_fehlt(x):
    return not (ZIEL / DOKUMENTORDNER / x["datei"]).exists()


def dokumente_html(eintraege):
    z = ['<ul class="dokumente">']
    for x in eintraege:
        typ = x["datei"].rsplit(".", 1)[-1].upper()
        if _dokument_fehlt(x):
            z.append('  <li><span class="dokument ist-offen"><b>%s</b><span>%s</span><em>folgt</em></span></li>'
                     % (e(x["name"]), e(x["info"])))
        else:
            z.append('  <li><a class="dokument" href="%s/%s" download><b>%s</b><span>%s</span>'
                     '<em>%s · %s</em></a></li>'
                     % (DOKUMENTORDNER, e(x["datei"]), e(x["name"]), e(x["info"]), typ,
                        groesse(ZIEL / DOKUMENTORDNER / x["datei"])))
    z.append('</ul>')
    return "\n".join(z)


# --- Strukturdaten (JSON-LD) ------------------------------------------------
#
# Ein Block je Seite im <head>: wer der Verein ist, wo er trainiert, wo die
# Seite in der Website steht. Google zeigt daraus Brotkrumen statt Adresse,
# die Hallen auf der Karte und den Verein im Wissensfeld rechts.

SEITENTYP = {
    "kontakt.html": "ContactPage",
    "verein.html": "AboutPage",
    "verein-geschichte.html": "AboutPage",
    "news.html": "CollectionPage",
}


def _adresse(strasse, plz, ort, kanton="SH"):
    a = {"@type": "PostalAddress"}
    if strasse:
        a["streetAddress"] = strasse
    a.update({"postalCode": plz, "addressLocality": ort, "addressRegion": kanton, "addressCountry": "CH"})
    return a


def _brotkrumen(seite, url, letzter=None):
    """Die sichtbare Brotkrumen-Navigation der Seite als BreadcrumbList."""
    m = re.search(r'<nav class="brotkrumen"[^>]*>(.*?)</nav>', seite, re.S)
    if not m:
        return None
    stufen = re.findall(r'<(a|span)\b([^>]*)>(.*?)</\1>', m.group(1), re.S)
    punkte = []
    for i, (tag, attribute, name) in enumerate(stufen, 1):
        ziel = url
        if tag == "a":
            href = re.search(r'href="([^"]*)"', attribute).group(1)
            ziel = BASIS_URL + ("" if href == "index.html" else href)
        name = html.unescape(re.sub(r"<[^>]+>", "", name)).replace("­", "").strip()
        if i == len(stufen) and letzter:
            name = letzter
        punkte.append({"@type": "ListItem", "position": i, "name": name, "item": ziel})
    return {"@type": "BreadcrumbList", "@id": url + "#brotkrumen", "itemListElement": punkte}


def strukturdaten(datei, titel, beschreibung, url, seite, beitrag=None):
    verein_id, website_id = BASIS_URL + "#verein", BASIS_URL + "#website"
    orte = {}
    for schluessel, o in HALLENORTE.items():
        adresse = BASIS_URL + HALLEN[schluessel]["seite"]
        orte[HALLEN[schluessel]["seite"]] = {
            "@type": "SportsActivityLocation",
            "@id": adresse + "#ort",
            "name": o["name"],
            "alternateName": o["auch"],
            "url": adresse,
            "address": _adresse(o["strasse"], o["plz"], o["ort"]),
            "geo": {"@type": "GeoCoordinates", "latitude": o["geo"][0], "longitude": o["geo"][1]},
        }
    breite, hoehe = bildmass(ZIEL / VEREIN["logo"])
    verband, verband_url = VEREIN["verband"]
    knoten = [{
        "@type": "SportsClub",
        "@id": verein_id,
        "name": VEREIN["name"],
        "alternateName": VEREIN["kurzname"],
        "description": VEREIN["beschreibung"],
        "url": BASIS_URL,
        "logo": {"@type": "ImageObject", "url": BASIS_URL + VEREIN["logo"], "width": breite, "height": hoehe},
        "image": OG_BILD,
        "sport": "Tischtennis",
        "foundingDate": VEREIN["gruendung"],
        "email": VEREIN["email"],
        "address": _adresse(None, VEREIN["plz"], VEREIN["ort"], VEREIN["kanton"]),
        "location": [{"@id": o["@id"]} for o in orte.values()],
        "areaServed": VEREIN["einzugsgebiet"],
        "memberOf": {"@type": "SportsOrganization", "name": verband, "url": verband_url},
        "sameAs": VEREIN["profile"] + [VEREINSSEITEN["uebersicht"]],
    }]
    knoten += orte.values()
    knoten.append({
        "@type": "WebSite",
        "@id": website_id,
        "url": BASIS_URL,
        "name": "TTC Neuhausen",
        "alternateName": VEREIN["name"],
        "inLanguage": "de-CH",
        "publisher": {"@id": verein_id},
    })
    webseite = {
        "@type": SEITENTYP.get(datei, "WebPage"),
        "@id": url + "#seite",
        "url": url,
        "name": titel,
        "description": beschreibung,
        "inLanguage": "de-CH",
        "isPartOf": {"@id": website_id},
        "about": {"@id": orte[datei]["@id"] if datei in orte else verein_id},
    }
    knoten.append(webseite)
    krumen = _brotkrumen(seite, url, beitrag and (beitrag.get("kurztitel") or beitrag["titel"]))
    if krumen:
        webseite["breadcrumb"] = {"@id": krumen["@id"]}
        knoten.append(krumen)
    if beitrag:
        knoten.append({
            "@type": "NewsArticle",
            "@id": url + "#beitrag",
            "headline": beitrag["titel"][:110],
            "datePublished": beitrag["datum"],
            "inLanguage": "de-CH",
            "mainEntityOfPage": {"@id": url + "#seite"},
            "image": [BASIS_URL + urllib.parse.quote(beitrag["bild"]) if beitrag["bild"] else OG_BILD],
            "author": ({"@type": "Person", "name": beitrag["autor"]} if beitrag["autor"]
                       else {"@id": verein_id}),
            "publisher": {"@id": verein_id},
        })
    daten = json.dumps({"@context": "https://schema.org", "@graph": knoten}, ensure_ascii=False, indent=1)
    return '<script type="application/ld+json">\n%s\n</script>' % daten.replace("</", "<\\/")


def ab_wurzel(seite):
    """Relative Verweise ab der Wurzel setzen. Die Fehlerseite wird unter
    jeder Adresse ausgeliefert, auch unter /2018/02/22/beitrag/ – dort
    zeigte «assets/css/base.css» ins Leere."""
    return re.sub(r'(\s(?:src|href)=")(?![a-z][a-z0-9+.-]*:|/|#)', r"\g<1>" + WURZELPFAD, seite)


# --- Zusammensetzen ---------------------------------------------------------

def warnhinweis(quelle):
    return ("<!-- Erzeugt von build.py – nicht hier ändern.\n"
            "     Inhalt: %s · Rahmen: vorlage/layout.html · Menü: vorlage/seiten.py\n"
            "     Bilder und Dokumente unter site/assets/ werden nicht erzeugt:\n"
            "     Datei mit gleichem Namen ersetzen genügt. -->\n" % quelle)


def ersetzungen():
    n, tage, stunden = trainingsumfang()
    feste = {
        "{{anmeldeformular}}": ANMELDEFORMULAR,
        "{{bildnachweis}}": e(NACHWEIS),
        "{{sponsorenzahl}}": str(len(SPONSOREN)),
        "{{mannschaftszahl}}": str(mannschaftszahl()),
        "{{saison}}": e(SAISON),
        "{{einheiten}}": str(n),
        "{{trainingstage}}": str(tage),
        "{{zeitleistenzahl}}": ZAHLWORTE.get(len(ZEITLEISTE), str(len(ZEITLEISTE))),
        "{{jahr}}": str(date.today().year),
        "{{vereinsalter}}": str(date.today().year - 1975),
        "{{basisurl}}": BASIS_URL,
        "{{robots}}": ROBOTS_META,
    }
    for name, adresse in VEREINSSEITEN.items():
        feste["{{clicktt:%s}}" % name] = adresse
    erzeugt = {
        "{{wochenplan}}": wochenplan_html,
        "{{woche_kurz}}": woche_kurz_html,
        "{{trainingsdaten}}": trainingsdaten_json,
        "{{mannschaften}}": mannschaften_html,
        "{{sponsoren}}": sponsoren_html,
        "{{ausruester}}": ausruester_html,
        "{{zeitleiste}}": zeitleiste_html,
        "{{archiv}}": archiv_html,
        "{{meistertitel}}": meistertitel_html,
        "{{news_start}}": news_start_html,
        "{{aktuell}}": aktuell_html,
        "{{newsliste}}": newsliste_html,
        "{{termine}}": termine_html,
        "{{dokumente}}": lambda: dokumente_html(DOKUMENTE),
        "{{beitrittsformulare}}": lambda: dokumente_html(BEITRITTSFORMULARE),
        "{{hallenprojekt}}": lambda: dokumente_html(HALLENPROJEKT),
    }
    return feste, erzeugt


def main():
    layout = (VORLAGE / "layout.html").read_text(encoding="utf-8")
    signet = (ZIEL / "assets/img/signet.svg").read_text(encoding="utf-8").strip()
    signet = signet.replace("<svg ", '<svg class="kopf__signet" aria-hidden="true" focusable="false" ', 1)
    signet = re.sub(r'\s(role|aria-label)="[^"]*"', "", signet, count=2)
    signet = re.sub(r"<title>.*?</title>", "", signet)
    if "--bilder-verkleinern" in sys.argv:
        bilder_aufbereiten()
    feste, erzeugt = ersetzungen()
    gebaut, fehlend = [], []

    def schreibe(datei, titel, beschreibung, rubrik, inhalt, quelle, beitrag=None):
        seite = layout.replace("{{inhalt}}", inhalt)
        for platzhalter, fn in erzeugt.items():
            if platzhalter in seite:
                seite = seite.replace(platzhalter, fn())
        seite = re.sub(r"\{\{zeiten:([^}]+)\}\}", lambda m: zeiten_html(m.group(1)), seite)
        seite = re.sub(r"\{\{kurzzeiten:([^}]+)\}\}", lambda m: kurzzeiten_html(m.group(1)), seite)
        seite = re.sub(r"\{\{trainer:([^}]+)\}\}", lambda m: trainer_zeiten_html(m.group(1)), seite)
        if datei == FEHLERSEITE:
            seite = seite.replace("{{robots}}", ROBOTS_NOINDEX)
        for platzhalter, wert in feste.items():
            seite = seite.replace(platzhalter, wert)
        url = BASIS_URL + ("" if datei == "index.html" else datei)
        og_bild, og_breite, og_hoehe, og_alt = teilbild(beitrag)
        seite = (seite.replace("{{ogbild}}", e(og_bild, quote=True))
                 .replace("{{ogbild_breite}}", str(og_breite))
                 .replace("{{ogbild_hoehe}}", str(og_hoehe))
                 .replace("{{ogbild_alt}}", e(og_alt, quote=True))
                 .replace("{{titel}}", e(titel))
                 .replace("{{beschreibung}}", e(beschreibung))
                 .replace("{{navigation}}", navigation_html(datei, rubrik))
                 .replace("{{signet}}", signet)
                 .replace("{{seitenname}}", datei[:-5])
                 .replace("{{url}}", url)
                 .replace("{{ogtyp}}", "article" if beitrag else "website")
                 .replace("{{artikel}}", '\n<meta property="article:published_time" content="%s">'
                          % beitrag["datum"] if beitrag else ""))
        if datei == FEHLERSEITE:
            seite = re.sub(r'\n<link rel="canonical"[^>]*>', "", seite.replace("{{strukturdaten}}", ""))
            seite = ab_wurzel(seite)
        else:
            seite = seite.replace("{{strukturdaten}}",
                                  strukturdaten(datei, titel, beschreibung, url, seite, beitrag))
        rest = re.findall(r"\{\{[^}]+\}\}", seite)
        if rest:
            sys.exit("%s: unbekannte Platzhalter %s" % (datei, ", ".join(sorted(set(rest)))))
        kopf, umbruch, rumpf = seite.partition("\n")
        (ZIEL / datei).write_text(kopf + umbruch + warnhinweis(quelle) + rumpf, encoding="utf-8")
        gebaut.append(datei)

    for datei, (titel, beschreibung, rubrik) in SEITEN.items():
        quelle = INHALT / datei
        if not quelle.exists():
            fehlend.append(datei)
            continue
        schreibe(datei, titel, beschreibung, rubrik, quelle.read_text(encoding="utf-8"), "inhalt/" + datei)

    ohne_text = []
    for b in BEITRAEGE:
        if not _hat_seite(b):
            ohne_text.append(b)
            continue
        schreibe(news_datei(b), "%s – TTC Neuhausen" % (b["kurztitel"] or b["titel"]),
                 (b["anriss"] or b["titel"])[:155], "News", beitrag_html(b),
                 "redaktion/news/%s.json" % b["kennung"], beitrag=b)

    for alt in ZIEL.glob("news-*.html"):
        if alt.name not in gebaut:
            alt.unlink()

    print("Gebaut: %d Seiten" % len(gebaut))
    if fehlend:
        print("Fehlende Fragmente in inhalt/: " + ", ".join(sorted(fehlend)))
    verwaist = sorted(p.name for p in INHALT.glob("*.html") if p.name not in SEITEN)
    if verwaist:
        print("Nicht in seiten.py eingetragen: " + ", ".join(verwaist))
    print("News: %d Beiträge, %d mit eigener Seite" % (len(BEITRAEGE), len(BEITRAEGE) - len(ohne_text))
          + (", %d nur als Meldung (ohne Text, nicht klickbar)" % len(ohne_text) if ohne_text else ""))
    print("Redaktion: %d Bilder und %d Dokumente aus redaktion/ übernommen."
          % (ABLAGE_ZAHL["bilder"], ABLAGE_ZAHL["dokumente"]))

    schreibe_serverdateien(gebaut)
    schreibe_redaktion()
    pruefe_farben()
    pruefe_verweise(gebaut)
    pruefe_weiterleitungen()
    schreibe_powershell()
    melde_dokumente()
    n, tage, stunden = trainingsumfang()
    print("Trainingsplan: %d Einheiten an %d Tagen, %s Stunden pro Woche."
          % (n, tage, ("%.2f" % stunden).rstrip("0").rstrip(".")))
    if VORSCHAU_URL:
        print("VORSCHAU für %s – noindex, robots.txt gesperrt." % BASIS_URL)


def schreibe_serverdateien(gebaut):
    (ZIEL / ".nojekyll").write_text("", encoding="utf-8")
    if VORSCHAU_URL:
        (ZIEL / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
        (ZIEL / "sitemap.xml").unlink(missing_ok=True)
        (ZIEL / ".htaccess").unlink(missing_ok=True)
        return
    (ZIEL / "robots.txt").write_text("User-agent: *\nAllow: /\nDisallow: /admin/\n\nSitemap: %ssitemap.xml\n"
                                     % SEITE_URL, encoding="utf-8")
    z = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    z += ["  <url><loc>%s</loc></url>" % e(BASIS_URL + ("" if d == "index.html" else d))
          for d in sorted(gebaut) if d != FEHLERSEITE]
    z.append("</urlset>\n")
    (ZIEL / "sitemap.xml").write_text("\n".join(z), encoding="utf-8")
    (ZIEL / ".htaccess").write_text(htaccess(), encoding="utf-8", newline="\n")


def schreibe_redaktion():
    """site/admin/config.yml aus vorlage/redaktion.yml. Die Adresse der Website
    kommt aus seiten.py – auch in der Vorschau, denn angemeldet wird immer
    auf dem echten Server (admin/anmelden.php braucht PHP)."""
    teile = urllib.parse.urlsplit(SEITE_URL)
    text = ((VORLAGE / "redaktion.yml").read_text(encoding="utf-8")
            .replace("{{seite_url}}", SEITE_URL.rstrip("/"))
            .replace("{{herkunft}}", "%s://%s" % (teile.scheme, teile.netloc)))
    rest = re.findall(r"\{\{(?:seite_url|herkunft)\}\}", text)
    if rest:
        sys.exit("vorlage/redaktion.yml: Platzhalter übrig: " + ", ".join(rest))
    (ZIEL / "admin").mkdir(exist_ok=True)
    (ZIEL / "admin/config.yml").write_text(
        "# ERZEUGT VON build.py aus vorlage/redaktion.yml – dort ändern, dann bauen.\n\n" + text,
        encoding="utf-8", newline="\n")


def _alte_adresse(pfad):
    """Alte Adresse als Muster für RewriteRule: genau diese, mit oder ohne / am Ende."""
    return "^%s/?$" % re.escape(pfad.strip("/"))


def htaccess():
    """site/.htaccess für Apache – der Server der bisherigen Website ist einer.

    Nur Anweisungen, die WordPress selbst schon braucht (mod_rewrite und
    Verwandte, AllowOverride FileInfo). «Options» oder «Expires» würden auf
    manchem Hosting die ganze Website mit Fehler 500 lahmlegen."""
    teile = urllib.parse.urlsplit(SEITE_URL)
    host = teile.hostname
    ohne_www = host[4:] if host.startswith("www.") else None
    basis = "https://" + host
    w = WURZELPFAD

    def ziel(seite):
        """Absolut mit https und www: eine einzige Weiterleitung, auch wenn der
        Server hinter einem Proxy selbst nur http sieht."""
        return basis + w + seite

    z = [
        "# .htaccess – ERZEUGT VON build.py, nicht von Hand ändern.",
        "# Weiterleitungen: vorlage/seo.py. Danach einmal build.py.",
        "#",
        "# Gehört in denselben Ordner wie index.html. Beim Hochladen per FTP",
        "# mitnehmen: viele Programme blenden Dateien mit Punkt vorne aus.",
        "",
        "ErrorDocument 404 %s%s" % (w, FEHLERSEITE),
        "ErrorDocument 410 %s%s" % (w, FEHLERSEITE),
        "AddDefaultCharset utf-8",
        "AddType font/woff2 .woff2",
        "AddType image/webp .webp",
        "AddType text/yaml .yml",
        "",
        "<IfModule mod_rewrite.c>",
        "RewriteEngine On",
        "",
        "# Die Fehlerseite, die Apache nach 404 oder 410 intern nachlädt, nicht",
        "# anfassen – sonst wird aus «410 Gone» eine Weiterleitung auf 404.html.",
        "RewriteCond %{ENV:REDIRECT_STATUS} ^[45][0-9][0-9]$",
        "RewriteRule ^ - [L]",
        "",
        "# Nie ausliefern: die Zugangsdaten der Redaktions-Anmeldung und den",
        "# Upload-Stand. Beide legt veroeffentlichen.py auf dem Server an.",
        "RewriteRule ^(admin/zugang\\.php|\\.veroeffentlicht\\.json)$ - [F,L]",
        "",
        "# PHP läuft nur in der Anmeldung der Redaktion. Jede andere solche Datei",
        "# wird nicht ausgeführt und nicht ausgeliefert, wo immer sie liegt.",
        "RewriteCond %{REQUEST_URI} \\.(php[0-9]?|phtml|phar|pht|cgi|pl|py|sh)(\\.|/|$) [NC]",
        "RewriteRule !^admin/anmelden\\.php$ - [F,L]",
        "",
        "# Alte Adressen stehen vor der Regel für https und www: ihr Ziel ist",
        "# schon absolut, so kommt jede in einem Schritt an.",
        "",
        "# Ordner ohne index.html nicht auflisten",
        "RewriteCond %{REQUEST_FILENAME} -d",
        "RewriteCond %{REQUEST_FILENAME}/index.html !-f",
        "RewriteRule ^ - [R=404,L]",
        "",
        "# --- Vorlagen des alten Themes und WordPress-Technik: 410 Gone",
        "RewriteRule ^(%s)/?$ - [G,L]" % "|".join(re.escape(p) for p in WEG),
    ]
    z += ["RewriteRule %s - [G,L]" % m for m in WEG_MUSTER]
    z += [
        "",
        "# --- Alte Kurzadressen von WordPress (?p=123, ?page_id=45, Suche)",
        "RewriteCond %{QUERY_STRING} (^|&)(p|cat|tag|m|author)=",
        "RewriteRule ^$ %s? [R=301,L]" % ziel("news.html"),
        "RewriteCond %{QUERY_STRING} (^|&)(page_id|s)=",
        "RewriteRule ^$ %s? [R=301,L]" % ziel(""),
        "",
        "# --- Dokumente der alten Website (vorlage/dokumente.py)",
    ]
    # Fehlt eine Datei noch, auf die Seite, die sie auflistet.
    for liste, seite in ((DOKUMENTE + BEITRITTSFORMULARE, "verein-downloads.html"),
                         (HALLENPROJEKT, "hallen-neue-halle.html")):
        for x in liste:
            alt = urllib.parse.urlsplit(x.get("herkunft", ""))
            if alt.hostname not in (host, ohne_www):
                continue
            neu = seite if _dokument_fehlt(x) else "%s/%s" % (DOKUMENTORDNER, x["datei"])
            z.append("RewriteRule ^%s$ %s [R=301,L]"
                     % (re.escape(urllib.parse.unquote(alt.path).lstrip("/")), ziel(neu)))
    z += ["", "# --- Seiten der alten Website (vorlage/seo.py)"]
    for alt, neu in WEITERLEITUNGEN.items():
        z.append("RewriteRule %s %s [R=301,L,NE,NC]" % (_alte_adresse(alt), ziel(neu)))
    z += ["", "# --- Ganze Bereiche: Beiträge, Archive, Anlässe"]
    for muster, neu in MUSTER:
        if NEWS_ARCHIV and neu == "news.html":
            z.append("RewriteRule %s %s%%{REQUEST_URI} [R=301,L,NE]" % (muster, NEWS_ARCHIV.rstrip("/")))
        else:
            z.append("RewriteRule %s %s [R=301,L]" % (muster, ziel(neu)))
    z += ["", "# --- Eine einzige Adresse: %s/" % basis]
    if ohne_www:
        z += ["RewriteCond %%{HTTP_HOST} ^%s$ [NC]" % re.escape(ohne_www),
              "RewriteRule ^ %s%%{REQUEST_URI} [R=301,L,NE]" % basis]
    z += [
        "RewriteCond %{HTTPS} !=on",
        "RewriteCond %{HTTP:X-Forwarded-Proto} !https",
        "RewriteCond %%{HTTP_HOST} ^%s$ [NC]" % re.escape(host),
        "RewriteRule ^ %s%%{REQUEST_URI} [R=301,L,NE]" % basis,
        "",
        "# index.html nicht als zweite Adresse der Startseite",
        "RewriteCond %{THE_REQUEST} ^[A-Z]+\\s[^?\\s]*/index\\.html[?\\s]",
        "RewriteRule ^(.*/)?index\\.html$ %s$1 [R=301,L]" % ziel(""),
        "",
        "# --- /training statt /training.html",
        "RewriteCond %{DOCUMENT_ROOT}/$1.html -f",
        "RewriteRule ^([a-z0-9-]+)/?$ %s$1.html [R=301,L]" % ziel(""),
        "",
        "# Browser fragen von sich aus nach /favicon.ico",
        "RewriteRule ^favicon\\.ico$ %s%s [L]" % (w, VEREIN["logo"]),   # intern, keine Weiterleitung
        "</IfModule>",
        "",
        "# --- Schneller laden: Google misst die Ladezeit mit",
        "<IfModule mod_deflate.c>",
        "  AddOutputFilterByType DEFLATE text/html text/css text/plain text/xml application/xml",
        "  AddOutputFilterByType DEFLATE application/javascript text/javascript application/json",
        "  AddOutputFilterByType DEFLATE application/ld+json image/svg+xml",
        "</IfModule>",
        "",
        "<IfModule mod_headers.c>",
        "  # Seiten, CSS, JavaScript und die Felder der Redaktion jedes Mal nachfragen",
        "  # (304, wenn unverändert), damit nach einem neuen Build niemand alte Teile sieht.",
        '  <FilesMatch "\\.(html|css|js|xml|txt|yml)$">',
        '    Header set Cache-Control "no-cache"',
        "  </FilesMatch>",
        "  # Bilder werden unter gleichem Namen ersetzt – eine Woche.",
        '  <FilesMatch "\\.(jpe?g|png|webp|svg|gif|ico)$">',
        '    Header set Cache-Control "public, max-age=604800"',
        "  </FilesMatch>",
        '  <FilesMatch "\\.woff2$">',
        '    Header set Cache-Control "public, max-age=31536000, immutable"',
        "  </FilesMatch>",
        '  <FilesMatch "\\.(pdf|docx|xlsx)$">',
        '    Header set Cache-Control "public, max-age=86400"',
        "  </FilesMatch>",
        '  Header always set X-Content-Type-Options "nosniff"',
        '  Header always set Referrer-Policy "strict-origin-when-cross-origin"',
        "</IfModule>",
        "",
    ]
    return "\n".join(z)


# --- Prüfungen --------------------------------------------------------------

def pruefe_farben():
    """Hex-Farben nur in tokens.css."""
    treffer = []
    for datei in sorted((ZIEL / "assets/css").glob("*.css")):
        if datei.name == "tokens.css":
            continue
        text = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)),
                      datei.read_text(encoding="utf-8"), flags=re.S)
        for nr, zeile in enumerate(text.splitlines(), 1):
            for wert in re.findall(r"(?<![%\w])#[0-9A-Fa-f]{3,8}\b", zeile):
                treffer.append("  %s:%d %s" % (datei.name, nr, wert))
    print(("Farben ausserhalb von tokens.css:\n" + "\n".join(treffer)) if treffer
          else "Farben: nur aus tokens.css.")


def pruefe_verweise(gebaut):
    """Dateien, Seiten und Sprungmarken, auf die verwiesen wird, müssen existieren."""
    ids = {}
    for d in gebaut:
        ids[d] = set(re.findall(r'\sid="([^"]+)"', (ZIEL / d).read_text(encoding="utf-8")))
    probleme = set()
    for d in gebaut:
        text = (ZIEL / d).read_text(encoding="utf-8")
        for attr, ziel in re.findall(r'\s(src|href|srcset)="([^"]+)"', text):
            # Nur srcset ist eine Liste; eine Adresse darf Kommas enthalten (Google Maps).
            for teil in (ziel.split(",") if attr == "srcset" else [ziel]):
                pfad = teil.strip().split(" ")[0]
                if not pfad or re.match(r"^(https?:|mailto:|tel:|data:|//)", pfad):
                    continue
                if pfad.startswith(WURZELPFAD):          # ab der Wurzel (Fehlerseite)
                    pfad = pfad[len(WURZELPFAD):] or "index.html"
                datei, _, anker = pfad.partition("#")
                datei = datei.split("?")[0] or d
                if datei.endswith(".html"):
                    if datei not in ids:
                        probleme.add("%s → %s" % (d, pfad))
                    elif anker and anker not in ids[datei]:
                        probleme.add("%s → %s (Sprungmarke fehlt)" % (d, pfad))
                elif not (ZIEL / datei).exists():
                    probleme.add("%s → %s" % (d, datei))
    print(("Verweise ins Leere:\n  " + "\n  ".join(sorted(probleme))) if probleme
          else "Verweise: alle Seiten, Dateien und Sprungmarken vorhanden.")


def pruefe_weiterleitungen():
    """Jede alte Adresse muss auf eine Seite und Sprungmarke zeigen, die es gibt."""
    probleme = []
    for alt, neu in list(WEITERLEITUNGEN.items()) + MUSTER:
        datei, _, anker = neu.partition("#")
        if not datei.endswith(".html"):
            continue
        if not (ZIEL / datei).exists():
            probleme.append("%s → %s" % (alt, neu))
        elif anker and ('id="%s"' % anker) not in (ZIEL / datei).read_text(encoding="utf-8"):
            probleme.append("%s → %s (Sprungmarke fehlt)" % (alt, neu))
    doppelt = sorted(set(WEITERLEITUNGEN) & set(WEG))
    if doppelt:
        probleme.append("in WEITERLEITUNGEN und WEG zugleich: " + ", ".join(doppelt))
    if probleme:
        print("Weiterleitungen ins Leere (vorlage/seo.py):\n  " + "\n  ".join(probleme))
    else:
        print("Weiterleitungen: %d alte Seiten, %d Bereiche, %d mit 410 Gone – alle Ziele vorhanden."
              % (len(WEITERLEITUNGEN), len(MUSTER), len(WEG) + len(WEG_MUSTER)))


def schreibe_powershell():
    """Erzeugt hol-dokumente.ps1 aus derselben Liste wie alles andere.

    hol-dokumente.py braucht Python, das auf Windows nicht von Haus aus da
    ist – PowerShell schon. Erzeugt statt abgetippt, damit die beiden Listen
    nicht auseinanderlaufen. Mit Byte-Order-Mark, sonst zeigt Windows
    PowerShell 5.1 die Umlaute als Buchstabensalat.
    """
    z = [
        "# hol-dokumente.ps1 — holt die Vereinsdokumente von der bisherigen",
        "# Website nach site\\assets\\dokumente\\.",
        "#",
        "# ERZEUGT VON build.py — nicht von Hand ändern. Die Liste steht in",
        "# vorlage/dokumente.py; nach einer Änderung dort einmal build.py.",
        "#",
        "# Starten: hol-dokumente.bat doppelklicken. Oder in PowerShell:",
        "#   powershell -ExecutionPolicy Bypass -File .\\hol-dokumente.ps1",
        "",
        "$ErrorActionPreference = 'Stop'",
        "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12",
        "$ProgressPreference = 'SilentlyContinue'   # sonst ist es zehnmal langsamer",
        "",
        "$ziel = Join-Path $PSScriptRoot 'site\\assets\\dokumente'",
        "New-Item -ItemType Directory -Force -Path $ziel | Out-Null",
        "",
        "$dateien = @(",
    ]
    for x in ALLE_DOKUMENTE:
        if not x.get("herkunft"):      # gab es auf der alten Website nie
            continue
        z.append("  @{ name = '%s'; url = '%s' }" % (x["datei"], x["herkunft"].replace("'", "''")))
    z += [
        ")",
        "",
        "Write-Host \"Vereinsdokumente nach site\\assets\\dokumente\\\"",
        "Write-Host \"$($dateien.Count) Dateien`n\"",
        "",
        "$gut = 0",
        "foreach ($d in $dateien) {",
        "  $pfad = Join-Path $ziel $d.name",
        "  if (Test-Path $pfad) {",
        "    Write-Host ('  schon da   ' + $d.name)",
        "    $gut++",
        "    continue",
        "  }",
        "  $temp = [System.IO.Path]::GetTempFileName()",
        "  try {",
        "    Invoke-WebRequest -Uri $d.url -OutFile $temp -UseBasicParsing -TimeoutSec 60",
        "  } catch {",
        "    Write-Host ('  FEHLER     ' + $d.name + ' - ' + $_.Exception.Message) -ForegroundColor Red",
        "    Remove-Item $temp -ErrorAction SilentlyContinue",
        "    continue",
        "  }",
        "  # Eine Fehlerseite ist auch eine Antwort. Wer eine 2-kB-",
        "  # «Seite nicht gefunden» als Statuten ablegt, merkt es erst,",
        "  # wenn jemand sie oeffnet.",
        "  $bytes = [System.IO.File]::ReadAllBytes($temp)",
        "  $kopf = if ($bytes.Length -ge 4) { [System.Text.Encoding]::ASCII.GetString($bytes[0..3]) } else { '' }",
        "  if ($bytes.Length -lt 4096 -and $kopf -ne '%PDF' -and $kopf.Substring(0,[Math]::Min(2,$kopf.Length)) -ne 'PK') {",
        "    Write-Host ('  VERDAECHTIG ' + $d.name + ' - nur ' + $bytes.Length + ' Bytes, sieht nicht nach einem Dokument aus. Nicht gespeichert.') -ForegroundColor Yellow",
        "    Remove-Item $temp -ErrorAction SilentlyContinue",
        "    continue",
        "  }",
        "  Move-Item $temp $pfad -Force",
        "  Write-Host ('  geholt     ' + $d.name.PadRight(38) + ('{0,6:N1}' -f ($bytes.Length / 1024)) + ' kB')",
        "  $gut++",
        "}",
        "",
        "Write-Host \"`n$gut von $($dateien.Count) bereit.\"",
        "if ($gut -lt $dateien.Count) {",
        "  Write-Host 'Die fehlenden bitte von Hand holen - die Adressen stehen bei'",
        "  Write-Host 'jedem Eintrag in vorlage/dokumente.py unter herkunft.'",
        "}",
        "Write-Host ''",
        "Read-Host 'Mit Enter schliessen'",
        "",
    ]
    (WURZEL / "hol-dokumente.ps1").write_text("\n".join(z), encoding="utf-8-sig", newline="\r\n")


def melde_dokumente():
    """Sagt, welche Dateien noch fehlen – und wo sie zu holen sind."""
    fehlend = [x for x in ALLE_DOKUMENTE if _dokument_fehlt(x)]
    if not fehlend:
        print("Dokumente: alle %d vorhanden." % len(ALLE_DOKUMENTE))
        return
    print("Dokumente: %d von %d fehlen unter site/%s/ und stehen so lange als «folgt» da."
          % (len(fehlend), len(ALLE_DOKUMENTE), DOKUMENTORDNER))
    print("  Holen: auf Windows hol-dokumente.bat doppelklicken, sonst «python3 hol-dokumente.py».")
    for x in fehlend:
        print("  %-40s ← %s" % (x["datei"], x.get("herkunft") or "von Hand ablegen"))


if __name__ == "__main__":
    main()
