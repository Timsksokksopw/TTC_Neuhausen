/* ==========================================================================
   main.js — Verhalten
   Alles hier ist Zusatz. Ohne JavaScript bleibt die Seite vollständig
   lesbar und bedienbar: Die Navigation ist dann ausgeklappt, Inhalte sind
   sichtbar, Zahlen stehen auf ihrem Endwert.
   ========================================================================== */

(function () {
  'use strict';

  var sanft = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var jahr = new Date().getFullYear();

  /* --- Jahreszahl im Fuss ------------------------------------------------
     Löst den Fehler «© Copyright 2018» der bisherigen Website dauerhaft. */
  document.querySelectorAll('[data-jahr]').forEach(function (el) {
    el.textContent = jahr;
  });

  /* --- Vereinsalter ------------------------------------------------------
     Stand im HTML als feste 50. Der Verein wurde 1975 gegründet, also
     stimmt jede feste Zahl höchstens ein Jahr lang. Im HTML steht der
     aktuell richtige Wert, damit auch ohne JavaScript nichts Falsches
     dasteht; hier wird er jedes Jahr von selbst nachgezogen. */
  document.querySelectorAll('[data-seit]').forEach(function (el) {
    var alter = jahr - parseInt(el.getAttribute('data-seit'), 10);
    if (!isNaN(alter) && alter > 0) {
      el.setAttribute('data-ziel', alter);
      if (!el.closest('.reveal')) el.textContent = alter;
    }
  });

  /* --- Mobile Navigation ------------------------------------------------- */
  var knopf = document.querySelector('.menu-knopf');
  var nav = document.querySelector('.nav');

  if (knopf && nav) {
    knopf.addEventListener('click', function () {
      var offen = nav.getAttribute('data-offen') === 'true';
      nav.setAttribute('data-offen', String(!offen));
      knopf.setAttribute('aria-expanded', String(!offen));
      document.body.style.overflow = !offen ? 'hidden' : '';
    });

    // Schliessen mit Escape, damit die Tastaturbedienung nicht feststeckt.
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.getAttribute('data-offen') === 'true') {
        nav.setAttribute('data-offen', 'false');
        knopf.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
        knopf.focus();
      }
    });
  }

  /* --- Wochenraster filtern ----------------------------------------------
     Gefilterte Einheiten werden zurückgenommen, nicht ausgeblendet. Die
     Woche behält so ihre Form: man sieht weiterhin, was am selben Abend
     sonst noch läuft, und die Zeilen springen nicht.

     Ohne JavaScript sind die Knöpfe per CSS gar nicht erst sichtbar —
     dann steht der volle Plan da, was ohne Filter das Richtige ist. */
  var woche = document.querySelector('.woche');

  if (woche) {
    var knoepfe = woche.querySelectorAll('.filter__knopf');
    var einheiten = woche.querySelectorAll('.einheit');
    var stand = woche.querySelector('.woche__stand');

    knoepfe.forEach(function (k) {
      k.addEventListener('click', function () {
        var zeigt = k.getAttribute('data-zeigt');
        var treffer = 0;

        woche.setAttribute('data-filter', zeigt);
        knoepfe.forEach(function (b) {
          b.setAttribute('aria-pressed', String(b === k));
        });

        einheiten.forEach(function (e) {
          var passt = (zeigt === 'alle' || e.getAttribute('data-angebot') === zeigt);
          e.classList.toggle('einheit--gedimmt', !passt);
          if (passt) treffer++;
        });

        // Vorlesesoftware bekommt sonst nicht mit, dass sich etwas geändert
        // hat — die Blöcke bleiben ja alle stehen.
        if (stand) {
          stand.textContent = (zeigt === 'alle')
            ? treffer + ' Trainingseinheiten pro Woche'
            : k.textContent + ': ' + treffer +
              (treffer === 1 ? ' Einheit' : ' Einheiten') + ' hervorgehoben';
        }
      });
    });

    if (stand) stand.textContent = einheiten.length + ' Trainingseinheiten pro Woche';
  }

  /* --- Zahlen hochzählen -------------------------------------------------
     Startet erst, wenn das Zahlenband im Blickfeld ist. */
  function zaehlen(el) {
    var ziel = parseInt(el.getAttribute('data-ziel'), 10);
    if (isNaN(ziel)) return;
    if (sanft) { el.textContent = ziel; return; }

    var dauer = 900;
    var start = performance.now();

    function schritt(jetzt) {
      var p = Math.min((jetzt - start) / dauer, 1);
      el.textContent = Math.round(ziel * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(schritt);
    }
    requestAnimationFrame(schritt);
  }

  /* --- Einblenden beim Scrollen ------------------------------------------
     Ohne IntersectionObserver werden alle Elemente sofort sichtbar. */
  var zuBeobachten = document.querySelectorAll('.reveal');

  if (!('IntersectionObserver' in window)) {
    zuBeobachten.forEach(function (el) {
      el.classList.add('sichtbar');
      var w = el.querySelector('[data-ziel]');
      if (w) w.textContent = w.getAttribute('data-ziel');
    });
    return;
  }

  var beobachter = new IntersectionObserver(function (eintraege) {
    eintraege.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add('sichtbar');
      beobachter.unobserve(e.target);
      var wert = e.target.querySelector('[data-ziel]');
      if (wert) zaehlen(wert);
    });
  }, { threshold: 0.2, rootMargin: '0px 0px -40px 0px' });

  zuBeobachten.forEach(function (el) { beobachter.observe(el); });
})();


