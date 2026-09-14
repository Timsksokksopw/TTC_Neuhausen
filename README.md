# TTC Neuhausen — Website-Prototyp

Statische Website, aufgebaut auf einem Design-System aus dem Vereinslogo.
Stand: 24. August 2026. Gestaltung und Umsetzung: Wendico.

## Öffnen

`site/index.html` im Browser öffnen. Es braucht keinen Server — die Seiten
laufen direkt vom Dateisystem.

## Muss ich Python können?

Nein. **Der Ordner `site/` ist die fertige Website** und wird jedes Mal
fertig gebaut mitgeliefert. Zum Anschauen, Hochladen oder Weitergeben
braucht es gar nichts.

`build.py` ist nur nötig, wenn **du selbst** etwas in `inhalt/` oder
`vorlage/` änderst. Dann:

1. Python holen, falls nicht vorhanden: <https://www.python.org/downloads/>
   — bei der Installation **«Add Python to PATH» ankreuzen**, sonst findet
   Windows es nachher nicht.
2. Im Explorer in den Projektordner gehen, mit der rechten Maustaste auf
   eine freie Stelle klicken → **«Im Terminal öffnen»**.
3. `python build.py` eintippen, Enter. (Auf Windows heisst der Befehl
   `python`, nicht `python3`.)

Es erscheint eine Liste der gebauten Seiten und darunter die Prüfungen.
Alles, was `build.py` schreibt, landet in `site/` — kaputt machen kann man
damit nichts, was nicht der nächste Lauf wieder richtet.

**Die Vereinsdokumente holst du ohne Python**: `hol-dokumente.bat`
doppelklicken, siehe unten.

## Ordner

```
ttcn-website/
├── build.py              Setzt die Seiten zusammen und prüft sie
├── hol-dokumente.bat     Holt die Vereinsdokumente — auf Windows doppelklicken
├── hol-dokumente.ps1     … dahinter; erzeugt von build.py, nicht von Hand ändern
├── hol-dokumente.py      … dasselbe für alle, die Python haben
├── .github/workflows/    Veröffentlicht die Vorschau auf GitHub Pages
├── vorlage/
│   ├── layout.html       Kopfzeile, Fuss, <head> — steht genau einmal im Projekt
│   ├── seiten.py         Adresse der Website, Navigation, Seitenverzeichnis
│   ├── trainingszeiten.py  Alle Trainingseinheiten der Woche
│   ├── mannschaften.py   Die Teams und ihre click-tt-Adressen
│   ├── sponsoren.py      Partner und Ausrüster
│   ├── geschichte.py     Zeitleiste, Vereinsarchiv, Meistertitel
│   ├── news.py           Beiträge — Karten, Liste und Beitragsseiten
│   └── dokumente.py      Downloads, Beitrittsformulare, Anmeldeformular
├── inhalt/               Ein Fragment je Seite, nur der <main>-Inhalt
└── site/                 Erzeugt — das ist die fertige Website
    ├── *.html            27 Seiten, dazu je eine je Beitrag mit Text
    └── assets/
        ├── css/
        │   ├── tokens.css        Farben, Schrift, Abstände, Schleier
        │   ├── base.css          Reset, Textfluss, Flächenkontexte
        │   ├── komponenten.css   Navigation, Buttons, Karten, Fotos, Tabellen, Fuss
        │   └── seiten.css        Hero, Auftakt, Trainingsplan, Zeitleiste, Beitrag
        ├── js/main.js
        ├── dokumente/            Statuten, Reglemente, Beitrittsformulare
        └── img/
            ├── logo*, signet, favicons
            ├── og-standard.jpg   Vorschaubild beim Teilen
            └── fotos/            Die Bildplätze der Website
```

## Ändern

**Inhalt einer Seite:** Datei in `inhalt/` bearbeiten, dann `python3 build.py`.

**Neue Seite:** Fragment in `inhalt/` anlegen, Eintrag in `vorlage/seiten.py`
ergänzen, `python3 build.py`.

**Menü, Kopfzeile oder Fuss:** `vorlage/seiten.py` beziehungsweise
`vorlage/layout.html` ändern, dann neu bauen. Die Änderung greift auf allen
27 Seiten.

**Farben oder Schriftgrössen:** nur `site/assets/css/tokens.css`. Kein
Farbwert steht ausserhalb dieser Datei — geprüft beim Build.

Warum der Build-Schritt: Kopfzeile, Navigation und Fuss stehen dadurch genau
einmal im Projekt. Ohne ihn müsste jede Menüänderung in 27 Dateien
nachgezogen werden, und genau dort entstehen in statischen Prototypen die
Abweichungen.

`build.py` meldet nach jedem Lauf drei Dinge: fehlende oder nicht
eingetragene Fragmente, Farbwerte ausserhalb von `tokens.css`, und verlinkte
Bilder, die es nicht gibt. Der letzte Punkt fängt den häufigsten Fehler nach
einem Bildwechsel ab — im Browser fällt ein falscher Dateiname sonst erst
auf, wenn jemand genau diese Stelle aufruft.

## Trainingszeiten ändern

**Nur `vorlage/trainingszeiten.py`, dann `python3 build.py`.**

Daraus entstehen drei Darstellungen, die sich nicht mehr auseinander
entwickeln können:

- das Wochenraster auf `training.html`
- die Tabelle darunter, mit Trainerangaben
- die Zeitentabellen auf `training-nachwuchs.html`,
  `training-breitensport.html` und `training-senioren.html`

Vorher standen dieselben Zeiten viermal abgetippt im HTML. Wer sie an
einer Stelle änderte, liess die anderen drei veralten.

**Die Zeitachse** steht als `RASTER_BAENDER` in derselben Datei. Sie
überspringt die Mittagsstunden, in denen nichts stattfindet — sonst
verbrauchte die leere Zeit einen guten Drittel der Breite, und die fehlt
genau dort, wo abends mehrere Angebote nebeneinanderliegen. Der Sprung ist
im Raster als Bruch markiert. Eine Einheit ausserhalb der Bänder bricht
den Build ab, mit dem Hinweis, welches Band fehlt — so ist es beim
Mittwochstraining am 25. August auch aufgefallen.

**Überschneidungen** rechnet `build.py` selbst aus. An drei Abenden
überlappen Nachwuchs und Breitensport um eine halbe Stunde; die Blöcke
rücken dann automatisch auf zwei Bahnen untereinander. In den alten
Tabellen war das nicht zu sehen.

