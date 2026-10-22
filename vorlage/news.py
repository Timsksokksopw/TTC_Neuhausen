# -*- coding: utf-8 -*-
"""News – Startseite, news.html und die Beitragsseiten.

Je Eintrag:
    kennung       Dateiname der Beitragsseite: news-<kennung>.html
    datum         JJJJ-MM-TT
    titel         volle Überschrift
    kurztitel     kürzer für Startseite und Karten (leer = titel)
    anriss        ein Satz für Listen, auf der Beitragsseite Vorspann (optional)
    text          Autorin/Autor (optional)
    bildnachweis  Fotografin/Fotograf (optional)
    bild          Datei unter site/assets/img/fotos/ (optional)
    bildalt       Alternativtext (leer, wenn das Bild nur Stimmung ist)
    absaetze      Fliesstext. Leer = Meldung ohne eigene Seite.
    pdf           Datei unter site/assets/dokumente/, verlinkt unter dem Text (optional)

Ein Absatz ist ein Text oder eines von:
    {"art": "titel", "text": "U13"}
    {"art": "zitat", "text": "…", "wer": "Lyo Bührer"}
    {"art": "liste", "titel": "Rangliste U13", "punkte": ["…", "…"]}

Die Beiträge von Lyo Bührer stehen ohne Fliesstext, bis der Originaltext
aus dem alten System hierher kopiert ist. Die Anrisse der Meldungen fassen
nur Fakten zusammen (Stand 23.9.2026, von ttc-neuhausen.ch).
"""

