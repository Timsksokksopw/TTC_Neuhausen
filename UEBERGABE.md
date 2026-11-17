# Übergabe: Redaktion und automatisches Veröffentlichen

Stand 10. November 2026. Für die nächste Sitzung (mit Claude): Diese Datei
zuerst lesen, dann README.md (Abschnitte «News», «Redaktion (/admin)» und
«Veröffentlichen auf Hostpoint») und REDAKTION.md.

## Ziel

Vereinsmitglieder schreiben News **ohne HTML und ohne GitHub-Konto**:
`www.ttc-neuhausen.ch/admin` → **Anmelden** mit Name und Passwort →
Formular → **Speichern**. Danach baut GitHub die Website und lädt sie per
SFTP auf Hostpoint. Auch jede andere Änderung (Push auf `main`) geht so
automatisch online.

Der Vorstand hat am 6.11.2026 schriftlich zugestimmt. Zugang bekommen
**Lyo Bührer** und **Urs Schärrer**.

## Aufbau

Zwei Repositories auf GitHub:

| | Was | Wer schreibt |
|---|---|---|
| `TTC_Neuhausen` (öffentlich) | die Website: Code, Seiten, Bilder, Workflows | nur Tim |
| `TTC_Neuhausen-News` (privat) | die **News-Ablage**: `news/`, `bilder/`, `dokumente/` | die Redaktion unter /admin, und Tim |

Lokal liegt die News-Ablage als Ordner `redaktion/` im Projekt (steht in der
`.gitignore` des Haupt-Repositorys).

Ablauf nach «Speichern» in der Redaktion: Commit in der News-Ablage → dort
läuft `melden.yml` und stösst im Haupt-Repository `hostpoint.yml` an → Job
«bauen» holt die Ablage und baut `site/` → Job «hochladen» lädt hoch.

**Warum so:** Der Schlüssel, den die Redaktion nach der Anmeldung im Browser
hat, gilt nur für die News-Ablage. Mit ihm lassen sich News ändern, sonst
nichts – kein Code, keine anderen Seiten, kein Hostpoint-Passwort.

## Stand

- **Online** (von Hand per FileZilla): die Website ohne `/admin`.
- **GitHub:** `TTC_Neuhausen` steht noch auf Commit 202c879 (22.10.). Alles
  Neue liegt nur im Arbeitsordner. `TTC_Neuhausen-News` gibt es noch nicht;
  `redaktion/` ist lokal ein gewöhnlicher Ordner (noch kein `git init`).
- **Lokal geprüft:** Build aus `redaktion/`; Übernahme mit absichtlich
  bösartigen Dateien (PHP, `bild.php.jpg`, falscher Inhalt, SVG, `.htaccess`,
  Unterordner) und Pfaden (`../`, fremde Adressen) – alles abgelehnt;
  Passwort-Seite in Edge, Prüfzeile gegen die Rechnung der Anmeldung; Upload
  gegen einen nachgestellten Server (erster Lauf, Änderung, Löschung,
  unvollständiges `site/`, Massenlöschung); YAML aller Workflows.
- **Erst auf GitHub/Hostpoint prüfbar:** die Workflows selbst (Übergabe
  zwischen den beiden Jobs, Anstoss aus der News-Ablage), `anmelden.php`
  (lokal kein PHP), die `.htaccess`-Sperre für PHP, Verknüpfungen (Symlinks)
  in der Ablage (Windows legt lokal keine an).

## Was noch zu tun ist

Reihenfolge einhalten – so gibt es keine fehlgeschlagenen Läufe.

1. **Zwei-Faktor-Anmeldung** für das GitHub-Konto und für Hostpoint
   einschalten. An diesen beiden Konten hängt alles.
2. **News-Ablage anlegen:** github.com → New repository → Name
   `TTC_Neuhausen-News`, **Private**, ohne README. Der Name muss genau so
   lauten (Haupt-Repository plus `-News`).
3. **Zwei Schlüssel erstellen** (github.com → Settings → Developer settings
   → Personal access tokens → Fine-grained tokens → Generate new token),
   Ablauf je so lang wie möglich:
   - «TTCN Redaktion»: Only select repositories → `TTC_Neuhausen-News`;
     Repository permissions → **Contents: Read and write**. Sonst nichts.
   - «TTCN Website anstossen»: Only select repositories → `TTC_Neuhausen`;
     Repository permissions → **Actions: Read and write**. Sonst nichts.
4. **Hostpoint vorbereiten** (Control Panel):
   - Webhosting → Advanced → **SSH-Zugang** aktivieren (sonst kein SFTP).
   - Passwort des Haupt-Accounts `ttcneuha`: bekannt, oder Advanced →
     **Passwort-Wechsel** (gilt dann auch in FileZilla).
   - Servername: Advanced → FTP → Einstellungen → «FTP-Server»
     (Form `sl00.web.hostpoint.ch`).
   - Zielordner: der Ordner, in dem heute `index.html` liegt, z. B.
     `www/ttc-neuhausen.ch`.