**Lange Bezeichnungen:** Ein Block im Raster ist je nach Dauer 120 bis 250
Pixel breit. Passt der volle Name nicht, bekommt die Einheit ein Feld
`kurz` — das steht dann im Raster, während Tabellen und Unterseiten
weiterhin die volle Bezeichnung des Vereins tragen.

**`build.py` meldet nach jedem Lauf** die Zahl der Einheiten und die
geleiteten Stunden pro Woche. Die Startseite und `verein.html` nennen
diese Zahl von Hand; so fällt auf, wenn sie auseinanderlaufen.

## Was der Build sonst noch anlegt

Neben den Seiten schreibt `build.py` drei Dateien nach `site/`:

- **`.nojekyll`** — sonst schickt GitHub Pages alles durch Jekyll.
- **`robots.txt`** — bei jedem Lauf neu, passend zum Modus. Nach einer
  Vorschau bliebe sonst ein `Disallow` stehen und die echte Website wäre
  für Google gesperrt.
- **`sitemap.xml`** — **hat vorher gefehlt.** `robots.txt` hat sie
  angekündigt, es gab sie aber nicht: jede Suchmaschine, die dem Verweis
  folgte, lief in einen Fehler 404. Sie entsteht jetzt aus derselben
  Liste wie die Seiten und kann deshalb weder eine vergessen noch eine
  nennen, die es nicht gibt. In der Vorschau-Fassung wird sie gelöscht —
  dort ist ohnehin alles gesperrt, und eine Sitemap mit den
  Vorschau-Adressen wäre eine Einladung, genau die zu indexieren.

## Nichts zeigt mehr auf die alte Website

Das war eine eigene Runde Arbeit, und sie ist erledigt: **kein `href` und
kein `src` in diesem Projekt zeigt noch auf das bisherige WordPress.**
Geprüft mit

```
grep -rnoE '(href|src)="https?://(www\.)?ttc-neuhausen\.ch[^"]*"' inhalt vorlage site
```

Was dabei **stehen bleibt und stehen bleiben muss**, ist `SEITE_URL` in
`vorlage/seiten.py`. Daraus baut der Build `canonical`, `og:url` und
`og:image` — das ist die Adresse der **neuen** Website, nicht ein Verweis
auf die alte. Sie sieht im Suchergebnis nur gleich aus.

Drei Dinge hingen daran:

**Die News** lagen gar nicht auf dieser Website. Die Karten verwiesen auf
die WordPress-Beiträge. Jetzt gibt es `vorlage/news.py` (siehe unten).

**Die vierzehn Downloads** lagen als PDF, XLSX und DOCX beim alten
WordPress. Jetzt gehören sie hierher, siehe `vorlage/dokumente.py`.

**Das Anmeldeformular** ist ein Microsoft-Forms-Formular, das auf der
alten Seite «Mitglied werden» eingebettet war; der Knopf zeigte auf jene
Seite. Jetzt zeigt er direkt auf das Formular — kein iframe, aus
demselben Grund wie bei den Ligatabellen. Die Adresse steht in
`vorlage/dokumente.py` unter `ANMELDEFORMULAR`. **Einmal anklicken und
prüfen**, ob das richtige Formular aufgeht.

## News

**Nur `vorlage/news.py`, dann `python3 build.py`.**

Daraus entstehen die drei Karten auf der Startseite, die Liste auf
`news.html` **und die Beitragsseiten selbst**. Vorher stand jeder Beitrag
zweimal abgetippt im HTML, und der Text stand gar nicht auf dieser
Website.

**Der Kern der Sache:** Hat ein Beitrag Fliesstext, erzeugt `build.py`
daraus `news-<kennung>.html`, und Karte wie Listeneintrag verweisen
darauf. Hat er keinen, bleibt er eine Meldung — Datum, Titel,
Herkunftsangabe, **ohne Verweis**. Eine Karte, die auf eine leere Seite
führt, ist schlechter als eine, die nicht klickbar ist; und ein Verweis
zurück auf die alte Website ist keine Lösung, sondern das Problem.
`build.py` zählt nach jedem Lauf, wie viele Beiträge noch ohne Text sind.

Für den Fliesstext gibt es neben dem gewöhnlichen Absatz drei Formen:
`titel` (Zwischentitel), `zitat` (mit Namensangabe) und `liste` (etwa
eine Rangliste, zweispaltig gesetzt). Wie sie geschrieben werden, steht
oben in `news.py`.

**Die drei bestehenden Beiträge haben noch keinen Text.** Titel, Datum,
Herkunftsangabe und Bild sind an der alten Website nachgeprüft, der
Fliesstext fehlt. Er ist von Lyo Bührer geschrieben — eine nacherzählte
Fassung unter seinem Namen wäre keine Übernahme, sondern eine Fälschung.
Also: aus dem alten Redaktionssystem kopieren, in `news.py` einsetzen,
neu bauen. Die Seiten entstehen dann von selbst.

## Downloads und Beitrittsformulare

**Nur `vorlage/dokumente.py`, dann `python3 build.py`.**

Die Dateien gehören nach `site/assets/dokumente/`. Beim ersten Mal holt
sie ein Skript in einem Durchgang von der bisherigen Website und benennt
sie gleich richtig:

| Wo | Was tun |
|---|---|
| **Windows** | `hol-dokumente.bat` **doppelklicken**. Braucht nichts ausser dem, was auf jedem Windows schon drauf ist. |
| macOS, Linux, oder mit Python | `python3 hol-dokumente.py` |

Beide machen dasselbe und arbeiten dieselbe Liste ab. Die `.ps1` hinter
der `.bat` wird von `build.py` aus `dokumente.py` **erzeugt** — abgetippt
wären es zwei Listen, die auseinanderlaufen können. Sie ist deshalb nicht
von Hand zu ändern.

Das Skript läuft **einmal**, vor dem Umzug, und gehört bewusst nicht in
den Build: eine Website, die bei jedem Bauen fremde Server anfragt, baut
irgendwann nicht mehr.

