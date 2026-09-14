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
from sponsoren import AUSRUESTER, SPONSOREN  # noqa: E402
from geschichte import (  # noqa: E402
    ARCHIV, MEISTERTITEL, NACHWEIS, ZEITLEISTE)
from news import AUF_STARTSEITE, BEITRAEGE  # noqa: E402
from dokumente import (  # noqa: E402
    ANMELDEFORMULAR, BEITRITTSFORMULARE, DOKUMENTE)

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


def sponsoren_html():
    """Das Kachelraster der Partner.

    Solange kein Logo hinterlegt ist, trägt die Kachel den Firmennamen.
    Sobald in sponsoren.py ein Dateiname steht, zeigt sie das Logo — das
    Raster bleibt gleich, es muss nichts umgebaut werden.
    """
    z = ['<div class="sponsoren">']
    for s in SPONSOREN:
        # Alle aufbereiteten Logos haben dieselbe Leinwand, deshalb stehen
        # width und height fest — so springt beim Nachladen nichts.
        inhalt = ('<img src="assets/img/partner/%s" alt="%s" '
                  'width="480" height="300" loading="lazy" decoding="async">'
                  % (s["logo"], html.escape(s["name"], quote=True))) if s["logo"] \
                 else html.escape(s["name"])
        if s["url"]:
            z.append('  <a class="sponsor" href="%s" target="_blank" rel="noopener">%s</a>'
                     % (html.escape(s["url"], quote=True), inhalt))
        else:
            z.append('  <div class="sponsor">%s</div>' % inhalt)
    z.append("</div>")
    return "\n".join(z)


def ausruester_html():
    """Der Ausrüster als eigenes Band über dem Raster."""
    a = AUSRUESTER
    marke = ('<img src="assets/img/partner/%s" alt="%s" loading="lazy">'
             % (a["logo"], html.escape(a["name"]))) if a["logo"] \
            else html.escape(a["name"])
    ziel = a["url"]
    return "\n".join([
        '<div class="ausruester">',
        '  <p class="ausruester__rolle label">%s</p>' % html.escape(a["rolle"]),
        '  <p class="ausruester__name">%s</p>' % marke,
        '  <p class="ausruester__text">%s</p>' % html.escape(a["text"]),
        ('  <a class="btn btn--klein" href="%s" target="_blank" rel="noopener">Zum Shop</a>'
         % html.escape(ziel, quote=True)) if ziel else "",
        '</div>'])


def _bildmass(pfad):
    """Breite und Höhe eines JPEG oder PNG, ohne Fremdbibliothek.

    Die Masse gehören als width/height ins <img>, sonst springt das Layout
    beim Nachladen. Sie im Datenfile von Hand zu pflegen hiesse, sie beim
    nächsten Zuschnitt zu vergessen — deshalb liest der Build sie direkt
    aus der Datei. Für PNG steht das Mass fix im IHDR, bei JPEG muss man
    sich bis zum SOF-Segment durchhangeln.
    """
    with open(pfad, "rb") as f:
        kopf = f.read(26)
        if kopf[:8] == b"\x89PNG\r\n\x1a\n":
            return (int.from_bytes(kopf[16:20], "big"),
                    int.from_bytes(kopf[20:24], "big"))
        if kopf[:2] != b"\xff\xd8":
            raise ValueError("Weder JPEG noch PNG: %s" % pfad)
        f.seek(2)
        while True:
            byte = f.read(1)
            while byte and byte != b"\xff":       # bis zum nächsten Marker
                byte = f.read(1)
            while byte == b"\xff":                # Füllbytes überspringen
                byte = f.read(1)
            if not byte:
                raise ValueError("Kein SOF-Segment in %s" % pfad)
            marker = byte[0]
            laenge = int.from_bytes(f.read(2), "big")
            # SOF0..SOF15, ohne DHT (C4), DNL (C8) und DAC (CC)
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                f.read(1)                          # Genauigkeit
                hoehe = int.from_bytes(f.read(2), "big")
                breite = int.from_bytes(f.read(2), "big")
                return (breite, hoehe)
            f.seek(laenge - 2, 1)


_ZAHLWORTE = {
    1: "einer", 2: "zwei", 3: "drei", 4: "vier", 5: "fünf", 6: "sechs",
    7: "sieben", 8: "acht", 9: "neun", 10: "zehn", 11: "elf", 12: "zwölf",
}


def _zahlwort(n):
    """Kleine Zahlen ausgeschrieben, grosse als Ziffern.

    «Fünfzig Jahre in acht Stationen» las sich gut, war aber nach dem
    ersten neuen Eintrag falsch. Ausgerechnet statt abgetippt — und weil
    im Fliesstext eine Ziffer hart wirkt, hier als Wort.
    """
    return _ZAHLWORTE.get(n, str(n))


