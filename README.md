# TTC Neuhausen — Website

Statische Website des Tischtennisclubs Neuhausen. Stand: 22. Oktober 2026,
Redesign «Sportmagazin», mit Redaktion unter /admin und Veröffentlichen
über GitHub. Gestaltung und Umsetzung: Wendico.

Der Stand vor dem Redesign liegt im Git-Verlauf (Commit «Final_Changes»).

## Öffnen

`site/index.html` im Browser öffnen. Es braucht keinen Server.

## Muss ich Python können?

Nein. **Der Ordner `site/` ist die fertige Website** und wird jedes Mal
fertig gebaut mitgeliefert. Zum Anschauen, Hochladen oder Weitergeben
braucht es nichts.

**News schreibt man in der Redaktion** unter `www.ttc-neuhausen.ch/admin` –
ohne Python, ohne HTML, siehe [REDAKTION.md](REDAKTION.md). Und jede
Änderung, die auf GitHub landet, baut und veröffentlicht GitHub selbst
(siehe «Veröffentlichen auf Hostpoint»).

`build.py` ist nur nötig, wenn **du selbst** etwas in `inhalt/` oder
`vorlage/` änderst und es vorher anschauen willst. Dann:

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
├── veroeffentlichen.py   Lädt site/ auf Hostpoint, nur was sich geändert hat
├── REDAKTION.md          Anleitung für alle, die News schreiben
├── hol-dokumente.bat     Holt die Vereinsdokumente – auf Windows doppelklicken
├── hol-dokumente.ps1     … dahinter; erzeugt von build.py, nicht von Hand ändern
├── hol-dokumente.py      … dasselbe für alle, die Python haben
├── .github/workflows/    hostpoint.yml: echte Website · vorschau.yml: GitHub Pages
├── vorlage/
│   ├── layout.html       Kopfzeile, Fuss, <head> – steht genau einmal im Projekt
│   ├── seiten.py         Adresse der Website, Menü, Titel und Beschreibung jeder Seite
│   ├── trainingszeiten.py  Alle Trainingseinheiten der Woche
│   ├── termine.py        Anlässe für Jahresprogramm und News
│   ├── mannschaften.py   Die Teams und ihre click-tt-Adressen
│   ├── sponsoren.py      Partner und Ausrüster
│   ├── geschichte.py     Zeitleiste, Vereinsarchiv, Meistertitel
│   ├── news.py           Format der News, Zahl der Meldungen auf der Startseite
│   ├── redaktion.yml     Felder der Redaktion unter /admin → site/admin/config.yml
│   ├── dokumente.py      Downloads, Beitrittsformulare, Unterlagen Hallensportzentrum
│   └── seo.py            Weiterleitungen der alten Adressen, Verein und Hallen für Google
├── redaktion/            Die News-Ablage: ein EIGENES Repository (…-News), hier nur
│                         als Ordner eingehängt – news/, bilder/, dokumente/
├── inhalt/               Ein Fragment je Seite, nur der Inhalt von <main>
│   └── news/             Die News, eine .json-Datei je Beitrag
└── site/                 Erzeugt – das ist die fertige Website
    ├── admin/            Die Redaktion: Sveltia CMS, Vorschau, Anmeldung (PHP)
    └── assets/
        ├── css/          tokens → base → komponenten → seiten
        ├── fonts/        Die drei Schriften, selbst gehostet, mit OFL.txt
        ├── js/main.js
        ├── dokumente/    Statuten, Reglemente, Formulare, Flyer
        └── img/          fotos/, news/, archiv/, partner/, personen/, Logo, Signet
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
| `news/*` | News: Titelbilder, Bilder im Text, Galerien – lädt die Redaktion hoch |
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

**Je Beitrag eine Datei unter `redaktion/news/`**, geschrieben in der
Redaktion (nächster Abschnitt) oder von Hand; das Format steht in
`vorlage/news.py`. Daraus entstehen der Block auf der Startseite, die Zeile
«Aktuell» im Tisch, die Liste auf `news.html` und die Beitragsseiten.

`redaktion/` ist die **News-Ablage**, ein eigenes Repository
(`TTC_Neuhausen-News`, privat) mit `news/`, `bilder/` und `dokumente/`. Es
gehört als Ordner neben `build.py` und steht hier in der `.gitignore`:

    git clone https://github.com/Timsksokksopw/TTC_Neuhausen-News.git redaktion