Es lädt nur die Adressen, die in `dokumente.py` unter `herkunft` stehen —
die eigenen Dateien des Vereins. Eine Antwort, die weder mit `%PDF-` noch
mit einem ZIP-Kopf beginnt und kleiner als 4 kB ist, wird **nicht**
gespeichert: sonst läge irgendwann eine «Seite nicht gefunden» als
Statuten im Ordner, und es fiele erst auf, wenn jemand sie öffnet.
Geprüft mit einem nachgestellten Server, der genau so eine Fehlerseite
statt der Statuten ausliefert — die dreizehn echten Dateien kamen an, die
Fehlerseite wurde abgewiesen.

**Ganz ohne Skript geht es auch:** die vierzehn Adressen im Browser
öffnen, die Dateien nach `site\assets\dokumente\` legen und dabei so
benennen, wie `dokumente.py` es unter `datei` sagt. `build.py` nennt nach
jedem Lauf beides — Name und Adresse — nebeneinander.

**Solange eine Datei fehlt**, steht ihr Eintrag ohne Verweis in der Liste
und trägt rechts «folgt» statt «PDF». Kein Fehler 404, kein Verweis
zurück. `build.py` nennt nach jedem Lauf die fehlenden Dateien samt der
Adresse, unter der sie zu holen sind.

Nebenbei: der Pfeil beim Dateiformat zeigt jetzt nach unten (↓) statt
schräg hinaus (↗). Das Dokument kommt herunter, es führt nicht mehr aus
der Website hinaus. Bei den Ligatabellen bleibt der schräge Pfeil.

## click-tt und die Teams-Seite

**Es gibt kein Widget.** click-tt.ch läuft auf nuLiga von nu Datenautomaten
und bietet weder ein offizielles Widget noch eine öffentliche
Schnittstelle — nachgeprüft bei click-tt.ch, Swiss Table Tennis und in den
Vereinsforen. Die frühere Notiz an dieser Stelle nannte ein
«hb_api-Widget von sportred»; das gehört zu handball.net und führt ins
Leere. Die Club-ID 33244 stimmt.

Was Vereine ersatzweise machen, ist ein iframe auf die nuLiga-Seite. Das
holt fremdes Layout in die eigene Seite, hat eine feste Höhe, ist auf dem
Handy mühsam, setzt Cookies eines Dritten — und ob nuLiga das Einbetten
zulässt, ist nirgends zugesichert und kann jederzeit gesperrt werden.

Deshalb hier der Weg, der immer funktioniert: `vorlage/mannschaften.py`
führt alle Teams mit Liga, Gruppe und Gruppennummer, `build.py` baut
daraus die Übersicht auf `teams.html`. Jede Zeile öffnet die offizielle
Tabelle bei click-tt. Auf der eigenen Seite steht damit nichts, was
veralten könnte.

**Zum Saisonwechsel:**

1. `https://www.click-tt.ch/cgi-bin/WebObjects/nuLigaTTCH.woa/wa/clubTeams?club=33244` öffnen
2. Für jede Mannschaft den Link auf die Ligatabelle kopieren
3. In `mannschaften.py` `championship` und `gruppe_id` nachführen, `SAISON` anpassen
4. `python3 build.py`

**Eine Falle bei den Adressen:** nuLiga erwartet das Leerzeichen im
Saisonkürzel als `+` und den Schrägstrich als `%2F`, also
`championship=STT+26%2F27`. Mit `%20` statt `+` öffnet die Seite ohne
Fehlermeldung eine *andere* Liga. `build.py` kodiert das richtig; wer
Adressen von Hand einträgt, sollte es wissen.

## Sponsoren ändern

**Nur `vorlage/sponsoren.py`, dann `python3 build.py`.**

Daraus entstehen der Partnerabschnitt auf der Startseite, das Raster auf
`partner.html` und die Zahl im Text — die stand vorher an drei Stellen
von Hand und war nach jeder Änderung falsch.

Jeder Eintrag hat ein Feld `logo`. Solange es leer ist, trägt die Kachel
den Firmennamen. Sobald dort ein Dateiname unter
`site/assets/img/partner/` steht, zeigt die Kachel das Logo — das
Raster bleibt gleich, es muss nichts umgebaut werden.

Der Ausrüster steht in derselben Datei als `AUSRUESTER` und erscheint als
eigenes Band über dem Raster, nicht als eine Kachel unter vielen.

### Ein neues Logo aufbereiten

Unter `site/assets/img/partner/` liegen **aufbereitete** Fassungen; die
Originale bleiben unangetastet in `site/assets/img/Sponsoren/`.

> **Warum «partner» und nicht «sponsoren»:** Windows unterscheidet in
> Dateinamen keine Gross- und Kleinschreibung. `sponsoren/` und
> `Sponsoren/` wären dort derselbe Ordner — die aufbereiteten Dateien
> lägen zwischen den Originalen, und ein Linux-Webserver, der sehr wohl
> unterscheidet, fände sie danach nicht mehr. Das wäre erst nach dem
> Aufschalten aufgefallen.

Aufbereitet heisst: freigestellt, auf die Marke beschnitten und mittig auf
eine Leinwand von **480 × 300** gesetzt — dabei nicht auf gleiche Breite
skaliert, sondern auf gleiche **Fläche**. Das ist der Unterschied zwischen
einer ruhigen und einer unruhigen Sponsorenwand: mit `object-fit` allein
wird ein 6:1-Wortzeichen winzig und ein quadratisches Signet riesig,
obwohl beide dieselbe Kachel füllen. Über die Fläche wiegen sie optisch
gleich viel. Im Stylesheet steht deshalb nur `width: 100%`.

Wer ein neues Logo dazulegt, macht es genauso: freistellen, beschneiden,
auf 480 × 300 zentrieren, Zielfläche rund 34 000 Pixel, Deckel bei
440 × 224. Dann in `sponsoren.py` den Dateinamen eintragen.

Zwei Dinge, über die man dabei stolpert:

- **Weisse Hintergründe stehen lassen.** Die Hälfte der Logos kommt mit
  weissem Grund. Die Kachel ist reines Weiss, dort verschwindet er. Weiss
  wegzurechnen zieht bei weichen Kanten (dem Falken) einen grauen Saum.
  Aus demselben Grund wechselt die Kachel beim Überfahren **nicht** die
  Hintergrundfarbe — sonst blitzen die weissen Kästen als Rechtecke auf.
- **Nur Hintergrund entfernen, der zusammenhängend am Rand liegt.** Bei
  Remondis geht das rote Markenfeld bis an den oberen Bildrand; ein
  globaler Farbtausch hätte das Feld mitgenommen und hohle
  Buchstabenumrisse hinterlassen.