/* ==========================================================================
   Lupe — Archivstücke gross ansehen
   ==========================================================================

   Zusatz, wie alles hier. Ohne JavaScript ist jedes Stück ein gewöhnlicher
   Link auf die Bilddatei; der Browser zeigt sie dann eben allein an. Das
   ist keine schöne, aber eine vollständige Lösung, und sie kostet nichts.

   Mit JavaScript wird daraus ein <dialog>. Absichtlich ein echtes
   <dialog> und kein selbstgebautes Overlay: Fokusfalle, Escape, das
   Sperren der Seite dahinter und die Rückgabe des Fokus an das Stück,
   von dem aus man geöffnet hat, bringt der Browser dann von selbst mit.
   Kennt ein Browser showModal() nicht, greift das Skript gar nicht ein —
   dann bleibt es beim Link, und nichts ist kaputt.
   ========================================================================== */
(function () {
  'use strict';

  var stuecke = Array.prototype.slice.call(
    document.querySelectorAll('a[data-lupe]'));
  if (!stuecke.length) return;

  var probe = document.createElement('dialog');
  if (typeof probe.showModal !== 'function') return;

  var lupe = document.createElement('dialog');
  lupe.className = 'lupe';
  lupe.innerHTML =
    '<p class="lupe__zaehler" aria-hidden="true"></p>' +
    '<button type="button" class="lupe__knopf lupe__zu" aria-label="Schliessen">×</button>' +
    '<button type="button" class="lupe__knopf lupe__zurueck" aria-label="Vorheriges Bild">‹</button>' +
    '<button type="button" class="lupe__knopf lupe__vor" aria-label="Nächstes Bild">›</button>' +
    '<figure class="lupe__buehne"><img alt=""><figcaption></figcaption></figure>';
  document.body.appendChild(lupe);

  var bild    = lupe.querySelector('img');
  var legende = lupe.querySelector('figcaption');
  var zaehler = lupe.querySelector('.lupe__zaehler');
  var einzeln = stuecke.length < 2;

  if (einzeln) {
    lupe.querySelector('.lupe__zurueck').hidden = true;
    lupe.querySelector('.lupe__vor').hidden = true;
  }

  var jetzt = 0;

  /* Die Bildlegende steht schon unter dem Stück. Sie hier noch einmal zu
     pflegen hiesse, sie zweimal zu pflegen — also wird sie von dort
     genommen. Der Wischhinweis gehört nicht mit, der gilt nur im Raster. */
  function legendeVon(el) {
    var figur = el.closest('figure');
    var text = figur ? figur.querySelector('figcaption') : null;
    if (!text) return '';
    var kopie = text.cloneNode(true);
    var wisch = kopie.querySelector('.artefakt__wisch');
    if (wisch) wisch.remove();
    return kopie.textContent.trim();
  }

  function zeige(i) {
    jetzt = (i + stuecke.length) % stuecke.length;
    var el = stuecke[jetzt];
    var img = el.querySelector('img');
    bild.src = el.getAttribute('href');
    bild.alt = img ? img.getAttribute('alt') : '';
    legende.textContent = legendeVon(el);
    zaehler.textContent = einzeln ? '' : (jetzt + 1) + ' von ' + stuecke.length;
  }

  /* Wohin der Fokus nach dem Schliessen zurückgeht. <dialog> macht das
     von selbst — aber nur, wenn das auslösende Element beim Öffnen den
     Fokus hatte. Bei einem Mausklick auf einen Link ist das nicht in
     jedem Browser der Fall, deshalb wird er hier gemerkt. */
  var zurueckZu = null;

  stuecke.forEach(function (el, i) {
    el.addEventListener('click', function (e) {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
      e.preventDefault();
      zurueckZu = el;
      zeige(i);
      lupe.showModal();
    });
  });

  lupe.querySelector('.lupe__zu').addEventListener('click', function () {
    lupe.close();
  });
  lupe.querySelector('.lupe__vor').addEventListener('click', function () {
    zeige(jetzt + 1);
  });
  lupe.querySelector('.lupe__zurueck').addEventListener('click', function () {
    zeige(jetzt - 1);
  });

  lupe.addEventListener('keydown', function (e) {
    if (einzeln) return;
    if (e.key === 'ArrowRight') { e.preventDefault(); zeige(jetzt + 1); }
    if (e.key === 'ArrowLeft')  { e.preventDefault(); zeige(jetzt - 1); }
  });

  /* Klick auf den Grund schliesst. Der Dialog füllt den Schirm, also wird
     geprüft, ob wirklich daneben und nicht auf Bild oder Knopf geklickt
     wurde. */
  lupe.addEventListener('click', function (e) {
    if (e.target === lupe || e.target.classList.contains('lupe__buehne')) {
      lupe.close();
    }
  });

  /* Beim Schliessen die Quelle leeren, sonst behält der Browser bei
     zwanzig Archivstücken alle geladenen Vollbilder im Speicher. */
  lupe.addEventListener('close', function () {
    bild.removeAttribute('src');
    if (zurueckZu) { zurueckZu.focus(); zurueckZu = null; }
  });
})();