def auftaktbilder():
    """Zählt die Bilder der Auftaktsfolge und prüft sie auf Lücken.

    Die Folge muss `bild-01.webp` bis `bild-NN.webp` lückenlos enthalten:
    das Skript rechnet den Dateinamen aus dem Bildindex aus, ein fehlendes
    Bild wäre also ein Loch mitten in der Fahrt. Beim Bauen fällt das auf,
    im Browser erst beim Scrollen — und auch dann nur dem, der genau
    hinschaut.
    """
    ordner = ZIEL / "assets" / "img" / "auftakt"
    da = sorted(p.stem for p in ordner.glob("bild-*.webp"))
    if not da:
        return 0
    nummern = sorted(int(n.split("-")[1]) for n in da)
    erwartet = list(range(1, len(nummern) + 1))
    if nummern != erwartet:
        fehlend = sorted(set(erwartet) - set(nummern))
        sys.exit("Fehler: Die Auftaktsfolge hat Lücken. Es fehlen: %s"
                 % ", ".join("bild-%02d.webp" % n for n in fehlend))
    return len(nummern)


AUFTAKT_BILDER = auftaktbilder()


def zeitleiste_html():
    """Die Zeitleiste der Vereinsgeschichte.

    Einträge, zu denen Archivmaterial vorliegt, bekommen einen Sprung ins
    entsprechende Kapitel. Die Zahl der Bilder zählt der Build selbst —
    sie wäre sonst das nächste, was beim Nachlegen eines Fotos veraltet.
    """
    umfang = {k["id"]: len(k["stuecke"]) for k in ARCHIV}

    z = ['<ol class="zeitleiste">']
    for e in ZEITLEISTE:
        z.append('  <li>')
        z.append('    <b>%s</b>' % html.escape(e["jahr"]))
        z.append('    <div>')
        z.append('      <h3>%s</h3>' % html.escape(e["titel"]))
        z.append('      <p>%s</p>' % html.escape(e["text"]))
        kap = e.get("kapitel", "")
        if kap and kap in umfang:
            # Nur die Zahl, nicht der Kapiteltitel: «12 Bilder: Die Halle,
            # die der Verein selbst gebaut hat» in Versalien war eine Zeile,
            # die lauter war als der Eintrag, zu dem sie gehört.
            wieviele = umfang[kap]
            z.append('      <a class="zeitleiste__spur" href="#archiv-%s">%s'
                     ' im Archiv</a>'
                     % (kap, "Ein Bild" if wieviele == 1
                        else "%d Bilder" % wieviele))
        z.append('    </div>')
        z.append('  </li>')
    z.append('</ol>')
    return "\n".join(z)


def _artefakt_html(s):
    """Ein einzelnes Stück aus dem Archiv.

    Die drei Formen unterscheiden sich nur in der Hülle, nicht im Kern:
    aussen immer <figure> mit Bildlegende, innen immer dasselbe Bild.

    Ohne JavaScript ist die Vergrösserung ein gewöhnlicher Link auf die
    Bilddatei — der Browser zeigt sie dann eben allein an. Das Skript
    macht daraus ein Overlay. Stücke mit `klein` bekommen gar keinen
    Link: eine 150 Pixel breite Vorlage bildschirmfüllend zu zeigen,
    macht sie nicht besser.
    """
    datei = s["datei"]
    pfad = ZIEL / "assets" / "img" / "archiv" / datei
    breite, hoehe = _bildmass(pfad)

    bild = ('<img src="assets/img/archiv/%s" alt="%s" '
            'width="%d" height="%d" loading="lazy" decoding="async">'
            % (datei, html.escape(s["alt"], quote=True), breite, hoehe))

    if s.get("klein"):
        kern = '<span class="artefakt__flaeche">%s</span>' % bild
    else:
        kern = ('<a class="artefakt__flaeche" href="assets/img/archiv/%s" '
                'data-lupe>%s</a>' % (datei, bild))

    if s["art"] == "streifen":
        # Eigenes Scrollfenster: der Streifen ist bis 4.8:1 breit und
        # würde auf dem Handy zu einem 70 Pixel hohen Band zusammenfallen.
        # tabindex macht das Fenster auch ohne Maus scrollbar.
        kern = ('<div class="streifenfenster" tabindex="0" role="group" '
                'aria-label="Filmstreifen, seitlich scrollbar">%s</div>'
                % kern)

    z = ['<figure class="artefakt artefakt--%s%s">'
         % (s["art"], " ist-klein" if s.get("klein") else "")]
    z.append('  %s' % kern)
    legende = []
    if s["text"]:
        legende.append(html.escape(s["text"]))
    if s["art"] == "streifen":
        # Der Hinweis steht nur auf schmalen Schirmen, wo das Fenster
        # wirklich scrollt — CSS blendet ihn sonst aus. Als echter Text und
        # nicht als content-Eigenschaft, damit er auch vorgelesen wird.
        legende.append('<span class="artefakt__wisch">Seitlich wischen</span>')
    if s.get("nachweis"):
        legende.append('<span class="artefakt__nachweis">Bild: %s</span>'
                       % html.escape(s["nachweis"]))
    if legende:
        z.append('  <figcaption>%s</figcaption>' % " ".join(legende))
    z.append('</figure>')
    return "\n".join("  " + zeile for zeile in z)