Vor dem Arbeiten `git -C redaktion pull`, danach dort committen und pushen –
News sind also zwei Schritte in zwei Repositories nur dann, wenn sich
zugleich am Aussehen etwas ändert. `build.py` spiegelt `bilder/` nach
`site/assets/img/news/` und `dokumente/` nach `site/assets/dokumente/news/`;
diese beiden Ordner gehören ganz der Ablage. Übernommen werden nur JPEG,
PNG, WebP und PDF, deren Inhalt zur Endung passt, mit einfachen Dateinamen,
ohne Unterordner und Verknüpfungen; alles andere steht als Warnung im
Protokoll. Ein Beitrag kann nur auf Bilder unter `/assets/img/` und PDFs
unter `/assets/dokumente/` zeigen.

Hat ein Beitrag Text, Bilder oder ein PDF, entsteht `news-<dateiname>.html`,
und alles verweist darauf. Hat er nichts davon, bleibt er eine Meldung ohne
Verweis. Den Dateinamen nach dem Veröffentlichen nicht mehr ändern – er ist
die Adresse. **Die Berichte von Lyo Bührer haben noch keinen Text** – er ist
aus dem alten Redaktionssystem zu kopieren, nicht nachzuerzählen.

Ein Beitrag kann haben: Titelbild (mit «wichtigem Bildteil» oben, Mitte
oder unten, wo es zugeschnitten wird), Absätze, Zwischentitel, Zitate,
Bilder im Text, Ranglisten, eine Galerie und ein PDF. Ein Klick auf ein
Bild öffnet die Lupe aus der Geschichte. Beim Teilen auf WhatsApp oder
Facebook erscheint das Titelbild (`assets/img/teilen/`, gerechnet beim
Veröffentlichen).

## Redaktion (/admin)

