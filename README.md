# TTC Neuhausen — Website

Statische Website des Tischtennisclubs Neuhausen. Stand: 23. September 2026,
Redesign «Sportmagazin». Gestaltung und Umsetzung: Wendico.

Der Stand vor dem Redesign liegt im Git-Verlauf (Commit «Final_Changes»).

## Öffnen

`site/index.html` im Browser öffnen. Es braucht keinen Server.

## Muss ich Python können?

Nein. **Der Ordner `site/` ist die fertige Website** und wird jedes Mal
fertig gebaut mitgeliefert. Zum Anschauen, Hochladen oder Weitergeben
braucht es nichts.

`build.py` ist nur nötig, wenn **du selbst** etwas in `inhalt/` oder
`vorlage/` änderst. Dann:

1. Python holen, falls nicht vorhanden: <https://www.python.org/downloads/>
   — bei der Installation **«Add Python to PATH» ankreuzen**.
2. Im Explorer in den Projektordner gehen, rechte Maustaste auf eine freie
   Stelle → **«Im Terminal öffnen»**.
3. `python build.py` eintippen, Enter. (Auf Windows `python`, nicht `python3`.)

Es erscheint die Zahl der gebauten Seiten und darunter die Prüfungen.
Alles, was `build.py` schreibt, landet in `site/`. **Nie `site/*.html` von
Hand ändern** — der nächste Lauf überschreibt es.

## Ordner

```
TTC_Neuhausen/
├── build.py              Setzt die Seiten zusammen und prüft sie
├── hol-dokumente.bat     Holt die Vereinsdokumente – auf Windows doppelklicken
├── hol-dokumente.ps1     … dahinter; erzeugt von build.py, nicht von Hand ändern
├── hol-dokumente.py      … dasselbe für alle, die Python haben
├── .github/workflows/    Veröffentlicht die Vorschau auf GitHub Pages
├── vorlage/
│   ├── layout.html       Kopfzeile, Fuss, <head> – steht genau einmal im Projekt
│   ├── seiten.py         Adresse der Website, Menü, Titel und Beschreibung jeder Seite
│   ├── trainingszeiten.py  Alle Trainingseinheiten der Woche
│   ├── termine.py        Anlässe für Jahresprogramm und News
│   ├── mannschaften.py   Die Teams und ihre click-tt-Adressen
│   ├── sponsoren.py      Partner und Ausrüster
│   ├── geschichte.py     Zeitleiste, Vereinsarchiv, Meistertitel
│   ├── news.py           Beiträge – Startseite, News-Liste, Beitragsseiten
│   └── dokumente.py      Downloads, Beitrittsformulare, Unterlagen Hallensportzentrum
├── inhalt/               Ein Fragment je Seite, nur der Inhalt von <main>
└── site/                 Erzeugt – das ist die fertige Website
    └── assets/
        ├── css/          tokens → base → komponenten → seiten
        ├── fonts/        Die drei Schriften, selbst gehostet, mit OFL.txt
        ├── js/main.js
        ├── dokumente/    Statuten, Reglemente, Formulare, Flyer
        └── img/          fotos/, archiv/, partner/, personen/, Logo, Signet
```

## Ändern

**Text einer Seite:** Datei in `inhalt/` bearbeiten, dann `python build.py`.

**Neue Seite:** Fragment in `inhalt/` anlegen, Eintrag in `vorlage/seiten.py`
ergänzen, bauen.

**Menü, Kopfzeile, Fuss:** `vorlage/seiten.py` beziehungsweise
`vorlage/layout.html`. Die Änderung greift auf allen Seiten.

**Farben, Schriften, Abstände:** nur `site/assets/css/tokens.css`. Kein
Farbwert steht ausserhalb dieser Datei – der Build prüft das.

### Platzhalter in den Fragmenten

Was sich aus den Daten in `vorlage/` ergibt, steht in den Fragmenten als
Platzhalter. So gibt es jede Angabe genau einmal.