/* ==========================================================================
   Auftakt — Bildfolge am Scrollrad
   ==========================================================================

   Fünfzig Einzelbilder einer Kamerafahrt, gesteuert vom Scrollstand. Der
   Abschnitt im HTML ist versteckt; sichtbar macht ihn erst dieses Skript,
   und auch nur, wenn zwei Dinge stimmen: grosser Schirm und keine Bitte um
   weniger Bewegung. Sonst bleibt es beim Hero darunter.

   **Hier stand einmal eine dritte Bedingung, `hover: hover`** — gedacht als
   «hat ein Zeigergerät», um Tablets auszuschliessen. Sie hat den Auftakt
   auf einem Laptop mit Touchscreen abgeschaltet: Chrome hält dort den
   Finger für das erste Zeigergerät und meldet `hover: none`, obwohl ein
   Trackpad danebenliegt. Das betrifft heute einen grossen Teil aller
   verkauften Laptops — also genau das Gerät, für das der Auftakt gemacht
   ist. Und es fällt niemandem auf, weil die Seite dann einfach den Hero
   zeigt und völlig in Ordnung aussieht.

   Die Breite allein tut, was verlangt war («nicht auf dem Handy»): auch
   das grösste Handy quer misst rund 930 px und bleibt unter 1024.

   Zwei Entscheide, die das Ergebnis ausmachen:

   · **Es wird nicht auf das vollständige Laden gewartet.** Gezeichnet wird
     immer das nächstgelegene Bild, das schon da ist. Während des Ladens
     ist die Fahrt dadurch grob und wird von selbst flüssig — besser als
     ein Ladebalken, hinter dem die Seite steht.

   · **Gezeichnet wird auf <canvas>, nicht über src-Wechsel an einem <img>.**
     Ein Bildwechsel per src zeigt beim ersten Durchlauf für einen Moment
     nichts; die Leinwand behält, was drauf ist, bis das neue Bild da ist.
   ========================================================================== */