`www.ttc-neuhausen.ch/admin` ist [Sveltia CMS](https://sveltiacms.app/en/docs):
ein Formular für News, deutsch, mit Vorschau im Stil der Website. Wer
speichert, macht einen Commit in die News-Ablage (`TTC_Neuhausen-News`) –
**nicht in dieses Repository**; den Rest erledigt GitHub (nächster
Abschnitt). Anleitung für die Schreibenden: [REDAKTION.md](REDAKTION.md).

- **Warum getrennt:** Nach der Anmeldung liegt der Schlüssel im Browser der
  Person. Er gilt nur für die News-Ablage. Wer ihn in die Hände bekommt,
  kann News verfälschen (und das lässt sich zurückholen), aber weder den
  Code noch die übrigen Seiten ändern noch an das Hostpoint-Passwort kommen.

- **Felder:** `vorlage/redaktion.yml`, daraus schreibt `build.py`
  `site/admin/config.yml`. Die Vorschau baut `site/admin/vorschau.js` mit
  den CSS-Dateien der Website nach – ändert sich `beitrag_html()` in
  `build.py`, gehört es auch dorthin.
- **Fotos** verkleinert schon der Browser beim Hochladen (WebP, höchstens
  2000 Pixel, auch HEIC vom iPhone). Was trotzdem gross ankommt, verkleinert
  `build.py --bilder-verkleinern` vor dem Hochladen auf den Server und
  entfernt dabei EXIF und Ortsangaben.
- **Anmeldung:** mit Name und Passwort, ohne GitHub-Konto. Hinter dem
  Knopf «Anmelden» (`site/admin/index.html` benennt Sveltias «Mit GitHub
  anmelden» um) steht `site/admin/anmelden.php`: Stimmt das Passwort, gibt
  es der Redaktion einen Zugangsschlüssel zu GitHub, den nur der Server
  kennt. Alle speichern damit unter diesem einen Konto.
  - `REDAKTION_SCHLUESSEL`: Fine-grained token (GitHub → Settings →
    Developer settings → Personal access tokens → Fine-grained tokens),
    **nur für `TTC_Neuhausen-News`**, Repository permissions → Contents
    «Read and write» – sonst nichts, insbesondere nicht «Workflows». Mit
    ihm holt auch der Workflow die News. Er läuft ab; GitHub mahnt vorher
    per Mail, dann einen neuen eintragen.
  - `REDAKTION_PASSWOERTER`: je Person eine Zeile. Die Person erstellt sie
    selbst unter `/admin/passwort.html` (`Name: pbkdf2-sha256$…`, eine
    Prüfzeile – ihr Passwort verlässt dabei ihren Browser nicht, auch der
    Verwalter kennt es nicht). `Name: Passwort` geht ebenfalls (mindestens
    12 Zeichen). Beim Namen zählt Gross/klein nicht. Das Secret lässt sich
    nicht auslesen: zum Ändern alle Zeilen neu eintragen, die Liste also
    aufbewahren (Prüfzeilen sind dafür unbedenklich).
  - Auf den Server gehen nur bekannte Dateiarten (`veroeffentlichen.py`,
    `ERLAUBT`); PHP nur `admin/anmelden.php`, und die `.htaccess` sperrt
    jede andere PHP-Datei. In die Ordner, in die die Redaktion hochlädt,
    kommen nur Bilder bzw. Dokumente.
  - `veroeffentlichen.py` legt daraus auf dem Server `admin/zugang.php` an,
    die Passwörter nur als Prüfsumme (PBKDF2); die `.htaccess` liefert die
    Datei nie aus. Nach fünf Fehlversuchen sperrt `anmelden.php` die
    Adresse für 15 Minuten.
  - **Jemand hört auf:** Zeile löschen, Workflow laufen lassen. Wer noch
    angemeldet ist, bleibt es aber, bis der Schlüssel wechselt – im
    Zweifel einen neuen Schlüssel erstellen, den alten löschen; dann melden
    sich alle neu an.
- **Version:** fest eingestellt in `site/admin/index.html`, mit
  `integrity`-Prüfsumme. Für eine neue Version beides zusammen ändern.

## Veröffentlichen auf Hostpoint

`.github/workflows/hostpoint.yml` läuft bei jedem Push auf `main` und nach
jedem «Speichern» in der Redaktion: holt die News-Ablage, baut mit
`build.py --bilder-verkleinern` und lädt per SFTP hoch, **nur was sich
geändert hat** (`veroeffentlichen.py`). Nach ein bis zwei Minuten ist die
Website aktuell; von Hand hochladen ist nicht mehr nötig.

- **Zwei getrennte Schritte:** «bauen» liest die News-Ablage und kennt kein
  Passwort des Servers; «hochladen» bekommt nur das fertige `site/` und
  führt nichts aus der Ablage aus. Es lädt nur bekannte Dateiarten, bricht
  ab, wenn `site/` unvollständig ist, und löscht nie auf einen Schlag einen
  grossen Teil der Website ohne Bestätigung von Hand.
- **Anstoss aus der Redaktion:** In der News-Ablage läuft nach jedem Commit
  `.github/workflows/melden.yml` und startet den Workflow hier (Secret
  `WEBSITE_AUSLOESEN` dort: Fine-grained token nur für dieses Repository,
  Actions «Read and write»).

- **Was oben ist**, steht auf dem Server in `.veroeffentlicht.json`.
  Gelöscht wird nur, was die Pipeline selbst hochgeladen hat; alles andere
  im Ordner bleibt liegen.
- **Das allererste Mal** lädt ein Push nichts hoch, sondern zeigt im
  Protokoll, was im Zielordner liegt und was er hochladen würde. Stimmt das,
  startet man den ersten Upload von Hand: Actions → «Website auf Hostpoint»
  → Run workflow. Dort gibt es auch «Nur anzeigen» und «Alles neu hochladen».
- **Zugang:** die Secrets `HOSTPOINT_SERVER`, `HOSTPOINT_BENUTZER`,
  `HOSTPOINT_PASSWORT`, `HOSTPOINT_ORDNER`, dazu für die Redaktion
  `REDAKTION_SCHLUESSEL` und `REDAKTION_PASSWOERTER` (Settings → Secrets
  and variables → Actions). Welche, steht oben in `hostpoint.yml`.
- **`site/` im Repository** kann hinter der Website zurückliegen: der Server
  bekommt immer den Build von GitHub, nicht die Dateien, die jemand lokal
  gebaut hat. Wer lokal arbeitet, holt vorher die neuen Commits (Pull) –
  die Redaktion schreibt ja mit.

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
- Weiterleitungen: jede alte Adresse zeigt auf eine Seite und Sprungmarke,
  die es gibt
- Zahl der Einheiten und Stunden im Trainingsplan

Dazu schreibt er `.nojekyll`, `robots.txt`, `sitemap.xml`, `.htaccess` und
`hol-dokumente.ps1`.

## Vorschau auf GitHub Pages

```
python3 build.py --vorschau https://name.github.io/ttcn-vorschau/
```

Der Schalter setzt `canonical`, `og:url` und `og:image` auf die
Vorschauadresse, gibt jeder Seite `noindex`, sperrt Suchmaschinen per
`robots.txt` aus und lässt `sitemap.xml` und `.htaccess` weg. Ohne
Schalter wird alles zurückgenommen.
`.github/workflows/vorschau.yml` baut bei jedem Push mit der richtigen
Adresse und veröffentlicht `site/`. Einrichten: Repository öffentlich,
unter *Settings → Pages* die Quelle auf **GitHub Actions** stellen.

## Suchmaschinen (SEO)

**Das Wichtigste sind die alten Adressen.** Die bisherige Website hat rund
2900 Adressen bei Google (89 Seiten, 2577 Beiträge seit 2008, 208 Anlässe).
Darauf verweisen Google, Verbände, andere Vereine und Zeitungen. Ohne
Weiterleitung wären das nach der Umstellung 2900 tote Links, und die neue
Website finge bei Google von vorne an.

`build.py` schreibt deshalb `site/.htaccess` (Apache, wie der bisherige
Server). Die Liste steht in **`vorlage/seo.py`**:

- `WEITERLEITUNGEN` – jede alte Seite auf ihre neue, z. B. `/trainingszeiten/`
  → `training.html`, die zwanzig Mannschaftsseiten → `teams.html`
- `MUSTER` – ganze Bereiche: alle Beiträge `/2018/02/22/…` → `news.html`,
  Anlässe → Jahresprogramm, Kategorien und Schlagworte → News
- `WEG` – die Vorlagenseiten des alten Themes («Sample Page», «Portfolio»):
  «410 Gone», damit Google sie vergisst
- die Dokumente der alten Website (aus `dokumente.py`) direkt auf die
  neuen Dateien

Alle Weiterleitungen zeigen absolut auf `https://www.ttc-neuhausen.ch/…`:
jede alte Adresse kommt in **einem** Schritt an, auch von `http://` oder
ohne `www`. Geprüft am 5. Oktober 2026 mit Apache 2.4 und allen 2910
Adressen der alten Sitemap: 2873 landen in einem Schritt auf einer Seite,
37 melden 410, keine endet im Leeren. Die `.htaccess` braucht nur, was
WordPress schon brauchte (mod_rewrite); auf Hosting mit «AllowOverride
FileInfo» läuft sie ohne Fehler 500.

**Die alten Beiträge.** 2577 Berichte gibt es auf der neuen Website nicht;
sie führen auf `news.html`. Google behandelt das mit der Zeit wie gelöscht.
Wer sie behalten will: das alte WordPress als Archiv weiterlaufen lassen
(etwa unter `archiv.ttc-neuhausen.ch`) und die Adresse in `seo.py` bei
`NEWS_ARCHIV` eintragen. Dann führt jeder alte Beitrag 1:1 ins Archiv.

**Was sonst auf jeder Seite steht**, alles von `build.py` erzeugt:

- Titel und Beschreibung aus `seiten.py`. Titel unter 60 Zeichen, mit dem,
  was gesucht wird («Tischtennis für Kinder und Jugendliche»), der
  Vereinsname am Schluss. Beschreibung unter 160 Zeichen.
- `canonical`, Open Graph (Vorschau auf WhatsApp, Facebook), `robots` mit
  grosser Bildvorschau
- **Strukturdaten** (JSON-LD): der Verein als `SportsClub` mit Logo,
  Gründungsjahr, Verband und Profilen; die beiden Hallen mit Adresse und
  Koordinaten (für Google Maps); Brotkrumen aus der sichtbaren
  Navigation; News-Beiträge mit Fliesstext als `NewsArticle`. Prüfen:
  <https://search.google.com/test/rich-results>
- `sitemap.xml` und `robots.txt`
- eine Fehlerseite `404.html` mit den meistgesuchten Seiten, `noindex`

**Nach der Aufschaltung:** In der [Google Search Console](https://search.google.com/search-console)
die Domain bestätigen, `https://www.ttc-neuhausen.ch/sitemap.xml`
einreichen und in den ersten Wochen unter «Seiten» nachsehen, ob alte
Adressen als «Nicht gefunden (404)» auftauchen. Jede davon gehört in
`seo.py`. Das Google-Unternehmensprofil (Maps) sollte auf die neuen
Hallenseiten verlinken.

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
- Fehlende Dokumente holen (`hol-dokumente.bat`), dann bauen – **solange
  die alte Website noch läuft**, danach sind die Dateien weg.
- Entscheiden, ob das alte News-Archiv weiterläuft (`NEWS_ARCHIV` in
  `vorlage/seo.py`, siehe «Suchmaschinen»).
- Hochladen erledigt die Pipeline, `.htaccess` inklusive (siehe
  «Veröffentlichen auf Hostpoint»). Liegt im Zielordner noch das alte
  WordPress, vorher dessen `index.php` entfernen – sonst kann der Server
  weiter WordPress statt `index.html` ausliefern. Danach stichprobenweise
  alte Adressen aufrufen, z. B. `/trainingszeiten/`.
- Sitemap in der Google Search Console einreichen.