| Platzhalter | ergibt |
|---|---|
| `{{wochenplan}}` | das Wochenraster mit Filter auf `training.html` |
| `{{zeiten:…}}` | eine Zeitentabelle, z. B. `{{zeiten:nachwuchs}}`, `{{zeiten:nachwuchs+Stützpunkt\|Förderkader}}`, `{{zeiten:halle=ebnat}}` |
| `{{kurzzeiten:…}}` | dasselbe kurz, für die Randspalte |
| `{{trainer:Name}}` | die Einheiten, die eine Person leitet |
| `{{mannschaften}}`, `{{mannschaftszahl}}` | die Teams mit click-tt-Links, ihre Zahl |
| `{{sponsoren}}`, `{{ausruester}}`, `{{sponsorenzahl}}` | Partnerwand, Ausrüster, Zahl |
| `{{zeitleiste}}`, `{{archiv}}`, `{{meistertitel}}` | Geschichte |
| `{{news_start}}`, `{{aktuell}}`, `{{newsliste}}` | News |
| `{{termine}}` | kommende Anlässe |
| `{{dokumente}}`, `{{beitrittsformulare}}`, `{{hallenprojekt}}` | Download-Listen |
| `{{einheiten}}`, `{{trainingstage}}`, `{{saison}}`, `{{vereinsalter}}` | Zahlen, vom Build gerechnet |

Ein Tippfehler in einem Platzhalter bricht den Build mit Hinweis ab – er
landet nie als `{{…}}` auf der Website.

## Die Startseite: der Tisch

Statt der fünfzig gezeichneten Einzelbilder steht oben ein Tisch, gebaut
aus CSS – keine Bilddateien, kein WebGL. Beim Scrollen dreht er sich aus
der Schrägansicht in die Draufsicht, der Ball verschwindet, und die vier
Felder der Platte werden zu den vier Angeboten: Nachwuchs, Breitensport,
Senioren, Schulen.

- **Läuft ab 1024 × 620 Pixel** und nur ohne «Bewegung reduzieren». Die
  Bedingung steht in `main.js` (`gross`). Darunter, auf dem Handy und ohne
  JavaScript steht der Tisch still, schräg, und die Angebote folgen als
  gewöhnliche Liste. Kein Scroll-Kapern auf dem Handy.
- **Die Bühne ist 250vh hoch**, die Fläche klebt. Die Drehung läuft über
  6–62 % des Wegs, die Angebote erscheinen bei 66–84 %.
- **Nur der Ball und seine Höhe tragen `preserve-3d`.** Bekommen alle
  Teile der Platte eine eigene 3D-Ebene, sortiert der Browser sie bei
  manchen Winkeln falsch, und es entstehen Löcher in der Kante.
- **Der Ball ruht**, solange der Tisch nicht im Bild ist (IntersectionObserver).

Sonst bewegt sich wenig, und immer als Zusatz: Karten neigen sich leicht
zum Zeiger (`data-kippen`, nur mit Maus), Filmstreifen und das Schema des
TTZ folgen dem Scrollstand (`data-tiefe`), die Anzeigetafel klappt ihre
Ziffern einmal durch. Mit «Bewegung reduzieren» steht alles still.

## Gestaltung

**Sportmagazin, hell.** Papier (`--papier`) und Tinte (`--tinte`) tragen
die Seiten, das Vereinsblau ist die Tischfläche und die Farbe für Zahlen
und Links. **Orange ist nur der Ball** – als Punkt vor der Rubrik, als
Balken, als Fläche; nie als Schrift auf hellem Grund (Kontrast 2.1).

Jede Unterseite ist wie ein Artikel gebaut: Aufmacher mit Rubrik, Titel,
Vorspann und grossem Bild mit Legende; dann Haupttext mit einer
Randspalte «Auf einen Blick»; dazwischen Flächen in Blau oder Nachtblau
für Zahlen und Zitate.

**Schriften**, alle unter der SIL Open Font License, selbst gehostet unter
`site/assets/fonts/` – es wird keine Verbindung zu Google aufgebaut:

- Sofia Sans Extra Condensed – Titel, Zahlen, Auszeichnung
- Schibsted Grotesk – Fliesstext
- Newsreader – Vorspann und Zitate

Die Schriften enthalten nur den lateinischen Zeichensatz. Pfeile sind
deshalb gezeichnet (`.pfeil`, eine CSS-Maske), nicht getippt.

**Flächen setzen ihren Kontext:** `.flaeche--papier`, `--papier2`,
`--weiss`, `--blau`, `--nacht`. Alles darin erbt Schrift- und Linienfarbe;
ein Knopf braucht keine Dunkel-Variante.

## Bilder

