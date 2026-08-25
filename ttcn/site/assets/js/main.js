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
