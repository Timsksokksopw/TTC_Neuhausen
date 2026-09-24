#!/usr/bin/env python3
"""Baut die Website: vorlage/layout.html + inhalt/*.html + Daten aus vorlage/*.py → site/

    python3 build.py                      echte Website
    python3 build.py --vorschau <Adresse> Vorschau (noindex, robots gesperrt)

Bearbeitet werden inhalt/ und vorlage/. site/*.html wird bei jedem Lauf neu
geschrieben; Bilder, Schriften und Dokumente unter site/assets/ nicht.
"""

import html
import json
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
from news import AUF_STARTSEITE, BEITRAEGE  # noqa: E402
from dokumente import ANMELDEFORMULAR, BEITRITTSFORMULARE, DOKUMENTE, HALLENPROJEKT  # noqa: E402
from termine import TERMINE  # noqa: E402

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
OG_BILD = BASIS_URL + "assets/img/og-standard.jpg"
ROBOTS_META = '\n<meta name="robots" content="noindex, nofollow">' if VORSCHAU_URL else ""


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
    """(Breite, Höhe) eines JPEG oder PNG, ohne Pillow."""
    with open(pfad, "rb") as f:
        kopf = f.read(26)
        if kopf[:8] == b"\x89PNG\r\n\x1a\n":
            return int.from_bytes(kopf[16:20], "big"), int.from_bytes(kopf[20:24], "big")
        if kopf[:2] != b"\xff\xd8":
            raise ValueError("Weder JPEG noch PNG: %s" % pfad)
        f.seek(2)
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
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                f.read(1)
                hoehe = int.from_bytes(f.read(2), "big")
                breite = int.from_bytes(f.read(2), "big")
                return breite, hoehe
            f.seek(laenge - 2, 1)


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

def news_datei(b):
    return "news-%s.html" % b["kennung"]


def _hat_text(b):
    return bool(b.get("absaetze"))


def _herkunft(b):
    teile = []
    if b.get("text"):
        teile.append("Text: " + b["text"])
    if b.get("bildnachweis"):
        teile.append("Bild: " + b["bildnachweis"])
    return " · ".join(teile)


def _news_neueste():
    return sorted(BEITRAEGE, key=lambda b: b["datum"], reverse=True)


def _newseintrag(b, klasse="meldung", kurz=True, mit_bild=False):
    titel = b.get("kurztitel") if kurz and b.get("kurztitel") else b["titel"]
    tag_a = ('<a class="%s" href="%s">' % (klasse, news_datei(b))) if _hat_text(b) \
        else '<article class="%s">' % klasse
    z = [tag_a]
    if mit_bild and b.get("bild"):
        breite, hoehe = bildmass(ZIEL / "assets/img/fotos" / b["bild"])
        z.append('  <div class="%s__bild"><img src="assets/img/fotos/%s" alt="%s" width="%d" height="%d" '
                 'loading="lazy" decoding="async"></div>' % (klasse, e(b["bild"]), e(b.get("bildalt", ""), quote=True),
                                                            breite, hoehe))
    z.append('  <time datetime="%s">%s</time>' % (b["datum"], datum_lang(b["datum"])))
    z.append('  <h3>%s</h3>' % e(titel))
    if b.get("anriss"):
        z.append('  <p>%s</p>' % e(b["anriss"]))
    if _herkunft(b):
        z.append('  <p class="%s__herkunft">%s</p>' % (klasse, e(_herkunft(b))))
    if _hat_text(b):
        z.append('  <span class="pfeil-link">Weiterlesen%s</span>' % PFEIL)
    z.append('</a>' if _hat_text(b) else '</article>')
    return "\n".join(z)


def news_start_html():
    """Startseite: der neueste Beitrag mit Bild gross, daneben die Liste."""
    neu = _news_neueste()
    gross = next((b for b in neu if b.get("bild")), neu[0])
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
    ziel = news_datei(b) if _hat_text(b) else "news.html"
    return ('<a class="aktuell__news" href="%s"><span class="aktuell__marke">Aktuell</span>'
            '<time datetime="%s">%s</time><span class="aktuell__titel">%s</span>%s</a>'
            % (ziel, b["datum"], datum_lang(b["datum"]), e(b.get("kurztitel") or b["titel"]), PFEIL))


def newsliste_html():
    neu = _news_neueste()
    z = ['<div class="newsliste">']
    jahr = None
    for b in neu:
        j = b["datum"][:4]
        if j != jahr:
            z.append('<h2 class="newsliste__jahr">%s</h2>' % j)
            jahr = j
        z.append(_newseintrag(b, "newseintrag", kurz=False, mit_bild=bool(b.get("bild"))))
    z.append('</div>')
    return "\n".join(z)


