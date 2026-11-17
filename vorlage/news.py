# -*- coding: utf-8 -*-
"""News – Startseite, news.html und die Beitragsseiten.

Die Beiträge stehen nicht hier, sondern je einer als Datei unter
redaktion/news/<kennung>.json. Geschrieben werden sie in der Redaktion unter
/admin (Sveltia CMS, Felder in vorlage/redaktion.yml); von Hand geht auch.
Die Beitragsseite heisst news-<kennung>.html – den Dateinamen deshalb nach
dem Veröffentlichen nicht mehr ändern.

Je Datei:
    titel         volle Überschrift (Pflicht)
    datum         JJJJ-MM-TT (Pflicht)
    anriss        ein Satz für Listen, auf der Beitragsseite Vorspann
    bild          Titelbild, z. B. "/assets/img/news/x.webp" (Pfad ab site/)
    bildalt       Alternativtext (leer, wenn das Bild nur Stimmung ist)
    ausschnitt    "oben", "mitte" oder "unten": welcher Teil des Titelbilds
                  sichtbar bleibt, wo es zugeschnitten wird (leer = mitte)
    absaetze      Fliesstext als Blöcke. Leer = Meldung ohne eigene Seite.
    galerie       weitere Bilder, als Galerie unter dem Text
    autor         Text: …
    bildnachweis  Bild: …
    kurztitel     kürzer für Startseite und Karten (leer = titel)
    pdf           Datei unter site/assets/dokumente/, verlinkt unter dem Text
    pdf_titel     Beschriftung dafür (leer = «Dokument als PDF»)

Ein Block in absaetze ist eines von:
    {"art": "absatz", "text": "…"}        jede Zeile wird ein Absatz
    {"art": "titel", "text": "U13"}        Zwischentitel
    {"art": "zitat", "text": "…", "wer": "Lyo Bührer"}
    {"art": "bild", "bild": "/assets/img/news/x.webp", "beschreibung": "…"}
    {"art": "liste", "titel": "Rangliste U13", "punkte": ["…", "…"]}

Die Beiträge von Lyo Bührer stehen ohne Fliesstext, bis der Originaltext
aus dem alten System hierher kopiert ist. Die Anrisse der Meldungen fassen
nur Fakten zusammen (Stand 23.9.2026, von ttc-neuhausen.ch).
"""

# Wie viele Meldungen auf der Startseite neben dem grossen Beitrag stehen.
AUF_STARTSEITE = 4