## Fotos einsetzen

Unter `site/assets/img/fotos/` liegt für jeden Bildplatz eine erzeugte
Platzhalterdatei. Zum Auswechseln: **gleicher Dateiname, Datei ersetzen,
`python3 build.py`.** Am HTML muss nichts geändert werden.

| Datei | Format | Wo es erscheint |
|---|---|---|
| `hero-halle.jpg` | ab 2000 px breit, quer | Startseite, ganzflächig hinter dem Titel |
| `angebot-nachwuchs.jpg` | 900 × 675 (4:3) | Startseite, Karte Nachwuchs |
| `angebot-breitensport.jpg` | 900 × 675 (4:3) | Startseite, Karte Breitensport |
| `angebot-senioren.jpg` | 900 × 675 (4:3) | Startseite, Karte Senioren |
| `angebot-schulen.jpg` | 900 × 675 (4:3) | Startseite, Karte Für Schulen |
| `halle-ebnat.jpg` | 1200 × 1500 (4:5) | Startseite, Bildsplit TTZ Ebnat |
| `helfer.jpg` | 900 × 675 (4:3) | Startseite, Helfereinsatz |
| `news-1.jpg` … `news-3.jpg` | 900 × 506 (16:9) | Startseite, letzte Beiträge |
| `og-standard.jpg` | 1200 × 630 | Vorschau beim Teilen — kein Foto, sondern eine gesetzte Karte |

Alle Bilder liegen in einem `.foto`-Rahmen mit `object-fit: cover`. Ein
abweichender Zuschnitt verzieht deshalb nichts, er wird mittig beschnitten.
Wichtig ist nur, dass das Motiv nicht ganz am Rand sitzt.

Für das Hero-Foto: querformatig, eher dunkel, Hauptmotiv rechts. Links liegt
ein Schleier, damit die Schrift lesbar bleibt — was dort steht, ist ohnehin
verdeckt.

## Geschichte und Archiv ändern

**Nur `vorlage/geschichte.py`, dann `python3 build.py`.**

Daraus entstehen die Zeitleiste, die Archivkapitel und das Jahresraster der
Meistertitel. Die Bildmasse liest der Build selbst aus den Dateien — sie
stehen nirgends von Hand, und ein neu zugeschnittenes Bild bringt seine
Masse einfach mit.

Ein Archivstück kennt drei Formen:

| `art` | wofür | wie es läuft |
|---|---|---|
| `streifen` | Filmstreifen, Kontaktbögen | über beide Spalten; auf dem Handy in einem eigenen Scrollfenster, damit die Bilder gross genug bleiben |
| `blatt` | Albumblätter, Einzelaufnahmen | im Raster, jedes in seinem eigenen Seitenverhältnis |
| `dokument` | Papier — Programm, Plakat, Urkunde | über beide Spalten, mit dem Text daneben |

Dazu `klein: True`, wenn die Vorlage zu klein für eine grosse Ansicht ist.
Das Stück läuft dann im Raster mit, lässt sich aber nicht vergrössern —
besser als ein unscharfes Vollbild.

Die Bilder liegen unter `site/assets/img/archiv/`. Sie sind bewusst **nicht**
auf ein einheitliches Mass beschnitten: die Sprossenlöcher, die Bildnummern,
«ILFORD HP5 PLUS» am Rand und die Handschrift «Glissahalle, Nov./Dez. 01»
sind das, was die Stücke sehenswert macht. Ein Kontaktbogen *ist* schon eine
Galerie.

Tims Originale liegen unverändert daneben in `site/assets/img/Geschichte/`.

## Personen: Porträt oder Kürzel

Auf `verein-vorstand.html` und `verein-trainerteam.html` trägt jede Karte
links entweder ein Bild oder das Kürzel der Person:

```html
<img class="person__marke" src="assets/img/personen/urs-schaerrer.jpg" alt=""
     width="60" height="60" loading="lazy">
<!-- oder -->
<p class="person__marke" aria-hidden="true">MH</p>
```

`alt=""` ist Absicht: der Name steht direkt daneben, das Bild trägt für
eine Vorlesesoftware nichts bei.

Die Bilder sind quadratisch zugeschnitten und liegen unter
`site/assets/img/personen/`. Die vier gelieferten Vorlagen sind 100 × 150
Pixel gross — deshalb 60 Pixel Anzeigebreite und keine mehr. Sie laufen
entsättigt (`filter: grayscale(1)` in `komponenten.css`), weil die vier
Aufnahmen aus vier verschiedenen Situationen stammen. Kommen einheitliche
Bilder, ist das eine Zeile weniger.

## Die Kopfzeile

Sie weicht beim Hinunterscrollen und kommt beim Hochscrollen zurück — auf
allen Seiten. Ganz oben (unter 140 px Scrollstand) ist sie immer da.

Zwei Schwellen, beide nötig: erst ab **140 px** darf sie überhaupt weichen,
sonst zuckt sie schon bei der ersten Radrastung. Und sie reagiert erst ab
**6 px** Richtungsänderung — ohne diese Totzone flackert sie am Trackpad,
dessen Werte um ein, zwei Pixel schwanken.

**Das offene Menü hält sie fest.** Wer auf dem Handy das Menü aufklappt und
darin scrollt, verlöre sonst die Kopfzeile samt Schliessknopf. Ebenso
kommt sie zurück, sobald etwas in ihr den Fokus bekommt — für alle, die
per Tastatur navigieren.

Ohne JavaScript bleibt sie schlicht immer stehen, also genau so wie vorher.

## Der Auftakt auf der Startseite

Fünfzig Einzelbilder einer gezeichneten Kamerafahrt über den Tisch. Beim
Scrollen läuft die Folge durch, danach beginnt die Seite.

**Er läuft ab `min-width: 1024px`**, nicht bei
`prefers-reduced-motion: reduce`, und nicht ohne JavaScript. In allen
anderen Fällen übernimmt der Hero darunter, der auf dem Laptop
ausgeblendet ist — es ist immer genau ein Auftakt da, nie zwei und nie
keiner.