def archiv_html():
    """Die Archivkapitel."""
    z = []
    for kapitel in ARCHIV:
        z.append('<section class="archivkapitel" id="archiv-%s">'
                 % kapitel["id"])
        z.append('  <header class="archivkapitel__kopf">')
        z.append('    <h2>%s</h2>' % html.escape(kapitel["titel"]))
        z.append('    <p class="archivkapitel__lead akzent">%s</p>'
                 % html.escape(kapitel["lead"]))
        z.append('  </header>')
        z.append('  <div class="archivraster">')
        for s in kapitel["stuecke"]:
            z.append(_artefakt_html(s))
        z.append('  </div>')
        z.append('</section>')
    return "\n".join(z)


def meistertitel_html():
    """Die Meistertitel als Jahresraster.

    Vorher standen die Jahre als Kommaliste da. Vierzehn Titel gegen drei
    ist aber eine Aussage, und die sieht man erst, wenn die Jahre
    nebeneinander stehen statt hintereinander.
    """
    z = ['<div class="titelbilanz">']
    for reihe in MEISTERTITEL:
        z.append('  <div class="titelreihe">')
        z.append('    <p class="titelreihe__wer label">%s</p>'
                 % html.escape(reihe["wer"]))
        z.append('    <p class="titelreihe__zahl">%d</p>' % len(reihe["jahre"]))
        z.append('    <p class="titelreihe__wort">%s</p>'
                 % ("Meistertitel" if len(reihe["jahre"]) != 1
                    else "Meistertitel"))
        z.append('    <ul class="titeljahre">')
        for jahr in reihe["jahre"]:
            z.append('      <li>%d</li>' % jahr)
        z.append('    </ul>')
        z.append('    <p class="titelreihe__text">%s</p>'
                 % html.escape(reihe["text"]))
        z.append('  </div>')
    z.append('</div>')
    return "\n".join(z)


# --------------------------------------------------------------------------
# Dokumente
# --------------------------------------------------------------------------
DOKUMENTORDNER = "assets/dokumente"


def _dokument_fehlt(eintrag):
    return not (ZIEL / DOKUMENTORDNER / eintrag["datei"]).exists()


def dokumentliste_html(eintraege):
    """Eine Liste zum Herunterladen.

    Ist die Datei da, ist der Eintrag ein Verweis mit dem Kürzel der
    Dateiendung rechts. Fehlt sie, steht derselbe Eintrag ohne Verweis da
    und trägt rechts «folgt». Ein Verweis auf eine Datei, die es nicht
    gibt, wäre ein Fehler 404; ein Verweis zurück auf die bisherige
    Website wäre genau das, was hier abgestellt werden soll.
    """
    z = ['<ul class="dokumentliste">']
    for e in eintraege:
        fehlt = _dokument_fehlt(e)
        kuerzel = e["datei"].rsplit(".", 1)[-1].upper()
        if fehlt:
            z.append('  <li><span class="dokument dokument--folgt">')
        else:
            z.append('  <li><a class="dokument" href="%s/%s" download>'
                     % (DOKUMENTORDNER, html.escape(e["datei"])))
        z.append('    <span class="dokument__name">%s</span>' % html.escape(e["name"]))
        z.append('    <span class="dokument__info">%s</span>' % html.escape(e["info"]))
        z.append('    <span class="dokument__typ">%s</span>'
                 % ("folgt" if fehlt else kuerzel))
        z.append('  </span></li>' if fehlt else '  </a></li>')
    z.append('</ul>')
    return "\n".join(z)


