# TTC Neuhausen — Website-Prototyp

Statische Website, aufgebaut auf einem Design-System aus dem Vereinslogo.
Stand: 24. August 2026. Gestaltung und Umsetzung: Wendico.

## Öffnen

`site/index.html` im Browser öffnen. Es braucht keinen Server — die Seiten
laufen direkt vom Dateisystem.

## Ordner

```
ttcn-website/
├── build.py              Setzt die Seiten zusammen und prüft sie
├── .github/workflows/    Veröffentlicht die Vorschau auf GitHub Pages
├── vorlage/
│   ├── layout.html       Kopfzeile, Fuss, <head> — steht genau einmal im Projekt
│   ├── seiten.py         Adresse der Website, Navigation, Seitenverzeichnis
│   ├── trainingszeiten.py  Alle Trainingseinheiten der Woche
│   └── mannschaften.py   Die Teams und ihre click-tt-Adressen
├── inhalt/               Ein Fragment je Seite, nur der <main>-Inhalt
└── site/                 Erzeugt — das ist die fertige Website
    ├── *.html            27 Seiten
    └── assets/
        ├── css/
        │   ├── tokens.css        Farben, Schrift, Abstände, Schleier
        │   ├── base.css          Reset, Textfluss, Flächenkontexte
        │   ├── komponenten.css   Navigation, Buttons, Karten, Fotos, Tabellen, Fuss
        │   └── seiten.css        Hero, Bildsplit, Ballbogen, Trainingsplan, Zeitleiste
        ├── js/main.js
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

## Fotos einsetzen

Unter `site/assets/img/fotos/` liegt für jeden Bildplatz eine erzeugte
Platzhalterdatei. Zum Auswechseln: **gleicher Dateiname, Datei ersetzen,
`python3 build.py`.** Am HTML muss nichts geändert werden.

| Datei | Format | Wo es erscheint |
|---|---|---|
| `hero-halle.jpg` | 2400 × 1350 (16:9) | Startseite, ganzflächig hinter dem Titel |
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

- **«35 Trainingsstunden pro Woche»** steht auf der Startseite und in
  `verein.html`. Aus dem aktuellen Plan ergeben sich **25 geleitete
  Stunden** (`build.py` rechnet sie nach jedem Lauf vor). Falls die 35 die
  freien Hallenzeiten mitzählen, gehört das dazugeschrieben; sonst gehört
  die Zahl korrigiert. Betrifft auch «Trainingsstunden 35 pro Woche» in
  den Vereinsfakten.
- **Elio Zarotti** steht auf `verein-trainerteam.html` als Trainer für
  Stellvertretungen und Nachwuchscoaching. Im Trainingsplan des Vereins
  kommt er nicht mehr vor. Ob der Eintrag bleibt, ist eine Vereinsfrage —
  ich habe ihn deshalb stehen lassen.

- **Fotos.** Die Bildplätze stehen, die Platzhalter auch. Sobald die Fotos
  da sind: Dateien mit den Namen aus der Tabelle oben ersetzen.
- **`SEITE_URL` in `vorlage/seiten.py`.** Steht auf
  `https://www.ttc-neuhausen.ch/`. Vor der Aufschaltung genau die Variante
  eintragen, auf die der Server am Ende weiterleitet — sonst zeigen
  `canonical` und die Teilen-Vorschau auf eine Adresse, die weiterleitet.
- **Jubiläumslogo.** `logo.svg`, `logo-blau.svg` und `logo-weiss.svg` tragen
  den Zusatz «Seit 50 Jahren am Tisch – der TTC Neuhausen feiert!». Das war
  2025. Für den Dauerbetrieb braucht es die Grundform des Logos; das Signet
  in der Kopfzeile ist davon nicht betroffen.
- **Schriften selbst hosten.** Im Prototyp laufen sie über Google Fonts. Vor
  der Aufschaltung auf den eigenen Server legen — schneller und
  datenschutzrechtlich sauberer.
- **Partnerlogos.** Die Kacheln tragen bisher nur den Firmennamen. Sobald
  ein Logo als SVG vorliegt, kommt es als `<img>` in die Kachel, das Raster
  bleibt gleich.
- **Mannschaftsaufstellungen** für die laufende Saison fehlen auf
  `teams.html` noch. Die Ligaeinteilung steht, die Kader nicht.
- **Impressum und Datenschutz.** Beide Seiten sind Entwürfe mit markierten
  Lücken. Es fehlt die offizielle Postadresse des Vereins.
- **Weiterleitungen.** Beim Umzug müssen die rund 50 alten Adressen per 301
  auf die neuen zeigen. Die Zuordnung liegt in `seitenstruktur.xlsx`.
- **Inhaltliche Lücken** sind auf den betroffenen Seiten sichtbar als
  Hinweisbox markiert, damit beim Durchklicken nichts übersehen wird.