**Hier stand einmal `hover: hover` dazu**, gedacht als «hat ein
Zeigergerät», um Tablets auszuschliessen. Sie hat den Auftakt auf
**Laptops mit Touchscreen** abgeschaltet: Chrome hält dort den Finger für
das erste Zeigergerät und meldet `hover: none`, obwohl ein Trackpad
danebenliegt. Das betrifft einen grossen Teil aller heute verkauften
Laptops — genau die Geräte, für die der Auftakt gemacht ist. Aufgefallen
ist es erst, als Tim den Effekt auf seinem eigenen Rechner nicht sah, denn
die Seite zeigt dann einfach den Hero und sieht völlig in Ordnung aus.

Nachgemessen gilt dasselbe für `any-hover`, `pointer` und `any-pointer` —
sobald ein Touchscreen im Spiel ist, melden sie alle «grob». Auf diese
Familie von Abfragen ist kein Verlass, wenn es darum geht, ein
Laptop von einem Tablet zu unterscheiden.

Die Breite allein tut, was verlangt war («nicht auf dem Handy»): auch das
grösste Handy quer misst rund 930 px. Ein Tablet quer bekommt den Auftakt
jetzt ebenfalls — bewusst in Kauf genommen, weil das Scrubben per Touch
funktioniert und die Alternative war, ihn auf jedem Touch-Laptop zu
verlieren.

Wichtig: **auf dem Handy wird kein einziges Bild geladen.** Die 1.3 MB
holt das Skript erst, wenn die Bedingung stimmt. Geprüft an acht Fällen:
1440, 1280, **1440 mit Touchscreen**, Tablet 1024 quer, **Handy quer
932 px**, Handy 390, reduzierte Bewegung, ohne JavaScript.

**Die Bedingung steht zweimal** — als `@media` im Stylesheet, das den
Abschnitt einblendet, und als `matchMedia` im Skript, das die Bilder holt.
`build.py` prüft, dass beide denselben Schirm meinen. Liefen sie
auseinander, gäbe es entweder einen eingeblendeten Abschnitt ohne Bilder
oder 1.3 MB Bilder für einen Abschnitt, den niemand sieht — beides sieht
man im Browser nicht.

### Bilder austauschen

Unter `site/assets/img/auftakt/` liegen `bild-01.webp` … `bild-NN.webp`,
**lückenlos durchnummeriert** — das Skript rechnet den Dateinamen aus dem
Bildindex aus. `build.py` zählt die Dateien selbst, trägt die Zahl ins
HTML ein und **bricht ab, wenn eine Nummer fehlt**.

Aufbereitet werden sie so: auf 1600 px Breite, WebP Qualität 80. Aus den
Originalen (1924 × 1076 JPEG, zusammen 24 MB) werden dabei 1.3 MB. Mehr
Breite bringt bei dieser flächigen Zeichnung nichts Sichtbares, kostet
aber sofort ein Megabyte.

Die Originale liegen in `Frames/` und sind in `.gitignore` — sie gehören
zum Material, nicht zur Website.

### Der Titel auf der Fahrt

Er liegt links, weil der Schleier dort am dichtesten ist, und ist in der
Breite begrenzt, damit er nicht in den hellen Teil hineinläuft. Beim
Abgehen wird er nicht bloss ausgeblendet, sondern steigt dabei ein Stück —
die Fahrt zieht unter ihm weg.

**`z-index: 2` ist hier keine Kosmetik.** Die Leinwand liegt absolut
positioniert über der Fläche; ein Textblock im normalen Fluss steht ohne
eigene Ebene dahinter und ist schlicht unsichtbar. Genau das war er eine
Fassung lang: das HTML stand da, der Schleier lag dafür bereit, das Skript
blendete ihn korrekt ab — nur sah man ihn nie. Die Ebenen lauten jetzt
Leinwand 0, Schleier 1, Titel 2, Abblende 3, Schlusskarte 4.

Gemessen am fertigen Bild, Kontrast je Glyphenpixel gegen den Untergrund
an genau derselben Stelle:

| Scrollstand | Deckung | Titel (Median / schlechtestes Pixel) | Lead |
|---|---|---|---|
| 0 % | 1.00 | 10.9:1 / **6.6:1** | 10.7:1 / **6.9:1** |
| 20 % | 0.80 | 6.4:1 / 4.5:1 | 5.7:1 / 4.5:1 |
| 30 % | 0.55 | 2.3:1 | 3.3:1 |

Solange der Titel voll dasteht, liegt selbst das schlechteste Pixel bei
6.6:1 — weit über AA. Ab 12 % geht er ab, und dann *soll* er verschwinden;
er steht nie statisch auf zu wenig Kontrast.

**Der Scrollhinweis steht nicht 24 px über dem unteren Rand, sondern
Kopfzeilenhöhe + 24.** Die klebende Fläche ist 100vh hoch und beginnt ganz
oben auf der Seite **unter** der Kopfzeile — ihr unterer Rand liegt also
anfangs um deren Höhe unter der Fensterkante. Mit blossen 24 px stünde der
Hinweis genau dann unter dem Fenster, wenn er gebraucht wird. Statt eine
Zahl zu raten, misst das Kopfzeilen-Skript die Höhe und veröffentlicht sie
als `--kopf-hoehe`; geprüft an 1024×768, 1280×720, 1440×900 und 1920×1080.

### Die Gestaltungsentscheide

**Der Schleier ist gerechnet, nicht geschätzt.** Der Textbereich der
fünfzig Bilder erreicht im hellsten Halbprozent RGB 234/245/255 — das sind
die weissen Tischlinien. Weisse Schrift darauf käme auf 1.1:1. Der Verlauf
hält dort, wo Text steht, mindestens rund 66 % Deckung; das ergibt selbst
über der hellsten Linie 5.7:1 und damit AA auch für die kleine Zeile. Nach
rechts läuft er aus, damit Schläger und Ball ihre Farbe behalten.

**Titel und Schleier gehen gemeinsam ab.** Der Titel steht bis 12 % ruhig
und ist bei 52 % weg; danach liegt die Fahrt frei. Erst lesen, dann
schauen, dann ankommen.

**Zwischen den Bildern wird überblendet.** Fünfzig Bilder sind für eine
Kamerafahrt wenig; hart umgeschaltet ruckelt es sichtbar. Deshalb wird der
Bruchteil zwischen zwei Bildern nicht weggerundet, sondern ausgespielt:
unteres Bild voll, oberes mit dem Bruchteil als Deckung darüber. Aus
fünfzig Stufen wird ein stufenloser Verlauf, ohne eine einzige zusätzliche
Datei.