| Datei unter `site/assets/img/` | Wo |
|---|---|
| `fotos/ttz-ebnat.jpg` | Hallen, TTZ Ebnat, Partner, Startseite, Breitensport |
| `fotos/nachwuchs-gruppe.jpg` | Nachwuchs, Schnupperpass |
| `fotos/breitensport-gruppe.jpg` | Breitensport, Verein |
| `fotos/senioren-gruppe.jpg` | Senioren, Mitglied werden |
| `fotos/halle-kinder.jpg` | Schnupperpass, Schulen |
| `fotos/helfer-altpapier.jpg` | Helfereinsatz, Startseite |
| `fotos/sttl-women.jpg`, `sttl-men.jpg` | Teams, Stützpunkt |
| `fotos/detail-ballwechsel.jpg` | Trainerteam, Einzeltraining |
| `fotos/finalrunde-nachwuchs.jpg` | Nachwuchs, Rhyfallhalle |
| `fotos/news-1.jpg` … `news-3.jpg` | News, über `vorlage/news.py` |
| `archiv/*` | Geschichte, TTZ Ebnat, Rhyfallhalle, Startseite |

**Austauschen:** gleicher Dateiname, Datei ersetzen, bauen. Die Bildmasse
liest der Build selbst aus der Datei. Wo ein Bild mit `object-fit: cover`
beschnitten wird, steht bei Bedarf `object-position` direkt im Fragment.

**Nicht mehr verwendet** und nur noch als Altbestand im Ordner:
`img/auftakt/` (die fünfzig Bilder des alten Auftakts), `auftakt-test.html`,
`fotos/hero-halle.jpg`, `fotos/halle-ebnat.jpg`, `fotos/helfer.jpg` und
`fotos/angebot-*.jpg`. Sie dürfen weg; gelöscht ist nichts.

## Trainingszeiten

**Nur `vorlage/trainingszeiten.py`, dann bauen.** Daraus entstehen das
Wochenraster, die Tabellen auf den Trainingsseiten, «Heute im Training»
auf der Startseite und die Wochenpläne im Trainerteam.

Die Zeitachse steht als `RASTER_BAENDER` in derselben Datei und
überspringt die Mittagsstunden. Eine Einheit ausserhalb der Bänder bricht
den Build mit Hinweis ab. Überschneidungen rechnet der Build selbst aus;
die Blöcke rücken dann auf zwei Bahnen.

## News

**Nur `vorlage/news.py`, dann bauen.** Daraus entstehen der Block auf der
Startseite, die Zeile «Aktuell» im Tisch, die Liste auf `news.html` und
die Beitragsseiten.

Hat ein Beitrag Fliesstext (`absaetze`), entsteht `news-<kennung>.html`,
und alles verweist darauf. Hat er keinen, bleibt er eine Meldung ohne
Verweis. **Die Berichte von Lyo Bührer haben noch keinen Text** – er ist
aus dem alten Redaktionssystem zu kopieren, nicht nachzuerzählen.

## Termine

**Nur `vorlage/termine.py`.** Vergangene Termine blendet die Website von
selbst aus, auch ohne neuen Build.

## Downloads

**Nur `vorlage/dokumente.py`, dann bauen.** Die Dateien liegen unter
`site/assets/dokumente/`. Fehlt eine, steht ihr Eintrag mit «folgt» und
ohne Verweis da, und der Build nennt Dateiname und Bezugsadresse.

Geholt werden fehlende Dateien in einem Durchgang: auf Windows
`hol-dokumente.bat` doppelklicken, sonst `python3 hol-dokumente.py`. Eine
Antwort, die kleiner als 4 kB ist und weder mit `%PDF` noch mit einem
ZIP-Kopf beginnt, wird nicht gespeichert – sonst läge irgendwann eine
Fehlerseite als Statuten im Ordner. Die `.ps1` erzeugt der Build aus
derselben Liste; nicht von Hand ändern.

Neu dazugekommen: `HALLENPROJEKT`, die drei Unterlagen zum
Hallensportzentrum (Flyer, Medienmitteilung, Flyer «Baustein 2026») für
`hallen-neue-halle.html`.

## Teams und click-tt

**Es gibt kein Widget.** click-tt.ch (nuLiga) bietet weder Widget noch
Schnittstelle. Deshalb führt `vorlage/mannschaften.py` alle Teams mit
Liga und Gruppennummer, und jede Zeile auf `teams.html` öffnet die
offizielle Tabelle. Auf der eigenen Seite steht nichts, was veralten kann.

**Zum Saisonwechsel:** Vereinsseite
`https://www.click-tt.ch/cgi-bin/WebObjects/nuLigaTTCH.woa/wa/clubTeams?club=33244`
öffnen, je Mannschaft `championship` und `gruppe_id` nachführen, `SAISON`
anpassen, bauen.

**Falle:** nuLiga erwartet im Saisonkürzel das Leerzeichen als `+`
(`championship=STT+26%2F27`). Mit `%20` öffnet sich ohne Fehlermeldung
eine *andere* Liga. Der Build kodiert das richtig.

