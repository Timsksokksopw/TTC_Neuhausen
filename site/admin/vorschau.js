/* Vorschau in der Redaktion: der Beitrag, wie er auf der Website steht – mit
   den Stilen der Website und demselben Aufbau wie beitrag_html() und
   galerie_html() in build.py. Ändert sich dort etwas, gehört es auch hierher. */
(function () {
  "use strict";
  if (!window.CMS || !window.h) return;
  var h = window.h;
  var site = new URL("../", document.baseURI).href;

  ["tokens", "base", "komponenten", "seiten"].forEach(function (name) {
    CMS.registerPreviewStyle(site + "assets/css/" + name + ".css");
  });
  CMS.registerPreviewStyle(
    "body { margin: 0; }" +
    ".vorschau .aufmacher { padding-top: 28px; }" +
    ".vorschau__hinweis { margin: 0 0 24px; padding: 14px 18px; border-left: 4px solid var(--blau);" +
    "  background: var(--papier-2); font-size: 15px; }",
    { raw: true });

  var MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
                "August", "September", "Oktober", "November", "Dezember"];

  function datumLang(wert) {
    var t = String(wert || "").slice(0, 10).split("-");
    return t.length === 3 && MONATE[+t[1] - 1] ? +t[2] + ". " + MONATE[+t[1] - 1] + " " + t[0] : "";
  }

  // Die Redaktion reicht Listen und Objekte je nach Version als Immutable
  // oder als gewöhnliche Werte – beides geht.
  function liste(wert) {
    if (!wert) return [];
    if (Array.isArray(wert)) return wert;
    if (typeof wert.toArray === "function") return wert.toArray();
    return [];
  }
  function feld(wert, name) {
    if (!wert) return "";
    return (typeof wert.get === "function" ? wert.get(name) : wert[name]) || "";
  }
  function text(wert) { return typeof wert === "string" ? wert.trim() : ""; }

  var NewsVorschau = function (props) {
    var daten = function (name) { return props.entry.getIn(["data", name]); };
    var bild = function (pfad) {
      if (!pfad) return "";
      var datei = props.getAsset(pfad);
      return datei ? String(datei) : site + String(pfad).replace(/^\//, "");
    };
    var img = function (pfad, alt, klasse) {
      return h("img", { src: bild(pfad), alt: alt || "", className: klasse || undefined });
    };

    var titel = text(daten("titel"));
    var ausschnitt = text(daten("ausschnitt"));
    var herkunft = [text(daten("autor")) && "Text: " + text(daten("autor")),
                    text(daten("bildnachweis")) && "Bild: " + text(daten("bildnachweis"))]
      .filter(Boolean).join(" · ");

    var inhalt = [];
    liste(daten("absaetze")).forEach(function (block, i) {
      var art = feld(block, "art") || "absatz";
      var wert = text(feld(block, "text"));
      if (art === "absatz") {
        wert.split(/\n+/).forEach(function (zeile, j) {
          if (zeile.trim()) inhalt.push(h("p", { key: i + "." + j }, zeile.trim()));
        });
      } else if (art === "titel" && wert) {
        inhalt.push(h("h2", { key: i }, wert));
      } else if (art === "zitat" && wert) {
        var wer = text(feld(block, "wer"));
        inhalt.push(h("blockquote", { key: i, className: "zitat" },
          h("p", null, wert), wer ? h("cite", null, wer) : null));
      } else if (art === "bild" && feld(block, "bild")) {
        var legende = text(feld(block, "beschreibung"));
        inhalt.push(h("figure", { key: i, className: "bild bild--im-text" },
          h("a", null, img(feld(block, "bild"), legende)),
          legende ? h("figcaption", null, legende) : null));
      } else if (art === "liste") {
        var punkte = liste(feld(block, "punkte")).map(function (p) {
          return text(typeof p === "string" ? p : feld(p, "punkt"));
        }).filter(Boolean);
        if (punkte.length) {
          inhalt.push(h("div", { key: i, className: "rangliste" },
            text(feld(block, "titel")) ? h("h3", null, text(feld(block, "titel"))) : null,
            h("ol", null, punkte.map(function (p, j) { return h("li", { key: j }, p); }))));
        }
      }
    });

    var galerie = liste(daten("galerie")).filter(Boolean);
    var hinweis = !inhalt.length && !galerie.length && !daten("pdf")
      ? h("p", { className: "vorschau__hinweis" },
          "Ohne Text steht der Beitrag nur als kurze Meldung in der News-Liste, ohne eigene Seite.")
      : null;
    if (daten("pdf")) {
      inhalt.push(h("p", { key: "pdf" }, h("a", { className: "pfeil-link" },
        text(daten("pdf_titel")) || "Dokument als PDF", h("span", { className: "pfeil", "aria-hidden": "true" }))));
    }

    return h("div", { className: "vorschau" },
      h("header", { className: "aufmacher aufmacher--schmal" },
        h("div", { className: "wrap" },
          h("p", { className: "rubrik" }, datumLang(daten("datum"))),
          h("h1", { className: "h1--mittel" }, titel || "Titel"),
          text(daten("anriss")) ? h("p", { className: "lead" }, text(daten("anriss"))) : null)),
      h("section", { className: "flaeche--papier eng" },
        h("div", { className: "wrap" },
          hinweis,
          daten("bild") ? h("figure", { className: "bild bild--breit" },
            img(daten("bild"), text(daten("bildalt")), ausschnitt && ausschnitt !== "mitte" ? "ausschnitt--" + ausschnitt : ""),
            herkunft ? h("figcaption", null, h("span", { className: "nachweis" }, herkunft)) : null) : null,
          h("div", { className: "text beitrag" }, inhalt),
          galerie.length ? h("section", { className: "galerie" },
            h("h2", { className: "galerie__titel" }, "Bilder ", h("span", null, galerie.length)),
            h("ul", { className: "galerie__raster" }, galerie.map(function (pfad, i) {
              return h("li", { key: i, style: { "--r": 1.5 } },
                h("figure", null, h("a", null, img(pfad, "Bild " + (i + 1)))));
            }))) : null)));
  };

  CMS.registerPreviewTemplate("news", NewsVorschau);
})();