Gemessen bei feinem Scrollen (8-px-Schritte, also Trackpad): **ohne
Überblendung zeigten 17 von 37 Schritten gar keine Änderung**, gefolgt von
einem Sprung — Verhältnis grösster zu mittlerer Änderung 3.27. Mit
Überblendung: kein einziger toter Schritt, Verhältnis 1.91.

**250vh Bühnenhöhe, davon 62 % für die Bilder.** Bei 100vh klebender
Fläche bleiben 150vh Weg; die Bildfolge läuft über die ersten 62 % davon,
also rund 18 px Scrollweg je Bild. Die übrigen 38 % gehören dem Schluss —
er braucht Platz, sonst ist er vorbei, bevor man ihn gesehen hat.

### Der Schluss

Er hat Tim zweimal nicht gefallen, und beide Male zu Recht. So sieht er
jetzt aus und das ist der Grund dafür:

**Die Fläche trägt die exakte Farbe des letzten Bildes.** `#66B2D2`, in
`tokens.css` als `--auftakt-grund`. Das ist kein passend gewähltes Blau,
sondern der Median der oberen 60 % von `bild-50.webp` — die Streuung liegt
dort bei rund 2 Werten je Kanal, die Fläche ist also praktisch einfarbig.
Nachgemessen an der fertigen Seite: letztes Bild `#66B3D3`, Abblende
`#66B2D2`. Ein Wert Unterschied in Grün und Blau, **die Naht ist
unsichtbar**.

**Der Ball muss erst weg sein.** Gezählt, nicht geschätzt: die gelbe
Fläche im Bild fällt über `bild-46` (3377 px) und `bild-47` (1914 px) auf
**null in `bild-48`** — dort ist der Ball hinter der Tischkante. Die
Abblende beginnt deshalb bei 60 % der Bühne, dem Moment, in dem sie
mathematisch leer ist, und ist bei 70 % durch. Dann steht die Fläche kurz
leer. Erst danach kommt die Karte.

**Der Bogen beginnt am Ball der Logofigur.** Das ist der Einfall, an dem
die ganze Karte hängt: der Ball kommt nicht irgendwoher zurück, sondern
wird gespielt — aus dem Vereinszeichen wird die Quelle der Bewegung statt
bloss eine Marke darunter. Der Anfangspunkt ist ausgemessen: im Logo ist
der Ball die einzige freistehende Form (Zusammenhangskomponente bei
x 79–84, y 25–29 der 511 × 120 grossen Vorlage, Mitte (81.5, 27.0)); über
den Anzeigefaktor 1.0176 und die Lage der Bogenfläche ergibt das
**(62.9, 215.5)**. Die Rechnung steht im Kommentar bei `.auftakt__wurf`;
wer das Logo tauscht, muss sie nachziehen.

**Vier Dinge nacheinander, alle am Scrollstand.** Ball herein und den
Bogen abfahren, während der sich unter ihm zeichnet — dann das Zeichen von
unten hoch — dann ein Strich, der aus der Mitte wächst — dann die Zeile.
Nichts davon läuft auf einer Zeitachse: wer zurückscrollt, sieht es
rückwärts. Das Skript setzt je Teil eine CSS-Variable, damit die
Staffelung an einer Stelle steht und nicht in verschachtelten `calc()`.

**Das Licht ist nicht Stimmung, sondern Kontrast.** Das Vereinsblau
`#00519E` käme auf der blossen Bildfarbe auf 3.32:1 — zu wenig. Der weiche
Lichtfleck darunter hebt den Grund auf rund 72 % Weiss; **gemessen am
fertigen Bild: 5.25:1**.

**Der Pfad steht zweimal** — als `<path d="…">` im HTML, damit er sich
zeichnen lässt, und als `offset-path` im CSS, damit der Ball ihn abfährt.
Ein gemeinsamer Ort ginge nicht: CSS kann keinen Pfad aus dem Dokument
lesen, SVG keinen aus dem Stylesheet. Dafür **prüft `build.py`, dass beide
gleich lauten** und bricht sonst ab. Gehen sie auseinander, sieht man
keinen Fehler, sondern nur einen Ball, der neben seiner eigenen Linie
herfliegt.

Aus demselben Grund hat der Ball **keinen Randausgleich**: `offset-anchor`
ist von Haus aus die Elementmitte, ein zusätzliches `margin: -18px` hätte
ihn um genau diese 18 px versetzt. Genau das war er eine Fassung lang, und
am Bogenende schaute die Spitze rechts unten unter ihm hervor.

Weil der Auftakt hell endet, ist auch **das Zahlenband darunter hell**
(`sektion--weiss`). Ein dunkles Band wäre eine Wand mitten in der Ankunft.
Auf dem Handy folgt es weiterhin auf den dunklen Hero — dort ist der
Wechsel gewollt.

**Gezeichnet wird auf `<canvas>`**, nicht über `src`-Wechsel an einem
`<img>`: ein Bildwechsel per `src` zeigt beim ersten Durchlauf kurz
nichts, die Leinwand behält ihr Bild, bis das neue da ist. Und es wird
**nicht auf das vollständige Laden gewartet** — gezeichnet wird immer das
nächstgelegene Bild, das schon da ist. Während des Ladens ist die Fahrt
dadurch grob und wird von selbst flüssig, statt dass ein Ladebalken die
Seite aufhält.

### Das Zahlenband

Es stand bis jetzt im Hero. Seit es zwei Auftakte gibt, schliesst es beide
ab und steht deshalb als eigene Sektion `.zahlenband` dazwischen.

## Vorschau auf GitHub Pages

Für Entwürfe, die jemand ansehen soll, bevor die Seite live geht.

```
python3 build.py --vorschau https://name.github.io/ttcn-vorschau/
```

Der Schalter ändert drei Dinge gegenüber dem normalen Bau:

- `canonical`, `og:url` und `og:image` zeigen auf die Vorschauadresse.
  Ohne das zeigt canonical auf `ttc-neuhausen.ch` — Google hielte den
  Entwurf für eine Kopie — und das Vorschaubild läge unter einer Adresse,
  die es dort noch nicht gibt: der Link hätte in WhatsApp und Instagram
  keine Vorschau.
- Jede Seite bekommt `<meta name="robots" content="noindex, nofollow">`.
- `site/robots.txt` sperrt Suchmaschinen komplett aus.

Ohne Schalter wird alles davon zurückgenommen. `robots.txt` wird bei
jedem Lauf neu geschrieben, damit nach einer Vorschau kein «Disallow» auf
der echten Website stehen bleibt.