## Sponsoren

**Nur `vorlage/sponsoren.py`, dann bauen.** Daraus entstehen die
Partnerwand auf `partner.html` und die Zahl im Text.

Unter `site/assets/img/partner/` liegen aufbereitete Logos (freigestellt,
auf 480 × 300 zentriert, auf gleiche **Fläche** statt gleiche Breite
skaliert, damit Wortmarken und Signete gleich schwer wirken). Die
Originale bleiben in `site/assets/img/Sponsoren/`. Der Ordner heisst
«partner», weil Windows `sponsoren` und `Sponsoren` nicht unterscheidet.

## Geschichte und Archiv

**Nur `vorlage/geschichte.py`, dann bauen.** Zeitleiste, Archivkapitel und
Meistertitel. Ein Archivstück ist `streifen` (Filmstreifen, seitlich
scrollbar), `blatt` (Albumblatt) oder `dokument`; `klein: True` für
Vorlagen, die für eine Vergrösserung zu klein sind. Ein Klick auf ein
Stück öffnet die Lupe (ein `<dialog>`, mit Pfeiltasten blätterbar).

Die Archivbilder sind bewusst nicht beschnitten: Sprossenlöcher,
Bildnummern und die Handschrift gehören dazu. Tims Originale liegen
unverändert in `site/assets/img/Geschichte/`.

## Was der Build prüft

Nach jedem Lauf meldet `build.py`:

- unbekannte Platzhalter (bricht ab)
- Farbwerte ausserhalb von `tokens.css`
- Verweise ins Leere: Seiten, Dateien **und Sprungmarken** (`#rechner`)
- fehlende Dokumente, mit Bezugsadresse
- Zahl der Einheiten und Stunden im Trainingsplan

Dazu schreibt er `.nojekyll`, `robots.txt`, `sitemap.xml` und
`hol-dokumente.ps1`.

## Vorschau auf GitHub Pages

```
python3 build.py --vorschau https://name.github.io/ttcn-vorschau/
```

Der Schalter setzt `canonical`, `og:url` und `og:image` auf die
Vorschauadresse, gibt jeder Seite `noindex` und sperrt Suchmaschinen per
`robots.txt` aus. Ohne Schalter wird alles zurückgenommen.
`.github/workflows/vorschau.yml` baut bei jedem Push mit der richtigen
Adresse und veröffentlicht `site/`. Einrichten: Repository öffentlich,
unter *Settings → Pages* die Quelle auf **GitHub Actions** stellen.

## Offene Punkte

**Vom Verein zu prüfen**

- **Impressum und Datenschutz** freigeben. Die internen Hinweise stehen
  jetzt als Kommentar im Fragment, nicht mehr sichtbar auf der Seite.
  Offen: Handelsregister-Eintrag (dann UID unter «Rechtsform»).
- **News:** Fliesstext der Berichte von Lyo Bührer einsetzen.
- **Anmeldeformular:** die Microsoft-Forms-Adresse in `dokumente.py`
  einmal anklicken.
- **Einzeltraining:** Preise und Mindestabo stammen von der bisherigen
  Website – noch aktuell?
- **Schulen:** Link zur School Trophy prüfen.
- **Elio Zarotti** steht im Trainerteam für Stellvertretungen, kommt im
  Trainingsplan aber nicht vor.
- **Johnson & Johnson:** weder Logo noch Adresse (im TTZ hängt eine
  Tafel «janssen»).
- **Sponsorenliste:** lag bei Kris Leibundgut zur Prüfung.
- **Logo:** Das bisherige trägt noch «Seit 50 Jahren am Tisch» (2025).
- **Hallensportzentrum:** Die Seite fasst Abstimmung, Finanzierung und
  Projekt Futuro nach den Unterlagen der Stiftung zusammen. Sobald es
  einen Zeitplan für Bau und Einzug gibt, gehört er dorthin.
- **TTZ Ebnat:** Das Schema auf der Seite zeigt zwölf Tische,
  ausdrücklich nicht massstäblich. Ein echter Hallenplan wäre besser.

**Vor der Aufschaltung**

- `SEITE_URL` in `vorlage/seiten.py` auf die endgültige Adresse setzen.
- Rund 50 alte Adressen per 301 auf die neuen weiterleiten
  (Zuordnung in `seitenstruktur.xlsx`).
- Fehlende Dokumente holen (`hol-dokumente.bat`), dann bauen.
