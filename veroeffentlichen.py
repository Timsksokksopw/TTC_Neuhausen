#!/usr/bin/env python3
"""Lädt site/ per SFTP auf Hostpoint – nur, was sich seit dem letzten Mal geändert hat.

Läuft in GitHub Actions (.github/workflows/hostpoint.yml) nach
«build.py --bilder-verkleinern». Von Hand geht es auch (braucht paramiko):

    HOSTPOINT_SERVER=… HOSTPOINT_BENUTZER=… HOSTPOINT_PASSWORT=… HOSTPOINT_ORDNER=www \\
        python3 veroeffentlichen.py [--probelauf] [--freigabe] [--alles]

    --probelauf   nur anzeigen, was geschähe
    --freigabe    darf auch das allererste Mal hochladen
    --alles       alles hochladen, auch Unverändertes

Was zuletzt hochgeladen wurde, steht auf dem Server in .veroeffentlicht.json
(Pfad → SHA-256). Hochgeladen wird, was neu ist oder sich geändert hat;
gelöscht nur, was dieses Skript selbst einmal hochgeladen hat und in site/
nicht mehr vorkommt. Alles andere im Ordner bleibt, wie es ist.

Ohne .veroeffentlicht.json – beim allerersten Mal – lädt das Skript nur mit
--freigabe hoch. Ein Push zeigt dann bloss an, was geschähe; den ersten
Upload startet man in GitHub unter Actions → «Website auf Hostpoint» →
Run workflow. So landet die Website nie unbemerkt im falschen Ordner.
"""