BEITRAEGE = [
    {
        "kennung": "herbstlehrgang-ttz-ebnat-2026",
        "datum": "2026-10-22",
        "titel": "Herbstlehrgang im TTZ Ebnat: 20 Stunden Training mit 32 Teilnehmenden",
        "kurztitel": "Herbstlehrgang im TTZ Ebnat mit 32 Teilnehmenden",
        "anriss": "Vier Tage voller Tischtennis mit Spielenden aus der ganzen Region.",
        "bild": "lehrgang-herbst-2026.jpg",
        "bildalt": "Trainingseinheit im TTZ Ebnat: Teilnehmende jeden Alters schauen zu, wie an einem Tisch eine Übung vorgezeigt wird.",
        "absaetze": [
            "Vier intensive Tage liegen hinter den Teilnehmenden des Herbstlehrgangs vom 15. bis 18. Oktober im Tischtenniszentrum Ebnat. Insgesamt 32 Teilnehmende waren mit viel Freude dabei und in der Halle herrschte eine tolle Stimmung. Von der ersten bis zur letzten Einheit wurde alles gegeben, wobei der Spass nie zu kurz kam.",
            "Geleitet wurde der Lehrgang an allen vier Tagen von Cheftrainer Pekka Pelz. Unterstützt wurde er dabei teils von Schweizermeister Timothy Falconnier, teils von Eric Miller. Krankheitsbedingt konnte Timothy leider nicht wie geplant alle Einheiten übernehmen.",
            "Neben Technik, Taktik sowie abwechslungsreichem Systemtraining kam auch die Athletik nicht zu kurz. Ausser zahlreichen Mitgliedern des TTCN waren auch Gäste aus vielen verschiedenen Vereinen der Region dabei. So entstanden immer wieder neue Trainingspaarungen mit ungewohnten Spielsystemen. Zwischen den Einheiten wurden im Tischtennisbeizli warme Mahlzeiten serviert, die für die nötige Energie sorgten.",
            {"art": "zitat", "text": "Ich bin mit unserem ersten Lehrgang in diesem Format sehr zufrieden. Die Stimmung in der Halle war grossartig, die Teilnehmenden haben vier Tage lang super mitgemacht und sich auch untereinander klasse verstanden. Ich denke, alle hatten eine gute Zeit, ich auf jeden Fall. Wir schauen schon jetzt mit Vorfreude auf die nächsten Lehrgänge.", "wer": "Pekka Pelz, Cheftrainer"},
            "Herzlichen Dank allen Teilnehmenden für ihren Einsatz, Timothy Falconnier sowie Eric Miller für die Unterstützung in der Halle und dem Team im Tischtennisbeizli für die Verpflegung.",
        ],
    },
    {
        "kennung": "medienmitteilung-forfait-sttl-women",
        "datum": "2026-10-19",
        "titel": "Medienmitteilung: STTL-Damen verlieren Forfait – TTCN zieht Entscheid weiter",
        "kurztitel": "STTL-Damen verlieren Forfait – TTCN zieht Entscheid weiter",
        "anriss": "Der Verein legt gegen die nachträglichen Forfaitniederlagen Rekurs bei Swiss Table Tennis ein.",
        "pdf": "medienmitteilung-forfait-sttl-2026.pdf",
        "absaetze": [
            "Der TTC Neuhausen wurde am Donnerstagabend darüber informiert, dass der Vorstand der STTL die beiden am ersten Spielwochenende der STTL-Women sportlich gewonnenen Meisterschaftsspiele gegen ZZ-Lancy und Zürich-Affoltern des Vereins nachträglich als Forfaitniederlagen wertet.",
            "Auslöser des Verfahrens war ein administrativer Fehler im Lizenzierungsprozess. Bei der Erfassung der Spielerin Melanie Merk wurde eine bereits vorhandene und gültig unterzeichnete Doping-Unterstellungserklärung nicht korrekt im System hinterlegt. Diesen Fehler bestreitet der TTC Neuhausen nicht.",
            "Nicht nachvollziehen kann der Verein hingegen die Schlussfolgerung, wonach Melanie Merk dadurch als nicht spielberechtigt gegolten haben soll.",
            "Die für STTL-Spielerinnen erforderliche Doping-Unterstellungserklärung wurde von Melanie Merk bereits am 22. Februar 2026 unterzeichnet und lag somit weit vor den betreffenden Meisterschaftsspielen vor. Die Spielerin war folglich bereits vor ihrem Einsatz den geltenden Anti-Doping-Bestimmungen unterstellt.",
            "Aus Sicht des TTC Neuhausen unterscheidet das einschlägige Reglement klar zwischen Spielerinnen, welche die erforderliche Unterstellungserklärung nicht unterzeichnet haben, und solchen, welche diese unterzeichnet haben. Der vorliegende Fall betrifft keine fehlende Doping-Unterstellung, sondern ausschliesslich einen Fehler bei der administrativen Erfassung einer bereits bestehenden und gültigen Erklärung.",
            "Nach Auffassung des Vereins findet sich in den massgebenden Reglementen keine Bestimmung, wonach eine Spielerin trotz unterzeichneter Unterstellungserklärung allein deshalb als nicht spielberechtigt gilt, weil die Erklärung zum Zeitpunkt des Einsatzes nicht im System hinterlegt war.",
            {"art": "zitat", "text": "Wir bestreiten den administrativen Fehler nicht. Wir bestreiten aber ausdrücklich die Auffassung, dass daraus automatisch eine fehlende Spielberechtigung resultiert. Aus unserer Sicht erfüllt Melanie Merk die reglementarischen Voraussetzungen, da die Unterstellungserklärung bereits Monate vor Saisonbeginn unterzeichnet wurde.", "wer": "Lyo Bührer, Co-Präsident und Sportlicher Leiter"},
            "Der Verein zeigt sich darüber hinaus auch vom Ablauf des Verfahrens enttäuscht. Vor der Beschlussfassung erhielt der TTC Neuhausen keine Möglichkeit, seinen Standpunkt direkt gegenüber dem entscheidenden Organ darzulegen. Zudem wurden die konkreten rechtlichen Grundlagen, auf welche sich der Entscheid stützt, trotz entsprechender Nachfrage erst zusammen mit dem Entscheid selbst kommuniziert. Aus Sicht des Vereins wurde dadurch eine sachgerechte Stellungnahme im Vorfeld unnötig erschwert.",
            {"art": "zitat", "text": "Unabhängig vom eigentlichen Entscheid hätten wir uns ein transparenteres und faireres Verfahren gewünscht. Zu einem geordneten Verfahren gehört aus unserer Sicht, dass ein betroffener Verein angehört wird und die rechtlichen Grundlagen kennt, bevor über einschneidende Sanktionen entschieden wird. Unsere Interpretation des Reglements wurde den zuständigen Stellen im Vorfeld mitgeteilt, ohne dass wir darauf eine Rückmeldung erhalten haben.", "wer": "Lyo Bührer"},
            "Der TTC Neuhausen ist überzeugt, dass der vorliegende Fall sowohl in reglementarischer als auch in verfahrensrechtlicher Hinsicht Fragen aufwirft, die einer unabhängigen Überprüfung bedürfen. Der Verein hat die Angelegenheit an seinen Rechtsbeistand übergeben und wird den Entscheid fristgerecht an die Rekurskommission von Swiss Table Tennis weiterziehen.",
            {"art": "zitat", "text": "Wir respektieren den Entscheid des STTL-Vorstands, teilen ihn aber nicht. Nach eingehender Prüfung sehen wir gute Gründe dafür, dass der Sachverhalt rechtlich und reglementarisch anders zu beurteilen ist. Deshalb werden wir Rekurs einlegen und blicken dem weiteren Verfahren vorsichtig zuversichtlich entgegen.", "wer": "Lyo Bührer"},
            "Der TTC Neuhausen wird den Rechtsweg nun konsequent weiterverfolgen und die Angelegenheit von der Rekurskommission beurteilen lassen. Fragen zu diesem Fall sind an die Sportliche Leitung des Vereins, Lyo Bührer, zu richten.",
            "Für den TTC Neuhausen: Lyo Bührer, Co-Präsident | Sportlicher Leiter, und Urs Schärrer, Co-Präsident",
        ],
    },
    {
        "kennung": "sttl-saisonvorschau-2026",
        "datum": "2026-09-21",
        "titel": "Titelrennen, Playoffkampf und Abstiegssorgen: So schätzt Lyo Bührer die STTL ein",
        "kurztitel": "So schätzt Lyo Bührer die neue STTL-Saison ein",
        "anriss": "Der Sportliche Leiter über Favoriten, Playoff-Rennen und Abstiegskampf.",
        "text": "Lyo Bührer",
        "absaetze": [],
    },
    {
        "kennung": "altpapier-september-2026",
        "datum": "2026-08-24",
        "titel": "Altpapiersammlung 5. September",
        "anriss": "Treffpunkt um 7 Uhr beim TTZ Ebnat. Gesucht sind 18 Helferinnen und Helfer.",
        "absaetze": [],
    },
    {
        "kennung": "sttl-women-nach-dem-umbruch",
        "datum": "2026-07-09",
        "titel": "STTL Women: TTC Neuhausen stellt sich nach Umbruch neu auf",
        "kurztitel": "STTL Women: neu aufgestellt nach dem Umbruch",
        "text": "Lyo Bührer",
        "bildnachweis": "René Zwald",
        "bild": "news-1.jpg",
        "bildalt": "Eine Spielerin im blauen Trikot ballt nach einem Punkt die Faust.",
        "absaetze": [],
    },
    {
        "kennung": "finalrunde-nachwuchs",
        "datum": "2026-06-22",
        "titel": "Finalrunde Nachwuchs: Alle drei Sprachregionen holen Titel in Neuhausen",
        "kurztitel": "Finalrunde Nachwuchs: alle drei Sprachregionen holen Titel",
        "text": "Lyo Bührer",
        "bildnachweis": "Andrii Lukatskyi",
        "bild": "news-2.jpg",
        "bildalt": "",
        "absaetze": [],
    },
    {
        "kennung": "sttl-men-weichen-neu-gestellt",
        "datum": "2026-06-22",
        "titel": "STTL Men: TTC Neuhausen stellt Weichen nach schwierigem Jahr neu",
        "kurztitel": "STTL Men: Weichen nach schwierigem Jahr neu gestellt",
        "text": "Lyo Bührer",
        "bildnachweis": "Ranil Jayanetti",
        "bild": "news-3.jpg",
        "bildalt": "Ein Spieler streckt sich am Tisch nach dem Ball.",
        "absaetze": [],
    },
    {
        "kennung": "abstimmung-hallensportzentrum",
        "datum": "2026-06-15",
        "titel": "Schaffhausen sagt JA – Ein Sieg für den Hallensport",
        "anriss": "Alle 26 Gemeinden stimmen dem Ausbau des Hallensportzentrums zu, der Kanton mit 73,9 Prozent.",
        "text": "Lyo Bührer",
        "absaetze": [],
    },
    {
        "kennung": "bronze-o40",
        "datum": "2026-05-19",
        "titel": "Joachim Klappenecker holt Bronze im O40-Einzel",
        "anriss": "Medaille an den Schweizer Meisterschaften der Seniorinnen und Senioren in Genf.",
        "absaetze": [],
    },
    {
        "kennung": "standaktionen-hallensportzentrum",
        "datum": "2026-05-18",
        "titel": "Standaktionen für Abstimmung Hallensportzentrum Schaffhausen gestartet",
        "anriss": "Zehn Stände in der ganzen Region – mit einem kleinen Tisch zum Mitspielen.",
        "absaetze": [],
    },
    {
        "kennung": "partnerschaft-tt-store",
        "datum": "2026-05-11",
        "titel": "TTC Neuhausen geht Partnerschaft mit TT-Store.ch ein",
        "anriss": "Ab der Saison 2026/27 rüstet TT-Store.ch den ganzen Verein aus, vom Nachwuchs bis zur STTL.",
        "absaetze": [],
    },
    {
        "kennung": "altpapier-mai-2026",
        "datum": "2026-05-11",
        "titel": "Altpapiersammlung vom 9. Mai 2026",
        "anriss": "15 Helferinnen und Helfer, fünf Fahrzeuge, Sonnenschein.",
        "absaetze": [],
    },
]

# Wie viele Meldungen auf der Startseite neben dem grossen Beitrag stehen.
AUF_STARTSEITE = 4