def schreibe_powershell():
    """Erzeugt hol-dokumente.ps1 aus derselben Liste wie alles andere.

    Warum es diese zweite Fassung gibt: hol-dokumente.py braucht Python.
    Auf Windows ist Python nicht von Haus aus da — PowerShell schon. Die
    .ps1 macht dasselbe und setzt nichts voraus; wer sie nicht mag, nimmt
    weiterhin die Python-Fassung.

    Erzeugt statt abgetippt, damit die beiden nicht auseinanderlaufen
    können. Wer die Dateiliste ändert, ändert nur dokumente.py.

    Mit Byte-Order-Mark geschrieben: ohne sie zeigt Windows PowerShell 5.1
    die Umlaute in den Meldungen als Buchstabensalat.
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
    for e in DOKUMENTE + BEITRITTSFORMULARE:
        z.append("  @{ name = '%s'; url = '%s' }"
                 % (e["datei"], e["herkunft"].replace("'", "''")))
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
        "    Write-Host ('  FEHLER     ' + $d.name + ' - ' + $_.Exception.Message)"
        " -ForegroundColor Red",
        "    Remove-Item $temp -ErrorAction SilentlyContinue",
        "    continue",
        "  }",
        "  # Eine Fehlerseite ist auch eine Antwort. Wer eine 2-kB-",
        "  # «Seite nicht gefunden» als Statuten ablegt, merkt es erst,",
        "  # wenn jemand sie oeffnet.",
        "  $bytes = [System.IO.File]::ReadAllBytes($temp)",
        "  $kopf = if ($bytes.Length -ge 4) { [System.Text.Encoding]::ASCII.GetString($bytes[0..3]) } else { '' }",
        "  if ($bytes.Length -lt 4096 -and $kopf -ne '%PDF' -and $kopf.Substring(0,[Math]::Min(2,$kopf.Length)) -ne 'PK') {",
        "    Write-Host ('  VERDAECHTIG ' + $d.name + ' - nur ' + $bytes.Length +"
        " ' Bytes, sieht nicht nach einem Dokument aus. Nicht gespeichert.')"
        " -ForegroundColor Yellow",
        "    Remove-Item $temp -ErrorAction SilentlyContinue",
        "    continue",
        "  }",
        "  Move-Item $temp $pfad -Force",
        "  Write-Host ('  geholt     ' + $d.name.PadRight(38) +"
        " ('{0,6:N1}' -f ($bytes.Length / 1024)) + ' kB')",
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
    (WURZEL / "hol-dokumente.ps1").write_text(
        "\n".join(z), encoding="utf-8-sig", newline="\r\n")


def melde_dokumente():
    """Sagt, welche Dateien noch fehlen — und wo sie zu holen sind."""
    fehlend = [e for e in DOKUMENTE + BEITRITTSFORMULARE if _dokument_fehlt(e)]
    if not fehlend:
        print("Dokumente: alle %d Dateien liegen unter site/%s."
              % (len(DOKUMENTE + BEITRITTSFORMULARE), DOKUMENTORDNER))
        return
    print("\nDokumente: %d von %d fehlen noch unter site/%s/ — die Einträge"
          % (len(fehlend), len(DOKUMENTE + BEITRITTSFORMULARE), DOKUMENTORDNER))
    print("stehen so lange ohne Verweis da. Holen: auf Windows")
    print("hol-dokumente.bat doppelklicken, sonst «python3 hol-dokumente.py».")
    for e in fehlend:
        print("  %-38s ← %s" % (e["datei"], e["herkunft"]))


# --------------------------------------------------------------------------
# News
# --------------------------------------------------------------------------
_MONATE = ("Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
           "August", "September", "Oktober", "November", "Dezember")


def _datum_lang(iso):
    """«2026-07-09» → «9. Juli 2026». Ohne führende Null, wie man es spricht."""
    jahr, monat, tag = (int(t) for t in iso.split("-"))
    return "%d. %s %d" % (tag, _MONATE[monat - 1], jahr)


def news_datei(beitrag):
    return "news-%s.html" % beitrag["kennung"]


def _hat_text(beitrag):
    return bool(beitrag.get("absaetze"))


def _news_titel(beitrag, kurz=False):
    if kurz and beitrag.get("kurztitel"):
        return beitrag["kurztitel"]
    return beitrag["titel"]


def _herkunft(beitrag):
    """«Text: Lyo Bührer, Bild: René Zwald» — nur was eingetragen ist."""
    teile = []
    if beitrag.get("text"):
        teile.append("Text: " + beitrag["text"])
    if beitrag.get("bildnachweis"):
        teile.append("Bild: " + beitrag["bildnachweis"])
    return ", ".join(teile)


def newskarten_html():
    """Die Karten auf der Startseite.

    Beiträge mit Text sind Karten zum Anklicken (<a class="bildkarte">),
    Beiträge ohne Text stehen als <div> mit derselben Gestalt da. Das ist
    der Unterschied zwischen «noch nicht übertragen» und «kaputt».
    """
    z = ['<div class="bildraster">']
    for b in BEITRAEGE[:AUF_STARTSEITE]:
        klick = _hat_text(b)
        if klick:
            z.append('  <a class="bildkarte reveal" href="%s">' % news_datei(b))
        else:
            z.append('  <div class="bildkarte bildkarte--still reveal">')
        z.append('    <div class="foto foto--16x9">')
        z.append('      <img src="assets/img/fotos/%s" alt="%s" width="900" height="506"'
                 ' loading="lazy" decoding="async">'
                 % (html.escape(b["bild"]), html.escape(b.get("bildalt", ""))))
        z.append('    </div>')
        z.append('    <div class="bildkarte__text">')
        z.append('      <time datetime="%s">%s</time>'
                 % (b["datum"], _datum_lang(b["datum"])))
        z.append('      <h3>%s</h3>' % html.escape(_news_titel(b, kurz=True)))
        z.append('      <p>%s</p>' % html.escape(_herkunft(b)))
        if klick:
            z.append('      <span class="bildkarte__mehr">Bericht lesen</span>')
        z.append('    </div>')
        z.append('  </a>' if klick else '  </div>')
    z.append('</div>')
    return "\n".join(z)


def newsliste_html():
    """Die Liste auf news.html — alle Beiträge, neueste zuerst."""
    z = ['<div class="newsliste">']
    for b in sorted(BEITRAEGE, key=lambda x: x["datum"], reverse=True):
        klick = _hat_text(b)
        if klick:
            z.append('  <a class="newseintrag" href="%s">' % news_datei(b))
        else:
            z.append('  <div class="newseintrag newseintrag--still">')
        z.append('    <time datetime="%s">%s</time>'
                 % (b["datum"], _datum_lang(b["datum"])))
        z.append('    <div><h3>%s</h3>' % html.escape(_news_titel(b)))
        z.append('      <p>%s</p></div>' % html.escape(_herkunft(b)))
        z.append('  </a>' if klick else '  </div>')
    z.append('</div>')
    return "\n".join(z)


def _absatz_html(stueck):
    """Ein Stück Fliesstext. Siehe news.py für die drei Sonderformen."""
    if isinstance(stueck, str):
        return '    <p>%s</p>' % html.escape(stueck)

    art = stueck.get("art", "p")
    if art == "titel":
        return '    <h2>%s</h2>' % html.escape(stueck["text"])
    if art == "zitat":
        z = ['    <blockquote class="beitrag__zitat">',
             '      <p>%s</p>' % html.escape(stueck["text"])]
        if stueck.get("wer"):
            z.append('      <cite>%s</cite>' % html.escape(stueck["wer"]))
        z.append('    </blockquote>')
        return "\n".join(z)
    if art == "liste":
        z = ['    <div class="beitrag__rangliste">']
        if stueck.get("titel"):
            z.append('      <p class="label">%s</p>' % html.escape(stueck["titel"]))
        z.append('      <ol>')
        for p in stueck["punkte"]:
            z.append('        <li>%s</li>' % html.escape(p))
        z.append('      </ol>')
        z.append('    </div>')
        return "\n".join(z)

    sys.exit("Fehler: Unbekannte Absatzart «%s» in news.py. Erlaubt sind "
             "titel, zitat und liste." % art)


def beitrag_html(beitrag):
    """Die ganze Beitragsseite als Inhaltsfragment."""
    bild = ZIEL / "assets/img/fotos" / beitrag["bild"]
    masse = _bildmass(bild)
    massangabe = ' width="%d" height="%d"' % masse if masse else ""

    z = ['<article class="beitrag">',
         '  <div class="seitenkopf seitenkopf--beitrag sektion--dunkel">',
         '    <div class="wrap">',
         '      <ul class="brotkrumen"><li><a href="index.html">Start</a></li>'
         '<li><a href="news.html">News</a></li><li>Beitrag</li></ul>',
         '      <time class="beitrag__datum" datetime="%s">%s</time>'
         % (beitrag["datum"], _datum_lang(beitrag["datum"])),
         '      <h1>%s</h1>' % html.escape(beitrag["titel"]),
         '      <p class="beitrag__herkunft">%s</p>' % html.escape(_herkunft(beitrag)),
         '    </div>',
         '  </div>',
         '',
         '  <div class="beitrag__bild">',
         '    <img src="assets/img/fotos/%s" alt="%s"%s fetchpriority="high" decoding="async">'
         % (html.escape(beitrag["bild"]), html.escape(beitrag.get("bildalt", "")),
            massangabe),
         '  </div>',
         '',
         '  <div class="sektion--weiss">',
         '    <div class="wrap beitrag__text">']
    for stueck in beitrag["absaetze"]:
        z.append(_absatz_html(stueck))
    z.append('    </div>')
    z.append('  </div>')
    z.append('')
    z.append('  <div class="sektion--hell">')
    z.append('    <div class="wrap btn-reihe">')
    z.append('      <a class="btn btn--leise" href="news.html">Alle Beiträge</a>')
    z.append('    </div>')
    z.append('  </div>')
    z.append('</article>')
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

    def schreibe(datei, titel, beschreibung, rubrik, inhalt):
        """Setzt eine Seite zusammen und legt sie unter site/ ab.

        Steht als eigene Funktion da, weil es zwei Arten von Seiten gibt:
        die 27 mit einem Fragment in inhalt/, und die Beitragsseiten, die
        build.py vollständig aus news.py erzeugt. Beide müssen durch
        dieselben Ersetzungen laufen — sonst fehlt der einen Sorte
        irgendwann die Navigation oder die Teilen-Vorschau, und niemand
        merkt es, weil beide für sich genommen funktionieren.
        """
        seite = layout
        seite = seite.replace("{{titel}}", html.escape(titel))
        seite = seite.replace("{{beschreibung}}", html.escape(beschreibung))
        seite = seite.replace("{{navigation}}", navigation_html(datei, rubrik))
        seite = seite.replace("{{signet}}", signet)
        seite = seite.replace("{{logo}}", logo)
        seite = seite.replace("{{inhalt}}", inhalt)
        # Nach {{inhalt}}, damit auch Platzhalter in den Fragmenten greifen.
        if "{{trainingsraster}}" in seite:
            seite = seite.replace("{{trainingsraster}}", trainingsraster_html())
        if "{{mannschaften}}" in seite:
            seite = seite.replace("{{mannschaften}}", mannschaften_html())
        if "{{sponsoren}}" in seite:
            seite = seite.replace("{{sponsoren}}", sponsoren_html())
        if "{{ausruester}}" in seite:
            seite = seite.replace("{{ausruester}}", ausruester_html())
        if "{{zeitleiste}}" in seite:
            seite = seite.replace("{{zeitleiste}}", zeitleiste_html())
        # Die Zahl der Stationen stand als «acht» im Text. Nach dem ersten
        # neuen Eintrag war sie falsch — also rechnet der Build sie aus.
        seite = seite.replace("{{zeitleistenzahl}}", _zahlwort(len(ZEITLEISTE)))
        if "{{archiv}}" in seite:
            seite = seite.replace("{{archiv}}", archiv_html())
        if "{{meistertitel}}" in seite:
            seite = seite.replace("{{meistertitel}}", meistertitel_html())
        if "{{newskarten}}" in seite:
            seite = seite.replace("{{newskarten}}", newskarten_html())
        if "{{newsliste}}" in seite:
            seite = seite.replace("{{newsliste}}", newsliste_html())
        if "{{dokumente}}" in seite:
            seite = seite.replace("{{dokumente}}", dokumentliste_html(DOKUMENTE))
        if "{{beitrittsformulare}}" in seite:
            seite = seite.replace("{{beitrittsformulare}}",
                                  dokumentliste_html(BEITRITTSFORMULARE))
        seite = seite.replace("{{anmeldeformular}}", ANMELDEFORMULAR)
        seite = seite.replace("{{bildnachweis}}", html.escape(NACHWEIS))
        seite = seite.replace("{{auftaktbilder}}", str(AUFTAKT_BILDER))
        seite = seite.replace("{{sponsorenzahl}}", str(len(SPONSOREN)))
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

    # --- Die Seiten mit einem Fragment in inhalt/ --------------------------
    for datei, (titel, beschreibung, rubrik) in SEITEN.items():
        quelle = INHALT / datei
        if not quelle.exists():
            fehlend.append(datei)
            continue
        schreibe(datei, titel, beschreibung, rubrik,
                 quelle.read_text(encoding="utf-8"))

    # --- Die Beitragsseiten, ganz aus news.py erzeugt ----------------------
    # Nur Beiträge mit Fliesstext bekommen eine Seite. Ohne Text bliebe eine
    # Überschrift mit einem Datum darunter — und die Karte auf der
    # Startseite verwiese auf nichts. Sie ist dann lieber nicht klickbar.
    ohne_text = []
    for b in BEITRAEGE:
        if not _hat_text(b):
            ohne_text.append(b)
            continue
        beschreibung = b["titel"]
        if len(beschreibung) > 155:
            beschreibung = beschreibung[:152].rstrip() + "…"
        schreibe(news_datei(b),
                 "%s – TTC Neuhausen" % _news_titel(b, kurz=True),
                 beschreibung, "News", beitrag_html(b))

    if AUFTAKT_BILDER:
        ordner = ZIEL / "assets/img/auftakt"
        bytes_ = sum(p.stat().st_size for p in ordner.glob("bild-*.webp"))
        print("Auftakt: %d Bilder, zusammen %.2f MB (nur Laptop)"
              % (AUFTAKT_BILDER, bytes_ / 1024 / 1024))
    print("Gebaut: %d Seiten" % len(gebaut))
    for d in sorted(gebaut):
        print("  " + d)
    if fehlend:
        print("\nFehlende Fragmente in inhalt/ (%d):" % len(fehlend))
        for d in sorted(fehlend):
            print("  " + d)

    if ohne_text:
        print("\nBeiträge ohne Fliesstext (%d) — Karte und Listeneintrag stehen"
              % len(ohne_text))
        print("da, sind aber nicht klickbar. Text in vorlage/news.py eintragen:")
        for b in ohne_text:
            print("  %s  %s" % (b["datum"], b["titel"]))

    # Verwaiste Fragmente melden: Datei vorhanden, aber nicht in seiten.py eingetragen.
    verwaist = [p.name for p in INHALT.glob("*.html") if p.name not in SEITEN]
    if verwaist:
        print("\nNicht in seiten.py eingetragen (%d):" % len(verwaist))
        for d in sorted(verwaist):
            print("  " + d)

    schreibe_serverdateien(gebaut)
    pruefe_farben()
    pruefe_dateien(gebaut)
    if AUFTAKT_BILDER:
        pruefe_bogen()
        pruefe_auftaktsbedingung()
    schreibe_powershell()
    melde_dokumente()
    melde_trainingsumfang()

    if IST_VORSCHAU:
        print("\nVORSCHAU-FASSUNG für %s" % BASIS_URL)
        print("  Alle Seiten tragen noindex, robots.txt sperrt Suchmaschinen aus.")
        print("  Für die echte Website ohne --vorschau neu bauen.")


def schreibe_serverdateien(gebaut):
    """Legt die drei Dateien an, die der Server erwartet.

    .nojekyll — GitHub Pages schickt Seiten sonst durch Jekyll und
    überspringt dabei alles, was mit einem Unterstrich beginnt. Wir haben
    solche Dateien zwar nicht, aber die Datei kostet nichts und macht das
    Verhalten unabhängig davon, was später dazukommt.

    robots.txt — wird bei jedem Lauf neu geschrieben, passend zum Modus.
    Sonst bliebe nach einer Vorschau ein «Disallow» stehen und die echte
    Website wäre für Google gesperrt.

    sitemap.xml — **hat vorher gefehlt.** robots.txt hat sie angekündigt,
    es gab sie aber nicht: jede Suchmaschine, die dem Verweis folgt, lief
    in einen Fehler 404. Jetzt entsteht sie aus derselben Liste, aus der
    auch die Seiten entstehen, und kann deshalb weder Seiten vergessen
    noch welche nennen, die es nicht gibt.
    """
    (ZIEL / ".nojekyll").write_text("", encoding="utf-8")

    if IST_VORSCHAU:
        robots = ("# Vorschau-Fassung, nicht die Website des Vereins.\n"
                  "User-agent: *\nDisallow: /\n")
    else:
        robots = ("User-agent: *\nAllow: /\n\nSitemap: %ssitemap.xml\n"
                  % SEITE_URL)
    (ZIEL / "robots.txt").write_text(robots, encoding="utf-8")

    # In der Vorschau keine Sitemap: dort ist ohnehin alles gesperrt, und
    # eine Sitemap mit den Vorschau-Adressen wäre nur eine Einladung,
    # genau die zu indexieren.
    if IST_VORSCHAU:
        (ZIEL / "sitemap.xml").unlink(missing_ok=True)
        return

    z = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for datei in sorted(gebaut):
        adresse = BASIS_URL + ("" if datei == "index.html" else datei)
        z.append("  <url><loc>%s</loc></url>" % html.escape(adresse))
    z.append("</urlset>")
    z.append("")
    (ZIEL / "sitemap.xml").write_text("\n".join(z), encoding="utf-8")


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

    Ausgenommen sind Masken. In `mask-image: linear-gradient(90deg,
    transparent, #000 45%)` ist #000 keine Farbe, sondern Deckung: der
    Browser liest daraus den Alphakanal, sichtbar wird nie Schwarz. Die
    Prüfung hat das anfangs angemahnt — zu Recht nach ihrem Wortlaut, zu
    Unrecht nach ihrem Zweck. Statt den Wert zu verstecken (`black` wäre
    durchgerutscht), kennt die Prüfung jetzt den Unterschied.
    """
    hexwert = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
    maske = re.compile(r"^\s*(-webkit-)?mask(-image)?\s*:")
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
            if maske.match(zeile):
                continue
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