import base64
import datetime
import hashlib
import hmac
import json
import os
import posixpath
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent
SITE = WURZEL / "site"
STAND = ".veroeffentlicht.json"
ZUGANG = "admin/zugang.php"
# Runden für die Prüfsummen der Passwörter (PBKDF2-SHA256, wie in anmelden.php).
RUNDEN = 600_000
# Kürzer darf ein Passwort der Redaktion nicht sein (wie in admin/passwort.html).
MINDESTENS = 12
# Gehört nicht auf den Server: nur für GitHub Pages, und die Zugangsdaten der
# Anmeldung kommen aus den Secrets, nicht aus einer Datei im Projekt.
NICHT_HOCHLADEN = {".nojekyll", STAND, ZUGANG}
# Nur diese Dateiarten gehen auf den Server. Alles andere bleibt unten – vor
# allem nichts, was der Server ausführen würde (PHP) oder was seine Regeln
# ändert (.htaccess in einem Unterordner).
ERLAUBT = {".html", ".css", ".js", ".xml", ".txt", ".yml", ".svg", ".ico", ".woff2",
           ".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".pdf", ".docx", ".xlsx"}
# Die beiden Ordner, die build.py aus der News-Ablage (redaktion/) füllt:
# dort nur Bilder bzw. PDFs – zweite Kontrolle nach der in build.py.
ORDNER_REDAKTION = {"assets/img/news/": {".jpg", ".jpeg", ".png", ".webp"},
                    "assets/dokumente/news/": {".pdf"}}
# Darf in keinem Dateinamen als Endung vorkommen, auch nicht in der Mitte.
AUSFUEHRBAR = {"php", "php3", "php4", "php5", "php7", "php8", "phtml", "phar", "pht", "phps", "cgi", "pl", "py",
               "sh", "shtml", "asp", "aspx", "jsp", "htaccess", "htpasswd", "ini", "exe"}
# Ohne diese Dateien ist site/ nicht die ganze Website.
PFLICHT = ("index.html", ".htaccess", "404.html", "admin/index.html", "admin/anmelden.php")
# Die einzigen Ausnahmen, je an genau einem Ort.
NUR_HIER = {".htaccess", "admin/anmelden.php"}

PROBELAUF = "--probelauf" in sys.argv
FREIGABE = "--freigabe" in sys.argv
ALLES = "--alles" in sys.argv


def umgebung(name):
    return os.environ.get(name, "").strip()


def zusammenfassung(text):
    """Ins Protokoll und, in GitHub Actions, auf die Übersichtsseite des Laufs."""
    print(text)
    datei = umgebung("GITHUB_STEP_SUMMARY")
    if datei:
        with open(datei, "a", encoding="utf-8") as f:
            f.write(text + "\n")


def hinweis(text, art="notice"):
    print("::%s::%s" % (art, text) if umgebung("GITHUB_ACTIONS") else text)


def darf_hoch(rel):
    """Ob eine Datei aus site/ auf den Server darf – nach Ort und Dateiart."""
    if rel in NUR_HIER:
        return True
    name = posixpath.basename(rel)
    endung = posixpath.splitext(name)[1].lower()
    # Keine versteckten Dateien und kein «bild.php.jpg»: Apache kann auch eine
    # Endung in der Mitte des Namens auswerten.
    if name.startswith(".") or any(teil.lower() in AUSFUEHRBAR for teil in name.split(".")[1:]):
        return False
    for ordner, arten in ORDNER_REDAKTION.items():
        if rel.startswith(ordner):
            return endung in arten
    return endung in ERLAUBT


def lokale_dateien():
    dateien, abgelehnt = {}, []
    for pfad in sorted(SITE.rglob("*")):
        if not pfad.is_file():
            continue
        rel = pfad.relative_to(SITE).as_posix()
        if rel in NICHT_HOCHLADEN or rel.endswith(".hochladen"):
            continue
        if darf_hoch(rel):
            dateien[rel] = pfad.read_bytes()
        else:
            abgelehnt.append(rel)
    if abgelehnt:
        hinweis("Nicht hochgeladen, weil die Dateiart hier nicht erlaubt ist: %s" % ", ".join(abgelehnt), "warning")
    return dateien


def _pruefzeile(wert):
    """Eine Prüfsumme aus admin/passwort.html («pbkdf2-sha256$Runden$Salz$Summe»):
    wert selbst, wenn sie vollständig ist, False, wenn nicht – und None, wenn
    wert gar keine Prüfsumme ist, sondern ein Passwort."""
    if not wert.startswith("pbkdf2-sha256$"):
        return None
    teile = wert.split("$")
    try:
        gut = (len(teile) == 4 and teile[1].isdigit() and RUNDEN <= int(teile[1]) <= 5 * RUNDEN
               and len(base64.b64decode(teile[2], validate=True)) >= 16
               and len(base64.b64decode(teile[3], validate=True)) == 32)
    except ValueError:
        gut = False
    return wert if gut else False


def _name(s):
    """Wie vergleichbar() in anmelden.php: ohne Gross/klein und doppelte Leerzeichen."""
    return " ".join(s.split()).lower()


def zugang_php():
    """admin/zugang.php aus den Secrets – oder None, wenn eines fehlt.

    REDAKTION_SCHLUESSEL ist der Zugangsschlüssel zu GitHub, den anmelden.php
    nach richtigem Passwort an die Redaktion gibt. REDAKTION_PASSWOERTER hat
    je Person eine Zeile – am besten die Prüfzeile, die sich die Person unter
    /admin/passwort.html selbst erstellt («Name: pbkdf2-sha256$…»): dann kennt
    nur sie ihr Passwort. «Name: Passwort» geht auch; auf den Server kommt
    davon nur eine Prüfsumme. Deren Salz hängt an Schlüssel und Name: Dieselben
    Secrets ergeben dieselbe Datei, sie geht also nur nach einer Änderung neu
    hoch."""
    schluessel, liste = umgebung("REDAKTION_SCHLUESSEL"), umgebung("REDAKTION_PASSWOERTER")
    if not (schluessel and liste):
        return None
    personen = {}
    for nr, zeile in enumerate(liste.splitlines(), 1):
        if not zeile.strip() or zeile.lstrip().startswith("#"):
            continue
        name, doppelpunkt, passwort = zeile.partition(":")
        name, passwort = _name(name), passwort.strip()
        # Die Meldungen nennen nur die Zeile, nie Name oder Passwort.
        if not (doppelpunkt and name and passwort):
            sys.exit("REDAKTION_PASSWOERTER, Zeile %d: erwartet «Name: Prüfzeile» oder «Name: Passwort»." % nr)
        if name in personen:
            sys.exit("REDAKTION_PASSWOERTER, Zeile %d: Der Name steht schon weiter oben." % nr)
        fertig = _pruefzeile(passwort)
        if fertig is False:
            sys.exit("REDAKTION_PASSWOERTER, Zeile %d: Die Prüfzeile ist unvollständig – unter "
                     "/admin/passwort.html neu erstellen und ganz kopieren." % nr)
        if fertig:
            personen[name] = fertig
            continue
        if len(passwort) < MINDESTENS:
            sys.exit("REDAKTION_PASSWOERTER, Zeile %d: Passwort zu kurz, mindestens %d Zeichen." % (nr, MINDESTENS))
        salz = hmac.new(schluessel.encode("utf-8"), ("redaktion:" + name).encode("utf-8"),
                        hashlib.sha256).digest()[:16]
        summe = hashlib.pbkdf2_hmac("sha256", passwort.encode("utf-8"), salz, RUNDEN)
        personen[name] = "pbkdf2-sha256$%d$%s$%s" % (RUNDEN, base64.b64encode(salz).decode("ascii"),
                                                     base64.b64encode(summe).decode("ascii"))

    def php(s):
        return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"
    zeilen = "".join("        %s => %s,\n" % (php(n), php(s)) for n, s in sorted(personen.items()))
    return ("<?php\n// ERZEUGT VON veroeffentlichen.py aus den GitHub-Secrets REDAKTION_SCHLUESSEL\n"
            "// und REDAKTION_PASSWOERTER – nicht von Hand ändern, nicht ins Repository.\n"
            "return [\n    'schluessel' => %s,\n    'personen' => [\n%s    ],\n];\n"
            % (php(schluessel), zeilen)).encode("utf-8")


def reihenfolge(pfad):
    """Erst Bilder, Schriften, CSS und JS, dann die Seiten, .htaccess zuletzt:
    eine neue Seite zeigt so nie auf eine Datei, die noch nicht oben ist."""
    if pfad == ".htaccess":
        return (3, pfad)
    if pfad.endswith((".html", ".xml", ".txt")):
        return (2, pfad)
    return (1, pfad)


def sha(daten):
    return hashlib.sha256(daten).hexdigest()


class Server:
    def __init__(self):
        import paramiko
        self.paramiko = paramiko
        host, port = umgebung("HOSTPOINT_SERVER"), int(umgebung("HOSTPOINT_PORT") or 22)
        self.ssh = paramiko.SSHClient()
        bekannt = umgebung("HOSTPOINT_HOSTKEY")
        if bekannt:
            art, schluessel = bekannt.split()[:2]
            name = host if port == 22 else "[%s]:%d" % (host, port)
            self.ssh.get_host_keys().add(name, art, paramiko.PKey.from_type_string(art, base64.b64decode(schluessel)))
            self.ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
        else:
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(host, port=port, username=umgebung("HOSTPOINT_BENUTZER"),
                             password=umgebung("HOSTPOINT_PASSWORT"), timeout=30, banner_timeout=30,
                             auth_timeout=30, look_for_keys=False, allow_agent=False)
        except paramiko.AuthenticationException:
            sys.exit("Anmeldung bei %s abgelehnt: HOSTPOINT_BENUTZER oder HOSTPOINT_PASSWORT stimmt nicht "
                     "(für SFTP der Benutzer des Webhostings, nicht ein FTP-Unterbenutzer)." % host)
        except (OSError, paramiko.SSHException) as fehler:
            sys.exit("Keine SFTP-Verbindung zu %s:%d: %s" % (host, port, fehler))
        schluessel = self.ssh.get_transport().get_remote_server_key()
        if not bekannt:
            print("Server-Schlüssel (für das Secret HOSTPOINT_HOSTKEY, optional): %s %s"
                  % (schluessel.get_name(), schluessel.get_base64()))
        self.sftp = self.ssh.open_sftp()
        self.ordner_da = set()

    def lesen(self, pfad):
        try:
            with self.sftp.open(pfad, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def ist_ordner(self, pfad):
        import stat
        try:
            return stat.S_ISDIR(self.sftp.stat(pfad).st_mode)
        except FileNotFoundError:
            return False

    def liste(self, pfad):
        return sorted(self.sftp.listdir(pfad))

    def ordner(self, basis, rel):
        """Die Ordner von rel unter basis anlegen, soweit es sie noch nicht gibt."""
        p = basis
        for teil in (t for t in rel.split("/") if t):
            p = posixpath.join(p, teil)
            if p in self.ordner_da:
                continue
            if not self.ist_ordner(p):
                self.sftp.mkdir(p)
                self.sftp.chmod(p, 0o755)
            self.ordner_da.add(p)

    def schreiben(self, pfad, daten):
        """Erst unter anderem Namen, dann umbenennen: wer die Seite gerade lädt,
        bekommt die alte oder die neue Datei, nie eine halbe."""
        neu = pfad + ".hochladen"
        with self.sftp.open(neu, "wb") as f:
            f.set_pipelined(True)
            f.write(daten)
        self.sftp.chmod(neu, 0o644)
        try:
            self.sftp.posix_rename(neu, pfad)
        except OSError:
            try:
                self.sftp.remove(pfad)
            except FileNotFoundError:
                pass
            self.sftp.rename(neu, pfad)

    def loeschen(self, pfad):
        try:
            self.sftp.remove(pfad)
        except FileNotFoundError:
            pass

    def schliessen(self):
        self.sftp.close()
        self.ssh.close()


def main():
    fehlt = [n for n in ("HOSTPOINT_SERVER", "HOSTPOINT_BENUTZER", "HOSTPOINT_PASSWORT", "HOSTPOINT_ORDNER")
             if not umgebung(n)]
    if fehlt:
        hinweis("Nichts hochgeladen: in GitHub fehlen die Secrets %s (Settings → Secrets and variables → "
                "Actions)." % ", ".join(fehlt), "warning")
        return
    if not (SITE / "index.html").is_file():
        sys.exit("site/index.html fehlt – zuerst build.py laufen lassen.")

    lokal = lokale_dateien()
    # Ein halbes site/ (abgebrochener Build, unvollständige Übergabe) würde auf
    # dem Server alles löschen, was darin fehlt – auch die .htaccess mit den
    # Sperren. Dann lieber gar nichts tun.
    unvollstaendig = [n for n in PFLICHT if n not in lokal]
    if unvollstaendig:
        sys.exit("site/ ist unvollständig (es fehlt: %s) – nichts hochgeladen." % ", ".join(unvollstaendig))
    zugang = zugang_php()
    if zugang is None:
        hinweis("REDAKTION_SCHLUESSEL und REDAKTION_PASSWOERTER fehlen: die Anmeldung in der Redaktion "
                "(/admin) geht erst, wenn beide als Secret eingetragen sind.", "warning")

    server = Server()
    ziel = umgebung("HOSTPOINT_ORDNER").rstrip("/") or "."
    if not server.ist_ordner(ziel):
        sys.exit("Den Ordner «%s» gibt es auf dem Server nicht. HOSTPOINT_ORDNER ist der Ordner, in dem "
                 "index.html liegen soll, z. B. www oder www/ttc-neuhausen.ch." % ziel)

    roh = server.lesen(posixpath.join(ziel, STAND))
    erstes_mal = roh is None
    try:
        alt = json.loads(roh.decode("utf-8"))["dateien"] if roh else {}
    except (ValueError, KeyError, TypeError):
        hinweis("%s auf dem Server ist unlesbar – lade alles neu hoch, lösche nichts." % STAND, "warning")
        alt = {}
    neu = {pfad: sha(daten) for pfad, daten in lokal.items()}
    hoch = sorted((p for p in lokal if ALLES or alt.get(p) != neu[p]), key=reihenfolge)
    weg = sorted(p for p in alt if p not in lokal)
    zugang_neu = zugang is not None and server.lesen(posixpath.join(ziel, ZUGANG)) != zugang

    # Verschwindet auf einmal ein grosser Teil der Website, stimmt eher etwas
    # mit dem Build nicht, als dass es so gewollt ist: von Hand bestätigen.
    if len(weg) > 25 and len(weg) > len(alt) // 4 and not (FREIGABE or PROBELAUF):
        server.schliessen()
        sys.exit("Der Lauf würde %d von %d Dateien auf dem Server löschen – nichts geändert. Ist das gewollt, "
                 "in GitHub unter Actions → «Website auf Hostpoint» → Run workflow → «Geändertes hochladen» "
                 "starten." % (len(weg), len(alt)))

    nur_zeigen = PROBELAUF or (erstes_mal and not FREIGABE)
    zusammenfassung("## Website auf Hostpoint\n")
    zusammenfassung("Ordner `%s` auf %s · %d Dateien in site/ · %d neu oder geändert · %d zu löschen%s\n"
                    % (ziel, umgebung("HOSTPOINT_SERVER"), len(lokal), len(hoch), len(weg),
                       " · Zugang der Redaktion neu" if zugang_neu else ""))
    if erstes_mal:
        inhalt = server.liste(ziel)
        zusammenfassung("**Erstes Mal:** auf dem Server liegt noch kein `%s`. Im Ordner liegt jetzt: %s\n"
                        % (STAND, ", ".join("`%s`" % n for n in inhalt[:40]) or "nichts"))
    if nur_zeigen:
        for titel, liste in (("Würde hochladen", hoch), ("Würde löschen", weg)):
            if liste:
                zusammenfassung("%s (%d):\n" % (titel, len(liste)))
                zusammenfassung("\n".join("- `%s`" % p for p in liste[:60]) + ("\n- …" if len(liste) > 60 else "") + "\n")
        if erstes_mal and not PROBELAUF:
            hinweis("Erster Upload noch nicht freigegeben – es wurde nichts geändert. Stimmt der Ordner oben, "
                    "in GitHub unter Actions → «Website auf Hostpoint» → Run workflow starten.", "warning")
        else:
            zusammenfassung("Probelauf – auf dem Server wurde nichts geändert.")
        server.schliessen()
        return

    for nr, pfad in enumerate(hoch, 1):
        server.ordner(ziel, posixpath.dirname(pfad))
        server.schreiben(posixpath.join(ziel, pfad), lokal[pfad])
        print("  hoch  %4d/%d  %s" % (nr, len(hoch), pfad))
    if zugang_neu:
        server.ordner(ziel, posixpath.dirname(ZUGANG))
        server.schreiben(posixpath.join(ziel, ZUGANG), zugang)
        print("  hoch  %s (aus den Secrets)" % ZUGANG)
    for pfad in weg:
        server.loeschen(posixpath.join(ziel, pfad))
        print("  weg   %s" % pfad)
    stand = {"zeit": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
             "commit": umgebung("GITHUB_SHA"), "dateien": neu}
    server.schreiben(posixpath.join(ziel, STAND), json.dumps(stand, indent=1, sort_keys=True).encode("utf-8"))
    server.schliessen()
    if hoch or weg:
        zusammenfassung("Hochgeladen:\n\n" + "\n".join("- `%s`" % p for p in hoch[:60])
                        + ("\n- …" if len(hoch) > 60 else "")
                        + ("\n\nGelöscht:\n\n" + "\n".join("- `%s`" % p for p in weg) if weg else "") + "\n")
    zusammenfassung("Fertig: %d hochgeladen, %d gelöscht." % (len(hoch), len(weg)))


if __name__ == "__main__":
    try:
        main()
    except SystemExit as ende:
        # Abbrüche mit Begründung in GitHub als rote Meldung oben im Lauf –
        # sonst steht der Grund nur tief im Protokoll.
        if isinstance(ende.code, str):
            hinweis(ende.code, "error")
            zusammenfassung("**Abgebrochen:** " + ende.code)
            sys.exit(1)
        raise
