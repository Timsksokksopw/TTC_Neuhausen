#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — setzt die Website zusammen.

    python3 build.py

Liest vorlage/layout.html und die Fragmente aus inhalt/, fügt Navigation,
Kopf- und Fusszeile ein und schreibt fertige HTML-Dateien nach site/.

Der Grund für diesen Schritt: Kopfzeile, Navigation und Fuss stehen genau
einmal im Projekt. Ohne ihn müsste jede Menüänderung in allen Seiten
nachgezogen werden — die häufigste Fehlerquelle in statischen Prototypen.

Beim Übertrag nach WordPress werden aus layout.html header.php und
footer.php, aus den Fragmenten in inhalt/ die Seiteninhalte.
"""

import html
import re
import sys
import urllib.parse
from pathlib import Path

WURZEL = Path(__file__).resolve().parent
sys.path.insert(0, str(WURZEL / "vorlage"))

from seiten import NAVIGATION, SEITEN, SEITE_URL  # noqa: E402
from trainingszeiten import (  # noqa: E402
    ANGEBOTE, EINHEITEN, HALLEN, RASTER_BAENDER, TAGE)
from mannschaften import (  # noqa: E402
    MANNSCHAFTEN, SAISON, VEREINSSEITEN, WETTBEWERBE)

INHALT = WURZEL / "inhalt"
VORLAGE = WURZEL / "vorlage"
ZIEL = WURZEL / "site"

def _vorschau_adresse():
    """Liest `--vorschau <Adresse>` von der Kommandozeile.

    Eine Vorschau liegt unter einer anderen Adresse als die spätere
    Website. Bleibt SEITE_URL stehen, zeigt `canonical` auf das Original
    und `og:image` auf eine Datei, die es dort noch nicht gibt — der Link
    hat dann in WhatsApp und Instagram keine Vorschau.

    Gibt None zurück, wenn ohne Schalter gebaut wird.
    """
    if "--vorschau" not in sys.argv:
        return None
    stelle = sys.argv.index("--vorschau")
    if stelle + 1 >= len(sys.argv) or sys.argv[stelle + 1].startswith("-"):
        sys.exit("Fehler: --vorschau braucht die Adresse, unter der die "
                 "Vorschau liegt.\n"
                 "  python3 build.py --vorschau https://name.github.io/repo/")
    adresse = sys.argv[stelle + 1]
    return adresse if adresse.endswith("/") else adresse + "/"


VORSCHAU_URL = _vorschau_adresse()
IST_VORSCHAU = VORSCHAU_URL is not None
BASIS_URL = VORSCHAU_URL or SEITE_URL

OG_BILD = BASIS_URL + "assets/img/og-standard.jpg"

# Eine öffentlich erreichbare Vorschau soll nicht bei Google landen —
# sonst konkurriert ein Entwurf der Vereinsseite mit der echten.
ROBOTS_META = ('\n<meta name="robots" content="noindex, nofollow">'
               if IST_VORSCHAU else "")


def _minuten(hhmm):
    """'18:30' → 1110. Ein Wert, mit dem sich rechnen lässt."""
    stunde, minute = hhmm.split(":")
    return int(stunde) * 60 + int(minute)


def _achse():
    """Baut die Zeitachse aus RASTER_BAENDER.

    Jede Viertelstunde eines Bandes ist eine Rasterspalte, zwischen zwei
    Bändern steht eine schmale Bruchspalte. Gibt zurück:

        linie     Minuten seit Mitternacht → Rasterlinie
        vorlage   der Wert für grid-template-columns
        marken    [(Spalte, "08"), ...] für die Zeitleiste
        brueche   Spaltennummern der Bruchspalten
    """
    linie, teile, marken, brueche = {}, [], [], []
    spalte = 1

    for i, (von, bis) in enumerate(RASTER_BAENDER):
        if i:
            brueche.append(spalte)
            teile.append("var(--bruch)")
            spalte += 1

        viertel = (_minuten(bis) - _minuten(von)) // 15
        teile.append("repeat(%d, 1fr)" % viertel)

        for k in range(viertel + 1):
            minute = _minuten(von) + k * 15
            linie[minute] = spalte + k
            # Volle Stunden bekommen eine Marke, die Bandkante nicht:
            # dort ist entweder der Bruch oder der Rand des Rasters.
            if minute % 60 == 0 and k < viertel:
                marken.append((spalte + k, "%02d" % (minute // 60)))

        spalte += viertel

    return linie, " ".join(teile), marken, brueche


ACHSE_LINIE, ACHSE_VORLAGE, ACHSE_MARKEN, ACHSE_BRUECHE = _achse()


def _spalte(hhmm):
    """Zeit → Rasterlinie. Meldet Zeiten, die in keinem Band liegen."""
    minute = _minuten(hhmm)
    if minute not in ACHSE_LINIE:
        raise ValueError(
            "%s liegt in keinem Band von RASTER_BAENDER — Band erweitern "
            "oder Zeit auf eine Viertelstunde runden." % hhmm)
    return ACHSE_LINIE[minute]


def _bahnen_zuteilen(einheiten):
    """Verteilt überlappende Einheiten eines Tages auf Bahnen übereinander.

    Am Dienstag, Donnerstag und Freitag überschneiden sich Nachwuchs- und
    Breitensporttraining um eine halbe Stunde. In einer Tabelle fällt das
    nicht auf, im Raster würden die Blöcke sonst übereinanderliegen.

    Verfahren: Einheiten nach Beginn sortieren und jede in die erste Bahn
    legen, die zu diesem Zeitpunkt frei ist. Gibt die Anzahl benötigter
    Bahnen zurück.
    """
    bahn_frei_ab = []
    for e in sorted(einheiten, key=lambda x: (_minuten(x["von"]), _minuten(x["bis"]))):
        beginn, ende = _minuten(e["von"]), _minuten(e["bis"])
        for i, frei_ab in enumerate(bahn_frei_ab):
            if frei_ab <= beginn:
                e["bahn"] = i + 1
                bahn_frei_ab[i] = ende
                break
        else:
            bahn_frei_ab.append(ende)
            e["bahn"] = len(bahn_frei_ab)
    return max(len(bahn_frei_ab), 1)


def _zeitspanne(e):
    return "%s – %s" % (e["von"], e["bis"])


def trainingsraster_html():
    """Baut Wochenraster und Tabelle aus trainingszeiten.EINHEITEN."""
    z = []
    nach_tag = {kurz: [dict(e) for e in EINHEITEN if e["tag"] == kurz]
                for kurz, _ in TAGE}

    # --- Steuerung: Filter und Legende --------------------------------------
    z.append('<div class="woche" data-filter="alle" style="--spalten:%s">'
             % ACHSE_VORLAGE)
    z.append('  <div class="woche__steuerung">')
    z.append('    <div class="filter" role="group" aria-label="Wochenplan nach Angebot filtern">')
    z.append('      <button class="filter__knopf" type="button" data-zeigt="alle"'
             ' aria-pressed="true">Alle</button>')
    for schluessel, angebot in ANGEBOTE.items():
        z.append('      <button class="filter__knopf" type="button" data-zeigt="%s"'
                 ' aria-pressed="false">%s</button>'
                 % (schluessel, html.escape(angebot["name"])))
    z.append('    </div>')

    z.append('    <ul class="legende">')
    for schluessel, halle in HALLEN.items():
        z.append('      <li><span class="legende__probe legende__probe--%s"></span>%s</li>'
                 % (schluessel, html.escape(halle["name"])))
    z.append('    </ul>')
    z.append('  </div>')

    # --- Das Raster ----------------------------------------------------------
    def stundenlinien():
        """Die senkrechten Stundenlinien und die Bruchmarkierung.

        Als Elemente statt als Hintergrundverlauf: die Spalten sind seit
        der Bandaufteilung nicht mehr gleich breit, ein sich
        wiederholender Verlauf träfe die Stunden nicht mehr.
        """
        teile = ['          <div class="stundenlinien" aria-hidden="true">']
        for spalte, _ in ACHSE_MARKEN:
            teile.append('            <i style="--pos:%d"></i>' % spalte)
        for spalte in ACHSE_BRUECHE:
            teile.append('            <i class="bruch" style="--pos:%d"></i>' % spalte)
        teile.append('          </div>')
        return teile

    z.append('  <div class="woche__rollen">')
    z.append('    <div class="woche__innen">')
    z.append('      <div class="skala" aria-hidden="true">')
    z.append('        <div class="skala__spur">')
    for spalte, beschriftung in ACHSE_MARKEN:
        z.append('          <span class="skala__marke" style="--pos:%d">%s</span>'
                 % (spalte, beschriftung))
    for spalte in ACHSE_BRUECHE:
        z.append('          <span class="skala__bruch" style="--pos:%d">···</span>' % spalte)
    z.append('        </div>')
    z.append('      </div>')

    leere_tage = []
    for kurz, lang in TAGE:
        einheiten = nach_tag[kurz]
        if not einheiten:
            leere_tage.append(lang)
            z.append('      <section class="wochentag wochentag--leer">')
            z.append('        <h3 class="wochentag__name">%s</h3>' % html.escape(lang))
            z.append('        <div class="wochentag__flaeche"><p class="wochentag__frei">Kein Training</p></div>')
            z.append('      </section>')
            continue

        anzahl_bahnen = _bahnen_zuteilen(einheiten)
        z.append('      <section class="wochentag" style="--bahnen:%d">' % anzahl_bahnen)
        z.append('        <h3 class="wochentag__name">%s</h3>' % html.escape(lang))
        z.append('        <div class="wochentag__flaeche">')
        z.extend(stundenlinien())
        for e in sorted(einheiten, key=lambda x: _minuten(x["von"])):
            halle = HALLEN[e["halle"]]
            angebot = ANGEBOTE[e["angebot"]]
            z.append(
                '          <a class="einheit einheit--%s" href="%s" data-angebot="%s"\n'
                '             style="--von:%d;--bis:%d;--bahn:%d">'
                % (e["halle"], angebot["seite"], e["angebot"],
                   _spalte(e["von"]), _spalte(e["bis"]), e["bahn"]))
            # Im Block die Kurzform, wo es eine gibt — in den Tabellen
            # steht weiterhin die volle Bezeichnung des Vereins.
            z.append('            <span class="einheit__gruppe">%s</span>'
                     % html.escape(e.get("kurz") or e["gruppe"]))
            z.append('            <span class="einheit__zeit">%s</span>'
                     % html.escape(_zeitspanne(e)))
            z.append('            <span class="einheit__halle">%s</span>'
                     % html.escape(halle["name"]))
            z.append('          </a>')
        z.append('        </div>')
        z.append('      </section>')
    z.append('    </div>')
    z.append('  </div>')

    z.append('  <p class="woche__stand" role="status" aria-live="polite"></p>')

    if leere_tage:
        z.append('  <p class="woche__fussnote">Am %s ist kein Training angesetzt. '
                 'Die Hallen stehen Mitgliedern mit Hallenbeitrag trotzdem offen.</p>'
                 % " und ".join(leere_tage))

    # --- Notizen je Angebot --------------------------------------------------
    z.append('  <ul class="notizen">')
    for schluessel, angebot in ANGEBOTE.items():
        z.append('    <li><b>%s</b> %s</li>'
                 % (html.escape(angebot["name"]), angebot["notiz"]))
    z.append('  </ul>')

    # --- Vollständige Tabelle ------------------------------------------------
    # Das Raster zeigt Zeit, Gruppe und Halle. Für die Trainerangaben fehlt
    # im Block der Platz, und wer lieber liest als schaut, bekommt hier
    # dieselben Daten in Zeilenform — auch für Vorlesesoftware und Druck.
    z.append('  <details class="volltabelle">')
    z.append('    <summary>Alle Angaben als Tabelle, mit Trainerinnen und Trainern</summary>')
    z.append('    <div class="tabelle-huelle">')
    z.append('      <table class="daten">')
    z.append('        <thead><tr><th>Tag</th><th>Zeit</th><th>Angebot</th>'
             '<th>Gruppe</th><th>Halle</th><th>Trainer</th></tr></thead>')
    z.append('        <tbody>')
    for kurz, lang in TAGE:
        for e in sorted(nach_tag[kurz], key=lambda x: _minuten(x["von"])):
            z.append('          <tr><td class="tag">%s</td><td class="zeit">%s</td>'
                     '<td>%s</td><td>%s</td><td><span class="halle halle--%s">%s</span></td>'
                     '<td>%s</td></tr>'
                     % (html.escape(lang), html.escape(_zeitspanne(e)),
                        html.escape(ANGEBOTE[e["angebot"]]["name"]),
                        html.escape(e["gruppe"]), e["halle"],
                        html.escape(HALLEN[e["halle"]]["name"]),
                        html.escape(e["trainer"]) or "—"))
    z.append('        </tbody>')
    z.append('      </table>')
    z.append('    </div>')
    z.append('  </details>')
    z.append('</div>')

    return "\n".join(z)


def _tabellen_url(m):
    """Die click-tt-Adresse der Ligatabelle einer Mannschaft.

    Die Kodierung ist heikel und geprüft: nuLiga erwartet das Leerzeichen
    im Saisonkürzel als «+» und den Schrägstrich als «%2F» — genau so,
    wie click-tt seine Adressen selbst schreibt. Mit «%20» statt «+»
    öffnet die Seite eine *andere* Liga, ohne Fehlermeldung. Deshalb
    quote_plus und nicht quote.

    Das kaufmännische Und wird fürs HTML-Attribut maskiert, sonst liest
    der Browser «&group» als angefangene Zeichenreferenz.
    """
    kennung = urllib.parse.quote_plus(m["championship"])
    return ("https://www.click-tt.ch/cgi-bin/WebObjects/nuLigaTTCH.woa/wa/"
            "groupPage?championship=%s&amp;group=%d" % (kennung, m["gruppe_id"]))


def mannschaften_html():
    """Die Mannschaftsübersicht mit Direktlinks auf die Ligatabellen.

    Jede Zeile führt auf die offizielle Tabelle bei click-tt. Die Zahlen
    dort sind immer aktuell, weil sie von dort kommen — auf der eigenen
    Seite steht nichts, was veralten könnte.
    """
    z = ['<div class="teams">']

    for schluessel, titel, untertitel in WETTBEWERBE:
        gruppe = [m for m in MANNSCHAFTEN if m["wettbewerb"] == schluessel]
        if not gruppe:
            continue

        z.append('  <section class="teamgruppe">')
        z.append('    <h3 class="teamgruppe__titel">%s</h3>' % html.escape(titel))
        z.append('    <p class="teamgruppe__unter">%s</p>' % html.escape(untertitel))
        z.append('    <ul class="teamliste">')
        for m in gruppe:
            z.append(
                '      <li><a class="team" href="%s" target="_blank" rel="noopener">'
                % _tabellen_url(m))
            z.append('        <span class="team__name">%s</span>' % html.escape(m["name"]))
            z.append('        <span class="team__liga">%s</span>' % html.escape(m["liga"]))
            z.append('        <span class="team__ziel">Tabelle</span>')
            z.append('      </a></li>')
        z.append('    </ul>')
        z.append('  </section>')

    z.append('</div>')
    return "\n".join(z)


def zeitentabelle_html(angebot_schluessel):
    """Die Zeiten eines einzelnen Angebots als Tabelle.

    Steht auf den Unterseiten training-nachwuchs, -breitensport und
    -senioren. Vorher waren das abgetippte Kopien der Zeiten von der
    Übersichtsseite — wer dort eine Zeit änderte, liess die Unterseite
    veralten. Jetzt kommen beide aus trainingszeiten.py.
    """
    reihenfolge = {kurz: i for i, (kurz, _) in enumerate(TAGE)}
    lang_name = dict(TAGE)
    passend = sorted(
        (e for e in EINHEITEN if e["angebot"] == angebot_schluessel),
        key=lambda e: (reihenfolge[e["tag"]], _minuten(e["von"])))

    z = ['<div class="tabelle-huelle"><table class="daten">',
         '  <thead><tr><th>Tag</th><th>Zeit</th><th>Halle</th><th>Gruppe</th></tr></thead>',
         '  <tbody>']

    voriger_tag = None
    for e in passend:
        # Wiederholter Tagesname bleibt leer — die Spalte liest sich ruhiger.
        tag = "" if e["tag"] == voriger_tag else html.escape(lang_name[e["tag"]])
        voriger_tag = e["tag"]
        halle = HALLEN[e["halle"]]
        z.append('    <tr><td class="tag">%s</td><td class="zeit">%s</td>'
                 '<td><span class="halle halle--%s">%s</span></td><td>%s</td></tr>'
                 % (tag, html.escape(_zeitspanne(e)), e["halle"],
                    html.escape(halle["name"]), html.escape(e["gruppe"])))

    z.append('  </tbody>')
    z.append('</table></div>')
    return "\n".join(z)


def navigation_html(aktuelle_datei, aktuelle_rubrik):
    """Baut die Menüliste und markiert den aktiven Punkt."""
    zeilen = []
    for titel, ziel, unterseiten in NAVIGATION:
        aktiv = (aktuelle_rubrik == titel)
        klasse = "nav__punkt nav__punkt--aktiv" if aktiv else "nav__punkt"
        aria = ' aria-current="page"' if ziel == aktuelle_datei else ""

        zeilen.append('        <li class="%s">' % klasse)
        zeilen.append('          <a class="nav__link" href="%s"%s>%s</a>'
                      % (ziel, aria, html.escape(titel)))

        if unterseiten:
            zeilen.append('          <ul class="nav__unter">')
            for u_titel, u_ziel in unterseiten:
                u_aria = ' aria-current="page"' if u_ziel == aktuelle_datei else ""
                zeilen.append('            <li><a href="%s"%s>%s</a></li>'
                              % (u_ziel, u_aria, html.escape(u_titel)))
            zeilen.append('          </ul>')

        zeilen.append('        </li>')
    return "\n".join(zeilen)


def main():
    layout = (VORLAGE / "layout.html").read_text(encoding="utf-8")
    signet = (ZIEL / "assets/img/signet.svg").read_text(encoding="utf-8")
    logo = (ZIEL / "assets/img/logo.svg").read_text(encoding="utf-8")

    # Die SVG-Wurzel bekommt eine Klasse, damit die Höhe per CSS steuerbar ist.
    signet = signet.replace("<svg ", '<svg aria-hidden="true" focusable="false" ', 1)
    logo = logo.replace("<svg ", '<svg aria-hidden="true" focusable="false" ', 1)

    gebaut, fehlend = [], []

    for datei, (titel, beschreibung, rubrik) in SEITEN.items():
        quelle = INHALT / datei
        if not quelle.exists():
            fehlend.append(datei)
            continue

        seite = layout
        seite = seite.replace("{{titel}}", html.escape(titel))
        seite = seite.replace("{{beschreibung}}", html.escape(beschreibung))
        seite = seite.replace("{{navigation}}", navigation_html(datei, rubrik))
        seite = seite.replace("{{signet}}", signet)
        seite = seite.replace("{{logo}}", logo)
        seite = seite.replace("{{inhalt}}", quelle.read_text(encoding="utf-8"))
        # Nach {{inhalt}}, damit auch Platzhalter in den Fragmenten greifen.
        if "{{trainingsraster}}" in seite:
            seite = seite.replace("{{trainingsraster}}", trainingsraster_html())
        if "{{mannschaften}}" in seite:
            seite = seite.replace("{{mannschaften}}", mannschaften_html())
        seite = seite.replace("{{saison}}", html.escape(SAISON))
        for name, adresse in VEREINSSEITEN.items():
            seite = seite.replace("{{clicktt:%s}}" % name, adresse)
        seite = re.sub(r"\{\{zeiten:([a-z]+)\}\}",
                       lambda m: zeitentabelle_html(m.group(1)), seite)
        seite = seite.replace("{{url}}", BASIS_URL + ("" if datei == "index.html" else datei))
        seite = seite.replace("{{basisurl}}", BASIS_URL)
        seite = seite.replace("{{ogbild}}", OG_BILD)
        seite = seite.replace("{{robots}}", ROBOTS_META)
        seite = seite.replace("{{basis}}", "")   # flache Struktur, alles im selben Ordner

        (ZIEL / datei).write_text(seite, encoding="utf-8")
        gebaut.append(datei)

    print("Gebaut: %d Seiten" % len(gebaut))
    for d in sorted(gebaut):
        print("  " + d)
    if fehlend:
        print("\nFehlende Fragmente in inhalt/ (%d):" % len(fehlend))
        for d in sorted(fehlend):
            print("  " + d)

    # Verwaiste Fragmente melden: Datei vorhanden, aber nicht in seiten.py eingetragen.
    verwaist = [p.name for p in INHALT.glob("*.html") if p.name not in SEITEN]
    if verwaist:
        print("\nNicht in seiten.py eingetragen (%d):" % len(verwaist))
        for d in sorted(verwaist):
            print("  " + d)

    schreibe_serverdateien()
    pruefe_farben()
    pruefe_dateien(gebaut)
    melde_trainingsumfang()

    if IST_VORSCHAU:
        print("\nVORSCHAU-FASSUNG für %s" % BASIS_URL)
        print("  Alle Seiten tragen noindex, robots.txt sperrt Suchmaschinen aus.")
        print("  Für die echte Website ohne --vorschau neu bauen.")


def schreibe_serverdateien():
    """Legt die zwei Dateien an, die der Server erwartet.

    .nojekyll — GitHub Pages schickt Seiten sonst durch Jekyll und
    überspringt dabei alles, was mit einem Unterstrich beginnt. Wir haben
    solche Dateien zwar nicht, aber die Datei kostet nichts und macht das
    Verhalten unabhängig davon, was später dazukommt.

    robots.txt — wird bei jedem Lauf neu geschrieben, passend zum Modus.
    Sonst bliebe nach einer Vorschau ein «Disallow» stehen und die echte
    Website wäre für Google gesperrt.
    """
    (ZIEL / ".nojekyll").write_text("", encoding="utf-8")

    if IST_VORSCHAU:
        robots = ("# Vorschau-Fassung, nicht die Website des Vereins.\n"
                  "User-agent: *\nDisallow: /\n")
    else:
        robots = ("User-agent: *\nAllow: /\n\nSitemap: %ssitemap.xml\n"
                  % SEITE_URL)
    (ZIEL / "robots.txt").write_text(robots, encoding="utf-8")


def melde_trainingsumfang():
    """Rechnet zusammen, wie viele geleitete Stunden die Woche hat.

    Die Startseite und verein.html nennen eine Zahl Trainingsstunden. Die
    steht dort von Hand und veraltet still, sobald sich der Plan ändert.
    Hier steht sie nach jedem Bauen daneben, damit die Abweichung auffällt.
    """
    stunden = sum(_minuten(e["bis"]) - _minuten(e["von"]) for e in EINHEITEN) / 60
    tage = len({e["tag"] for e in EINHEITEN})
    print("Trainingsplan: %d Einheiten an %d Tagen, %.2g geleitete Stunden pro Woche."
          % (len(EINHEITEN), tage, stunden))


def pruefe_farben():
    """Kein Farbwert ausserhalb von tokens.css.

    Sonst driftet die Palette: irgendwann steht ein handgemischtes Blau im
    Stylesheet, und die Umstellung einer Farbe wirkt nicht mehr überall.
    Durchsichtigkeit über rgba() und color-mix() ist erlaubt — die leitet
    sich von einem bestehenden Wert ab und erfindet keinen neuen.
    """
    hexwert = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
    treffer = []

    def ohne_kommentare(text):
        """Leert /* ... */ aus, auch über mehrere Zeilen, behält aber die
        Zeilenumbrüche — sonst stimmen die gemeldeten Zeilennummern nicht.
        Nötig, weil in den Kommentaren begründet steht, welche Farbwerte
        wie geprüft wurden; das sind Belege, keine Verwendungen."""
        return re.sub(r"/\*.*?\*/",
                      lambda m: re.sub(r"[^\n]", " ", m.group(0)),
                      text, flags=re.S)

    for datei in sorted((ZIEL / "assets/css").glob("*.css")):
        if datei.name == "tokens.css":
            continue
        text = ohne_kommentare(datei.read_text(encoding="utf-8"))
        for nr, zeile in enumerate(text.splitlines(), 1):
            for wert in hexwert.findall(zeile):
                treffer.append("  %s:%d  %s" % (datei.name, nr, wert))

    if treffer:
        print("\nFarbwerte ausserhalb von tokens.css (%d):" % len(treffer))
        print("\n".join(treffer))
    else:
        print("\nFarben: alle Werte stammen aus tokens.css.")


def pruefe_dateien(gebaut):
    """Meldet verlinkte Bilder und Dateien, die es nicht gibt.

    Fängt den häufigsten Fehler nach einem Bildwechsel ab: Dateiname im
    HTML geändert, Datei aber anders benannt abgelegt. Im Browser sieht man
    das erst, wenn man die betroffene Stelle wirklich aufruft.
    """
    verweis = re.compile(r'(?:src|href)="(assets/[^"#?]+)"')
    fehlend = set()

    for datei in gebaut:
        text = (ZIEL / datei).read_text(encoding="utf-8")
        for pfad in verweis.findall(text):
            if not (ZIEL / pfad).exists():
                fehlend.add(pfad)

    if fehlend:
        print("\nVerlinkt, aber nicht vorhanden (%d):" % len(fehlend))
        for pfad in sorted(fehlend):
            print("  " + pfad)
    else:
        print("Dateien: alle verlinkten Bilder und Stylesheets sind vorhanden.")


if __name__ == "__main__":
    main()