def pruefe_bogen():
    """Prüft, dass der Flugbogen im Auftakt zweimal gleich lautet.

    Der Bogen steht notgedrungen doppelt: einmal als <path d="…"> im
    HTML, damit er sich zeichnen lässt, und einmal als offset-path im
    CSS, damit der Ball ihn abfährt. Ein gemeinsamer Ort wäre schöner,
    aber CSS kann keinen Pfad aus dem Dokument lesen und SVG keinen aus
    dem Stylesheet.

    Gehen die beiden auseinander, sieht man keinen Fehler, sondern nur
    einen Ball, der neben seiner eigenen Linie herfliegt — genau die
    Sorte Abweichung, die man im Browser übersieht und die hier eine
    Zeile kostet.
    """
    html = (ZIEL / "index.html").read_text(encoding="utf-8")
    css = (ZIEL / "assets/css/seiten.css").read_text(encoding="utf-8")

    im_html = re.search(r'class="auftakt__bogen".*?<path d="([^"]+)"', html, re.S)
    im_css = re.search(r'offset-path:\s*path\("([^"]+)"\)', css)

    if not im_html or not im_css:
        sys.exit("Fehler: Der Auftaktsbogen fehlt in index.html oder in "
                 "seiten.css. Beide müssen denselben Pfad tragen.")

    # Leerraum vereinheitlichen: «M 56 234» und «M56,234» sind derselbe Pfad.
    glatt = lambda s: re.sub(r"[\s,]+", " ", s).strip()
    if glatt(im_html.group(1)) != glatt(im_css.group(1)):
        sys.exit("Fehler: Der Auftaktsbogen lautet zweimal verschieden.\n"
                 "  index.html : %s\n"
                 "  seiten.css : %s\n"
                 "Der Ball folgt dem Pfad aus dem CSS, gezeichnet wird der "
                 "aus dem HTML. Beide angleichen."
                 % (im_html.group(1), im_css.group(1)))

    print("Auftakt: Bogen und Ballbahn stimmen überein.")