(function () {
  'use strict';

  var abschnitt = document.querySelector('[data-auftakt]');
  if (!abschnitt) return;

  var ANZAHL = parseInt(abschnitt.getAttribute('data-bilder'), 10);
  if (!ANZAHL || ANZAHL < 2) return;

  // Muss wörtlich derselbe Ausdruck sein wie im CSS, sonst lädt das Skript
  // Bilder für einen Abschnitt, den die Regel gar nicht einblendet — oder
  // umgekehrt. build.py prüft das nach jedem Lauf.
  var gross = window.matchMedia('(min-width: 1024px)');
  var sanft = window.matchMedia('(prefers-reduced-motion: reduce)');

  var buehne    = abschnitt.querySelector('.auftakt__buehne');
  var fest      = abschnitt.querySelector('.auftakt__fest');
  var leinwand  = abschnitt.querySelector('.auftakt__leinwand');
  var stift     = leinwand.getContext('2d', { alpha: false });

  var bilder  = new Array(ANZAHL);
  var bereit  = new Array(ANZAHL);
  var laeuft  = false;          // Auftakt ist eingeschaltet
  var gemalt  = -1;             // Kennung des zuletzt gemalten Zustands
  var wartend = false;          // ein Frame ist schon angefordert

  /* --- Bilder holen ------------------------------------------------------
     Das erste zuerst und allein: sobald es da ist, steht etwas auf der
     Leinwand und der Auftakt darf sichtbar werden. Erst danach der Rest,
     der Reihe nach. Scheitert schon das erste, bleibt alles aus. */
  function adresse(i) {
    return 'assets/img/auftakt/bild-' + (i + 1 < 10 ? '0' : '') + (i + 1) + '.webp';
  }

  function hole(i, fertig) {
    var bild = new Image();
    bild.decoding = 'async';
    bild.onload = function () {
      bilder[i] = bild; bereit[i] = true;
      if (fertig) fertig(true);
      zeichne();
    };
    bild.onerror = function () { if (fertig) fertig(false); };
    bild.src = adresse(i);
  }

  function holeRest() {
    var i = 1;
    (function weiter() {
      if (i >= ANZAHL) return;
      var k = i++;
      hole(k, weiter);
    })();
  }

  /* --- Zeichnen ----------------------------------------------------------
     Die Bilder sind 16:9, das Fenster ist es fast nie. Deshalb wird wie bei
     object-fit: cover skaliert und mittig beschnitten. */
  function naechstesDa(ziel) {
    if (bereit[ziel]) return ziel;
    for (var d = 1; d < ANZAHL; d++) {
      if (ziel - d >= 0 && bereit[ziel - d]) return ziel - d;
      if (ziel + d < ANZAHL && bereit[ziel + d]) return ziel + d;
    }
    return -1;
  }

  function masse() {
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var b = Math.round(fest.clientWidth * dpr);
    var h = Math.round(fest.clientHeight * dpr);
    if (leinwand.width !== b || leinwand.height !== h) {
      leinwand.width = b; leinwand.height = h;
      gemalt = -1;                       // Grösse geändert: neu zeichnen
    }
  }

  /* Ein Bild flächendeckend zeichnen — wie object-fit: cover. Die Vorlagen
     sind 16:9, das Fenster ist es fast nie. */
  function male(bild, deckung) {
    var cb = leinwand.width, ch = leinwand.height;
    var faktor = Math.max(cb / bild.naturalWidth, ch / bild.naturalHeight);
    var b = bild.naturalWidth * faktor, h = bild.naturalHeight * faktor;
    if (deckung !== 1) stift.globalAlpha = deckung;
    stift.drawImage(bild, (cb - b) / 2, (ch - h) / 2, b, h);
    stift.globalAlpha = 1;
  }

  /* --- Zeichnen mit Überblendung -----------------------------------------
     Fünfzig Bilder auf 130vh Scrollweg sind rund 23 Pixel je Bild — eine
     Rastung am Mausrad überspringt davon gut vier. Hart umgeschaltet
     ruckelt das sichtbar, und genau so sah es zuerst auch aus.

     Deshalb wird der Bruchteil zwischen zwei Bildern nicht weggerundet,
     sondern ausgespielt: das untere Bild voll, das obere mit dem
     Bruchteil als Deckung darüber. Aus fünfzig Stufen wird ein
     stufenloser Verlauf. Kostet keine einzige zusätzliche Datei.

     Liegt das obere Bild noch nicht vor, bleibt es beim unteren — dann
     ist es eben kurz stufig statt falsch. */
  function zeichne() {
    if (!laeuft) return;

    var genau = bildstand(fortschritt()) * (ANZAHL - 1);
    var unten = Math.floor(genau);
    var anteil = genau - unten;
    if (unten >= ANZAHL - 1) { unten = ANZAHL - 1; anteil = 0; }

    var a = naechstesDa(unten);
    if (a < 0) return;

    var b = (anteil > 0.01 && bereit[unten + 1]) ? unten + 1 : -1;
    var kennung = a * 1000 + (b < 0 ? 0 : Math.round(anteil * 100) + 1);
    if (kennung === gemalt) return;

    male(bilder[a], 1);
    if (b >= 0) male(bilder[b], anteil);
    gemalt = kennung;
  }

  /* --- Scrollstand -------------------------------------------------------
     0 am oberen Rand der Bühne, 1 wenn sie durchgescrollt ist. */
  function fortschritt() {
    var kasten = buehne.getBoundingClientRect();
    var strecke = kasten.height - window.innerHeight;
    if (strecke <= 0) return 0;
    var p = -kasten.top / strecke;
    return p < 0 ? 0 : (p > 1 ? 1 : p);
  }

  /* Der Titel steht am Anfang ruhig, tritt dann ab und ist bei gut der
     Hälfte weg. Die letzte Strecke gehört dem Bild allein. */
  function textDeckung(p) {
    if (p <= 0.12) return 1;
    if (p >= 0.52) return 0;
    return 1 - (p - 0.12) / 0.40;
  }

  /* --- Der Ablauf am Ende ------------------------------------------------
     Die Bilder laufen nicht über die ganze Bühne, sondern nur über die
     ersten BILDER_BIS. Der Rest gehört der Schlusskarte — sonst bliebe für
     sie ein Streifen von hundert Pixeln, und eine gestaffelte Einblendung
     braucht Weg.

     Der Ball verschwindet in Bild 48 hinter der Tischkante; gemessen am
     Gelbanteil der Bilder, nicht geschätzt. Das ist bei 47/49 der Folge,
     also kurz vor deren Ende — die Abblende setzt genau dort ein und
     schneidet ihn nicht mehr im Flug ab. */
  var BILDER_BIS = 0.62;

  /* Bildindex aus dem Gesamtfortschritt. Nach BILDER_BIS steht das letzte
     Bild still — darunter liegt dann ohnehin die Fläche. */
  function bildstand(p) {
    return Math.min(1, p / BILDER_BIS);
  }

  /* Blendet zwischen zwei Marken von 0 auf 1. Die Staffelung der
     Schlusskarte steht damit hier und nicht in verschachtelten calc(). */
  function spanne(p, von, bis) {
    if (p <= von) return 0;
    if (p >= bis) return 1;
    return (p - von) / (bis - von);
  }

  /* Weich anlaufen und weich auslaufen — linear wirkt bei Bewegung hart. */
  function weich(x) { return x * x * (3 - 2 * x); }

  function aktualisiere() {
    var p = fortschritt();
    var st = fest.style;

    st.setProperty('--auftakt-text', textDeckung(p).toFixed(3));
    st.setProperty('--auftakt-hinweis', (p <= 0.02 ? 1 : 0).toFixed(0));

    /* Die Fläche kommt erst, wenn der Ball hinter der Kante ist. */
    st.setProperty('--auftakt-abblende', weich(spanne(p, 0.60, 0.70)).toFixed(3));

    /* Dann ein Moment leere Fläche — und der Ball kommt zurück. */
    var k = spanne(p, 0.70, 1.0);          // Fortschritt der Schlusskarte
    st.setProperty('--auftakt-licht',    weich(spanne(k, 0.00, 0.26)).toFixed(3));
    st.setProperty('--auftakt-ball-da',  spanne(k, 0.10, 0.18).toFixed(3));
    st.setProperty('--auftakt-ball-weg', weich(spanne(k, 0.10, 0.48)).toFixed(3));
    st.setProperty('--auftakt-bogen',    weich(spanne(k, 0.10, 0.52)).toFixed(3));
    st.setProperty('--auftakt-logo',     weich(spanne(k, 0.40, 0.68)).toFixed(3));
    st.setProperty('--auftakt-strich',   weich(spanne(k, 0.58, 0.80)).toFixed(3));
    st.setProperty('--auftakt-zeile',    weich(spanne(k, 0.68, 0.92)).toFixed(3));

    zeichne();
  }

  function beiScroll() {
    if (wartend) return;
    wartend = true;
    requestAnimationFrame(function () { aktualisiere(); wartend = false; });
  }

  function beiGroesse() { masse(); aktualisiere(); }

  /* --- Ein- und ausschalten ---------------------------------------------- */
  function einschalten() {
    if (laeuft) return;
    laeuft = true;
    abschnitt.hidden = false;
    document.documentElement.classList.add('auftakt-an');
    masse();
    aktualisiere();
    window.addEventListener('scroll', beiScroll, { passive: true });
    window.addEventListener('resize', beiGroesse);
  }

  function ausschalten() {
    if (!laeuft) return;
    laeuft = false;
    abschnitt.hidden = true;
    document.documentElement.classList.remove('auftakt-an');
    window.removeEventListener('scroll', beiScroll);
    window.removeEventListener('resize', beiGroesse);
  }

  function pruefe() {
    if (gross.matches && !sanft.matches) einschalten();
    else ausschalten();
  }

  if (!gross.matches || sanft.matches) {
    // Nichts laden, was hier niemand sieht — das sind 1.3 MB.
    // Wird das Fenster später breit genug, wird nachgeholt.
    var einmal = function () {
      if (gross.matches && !sanft.matches) {
        gross.removeEventListener('change', einmal);
        start();
      }
    };
    gross.addEventListener('change', einmal);
    return;
  }

  function start() {
    hole(0, function (erfolg) {
      if (!erfolg) return;          // Bildfolge fehlt: Hero bleibt stehen
      pruefe();
      holeRest();
      gross.addEventListener('change', pruefe);
      sanft.addEventListener('change', pruefe);
    });
  }

  start();
})();