**Einrichten (einmalig):**

1. Auf github.com ein Repository anlegen, zum Beispiel `ttcn-vorschau`.
   Es muss **öffentlich** sein — GitHub Pages funktioniert mit einem
   kostenlosen Konto nur bei öffentlichen Repositories. Deshalb das
   noindex: die Seite ist erreichbar, wer den Link hat, kommt rein.
2. Den Inhalt dieses Ordners hochladen (inklusive `.github/`).
3. Unter *Settings → Pages → Build and deployment → Source* auf
   **GitHub Actions** stellen.
4. Fertig. `.github/workflows/vorschau.yml` baut bei jedem Push neu und
   veröffentlicht `site/`. Die Adresse holt sich der Ablauf von GitHub
   selbst; sie muss nirgends eingetragen werden und stimmt auch nach
   einer Umbenennung noch.

Die Adresse steht danach unter *Settings → Pages* und im Reiter
*Actions* beim grünen Häkchen.

**Wenn die Vorschau nicht öffentlich sein darf:** GitHub Pages kann das
mit einem kostenlosen Konto nicht. Cloudflare Pages und Netlify können
eine Vorschau mit Passwort schützen — dort lädt man denselben `site/`-
Ordner hoch.

## Design-System

Alles leitet sich aus der gemessenen Logofarbe **#204E94** ab. Die ganze
Palette teilt deren Farbton (258.8° in OKLCH), auch die Grautöne. Vier
Flächen — dunkel, dunkel-erhöht, hell, weiss — plus das Vereinsblau als
Akzentfläche.

Eine Sektion setzt ihren Flächenkontext über eine Klasse
(`.sektion--dunkel`, `--hell`, `--weiss`, `--marke`), alle Komponenten darin
erben ihn. Ein Button braucht deshalb keine eigene Dunkel-Variante.

Über Fotos liegt immer ein Schleier aus derselben dunklen Fläche
(`--schleier-*`), damit heller Text unabhängig vom Bild lesbar bleibt.

Alle Text- und Flächenpaarungen sind gegen WCAG 2.1 AA geprüft. Das
Vereinsblau erreicht auf dunklem Grund nur 2.32 und wird dort deshalb nie
als Fläche oder Text eingesetzt — dafür steht `--ttc-blau-300`.

Schriften: Archivo (Auszeichnung), Atkinson Hyperlegible (Fliesstext),
Newsreader kursiv (Akzent). Alle drei unter SIL Open Font License.

**Bewegung** ist überall Zusatz, nie Voraussetzung. Der Ballbogen zeichnet
sich beim Scrollen, wo der Browser scroll-gesteuerte Animationen kennt; wo
nicht, steht er fertig da. Die eingeblendeten Elemente werden nur versteckt,
wenn JavaScript läuft — ohne JavaScript ist die Seite vollständig sichtbar.

## Am 24. August behoben

- **Hero auf dem Handy.** «Schnuppern» lief bei 390 px rechts aus dem Bild
  und wurde vom `overflow: hidden` des Heros abgeschnitten. Die oberste
  Schriftgradstufe war zu steil gestellt; dazu kommen jetzt `hyphens` und
  `overflow-wrap` als Auffangnetz.
- **Seiten liessen sich auf dem Handy seitwärts schieben.** Auf
  `training.html`, `training-nachwuchs.html` und `verein-mitglied-werden.html`
  sprengten die Tabellen die Seite: Raster-Elemente haben von sich aus
  `min-width: auto` und wachsen mit ihrem breitesten Inhalt mit. Jetzt
  scrollt die Tabelle in ihrem eigenen Kasten, die Seite steht still.
- **Beitragstabelle war auf dem Handy abgeschnitten.** `overflow: hidden`
  hielt die runden Ecken, kappte aber die Spalten Monat und Jahr, ohne dass
  man sie erreichen konnte.
- **Ohne JavaScript blieb die halbe Seite unsichtbar.** `.reveal` startete
  auf `opacity: 0`. Versteckt wird jetzt nur, wenn JavaScript wirklich läuft.
- **Keine Vorschau beim Teilen.** Ein Link in WhatsApp oder Instagram zeigte
  nichts. Jetzt liegen OG- und Twitter-Angaben plus ein gesetztes
  Vorschaubild im `<head>`, dazu `canonical` und Vereinsangaben für Google.
- **50 statt 51 Jahre.** Gegründet 1975. Die Zahl steht richtig im HTML und
  zählt sich über `data-seit` jedes Jahr selbst weiter.

## Wochenraster: die Gestaltungsentscheide

**Tage als Zeilen, Zeit nach rechts.** Bei sieben Tagesspalten bliebe je
Block ein Streifen von rund 140 px — zu wenig für Gruppenname und Zeit.
Als Zeile hat jeder Block die volle Breite.

**Die Farbe trägt die Halle**, nicht das Angebot. Nur zwei Werte, und im
Design-System bestand die Zuordnung schon. Geprüft gegen Weiss: das
Vereinsblau trennt vom Neutralton mit ΔE 28.8 für normales Sehen und 27.0
bei Rotschwäche — deutlich über der Schwelle von 8. Der Neutralton liegt
bewusst unter dem Buntheitsminimum und unter 3:1 Kontrast, er ist ja der
Grauton der Marke. Aufgefangen ist das dadurch, dass die Halle nie allein
über Farbe läuft: die Rhyfallhalle ist zusätzlich schraffiert, jeder
ausreichend breite Block nennt sie im Text, es gibt eine Legende, und
unter dem Raster stehen alle Angaben als Tabelle.

**Das Angebot läuft über den Filter, nicht über Farbe.** Drei nominale
Kategorien liessen sich in einer bewusst einfarbigen Palette nur über
Helligkeitsstufen trennen — und die lesen sich als Rangfolge, die es hier
nicht gibt.

**Gefiltert wird durch Zurücknehmen, nicht durch Ausblenden.** Die Woche
behält ihre Form, man sieht weiterhin, was am selben Abend sonst läuft,
und die Zeilen springen nicht.

**Auf dem Handy verschwindet der Zeitstrahl.** Vierzehn Stunden auf
390 px sind unlesbar. Stattdessen Tag für Tag, jede Einheit als volle
Karte mit Zeit und Halle im Klartext.