def pruefe_auftaktsbedingung():
    """Prüft, dass CSS und Skript denselben Schirm meinen.

    Die Bedingung steht zweimal: als `@media` im Stylesheet, das den
    Abschnitt einblendet, und als `matchMedia` im Skript, das die Bilder
    holt. Laufen sie auseinander, entsteht einer von zwei stillen Fehlern
    — ein eingeblendeter Abschnitt ohne Bilder, oder 1.3 MB Bilder für
    einen Abschnitt, den niemand sieht. Beides fällt im Browser nicht auf.
    """
    css = (ZIEL / "assets/css/seiten.css").read_text(encoding="utf-8")
    js = (ZIEL / "assets/js/main.js").read_text(encoding="utf-8")

    im_css = re.search(r"@media\s*\(([^)]*min-width[^)]*)\)\s*\{\s*\n"
                       r"\s*html\.auftakt-an", css)
    im_js = re.search(r"var gross = window\.matchMedia\('([^']+)'\)", js)

    if not im_css or not im_js:
        sys.exit("Fehler: Die Auftaktsbedingung ist in seiten.css oder in "
                 "main.js nicht auffindbar. Beide müssen denselben Schirm "
                 "meinen.")

    glatt = lambda s: re.sub(r"\s+", " ", s).strip().strip("()")
    if glatt(im_css.group(1)) != glatt(im_js.group(1)):
        sys.exit("Fehler: Der Auftakt wird unter anderen Bedingungen "
                 "eingeblendet als geladen.\n"
                 "  seiten.css : (%s)\n"
                 "  main.js    : %s\n"
                 "Sonst gibt es entweder einen leeren Abschnitt oder Bilder, "
                 "die niemand sieht." % (im_css.group(1), im_js.group(1)))

    print("Auftakt: Einblenden und Laden gelten für denselben Schirm (%s)."
          % im_js.group(1))


if __name__ == "__main__":
    main()