/* ==========================================================================
   Kopfzeile: weicht beim Hinunterscrollen, kommt beim Hochscrollen zurück
   ==========================================================================

   Gilt auf allen Seiten. Ohne JavaScript bleibt sie schlicht immer stehen,
   also genau so, wie sie vorher war.

   Die Schwellen sind bewusst ungleich: erst ab 140 px Scrollstand darf sie
   überhaupt weichen (sonst zuckt sie schon bei der ersten Radrastung), und
   sie reagiert erst ab 6 px Richtungsänderung. Ohne diese Totzone flackert
   sie beim Trackpad, dessen Werte um ein, zwei Pixel schwanken.
   ========================================================================== */
(function () {
  'use strict';

  var kopf = document.querySelector('.kopf');
  if (!kopf) return;
  var nav = document.querySelector('.nav');
  var wurzel = document.documentElement;

  var AB       = 140;   // darunter ist die Kopfzeile immer da
  var TOTZONE  = 6;     // kleinere Bewegungen zählen nicht

  var letzter = window.scrollY || 0;
  var wartend = false;

  function pruefe() {
    var jetzt = window.scrollY || 0;
    var weg   = jetzt - letzter;

    if (Math.abs(weg) < TOTZONE) return;

    // Offenes Menü hält die Kopfzeile fest — sonst führe der Schliessknopf
    // mit ihr davon.
    var menueOffen = nav && nav.getAttribute('data-offen') === 'true';

    if (jetzt <= AB || weg < 0 || menueOffen) {
      wurzel.classList.remove('kopf-weg');
    } else {
      wurzel.classList.add('kopf-weg');
    }
    letzter = jetzt;
  }

  window.addEventListener('scroll', function () {
    if (wartend) return;
    wartend = true;
    requestAnimationFrame(function () { pruefe(); wartend = false; });
  }, { passive: true });

  // Wer per Tastatur in die Seite springt, soll die Kopfzeile sehen.
  document.addEventListener('focusin', function (e) {
    if (kopf.contains(e.target)) wurzel.classList.remove('kopf-weg');
  });

  /* Die Höhe der Kopfzeile als CSS-Grösse veröffentlichen.
     -----------------------------------------------------------------
     Die Kopfzeile steht im Fluss, nicht darüber. Ein Abschnitt mit
     `position: sticky; top: 0; height: 100vh` beginnt deshalb ganz oben
     auf der Seite nicht bei 0, sondern unter ihr — und sein unterer
     Rand liegt um genau diese Höhe unter der Fensterkante. Wer etwas an
     diesen unteren Rand hängt (der Scrollhinweis im Auftakt), müsste
     sonst eine Zahl raten, die beim nächsten Umbau der Kopfzeile still
     falsch wird.

     Gemessen statt geschätzt, und bei jeder Breitenänderung neu. */
  function hoeheMelden() {
    wurzel.style.setProperty('--kopf-hoehe', kopf.offsetHeight + 'px');
  }
  hoeheMelden();
  window.addEventListener('resize', hoeheMelden, { passive: true });
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(hoeheMelden);   // Schriftwechsel ändert die Höhe
  }
})();