def _absatz_html(s):
    if isinstance(s, str):
        return '<p>%s</p>' % e(s)
    art = s.get("art")
    if art == "titel":
        return '<h2>%s</h2>' % e(s["text"])
    if art == "zitat":
        wer = '<cite>%s</cite>' % e(s["wer"]) if s.get("wer") else ""
        return '<blockquote class="zitat"><p>%s</p>%s</blockquote>' % (e(s["text"]), wer)
    if art == "liste":
        punkte = "".join("<li>%s</li>" % e(p) for p in s["punkte"])
        titel = '<h3>%s</h3>' % e(s["titel"]) if s.get("titel") else ""
        return '<div class="rangliste">%s<ol>%s</ol></div>' % (titel, punkte)
    sys.exit("news.py: unbekannte Absatzart «%s» (erlaubt: titel, zitat, liste)" % art)


def beitrag_html(b):
    bild = ""
    if b.get("bild"):
        breite, hoehe = bildmass(ZIEL / "assets/img/fotos" / b["bild"])
        bild = ('<figure class="bild bild--breit"><img src="assets/img/fotos/%s" alt="%s" width="%d" height="%d">'
                '<figcaption><span class="nachweis">%s</span></figcaption></figure>'
                % (e(b["bild"]), e(b.get("bildalt", ""), quote=True), breite, hoehe, e(_herkunft(b))))
    absaetze = "\n".join(_absatz_html(s) for s in b["absaetze"])
    return """<header class="aufmacher aufmacher--schmal">
  <div class="wrap">
    <nav class="brotkrumen" aria-label="Brotkrumen"><a href="index.html">Start</a><a href="news.html">News</a><span aria-current="page">Beitrag</span></nav>
    <p class="rubrik"><time datetime="%s">%s</time></p>
    <h1 class="h1--mittel">%s</h1>
  </div>
</header>
<section class="flaeche--papier eng">
  <div class="wrap">%s
    <div class="text beitrag">
%s
    </div>
    <p><a class="pfeil-link" href="news.html">Alle Beiträge%s</a></p>
  </div>
</section>""" % (b["datum"], datum_lang(b["datum"]), e(b["titel"]), bild, absaetze, PFEIL)


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
        "{{ogbild}}": OG_BILD,
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
    feste, erzeugt = ersetzungen()
    gebaut, fehlend = [], []

    def schreibe(datei, titel, beschreibung, rubrik, inhalt, quelle):
        seite = layout.replace("{{inhalt}}", inhalt)
        for platzhalter, fn in erzeugt.items():
            if platzhalter in seite:
                seite = seite.replace(platzhalter, fn())
        seite = re.sub(r"\{\{zeiten:([^}]+)\}\}", lambda m: zeiten_html(m.group(1)), seite)
        seite = re.sub(r"\{\{kurzzeiten:([^}]+)\}\}", lambda m: kurzzeiten_html(m.group(1)), seite)
        seite = re.sub(r"\{\{trainer:([^}]+)\}\}", lambda m: trainer_zeiten_html(m.group(1)), seite)
        for platzhalter, wert in feste.items():
            seite = seite.replace(platzhalter, wert)
        seite = (seite.replace("{{titel}}", e(titel))
                 .replace("{{beschreibung}}", e(beschreibung))
                 .replace("{{navigation}}", navigation_html(datei, rubrik))
                 .replace("{{signet}}", signet)
                 .replace("{{seitenname}}", datei[:-5])
                 .replace("{{url}}", BASIS_URL + ("" if datei == "index.html" else datei)))
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
        if not _hat_text(b):
            ohne_text.append(b)
            continue
        schreibe(news_datei(b), "%s – TTC Neuhausen" % (b.get("kurztitel") or b["titel"]),
                 b["titel"][:155], "News", beitrag_html(b), "vorlage/news.py (%s)" % b["kennung"])

    for alt in ZIEL.glob("news-*.html"):
        if alt.name not in gebaut:
            alt.unlink()

    print("Gebaut: %d Seiten" % len(gebaut))
    if fehlend:
        print("Fehlende Fragmente in inhalt/: " + ", ".join(sorted(fehlend)))
    verwaist = sorted(p.name for p in INHALT.glob("*.html") if p.name not in SEITEN)
    if verwaist:
        print("Nicht in seiten.py eingetragen: " + ", ".join(verwaist))
    if ohne_text:
        print("News ohne Fliesstext (stehen als Meldung, nicht klickbar): %d" % len(ohne_text))

    schreibe_serverdateien(gebaut)
    pruefe_farben()
    pruefe_verweise(gebaut)
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
        return
    (ZIEL / "robots.txt").write_text("User-agent: *\nAllow: /\n\nSitemap: %ssitemap.xml\n" % SEITE_URL,
                                     encoding="utf-8")
    z = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    z += ["  <url><loc>%s</loc></url>" % e(BASIS_URL + ("" if d == "index.html" else d)) for d in sorted(gebaut)]
    z.append("</urlset>\n")
    (ZIEL / "sitemap.xml").write_text("\n".join(z), encoding="utf-8")


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
        print("  %-40s ← %s" % (x["datei"], x["herkunft"]))


if __name__ == "__main__":
    main()