**Ohne JavaScript** sind die Filterknöpfe gar nicht erst sichtbar — dann
steht der vollständige Plan da, was ohne Filter das Richtige ist.

## Offene Punkte

Stand nach der Rückmeldung von Lyo Bührer vom 25. August 2026.

**Wartet auf Material**

- **Logo.** Das bisherige trägt den Jubiläumszusatz «Seit 50 Jahren am
  Tisch» — das war 2025. Das neue Logo liegt vor und wird zusammen mit den
  Fotos eingesetzt. Betrifft `logo.svg`, `logo-blau.svg`, `logo-weiss.svg`;
  das Signet in der Kopfzeile bleibt.
- **Fotos.** Dateinamen und Formate stehen in der Tabelle weiter oben.
- **Jahresprogramm.** Wird vom Verein erstellt und verschickt; die Seite
  übernimmt es dann direkt.
- **Sponsoren.** Die Liste liegt bei Kris Leibundgut zur Prüfung.
- **Johnson & Johnson.** Weder Logo noch Hinweis, welche Gesellschaft
  gemeint ist — in Schaffhausen sitzt die Cilag AG. Bis das geklärt ist,
  steht die Kachel ohne Bild und ohne Link da. Ein Link auf den
  Weltkonzern wäre geraten.
- **Klingler** und **Restaurant zum alten Schützenhaus** liegen nur in
  Weiss vor und sind zurzeit umgekehrt, damit sie auf der hellen Kachel
  sichtbar sind. Dunkle Originalfassungen wären besser.
- **Vereinszeichen als SVG.** `logo-ttcn.png` ist 511 px breit und wird
  auf der Schlusskarte 520 px gross gezeigt — eine Spur weich. Kommt das
  Zeichen als SVG, ist der Punkt erledigt; der ausgemessene Bogenanfang
  ist dann **nachzurechnen** (Rechnung im Kommentar bei `.auftakt__wurf`).

**Entscheide beim Verein**

- **«35 Trainingsstunden pro Woche»** steht auf der Startseite und in
  `verein.html`. Aus dem Plan ergeben sich **25 geleitete Stunden**
  (`build.py` rechnet sie nach jedem Lauf vor). Zählen die 35 die freien
  Hallenzeiten mit? Dann gehört das dazugeschrieben.
- **Elio Zarotti** steht auf `verein-trainerteam.html` als Trainer für
  Stellvertretungen. Im Trainingsplan kommt er nicht mehr vor. Eintrag
  stehen gelassen, weil das eine Vereinsfrage ist.
- **Impressum:** Ist der Verein im Handelsregister eingetragen? Falls ja,
  gehört die UID unter «Rechtsform». Ein Verein ohne kaufmännischen
  Betrieb muss sich nicht eintragen, viele tun es trotzdem. Solange das
  offen ist, steht dort keine Nummer — eine geratene wäre schlimmer als
  keine. Die Angaben der Agentur sind eingetragen (vom Impressum auf
  wendico.ch übernommen, bitte gegenlesen).
- **Datenschutz:** Der Text beschreibt jetzt den tatsächlichen Stand und
  ist vom Verein freizugeben. Zwei Angaben waren sachlich falsch und sind
  korrigiert: die Schriften kommen im Prototyp **noch von Google**, nicht
  vom eigenen Server; und die Ligatabellen werden **nicht** vom Verband
  geladen, sondern verlinkt — es wird also gar nichts nachgeladen. Sobald
  die Schriften umziehen, ist der Abschnitt «Externe Dienste»
  nachzuführen.

**Vor der Aufschaltung**

- **`SEITE_URL`** in `vorlage/seiten.py` prüfen — genau die Variante
  eintragen, auf die der Server am Ende weiterleitet.
- ~~**Downloads.**~~ Erledigt am 14. September: alle vierzehn Dateien
  liegen unter `site/assets/dokumente/`, jede geprüft (echte PDF- und
  ZIP-Köpfe, lesbar, sieben verschiedene Beitrittsformulare).
- **News.** Der Fliesstext der drei Beiträge fehlt noch, siehe oben. Ohne
  ihn sind die Karten nicht klickbar.
- **Anmeldeformular.** Die Microsoft-Forms-Adresse in
  `vorlage/dokumente.py` einmal anklicken und prüfen.
- **Vorstand.** Die Seite zeigt den Stand **ab der Generalversammlung vom
  15. September 2026** — so gewünscht. Bis dahin steht dort eine
  Zusammensetzung, die noch nicht gilt; der Hinweis unten auf der Seite
  sagt das.
- **Schriften selbst hosten** statt über Google Fonts.
- **Weiterleitungen.** Rund 50 alte Adressen per 301 auf die neuen. Die
  Zuordnung liegt in `seitenstruktur.xlsx`.
- **Inhaltliche Lücken** sind auf den betroffenen Seiten als Hinweisbox
  markiert.

## Was am 25. August aus der Rückmeldung kam

- Vereinsname ist **«Tischtennisclub Neuhausen»** ohne «am Rheinfall».
  Der Zusatz steht nur noch dort, wo er echte Ortsangabe ist — die
  Rhyfallhalle liegt in 8212 Neuhausen am Rheinfall.
- Die drei neuesten News stehen neu **direkt unter dem Hero**.
- Vorstand neu aufgestellt, zwei Ressorts als vakant ausgewiesen,
  erweiterter Vorstand als eigener Abschnitt.
- Seniorenbeitrag CHF 22 statt 25 im Monat.
- Schnupperpass in **drei Arten**: Nachwuchs 330, Breitensport 270,
  Senioren 210.
- **Breitensport stand verkehrt herum:** zuerst eine halbe Stunde freies
  Einspielen, während der Nachwuchs noch am Tisch ist, danach eine Stunde
  geführt. War an vier Stellen falsch.
- Stützpunkt ist **OTTV-anerkannt**, nicht mehr STT. Kontakt ist Lyo
  Bührer als Leiter Stützpunkt Neuhausen.
- Bildrechte für die Geschichte sind geklärt: Archivbilder gehören dem
  Verein, neuere sind von Pascal Oesch.
- Aufstellungen STTL Men und Women eingetragen.
- Impressum mit Postadresse (8200 Schaffhausen, keine Strasse) und
  Zeichnungsberechtigung beim Vorstand ohne erweiterten Vorstand.
- TTZ Ebnat: Ebnatstrasse 35, 8200 Schaffhausen.
