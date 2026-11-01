/* ==========================================================================
   123 school - gedeeld script voor alle pagina's (v2)
   Bevat: antwoord openklappen (KB), menuknop, toegankelijkheid, meerkeuze-quiz (MP) met
   willekeurige volgorde en pagina's van 15 vragen, zwevende knop "Controleer nu", en
   de scripts van de beginpagina. Alleen frontend, geen server nodig.
   Derde-partijbibliotheken (w3.js, w3data.js, jQuery, Bootstrap) staan nog steeds in de HTML.
   ========================================================================== */

var VRAGEN_PER_PAGINA = 15;

/* Voer een functie uit zodra de pagina geladen is (ook als dat al gebeurd is). */
function klaar(fn) {
  /* Met i18n.js (window.i18nKlaar) wachten we tot de tekst uit de JSON-bestanden in de pagina staat. */
  var start = function () { if (window.i18nKlaar) { window.i18nKlaar.then(fn); } else { fn(); } };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
}

/* Tekst in de taal van de pagina (lang/<taal>/ui.json via i18n.js). */
function T(sleutel, vars) { return window.i18n ? window.i18n.t(sleutel, vars) : sleutel; }
function taalIsEN() { return !!window.i18n && window.i18n.lang === 'en'; }

/* Schud een lijst willekeurig (Fisher-Yates). Geeft een nieuwe lijst terug. */
function schud(lijst) {
  var a = lijst.slice();
  for (var i = a.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var t = a[i]; a[i] = a[j]; a[j] = t;
  }
  return a;
}

/* ---------- Navigatie en antwoorden openklappen ---------- */

/* Antwoord openen of sluiten (KB-pagina's en spelletjesknoppen op de beginpagina).
   Met een tweede argument (this) moet je eerst iets typen voordat het antwoord opengaat (Sorteren-pagina). */
function myFunction(id, knop) {
  var x = document.getElementById(id);
  if (!x) { return; }
  if (knop) {
    var input = knop.nextElementSibling;
    if (input && input.value.length < 1) {
      /* Geen pop-up (alert): een rustige melding naast het invoerveld */
      var melding = input.parentNode.querySelector('.inline-melding');
      if (!melding) {
        melding = document.createElement('p');
        melding.className = 'inline-melding';
        melding.setAttribute('role', 'alert');
        input.parentNode.insertBefore(melding, input.nextSibling);
      }
      melding.textContent = T('kb.typ_eerst');
      return;
    }
  }
  var voor = x.previousElementSibling;
  if (x.className.indexOf('w3-show') == -1) {
    x.className += ' w3-show';
    if (voor) { voor.className = voor.className.replace('w3-black', 'spel-open'); }
  } else {
    x.className = x.className.replace(' w3-show', '');
    if (voor) { voor.className = voor.className.replace('spel-open', 'w3-black'); }
  }
}

/* Menuknop voor kleine schermen */
function openNav(sluit) {
  var x = document.getElementById('navDemo');
  if (!x) { return; }
  var open = x.className.indexOf('w3-show') != -1;
  if (open) {
    x.className = x.className.replace(' w3-show', '');
  } else if (sluit !== true) {
    x.className += ' w3-show';
    open = false;
  }
  var knop = document.querySelector('[aria-controls="navDemo"]');
  if (knop) { knop.setAttribute('aria-expanded', x.className.indexOf('w3-show') != -1 ? 'true' : 'false'); }
}
/* Het menu sluit zelf als je een onderdeel kiest of op Escape drukt (anders blijft het over de pagina hangen) */
document.addEventListener('click', function (e) {
  var a = e.target.closest ? e.target.closest('#navDemo a') : null;
  if (a) { openNav(true); }
});
document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') { openNav(true); }
});

/* Zijmenu (beginpagina) */
function w3_open() {
  var x = document.getElementById('mySidebar');
  if (!x) { return; }
  x.style.width = '300px';
  x.style.paddingTop = '10%';
  x.style.display = 'block';
}
function w3_close() {
  var x = document.getElementById('mySidebar');
  if (x) { x.style.display = 'none'; }
}

/* Zet bij elk antwoord ook tekst "Goed" of "Niet goed", zodat de uitkomst niet alleen aan kleur te zien is. */
function markeer(container, goed) {
  var oud = container.querySelector('.uitslag');
  if (oud) { oud.parentNode.removeChild(oud); }
  var el = document.createElement('div');
  el.className = 'uitslag ' + (goed ? 'uitslag-goed' : 'uitslag-fout');
  el.textContent = goed ? T('res.goed') : T('res.fout');
  container.appendChild(el);
}