5. **Secrets eintragen** (je Repository → Settings → Secrets and variables
   → Actions → New repository secret):
   - in `TTC_Neuhausen`: `HOSTPOINT_SERVER`, `HOSTPOINT_BENUTZER`
     (= `ttcneuha`), `HOSTPOINT_PASSWORT`, `HOSTPOINT_ORDNER` (ohne `/` am
     Schluss), `REDAKTION_SCHLUESSEL` (= Schlüssel «TTCN Redaktion»).
   - in `TTC_Neuhausen-News`: `WEBSITE_AUSLOESEN` (= Schlüssel «TTCN Website
     anstossen»).
6. **Committen und pushen** (Claude, nach Rückfrage):
   - News-Ablage: in `redaktion/` `git init -b main`, alles committen, mit
     `[skip ci]` in der Nachricht (sonst stösst der erste Push die Website
     an, bevor es deren Workflow gibt), Remote setzen, pushen.
   - Haupt-Repository: vorher `git rm -r --cached site/assets/img/news`
     (der Ordner gehört jetzt der Ablage und steht in der `.gitignore`),
     dann committen und pushen. Der Lauf baut und zeigt nur an, was er
     hochladen würde.
7. **Erster Upload von Hand:** `TTC_Neuhausen` → Actions → «Website auf
   Hostpoint» → Run workflow → zuerst «Nur anzeigen (Probelauf)»,
   Ordnerinhalt prüfen, dann «Geändertes hochladen». Beim ersten Mal lädt
   er alles; löschen wird er nichts, was er nicht selbst hochgeladen hat.
8. **Passwörter:** Tim (zum Testen), Lyo und Urs legen ihr Passwort selbst
   fest: `www.ttc-neuhausen.ch/admin/passwort.html` → Prüfzeile an Tim. Die
   Zeilen als Secret `REDAKTION_PASSWOERTER` in `TTC_Neuhausen` eintragen,
   Workflow laufen lassen («Geändertes hochladen»): Im Protokoll steht
   «Zugang der Redaktion neu». Die Liste aufbewahren – das Secret lässt
   sich nicht auslesen, zum Ändern trägt man alle Zeilen neu ein.
9. **Testen:**
   - `/admin` → Anmelden → Testbeitrag mit Foto speichern → nach ein bis
     zwei Minuten auf der Website → wieder löschen.
   - Falsches Passwort: Meldung, kein Login. Sechsmal falsch: Sperre.
   - `www.ttc-neuhausen.ch/admin/zugang.php` und irgendeine erfundene
     `…/x.php` müssen «403 Forbidden» geben.
   - In den Läufen beider Repositories darf nichts rot sein.
10. **Schreibende einweihen:** REDAKTION.md an Lyo und Urs, je einzeln.

## Ab dann

- **Nicht mehr per FileZilla hochladen.** Der Server bekommt den Build von
  GitHub; was nur von Hand oben ist, überschreibt der nächste Lauf.
- Lokal an News arbeiten: `git -C redaktion pull` (die Redaktion schreibt
  mit), ändern, in `redaktion/` committen und pushen. Am Aussehen arbeiten:
  wie bisher im Haupt-Repository.
- Jemand hört auf: Zeile aus `REDAKTION_PASSWOERTER` löschen, Workflow
  laufen lassen. Ist die Person noch angemeldet, zusätzlich den Schlüssel
  «TTCN Redaktion» neu erstellen und den alten löschen (dann melden sich
  alle neu an).
- Die Schlüssel laufen ab; GitHub mahnt vorher per Mail. Dann neu erstellen
  und das jeweilige Secret ersetzen.
- Schlägt ein Lauf fehl, bleibt die Website, wie sie ist; GitHub schickt
  Tim eine Mail. Häufigster Grund: ein Beitrag zeigt auf ein Bild, das in
  der Ablage gelöscht wurde – steht im Protokoll.

## Was bleibt (Restrisiken)

- Wer den Redaktions-Schlüssel hat, kann News verfälschen, löschen oder den
  Verlauf der News-Ablage überschreiben. Zurückholen: aus dem Verlauf auf
  GitHub, sonst aus der lokalen Kopie `redaktion/` (regelmässig pullen).
  Mit GitHub Pro liesse sich der Zweig zusätzlich gegen Überschreiben
  schützen (bei privaten Repositories sonst nicht möglich).
- Alle Änderungen der Redaktion erscheinen auf GitHub unter Tims Konto;
  wer was geschrieben hat, ist dort nicht zu sehen.
- `TTC_Neuhausen` ist öffentlich: Code und alle Commits sind für jeden
  lesbar. Zugangsdaten stehen nirgends im Repository, nur in den Secrets.
- Die Vorschau auf GitHub Pages (`vorschau.yml`) zeigt dieselben News wie
  die Website und braucht dafür ebenfalls `REDAKTION_SCHLUESSEL`.
