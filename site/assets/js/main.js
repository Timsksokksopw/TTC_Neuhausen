/* TTC Neuhausen – Verhalten. Alles hier ist Zusatz: ohne JavaScript bleibt
   jede Seite vollständig lesbar und bedienbar. */
(function () {
  "use strict";

  var html = document.documentElement;
  var ruhig = window.matchMedia("(prefers-reduced-motion: reduce)");
  var TAGE = ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"];
  var TAGNAMEN = { Mo: "Montag", Di: "Dienstag", Mi: "Mittwoch", Do: "Donnerstag", Fr: "Freitag", Sa: "Samstag", So: "Sonntag" };
  var jetzt = new Date();
  var heute = TAGE[jetzt.getDay()];

  function alle(sel, wo) { return Array.prototype.slice.call((wo || document).querySelectorAll(sel)); }
  function begrenzt(x, a, b) { return Math.min(Math.max(x, a), b); }
  function stueck(p, von, bis) { return begrenzt((p - von) / (bis - von), 0, 1); }
  function weich(t) { return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  function mix(a, b, t) { return a + (b - a) * t; }
  function minuten(hhmm) { var t = hhmm.split(":"); return +t[0] * 60 + +t[1]; }

  alle("[data-jahr]").forEach(function (el) { el.textContent = jetzt.getFullYear(); });

  /* --- Kopfzeile: weicht beim Hinunterscrollen, kommt beim Hochscrollen --- */
  var kopf = document.querySelector("[data-kopf]");
  var knopf = document.querySelector(".kopf__menue");
  var zuletzt = window.scrollY;
  var kopfTick = false;

  function kopfPruefen() {
    var y = window.scrollY;
    var offen = html.classList.contains("menue-offen");
    if (!offen && Math.abs(y - zuletzt) > 6) {
      html.classList.toggle("kopf-weg", y > zuletzt && y > 160);
      zuletzt = y;
    }
    kopfTick = false;
  }
  window.addEventListener("scroll", function () {
    if (!kopfTick) { kopfTick = true; requestAnimationFrame(kopfPruefen); }
  }, { passive: true });
  if (kopf) kopf.addEventListener("focusin", function () { html.classList.remove("kopf-weg"); });

  function hoeheMelden() {
    if (kopf) html.style.setProperty("--kopf-hoehe", kopf.offsetHeight + "px");
  }
  hoeheMelden();
  window.addEventListener("resize", hoeheMelden);

  /* --- Menü auf kleinen Schirmen ---------------------------------------- */
  function menue(auf) {
    html.classList.toggle("menue-offen", auf);
    knopf.setAttribute("aria-expanded", String(auf));
    knopf.querySelector(".kopf__menue-text").textContent = auf ? "Schliessen" : "Menü";
  }
  if (knopf) {
    knopf.addEventListener("click", function () { menue(!html.classList.contains("menue-offen")); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && html.classList.contains("menue-offen")) { menue(false); knopf.focus(); }
    });
    window.matchMedia("(min-width: 1061px)").addEventListener("change", function (m) { if (m.matches) menue(false); });
  }

  /* --- Bühne der Startseite: der Tisch dreht sich in die Draufsicht ------ */
  var buehne = document.querySelector("[data-buehne]");
  if (buehne) {
    var gross = window.matchMedia("(min-width: 1024px) and (min-height: 620px)");
    var tisch = buehne.querySelector(".tisch");
    var tick = false;

    var setzen = function () {
      tick = false;
      if (!buehne.classList.contains("ist-aktiv")) return;
      var r = buehne.getBoundingClientRect();
      var p = begrenzt(-r.top / (r.height - window.innerHeight), 0, 1);
      var t = weich(stueck(p, .06, .62));
      var s = buehne.style;
      s.setProperty("--rx", mix(58, 0, t).toFixed(2) + "deg");
      s.setProperty("--rz", mix(-30, 0, t).toFixed(2) + "deg");
      s.setProperty("--s", mix(.5, 1, t).toFixed(4));
      s.setProperty("--tx", mix(window.innerWidth * .22, 0, t).toFixed(1) + "px");
      s.setProperty("--ty", mix(window.innerHeight * .03, 0, t).toFixed(1) + "px");
      s.setProperty("--text-o", (1 - stueck(p, .04, .3)).toFixed(3));
      s.setProperty("--text-y", (-80 * stueck(p, .04, .3)).toFixed(1) + "px");
      s.setProperty("--aktuell-o", (1 - stueck(p, 0, .16)).toFixed(3));
      s.setProperty("--ball-o", (1 - stueck(p, .5, .62)).toFixed(3));
      var a = stueck(p, .66, .84);
      s.setProperty("--angebote-o", a.toFixed(3));
      buehne.classList.toggle("angebote-an", a > .6);
    };
    var anfordern = function () { if (!tick) { tick = true; requestAnimationFrame(setzen); } };

    var umschalten = function () {
      var an = gross.matches && !ruhig.matches;
      buehne.classList.toggle("ist-aktiv", an);
      if (!an) {
        ["--rx", "--rz", "--s", "--tx", "--ty", "--text-o", "--text-y", "--aktuell-o", "--ball-o", "--angebote-o"]
          .forEach(function (v) { buehne.style.removeProperty(v); });
        buehne.classList.remove("angebote-an");
      }
      setzen();
    };
    umschalten();
    gross.addEventListener("change", umschalten);
    ruhig.addEventListener("change", umschalten);
    window.addEventListener("scroll", anfordern, { passive: true });
    window.addEventListener("resize", anfordern);

    // Der Ball ruht, solange niemand den Tisch sieht.
    if ("IntersectionObserver" in window && tisch) {
      new IntersectionObserver(function (e) {
        tisch.classList.toggle("ist-pause", !e[0].isIntersecting);
      }).observe(tisch);
    }
  }

  /* --- Heute im Training ------------------------------------------------ */
  var datenEl = document.getElementById("trainingsdaten");
  var heuteEl = document.querySelector("[data-heute]");
  if (datenEl && heuteEl) {
    var einheiten = JSON.parse(datenEl.textContent);
    var nun = jetzt.getHours() * 60 + jetzt.getMinutes();
    var heuteListe = einheiten.filter(function (x) { return x.tag === heute && minuten(x.bis) > nun; });
    var text;
    if (heuteListe.length) {
      var x = heuteListe[0];
      var laeuft = minuten(x.von) <= nun;
      text = "<b>" + (laeuft ? "Jetzt in der Halle:" : "Heute, " + x.von + ":") + "</b> " + x.gruppe +
        ", " + x.halle + (heuteListe.length > 1 ? " · danach noch " + (heuteListe.length - 1) : "");
    } else {
      var reihenfolge = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"];
      var start = reihenfolge.indexOf(heute);
      var naechste = null;
      for (var i = 1; i <= 7 && !naechste; i++) {
        var tag = reihenfolge[(start + i) % 7];
        naechste = einheiten.filter(function (x) { return x.tag === tag; })[0] || null;
      }
      text = naechste ? "<b>Heute kein Training mehr.</b> Nächstes: " + TAGNAMEN[naechste.tag] + ", " +
        naechste.von + ", " + naechste.gruppe : "";
    }
    if (text) {
      heuteEl.innerHTML = text + ' · <a href="training.html">Wochenplan</a>';
      heuteEl.hidden = false;
    }
  }
  var listeEl = document.querySelector("[data-heute-liste]");
  if (datenEl && listeEl) {
    var alleEinheiten = JSON.parse(datenEl.textContent);
    var jetztMin = jetzt.getHours() * 60 + jetzt.getMinutes();
    var heutige = alleEinheiten.filter(function (x) { return x.tag === heute; });
    if (heutige.length) {
      listeEl.innerHTML = heutige.map(function (x) {
        var zustand = minuten(x.bis) <= jetztMin ? "ist-vorbei" : (minuten(x.von) <= jetztMin ? "ist-jetzt" : "");
        return '<li class="' + zustand + '"><b>' + x.von + '</b><span><strong>' + x.gruppe + '</strong>' +
          x.halle + ", bis " + x.bis + "</span></li>";
      }).join("");
    } else {
      listeEl.innerHTML = '<li class="heutetafel__leer">Heute, am ' + TAGNAMEN[heute] +
        ", ist kein Training angesetzt. Mitglieder mit Hallenbeitrag spielen im TTZ Ebnat trotzdem.</li>";
    }
  }
  alle('.woche__tag[data-tag="' + heute + '"], .plan__tag[data-tag="' + heute + '"]').forEach(function (el) {
    el.classList.add("ist-heute");
  });

  /* --- Wochenplan: nach Angebot hervorheben ------------------------------ */
  alle("[data-plan]").forEach(function (plan) {
    var knoepfe = alle(".plan__filter button", plan);
    var bloecke = alle(".einheit", plan);
    var stand = plan.querySelector("[data-plan-stand]");
    knoepfe.forEach(function (k) {
      k.addEventListener("click", function () {
        var zeigt = k.getAttribute("data-zeigt");
        var n = 0;
        plan.setAttribute("data-filter", zeigt);
        knoepfe.forEach(function (b) { b.setAttribute("aria-pressed", String(b === k)); });
        bloecke.forEach(function (b) {
          var passt = zeigt === "alle" || b.getAttribute("data-angebot") === zeigt;
          b.classList.toggle("ist-leise", !passt);
          if (passt) n++;
        });
        if (stand) stand.textContent = (zeigt === "alle" ? "Alle " : k.textContent + ": ") + n + " Einheiten hervorgehoben";
      });
    });
  });

  /* --- Termine: Vergangenes ausblenden, auch ohne neuen Build ------------ */
  var iso = jetzt.getFullYear() + "-" + ("0" + (jetzt.getMonth() + 1)).slice(-2) + "-" + ("0" + jetzt.getDate()).slice(-2);
  alle("[data-termine]").forEach(function (liste) {
    var sichtbar = 0;
    alle("[data-datum]", liste).forEach(function (t) {
      var vorbei = t.getAttribute("data-datum") < iso;
      t.hidden = vorbei;
      if (!vorbei) sichtbar++;
    });
    var leer = liste.querySelector(".termine__leer");
    if (leer) leer.hidden = sichtbar > 0;
  });

  /* --- Anzeigetafel: Ziffern klappen beim Hereinscrollen ------------------ */
  function tafelBauen(dd) {
    var ziel = dd.getAttribute("data-zahl");
    dd.setAttribute("aria-label", ziel);
    dd.textContent = "";
    ziel.split("").forEach(function (z) {
      var k = document.createElement("span");
      k.className = "ziffer";
      k.setAttribute("aria-hidden", "true");
      k.textContent = z;
      k.dataset.ziel = z;
      dd.appendChild(k);
    });
  }
  function klappen(k, schritte, warten) {
    var ziel = +k.dataset.ziel;
    var werte = [];
    for (var i = schritte; i > 0; i--) werte.push((ziel - i + 10) % 10);
    werte.push(ziel);
    k.textContent = werte[0];
    var j = 0;
    setTimeout(function weiter() {
      j++;
      if (j >= werte.length) return;
      k.animate([{ transform: "rotateX(0deg)" }, { transform: "rotateX(-90deg)" }],
        { duration: 70, easing: "ease-in" }).onfinish = function () {
        k.textContent = werte[j];
        k.animate([{ transform: "rotateX(90deg)" }, { transform: "rotateX(0deg)" }],
          { duration: 90, easing: "ease-out" }).onfinish = weiter;
      };
    }, warten);
  }
  alle("[data-tafel] dd[data-zahl]").forEach(tafelBauen);
  if (!ruhig.matches && "IntersectionObserver" in window && Element.prototype.animate) {
    var tafelBeobachter = new IntersectionObserver(function (eintraege) {
      eintraege.forEach(function (e) {
        if (!e.isIntersecting) return;
        tafelBeobachter.unobserve(e.target);
        alle(".ziffer", e.target).forEach(function (k, i) { klappen(k, 4 + (i % 3), 120 + i * 70); });
      });
    }, { threshold: .5 });
    alle("[data-tafel]").forEach(function (t) { tafelBeobachter.observe(t); });
  }

  /* --- Tiefe: Filmstreifen & Co. folgen dem Scrollstand -------------------- */
  var tiefen = alle("[data-tiefe]");
  if (tiefen.length && !ruhig.matches) {
    var tiefeTick = false;
    var tiefeSetzen = function () {
      tiefeTick = false;
      tiefen.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.bottom < 0 || r.top > window.innerHeight) return;
        var q = begrenzt((window.innerHeight - r.top) / (window.innerHeight + r.height), 0, 1);
        el.style.setProperty("--q", q.toFixed(4));
      });
    };
    window.addEventListener("scroll", function () {
      if (!tiefeTick) { tiefeTick = true; requestAnimationFrame(tiefeSetzen); }
    }, { passive: true });
    tiefeSetzen();
  }

  /* --- Kippen: Karten neigen sich leicht zum Zeiger ----------------------- */
  if (window.matchMedia("(hover: hover) and (pointer: fine)").matches && !ruhig.matches) {
    alle("[data-kippen]").forEach(function (el) {
      el.addEventListener("pointermove", function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - .5;
        var y = (e.clientY - r.top) / r.height - .5;
        el.classList.add("ist-gekippt");
        el.style.setProperty("--kx", (x * 7).toFixed(2) + "deg");
        el.style.setProperty("--ky", (-y * 5).toFixed(2) + "deg");
      });
      el.addEventListener("pointerleave", function () {
        el.classList.remove("ist-gekippt");
        el.style.removeProperty("--kx");
        el.style.removeProperty("--ky");
      });
    });
  }

  /* --- Einblenden ------------------------------------------------------- */
  var auftauchen = alle(".auftauchen");
  if (auftauchen.length) {
    if (!("IntersectionObserver" in window)) {
      auftauchen.forEach(function (el) { el.classList.add("ist-sichtbar"); });
    } else {
      var sicht = new IntersectionObserver(function (eintraege) {
        eintraege.forEach(function (e) {
          if (e.isIntersecting) { e.target.classList.add("ist-sichtbar"); sicht.unobserve(e.target); }
        });
      }, { rootMargin: "0px 0px -8% 0px" });
      auftauchen.forEach(function (el) { sicht.observe(el); });
    }
  }

  /* --- Beitragsrechner --------------------------------------------------- */
  alle("[data-rechner]").forEach(function (form) {
    var ausgabe = form.querySelector("[data-rechner-ergebnis]");
    var legi = form.querySelector("input[name=kulturlegi]");
    function franken(x) { return x % 1 ? x.toFixed(2) : x + ".–"; }
    function rechnen() {
      var wahl = form.querySelector("input[name=kategorie]:checked");
      if (!wahl) return;
      var beitrag = +wahl.getAttribute("data-monat");
      var mitLegi = legi.checked && wahl.hasAttribute("data-legi");
      if (mitLegi) beitrag = Math.round(beitrag * 30) / 100;
      var halle = wahl.hasAttribute("data-halle") ? 18 : 0;
      var total = beitrag + halle;
      ausgabe.innerHTML = "<b>CHF " + franken(total) + "</b> im Monat" +
        "<span>CHF " + franken(Math.round(total * 12 * 100) / 100) + " im Jahr</span>" +
        "<small>Beitrag " + franken(beitrag) + (halle ? " + Hallenbeitrag 18.–" : "") +
        (legi.checked && !mitLegi ? " · KulturLegi gilt für AktivPlus und AktivPlus Senioren" : "") + "</small>";
    }
    form.addEventListener("change", rechnen);
    rechnen();
  });

  /* --- Lupe: Archivstücke gross ansehen ------------------------------------ */
  var stuecke = alle("a[data-lupe]");
  if (stuecke.length && typeof document.createElement("dialog").showModal === "function") {
    var lupe = document.createElement("dialog");
    lupe.className = "lupe";
    lupe.innerHTML = '<p class="lupe__zaehler" aria-hidden="true"></p>' +
      '<button type="button" class="lupe__knopf lupe__zu" aria-label="Schliessen">×</button>' +
      '<button type="button" class="lupe__knopf lupe__zurueck" aria-label="Vorheriges Bild">‹</button>' +
      '<button type="button" class="lupe__knopf lupe__vor" aria-label="Nächstes Bild">›</button>' +
      '<figure class="lupe__buehne"><img alt=""><figcaption></figcaption></figure>';
    document.body.appendChild(lupe);
    var bild = lupe.querySelector("img");
    var legende = lupe.querySelector("figcaption");
    var zaehler = lupe.querySelector(".lupe__zaehler");
    var nr = 0;
    var zeige = function (i) {
      nr = (i + stuecke.length) % stuecke.length;
      var a = stuecke[nr];
      var fig = a.closest("figure");
      var cap = fig && fig.querySelector("figcaption");
      bild.src = a.getAttribute("href");
      bild.alt = a.querySelector("img").getAttribute("alt");
      legende.textContent = cap ? cap.textContent.trim() : "";
      zaehler.textContent = (nr + 1) + " / " + stuecke.length;
    };
    stuecke.forEach(function (a, i) {
      a.addEventListener("click", function (e) {
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
        e.preventDefault();
        zeige(i);
        lupe.showModal();
      });
    });
    lupe.querySelector(".lupe__zu").addEventListener("click", function () { lupe.close(); });
    lupe.querySelector(".lupe__vor").addEventListener("click", function () { zeige(nr + 1); });
    lupe.querySelector(".lupe__zurueck").addEventListener("click", function () { zeige(nr - 1); });
    lupe.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { e.preventDefault(); zeige(nr + 1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); zeige(nr - 1); }
    });
    lupe.addEventListener("click", function (e) { if (e.target === lupe) lupe.close(); });
  }
})();