/* Externe pagina's laden (menu) met w3data.js */
/* (pilot: menu en voet komen uit i18n.js, geen w3IncludeHTML nodig) */

/* ---------- Toegankelijkheid voor de vraag-antwoordpagina's (KB) ---------- */
klaar(function () {
  var knoppen = document.querySelectorAll('button[onclick^="myFunction"]');
  knoppen.forEach(function (knop) {
    var m = knop.getAttribute('onclick').match(/myFunction\(["']([^"']+)["']/);
    if (!m) { return; }
    knop.setAttribute('aria-controls', m[1]);
    knop.setAttribute('aria-expanded', 'false');
    knop.addEventListener('click', function () {
      var doel = document.getElementById(m[1]);
      var open = doel && doel.className.indexOf('w3-show') !== -1;
      knop.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });
});

/* ---------- Pagina's van 15 vragen met knop "Meer vragen (nog X)" ----------
   blokken: lijst met elementen (een per vraag), allemaal in dezelfde ouder; de knop komt in ouder vlak voor anker (of aan het eind).
   Alles na de eerste 15 wordt verborgen (hidden). Geeft een functie terug die het aantal getoonde vragen levert. */
function maakPaginering(blokken, ouder, anker, focusDoel) {
  var totaal = blokken.length;
  var getoond = Math.min(VRAGEN_PER_PAGINA, totaal);
  for (var i = getoond; i < totaal; i++) { blokken[i].hidden = true; }
  var info = { getoond: function () { return getoond; }, totaal: totaal };
  if (totaal <= VRAGEN_PER_PAGINA) { return info; }

  var wrap = document.createElement('div');
  wrap.className = 'meer-vragen w3-center';
  var knop = document.createElement('button');
  knop.type = 'button';
  knop.className = 'w3-button knop-blauw';
  wrap.appendChild(knop);
  ouder.insertBefore(wrap, anker);

  function label() { knop.textContent = T('meer', { n: totaal - getoond }); }
  label();
  knop.addEventListener('click', function () {
    var eerste = getoond;
    getoond = Math.min(getoond + VRAGEN_PER_PAGINA, totaal);
    for (var i = eerste; i < getoond; i++) { blokken[i].hidden = false; }
    var doel = focusDoel(blokken[eerste]);
    if (getoond >= totaal) { wrap.parentNode.removeChild(wrap); } else { label(); }
    /* Focus naar de eerste nieuwe vraag, zonder dat de pagina verspringt */
    if (doel && doel.focus) { doel.focus({ preventScroll: true }); }
  });
  return info;
}

/* ---------- KB-pagina's: vragen in willekeurige volgorde, eerst 15 tonen ---------- */
klaar(function () {
  var knoppen = document.querySelectorAll('button.vraag-knop');
  if (!knoppen.length) { return; }
  var ouder = knoppen[0].parentNode.parentNode;
  var blokken = [];
  knoppen.forEach(function (k) {
    if (k.parentNode.parentNode === ouder) { blokken.push(k.parentNode); }
  });
  if (blokken.length < 2) { return; }

  /* Browsers onthouden getypte antwoorden op positie; na het husselen zou dat verkeerd gaan. */
  document.querySelectorAll('input[type=text]').forEach(function (inp) { inp.setAttribute('autocomplete', 'off'); });

  var anker = blokken[blokken.length - 1].nextSibling;
  var gehusseld = schud(blokken);
  gehusseld.forEach(function (b) { ouder.removeChild(b); });
  gehusseld.forEach(function (b) { ouder.insertBefore(b, anker); });
  maakPaginering(gehusseld, ouder, anker, function (blok) { return blok.querySelector('button.vraag-knop'); });
});

/* ---------- KB-pagina's: zwevende knop "Controleer antwoorden" ----------
   Kijkt alleen de ingevulde antwoorden na (lege vragen blijven dicht). Per vraag: goed of niet goed, het juiste antwoord
   en de uitleg verschijnen onder de vraag. Het vergelijken is ruimhartig: hoofdletters, spaties, komma of punt,
   een ontbrekende eenheid en schrijfwijzen van machten van 10 maken niet uit. Lange tekstantwoorden worden niet
   automatisch beoordeeld: daar staat "Vergelijk zelf met het juiste antwoord". */
var SUPERS = { '\u2070': '0', '\u00b9': '1', '\u00b2': '2', '\u00b3': '3', '\u2074': '4', '\u2075': '5', '\u2076': '6', '\u2077': '7', '\u2078': '8', '\u2079': '9', '\u207b': '-', '\u207a': '+' };

function kbTekstVanAntwoord(box) {
  var kopie = box.cloneNode(true);
  Array.prototype.forEach.call(kopie.querySelectorAll('.uitleg, .uitslag'), function (e) { e.parentNode.removeChild(e); });
  Array.prototype.forEach.call(kopie.querySelectorAll('sup'), function (e) { e.textContent = '^' + e.textContent; });
  return (kopie.textContent || '').replace(/\s+/g, ' ').trim();
}

function kbNormaal(t) {
  t = String(t).toLowerCase();
  /* EN: komma = duizendtalscheiding ("1,000" = 1000); NL: komma is de decimaalteken en blijft zo */
  if (taalIsEN()) { t = t.replace(/(^|[^0-9.,])([0-9]{1,3}(?:,[0-9]{3})+)(?![0-9,])/g, function (m, v, g) { return v + g.replace(/,/g, ''); }); }
  t = t.replace(/[\u2070\u00b9\u00b2\u00b3\u2074-\u207b]/g, function (c) { return SUPERS[c] === undefined ? c : (/[0-9]/.test(SUPERS[c]) || SUPERS[c] === '-' || SUPERS[c] === '+' ? SUPERS[c] : c); });
  t = t.replace(/[\s\u00a0]+/g, '').replace(/[\u2212\u2013\u2014]/g, '-').replace(/,/g, '.').replace(/[\u00b7\u00d7*]/g, 'x');
  return t;
}

/* Getal + eenheid: "10.0g", "3.40x10-3mol", "5/6", "25%" */
function kbGetal(t) {
  var s = kbNormaal(t).replace(/[\^{}()]/g, '');
  var m = /^(-?\d+(?:\.\d+)?(?:\/\d+)?(?:x10-?\d+)?)(.*)$/.exec(s);
  return m ? { getal: m[1], eenheid: m[2].replace(/[^a-z0-9%\/\u00b0]/g, '') } : null;
}

function kbWaarde(g) {
  var m = /^(-?\d+(?:\.\d+)?)(?:\/(\d+))?(?:x10(-?\d+))?$/.exec(g);
  if (!m) { return NaN; }
  return parseFloat(m[1]) / (m[2] ? parseFloat(m[2]) : 1) * Math.pow(10, m[3] ? parseInt(m[3], 10) : 0);
}

/* Beoordeelt een antwoord tegen een antwoordbox.
   1. data-goed="39,5 g|40 g": elk van die opties is goed.
   2. Zonder data-goed: de hele tekst van de box, en bij een uitgewerkt rekenantwoord ("a x b = c g (d g in 2 significante
      cijfers)") ook het eindantwoord (na het laatste "=") en de waarden in haakjes. Een leerling die alleen het getal typt is dus goed;
      het eerste getal van de uitwerking (een tussenstap) niet. Dit gebeurt lokaal, voordat de AI eraan te pas komt. */
function kbBeoordeelBox(ingevuld, box) {
  var lijst = box.getAttribute('data-goed');
  if (lijst) {
    var eerste = null;
    var opties = lijst.split('|');
    for (var n = 0; n < opties.length; n++) {
      var r0 = kbBeoordeel(ingevuld, opties[n]);
      if (r0.oordeel === 'goed') { return r0; }
      if (!eerste) { eerste = r0; }
    }
    return eerste;
  }
  var verwacht = kbTekstVanAntwoord(box);
  var r = kbBeoordeel(ingevuld, verwacht);
  if (r.oordeel === 'goed') { return r; }
  var eind = kbEindantwoorden(verwacht);
  if (!eind.length) { return r; }
  var beste = null;
  for (var k = 0; k < eind.length; k++) {
    var x = kbVergelijkGetal(ingevuld, kbGetal(eind[k]));
    if (x.oordeel === 'goed') { return x; }
    if (x.oordeel === 'half' && !beste) { beste = x; }
  }
  if (beste) { return beste; }
  if (/^\s*(?:[A-Za-z\u0370-\u03ff][A-Za-z0-9_]{0,3}\s*=\s*)?[-\u2212]?\d/.test(ingevuld)) { return { oordeel: 'fout', hint: '', numeriek: true }; }
  return r;
}

/* TIJDELIJKE TWEAK (alleen EN-pilot): staat er een "=" in het antwoord ("8x2.5=20", "x = 20", "8 x 2,5 = 20 g"), dan telt alleen
   wat na het laatste "=" staat (getrimd). Het deel ervoor (de berekening) wordt dus niet beoordeeld; "20=8x2.5" wordt daarom
   als "8x2.5" gelezen en blijft fout bij een verwacht antwoord 20. Alleen in het lokale getallen-pad; het AI-pad krijgt de volledige tekst. */
function kbNaLaatsteIs(ingevuld) {
  var t = String(ingevuld), k = t.lastIndexOf('=');
  return k === -1 ? t : t.slice(k + 1).trim();
}

/* Vergelijkt wat de leerling typte met een verwacht getal v = kbGetal(...): komma of punt, eenheid mag ontbreken,
   schrijfwijze van machten van 10 maakt niet uit. Zelfde waarde maar andere afronding of eenheid = 'half'. */
function kbVergelijkGetal(ingevuld, v) {
  var i = kbGetal(kbNaLaatsteIs(ingevuld).replace(/^\s*[A-Za-z\u0370-\u03ff][A-Za-z0-9_]{0,3}\s*=\s*/, ''));
  if (i && i.getal === v.getal && (i.eenheid === '' || v.eenheid === '' || i.eenheid.replace(/x/g, '') === v.eenheid.replace(/x/g, ''))) { return { oordeel: 'goed', hint: '', numeriek: true }; }
  if (i && i.getal === v.getal) { return { oordeel: 'half', hint: T('kb.hint_eenheid'), numeriek: true }; }
  if (i && i.getal !== v.getal && Math.abs(kbWaarde(i.getal) - kbWaarde(v.getal)) < 1e-12 * Math.max(1, Math.abs(kbWaarde(v.getal))) && v.getal.indexOf('/') === -1) {
    return { oordeel: 'half', hint: T('kb.hint_afronding'), numeriek: true };
  }
  return { oordeel: 'fout', hint: '', numeriek: true };
}

/* Eindantwoorden uit een uitgewerkt model: "39,5 g" uit "0,79 x 50 = 39,5 g (40 g in 2 significante cijfers)".
   Geeft de lijst getal-opties: de waarde na het laatste "=" (zonder haakjes) en elke waarde in haakjes die voor
   "in N significante cijfers" staat. Lege lijst = geen uitgewerkt rekenantwoord (dan geldt de hele tekst). */
function kbEindantwoorden(verwacht) {
  var t = String(verwacht);
  var uit = [];
  /* Lijstantwoorden als "K = 2, L = 8, M = 7" zijn geen uitgewerkt rekenantwoord */
  if (/\b[A-Za-z]\s*=\s*[0-9.,]+\s*[,;]\s*[A-Za-z]\s*=/.test(t)) { return uit; }
  function toevoegen(x) {
    x = String(x).replace(/[.;:,]+\s*$/, '').trim();
    var g = kbGetal(x);
    if (g && g.eenheid.length <= 14 && uit.indexOf(x) === -1) { uit.push(x); }
  }
  var haakjes = t.match(/\([^()]*\)/g) || [];
  haakjes.forEach(function (h) {
    var m = /^\(\s*([^()]*?)\s+in\s+[0-9]+\s+significant/i.exec(h);
    if (m) { toevoegen(m[1]); }
  });
  /* Haakjes met uitleg weg, maar eenheden als mol/(L·s) blijven staan */
  var kaal = t.replace(/\([^()]*\)/g, function (h) { return /^\(\s*[A-Za-z\u00b5\u03a9\u00b0]{1,3}\s*[\u00b7\/*\u00d7]\s*[A-Za-z\u00b5\u03a9\u00b0]{1,3}[0-9^]*\s*\)$/.test(h) ? h : ' '; }).replace(/\s+/g, ' ').trim();
  var p = kaal.lastIndexOf('=');
  if (p !== -1) {
    var eind = kaal.slice(p + 1).trim();
    var d = eind.split(new RegExp(',?\\s+(?:' + T('kb.dus_regex') + ')\\s+', 'i'));   /* "10,8, dus 11 MJ": beide mogen */
    d.reverse().forEach(toevoegen);
    /* Antwoord vooraan, uitwerking erachter: "48 s: 50 -> 30 ..., dus 12 s x 4 = 48 s" */
    if (uit.length) {
      var v = /^([^:=\s][^:=]{0,24}?):\s+(?=[A-Za-z\u0394\u03a3(])/.exec(kaal);
      if (v && kbGetal(v[1])) { toevoegen(v[1]); }
    }
  }
  return uit;
}

/* Geeft { oordeel: 'goed' | 'half' | 'fout' | 'zelf', hint: '', numeriek: true/false }
   half = de waarde klopt, maar de eenheid of de afronding niet (lokaal bepaald, zonder AI) */
/* Is dit een getal met hooguit een korte eenheid ("3,40 mol", "5 g/cm3") en niet een zin als "10 N naar rechts"? */
function kbIsGetalMetEenheid(verwacht, v) {
  if (!v || v.eenheid.length > 7 || /[()]/.test(verwacht)) { return false; }
  var rest = String(verwacht).replace(/[x\u00d7\u00b7*]\s*10\s*\^?\s*[-\u2212]?\s*[0-9\u2070-\u2079\u207b]+/i, ' ').replace(/^[\s\-\u2212]*[0-9]+(?:[.,][0-9]+)?(?:\s*\/\s*[0-9]+)?/, ' ');
  return rest.trim().split(/\s+/).filter(function (t) { return t; }).length <= 2;
}
function kbBeoordeel(ingevuld, verwacht) {
  var v = kbGetal(verwacht);
  if (kbIsGetalMetEenheid(verwacht, v)) { return kbVergelijkGetal(ingevuld, v); }
  /* letters, cijfers, Griekse letters en rekentekens tellen mee; spaties en leestekens niet */
  var tekst = function (x) { return kbNormaal(x).replace(/[^a-z0-9\u00e0-\u00ff\u0370-\u03ff=+\-\u2212*:\/\u00d7\u00b7<>%]/g, ''); };
  var ruw = verwacht.replace(/\^/g, '');
  var delen = ruw.indexOf('=') === -1 ? ruw.split(new RegExp('\\s+(?:' + T('kb.of_regex') + ')\\s+|\\/')).filter(function (d) { return tekst(d).length >= 4; }) : [];
  var opties = [ruw, ruw.replace(/\([^)]*\)/g, '')].concat(delen);
  opties = opties.map(tekst).filter(function (o) { return o.length > 0; });
  if (!opties.length) { return { oordeel: 'zelf', hint: '', numeriek: false }; }
  if (opties.indexOf(tekst(ingevuld)) !== -1) { return { oordeel: 'goed', hint: '', numeriek: false }; }
  if (tekst(ruw).length > 30) { return { oordeel: 'zelf', hint: '', numeriek: false }; }
  return { oordeel: 'fout', hint: '', numeriek: false };
}

klaar(function () {
  var knoppen = Array.prototype.slice.call(document.querySelectorAll('button.vraag-knop'));
  var blokken = knoppen.map(function (k) { return k.parentNode; }).filter(function (b) {
    return b.querySelector('input[type=text]') && b.querySelector('.antwoord-box');
  });
  if (!blokken.length) { return; }
  var ouder = blokken[0].parentNode;
  var laatste = blokken.filter(function (b) { return b.parentNode === ouder; }).pop();
  var wrap = laatste.nextElementSibling && laatste.nextElementSibling.classList.contains('meer-vragen') ? laatste.nextElementSibling : laatste;
  var ref = wrap.nextSibling;

  var onder = document.createElement('div');
  onder.className = 'kb-controle w3-center';
  var origineel = document.createElement('button');
  origineel.type = 'button';
  origineel.id = 'kb-controleer';
  origineel.className = 'w3-button knop-blauw';
  origineel.textContent = T('kb.controleer');
  var uitslag = document.createElement('div');
  uitslag.id = 'kb-uitslag';
  uitslag.setAttribute('role', 'status');
  uitslag.setAttribute('aria-live', 'polite');
  onder.appendChild(origineel); onder.appendChild(uitslag);
  ouder.insertBefore(onder, ref);

  function wis(blok) {
    var inp = blok.querySelector('input[type=text]');
    inp.classList.remove('kb-goed', 'kb-fout');
    inp.removeAttribute('aria-invalid');
    var oud = blok.querySelector('.kb-oordeel');
    if (oud) { oud.parentNode.removeChild(oud); }
  }
  function sluit(blok) {
    var box = blok.querySelector('.antwoord-box');
    box.className = box.className.replace(' w3-show', '');
    var k = blok.querySelector('button.vraag-knop');
    if (k) { k.setAttribute('aria-expanded', 'false'); }
  }
  blokken.forEach(function (blok) {
    /* Wijzig je je antwoord, dan verdwijnt de uitslag bij die vraag en gaat het juiste antwoord weer dicht */
    blok.querySelector('input[type=text]').addEventListener('input', function () { wis(blok); sluit(blok); });
  });

  var TITELS = { goed: T('res.goed'), half: T('res.half'), fout: T('res.fout'), zelf: T('res.zelf'), bezig: T('res.bezig') };
  var KLASSEN = { goed: 'uitslag-goed', half: 'uitslag-half', fout: 'uitslag-fout', zelf: 'uitslag-zelf', bezig: 'uitslag-zelf' };
  function toonOordeel(blok, oordeel, extra, openAntwoord) {
    var inp = blok.querySelector('input[type=text]');
    var box = blok.querySelector('.antwoord-box');
    wis(blok);
    var el = document.createElement('div');
    el.className = 'kb-oordeel uitslag ' + KLASSEN[oordeel];
    var kop = document.createElement('span');
    kop.textContent = TITELS[oordeel];
    el.appendChild(kop);
    if (extra) {
      var tip = document.createElement('span');
      tip.className = 'kb-tip';
      tip.textContent = ' ' + extra;
      el.appendChild(tip);
    }
    inp.classList.remove('kb-half');
    if (oordeel === 'goed' || oordeel === 'half' || oordeel === 'fout') {
      inp.classList.add(oordeel === 'goed' ? 'kb-goed' : (oordeel === 'half' ? 'kb-half' : 'kb-fout'));
      if (oordeel === 'fout') { inp.setAttribute('aria-invalid', 'true'); }
    }
    inp.parentNode.insertBefore(el, box);
    var k = blok.querySelector('button.vraag-knop');
    if (openAntwoord) {
      if (box.className.indexOf('w3-show') === -1) { box.className += ' w3-show'; }
      if (k) { k.setAttribute('aria-expanded', 'true'); }
    } else {
      sluit(blok);
    }
  }

  var bezigMetAI = false;
  origineel.addEventListener('click', function () {
    if (bezigMetAI) { return; }
    var lijst = [];   /* alle ingevulde vragen */
    var vragenAI = []; /* de vragen die de AI mag nakijken (alleen als ai-nakijken.js op de pagina staat) */
    var ai = window.kbAI && typeof window.kbAI.nakijken === 'function' ? window.kbAI : null;
    blokken.forEach(function (blok) {
      if (blok.hidden) { return; }
      var inp = blok.querySelector('input[type=text]');
      var box = blok.querySelector('.antwoord-box');
      var tekst = inp.value.replace(/\s+/g, ' ').trim();
      wis(blok);
      if (!tekst) { return; }
      var verwacht = kbTekstVanAntwoord(box);
      var r = kbBeoordeelBox(tekst, box);
      var it = { blok: blok, tekst: tekst, verwacht: verwacht, r: r, oordeel: r.oordeel, extra: r.hint };
      lijst.push(it);
      if (ai && r.oordeel !== 'goed' && ai.komtInAanmerking({ local: r.oordeel, numeriek: r.numeriek, verwacht: verwacht, ingevuld: tekst })) {
        var eerder = blok._kbAI && blok._kbAI.tekst === tekst ? blok._kbAI : null;
        if (eerder) {
          it.oordeel = eerder.verdict; it.extra = eerder.tip; it.klaar = true;
        } else {
          it.ai = true; vragenAI.push(it);
        }
      }
    });
    if (!lijst.length) {
      uitslag.innerHTML = '<p class="inline-melding">' + T('kb.vul_in') + '</p>';
      return;
    }
    function tonenAntwoord(it) {
      if (it.ai || it.klaar) { return it.oordeel === 'goed' || (it.blok._kbPoging || 0) >= 2 || it.oordeel === 'zelf'; }
      return true;
    }
    function weergeven() {
      lijst.forEach(function (it) {
        var extra = it.extra;
        if ((it.ai || it.klaar) && (it.oordeel === 'half' || it.oordeel === 'fout') && !tonenAntwoord(it)) {
          extra = (extra ? extra + ' ' : '') + T('kb.pas_aan');
        }
        toonOordeel(it.blok, it.oordeel, extra, tonenAntwoord(it));
      });
      var n = { goed: 0, half: 0, fout: 0, zelf: 0 };
      lijst.forEach(function (it) { n[it.oordeel]++; });
      var rest = 0;
      blokken.forEach(function (b) { if (!b.hidden && !b.querySelector('input[type=text]').value.trim()) { rest++; } });
      uitslag.textContent = T('kb.uitslag', { goed: n.goed, n: lijst.length }) +
        (n.half ? T('kb.uitslag_half', { n: n.half }) : '') + (n.zelf ? T('kb.uitslag_zelf', { n: n.zelf }) : '') +
        (rest ? T('kb.uitslag_rest', { n: rest }) : '');
    }
    /* Eerst de lokale uitslag: goed/niet goed meteen, de AI-vragen krijgen "Wordt nagekeken" */
    lijst.forEach(function (it) {
      if (it.ai) { toonOordeel(it.blok, 'bezig', '', false); } else if (!it.klaar) { toonOordeel(it.blok, it.oordeel, it.extra, true); } else { toonOordeel(it.blok, it.oordeel, it.extra, tonenAntwoord(it)); }
    });
    if (!vragenAI.length) { weergeven(); return; }

    bezigMetAI = true;
    var oudeTekst = origineel.textContent;
    origineel.disabled = true; zweef.disabled = true;
    origineel.textContent = T('kb.bezig'); zweef.textContent = T('kb.bezig');
    uitslag.textContent = T('kb.even_geduld');
    var verzoek = vragenAI.map(function (it, n) {
      it.id = 'v' + n;
      return { id: it.id, question: it.blok.querySelector('button.vraag-knop').textContent.replace(/\s+/g, ' ').trim(),
               modelAnswer: it.verwacht, studentAnswer: it.tekst, attempt: Math.min((it.blok._kbPoging || 0) + 1, 2) };
    });
    var fout = false;
    var belofte;
    try { belofte = ai.nakijken(verzoek); } catch (e) { belofte = Promise.reject(e); }
    Promise.resolve(belofte).then(function (res) {
      vragenAI.forEach(function (it) {
        var x = res && res[it.id];
        if (x && ['goed', 'half', 'fout'].indexOf(x.verdict) !== -1) {
          it.oordeel = x.verdict; it.extra = typeof x.tip === 'string' ? x.tip.slice(0, 240) : '';
          it.blok._kbPoging = verzoek[vragenAI.indexOf(it)].attempt;
          it.blok._kbAI = { tekst: it.tekst, verdict: x.verdict, tip: it.extra };
        } else {
          it.oordeel = 'zelf'; it.extra = T('kb.ai_fout'); it.ai = true; fout = true;
        }
      });
    }, function () {
      vragenAI.forEach(function (it) { it.oordeel = 'zelf'; it.extra = T('kb.ai_fout'); });
    }).then(function () {
      bezigMetAI = false;
      origineel.disabled = false; zweef.disabled = false;
      origineel.textContent = oudeTekst; zweef.textContent = oudeTekst;
      weergeven();
    });
  });

  var zweef = document.createElement('button');
  zweef.type = 'button';
  zweef.id = 'zweefknop';
  zweef.className = 'zweefknop';
  zweef.textContent = T('kb.controleer');
  zweef.setAttribute('aria-label', T('kb.controleer_aria'));
  zweef.addEventListener('click', function () { origineel.click(); });
  document.body.appendChild(zweef);
  document.body.classList.add('heeft-zweefknop', 'zweef-hoog');
  /* Bedekt de zwevende knop het invoerveld waarin je typt (toetsenbord op een smal scherm)? Dan gaat de knop even weg. */
  function knopBedektInvoer() {
    var a = document.activeElement;
    var tekstveld = a && a.matches && a.matches('input[type=text]');
    var weg = false;
    if (tekstveld && !zweef.hidden) {
      document.body.classList.remove('zweef-typen');
      var k = zweef.getBoundingClientRect(), r = a.getBoundingClientRect();
      weg = k.width > 0 && !(k.right < r.left || k.left > r.right || k.bottom < r.top || k.top > r.bottom);
    }
    document.body.classList.toggle('zweef-typen', weg);
  }
  document.addEventListener('focusin', function () { setTimeout(knopBedektInvoer, 350); });
  document.addEventListener('focusout', function () { document.body.classList.remove('zweef-typen'); });
  if (window.visualViewport) { window.visualViewport.addEventListener('resize', knopBedektInvoer); }
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (items) { zweef.hidden = items[0].isIntersecting; }).observe(origineel);
  }
});

/* ---------- Meerkeuzepagina's (MP): willekeurige volgorde, pagina's van 15, nakijken ----------
   De pagina levert alleen de vragen: var myQuestions = [{question, answers:{a:..,b:..}, correctAnswer:'a', fixed:true?}].
   fixed:true = de volgorde van de antwoorden blijft zoals in de lijst (bijv. kleuren). */
klaar(function () {
  var quiz = document.getElementById('quiz');
  var uitslag = document.getElementById('results');
  var knopNakijken = document.getElementById('submit');
  if (!quiz || !uitslag || !knopNakijken || typeof myQuestions === 'undefined') { return; }

  var letters = 'abcdefgh';
  var vragen = schud(myQuestions.map(function (q, i) { return { q: q, nr: i }; })).map(function (v) {
    var sleutels = Object.keys(v.q.answers);
    var opties = sleutels.map(function (s) { return { tekst: v.q.answers[s], goed: s === v.q.correctAnswer }; });
    if (!v.q.fixed) { opties = schud(opties); }
    return { q: v.q, nr: v.nr, opties: opties };
  });

  var html = vragen.map(function (v) {
    var antw = v.opties.map(function (o, k) {
      return '<label><input type="radio" name="question' + v.nr + '" value="' + letters[k] + '">' + letters[k] + ': ' + o.tekst + '</label>';
    }).join('');
    return '<div class="vraag-blok"><div class="question" tabindex="-1">' + v.q.question + '</div><div class="answers">' + antw + '</div></div>';
  });
  quiz.innerHTML = html.join('');
  var blokken = Array.prototype.slice.call(quiz.querySelectorAll('.vraag-blok'));

  var pag = maakPaginering(blokken, knopNakijken.parentNode, knopNakijken, function (blok) { return blok.querySelector('.question'); });

  knopNakijken.onclick = function () {
    var aantal = pag.getoond();
    var goed = 0;
    for (var i = 0; i < aantal; i++) {
      var antwoorden = blokken[i].querySelector('.answers');
      var gekozen = antwoorden.querySelector('input:checked');
      var juist = gekozen && vragen[i].opties[letters.indexOf(gekozen.value)].goed;
      /* Alleen het gekozen antwoord krijgt een kleur: goed = groen en vet, fout = rood en rustig.
         Het juiste antwoord wordt bij een fout niet verklapt, zodat een tweede ronde mogelijk blijft. */
      Array.prototype.forEach.call(antwoorden.querySelectorAll('label'), function (l) {
        l.classList.remove('optie-goed', 'optie-fout');
      });
      if (gekozen) { gekozen.parentNode.classList.add(juist ? 'optie-goed' : 'optie-fout'); }
      if (juist) { goed++; }
      markeer(antwoorden, !!juist);
    }
    uitslag.innerHTML = T('mp.uitslag', { goed: goed, n: aantal });
  };
});

/* ---------- Zwevende knop "Controleer nu" voor de meerkeuzepagina's (MP) ----------
   Klikt op de gewone knop, dus het nakijken blijft precies hetzelfde en de pagina blijft op dezelfde plek staan.
   Zodra de gewone knop zelf in beeld is, verdwijnt de zwevende knop. */
klaar(function () {
  var origineel = document.getElementById('submit');
  var uitslag = document.getElementById('results');
  if (!origineel || !uitslag || !document.getElementById('quiz')) { return; }

  var zweef = document.createElement('button');
  zweef.type = 'button';
  zweef.id = 'zweefknop';
  zweef.className = 'zweefknop';
  zweef.textContent = T('mp.controleer');
  zweef.setAttribute('aria-label', T('mp.controleer_aria'));
  zweef.addEventListener('click', function () { origineel.click(); });
  document.body.appendChild(zweef);
  document.body.classList.add('heeft-zweefknop', 'zweef-hoog');

  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (items) {
      zweef.hidden = items[0].isIntersecting;
    }).observe(origineel);
  }
});

/* ---------- Beginpagina (index.html, met jQuery) ---------- */
if (window.jQuery) {
  jQuery(function ($) {
    /* Soepel scrollen naar een onderdeel via het menu en de knop "Naar Top" */
    $(".navbar a, footer a[href='#myPage']").on('click', function (event) {
      if (this.hash !== "") {
        event.preventDefault();
        var hash = this.hash;
        $('html, body').animate({ scrollTop: $(hash).offset().top }, 900, function () {
          window.location.hash = hash;
        });
      }
    });
    /* Blokjes verschijnen tijdens het scrollen (klasse .slide) */
    $(window).scroll(function () {
      $(".slideanim").each(function () {
        var pos = $(this).offset().top;
        var winTop = $(window).scrollTop();
        if (pos < winTop + 600) { $(this).addClass("slide"); }
      });
    });
  });
}

/* KB-vragen: elke vraag met eigen invoerveld, antwoord en terugkoppeling in een eigen kader (zie .kb-item in 123school.css) */
klaar(function () {
  var knoppen = document.querySelectorAll('button.vraag-knop');
  for (var i = 0; i < knoppen.length; i++) {
    var ouder = knoppen[i].parentNode;
    if (ouder && ouder !== document.body && ouder.tagName === 'DIV') { ouder.classList.add('kb-item'); }
  }
  /* kort eindantwoord in het antwoordvak: markeren, zodat het in 123school.css opvalt (voorvoegsel 'Antwoord:' via CSS, tekst blijft ongewijzigd) */
  var eerste = document.querySelectorAll('.antwoord-box > p:first-child');
  for (var j = 0; j < eerste.length; j++) {
    if (!eerste[j].classList.contains('uitleg') && eerste[j].textContent.replace(/\s+/g, ' ').trim().length <= 60) { eerste[j].classList.add('eindantwoord'); }
  }
});
