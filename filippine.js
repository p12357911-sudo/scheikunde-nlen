/* ==========================================================================
   123 school - filippine (woordpuzzel) voor alle puzzelpagina's
   Een pagina levert alleen de gegevens, als JSON in:
     <script type="application/json" id="filippine-data">
       { "titel": "...", "sleutelwoord": "ATOOMBINDING",
         "rijen": [ { "omschrijving": "...", "antwoord": "ALKAAN", "sleutelpositie": 1 }, ... ] }
     </script>
   en een leeg vak: <div id="filippine"></div>
   sleutelpositie = de letter van het antwoord (1 = eerste letter) die in het sleutelwoord komt.
   Spaties en streepjes in een antwoord tellen niet mee als vakje.
   Het script maakt de figuur van een filippine: per woord een rij met een vakje per letter (met in elk vakje
   een klein cijfer: gelijk cijfer = gelijke letter), de rijen zo opgeschoven dat de gele sleutelvakjes onder
   elkaar staan. Op een breed scherm is dat het klassieke raster, op een smal scherm (telefoon) een kaartje per rij.
   Onder de figuur staat een tabel 'Oplossing' waarin de leerling zelf de letters van de gele vakjes invult.
   De zwevende knop "Controleer antwoorden" kijkt de volledig ingevulde rijen en de ingevulde oplossingsvakjes na.
   Stijl: filippine.css (eigen bestand, met versienummer in de link).
   ========================================================================== */
(function () {
  'use strict';

  function schoon(t) { return String(t).toUpperCase().replace(/[^A-Z\u00C0-\u00DE]/g, ''); }

  function el(naam, klasse, tekst) {
    var e = document.createElement(naam);
    if (klasse) { e.className = klasse; }
    if (tekst !== undefined) { e.textContent = tekst; }
    return e;
  }

  function T(k, v) { return (window.i18n && window.i18n.t) ? window.i18n.t(k, v) : k; }

  function start() {
    var wortel = document.getElementById('filippine');
    var gegevensTag = document.getElementById('filippine-data');
    if (!wortel || !gegevensTag) { return; }
    wortel.classList.add('fil-wortel');
    var data;
    try { data = JSON.parse(gegevensTag.textContent); } catch (fout) { console.error('filippine: gegevens onleesbaar', fout); return; }

    var rijen = data.rijen.map(function (r, i) {
      var woord = schoon(r.antwoord);
      return { nr: i + 1, omschrijving: r.omschrijving, antwoord: woord, weergave: r.antwoord, pos: r.sleutelpositie, vakjes: [], kaart: null, melding: null };
    });
    var sleutel = rijen.map(function (r) { return r.antwoord.charAt(r.pos - 1); }).join('');
    if (data.sleutelwoord && schoon(data.sleutelwoord) !== sleutel) {
      console.warn('filippine: sleutelwoord klopt niet met de sleutelletters', data.sleutelwoord, sleutel);
    }
    var maxVoor = Math.max.apply(null, rijen.map(function (r) { return r.pos - 1; }));

    /* ----- cijfercode: elke letter krijgt een vast cijfer (zelfde letter = zelfde cijfer) ----- */
    var letters = [];
    rijen.forEach(function (r) { r.antwoord.split('').forEach(function (c) { if (letters.indexOf(c) === -1) { letters.push(c); } }); });
    letters.sort();
    var zaad = 0, sleutelTekst = String(data.titel || '') + sleutel;
    for (var z = 0; z < sleutelTekst.length; z++) { zaad = (zaad * 31 + sleutelTekst.charCodeAt(z)) >>> 0; }
    function toeval() { zaad = (zaad + 0x6D2B79F5) >>> 0; var t = zaad; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }
    var codes = letters.map(function (c, i) { return i + 1; });
    for (var q = codes.length - 1; q > 0; q--) { var w = Math.floor(toeval() * (q + 1)); var tmp = codes[q]; codes[q] = codes[w]; codes[w] = tmp; }
    var codeVan = {};
    letters.forEach(function (c, i) { codeVan[c] = codes[i]; });

    function maakVakje(label, sleutelvak, code) {
      var cel = el('span', 'fil-cel' + (sleutelvak ? ' fil-cel-sleutel' : ''));
      var inp = document.createElement('input');
      inp.type = 'text';
      inp.className = 'fil-vakje' + (sleutelvak ? ' fil-sleutel' : '');
      inp.setAttribute('autocomplete', 'off');
      inp.setAttribute('autocapitalize', 'characters');
      inp.setAttribute('autocorrect', 'off');
      inp.setAttribute('spellcheck', 'false');
      inp.setAttribute('enterkeyhint', 'next');
      inp.setAttribute('aria-label', label);
      cel.appendChild(inp);
      if (code) { var c = el('span', 'fil-code', String(code)); c.setAttribute('aria-hidden', 'true'); cel.appendChild(c); }
      return { cel: cel, inp: inp };
    }

    /* ----- omschrijvingen (op een breed scherm als lijst boven de figuur) ----- */
    var clues = el('div', 'fil-clues');
    clues.appendChild(el('h3', 'fil-kop', T('puz.omschrijvingen')));
    var cluesLijst = el('div', 'fil-clues-lijst');
    rijen.forEach(function (r) {
      var p = el('p', 'fil-clue');
      p.appendChild(el('span', 'fil-nr', String(r.nr)));
      p.appendChild(document.createTextNode(' ' + r.omschrijving));
      cluesLijst.appendChild(p);
    });
    clues.appendChild(cluesLijst);

    /* ----- figuur: rijen opbouwen ----- */
    var lijst = el('div', 'fil-figuur');
    lijst.setAttribute('role', 'group');
    lijst.setAttribute('aria-label', T('puz.figuur_aria', { n: rijen.length }));
    var maxNa = Math.max.apply(null, rijen.map(function (r) { return r.antwoord.length - r.pos; }));
    var kolommen = maxVoor + 1 + maxNa;
    wortel.style.setProperty('--kol', String(kolommen));
    wortel.style.setProperty('--versch-max', String(maxVoor));
    rijen.forEach(function (r) {
      var kaart = el('div', 'fil-rij');
      r.kaart = kaart;
      var kop = el('div', 'fil-omschrijving');
      kop.appendChild(el('span', 'fil-nr', r.nr + '.'));
      kop.appendChild(document.createTextNode(' ' + r.omschrijving + ' '));
      kop.appendChild(el('span', 'fil-lengte', T('puz.lengte', { n: r.antwoord.length })));
      kaart.appendChild(kop);
      var regel = el('div', 'fil-regel');
      kaart.style.setProperty('--versch', String(maxVoor - (r.pos - 1)));
      var nrvak = el('span', 'fil-nrvak', String(r.nr));
      nrvak.setAttribute('aria-hidden', 'true');
      regel.appendChild(nrvak);
      var vak = el('div', 'fil-vakjes');
      vak.setAttribute('role', 'group');
      vak.setAttribute('aria-label', T('puz.antwoord_aria', { nr: r.nr, n: r.antwoord.length }));
      for (var k = 0; k < r.antwoord.length; k++) {
        var v = maakVakje(T('puz.letter_aria', { nr: r.nr, k: k + 1, n: r.antwoord.length }) + (k === r.pos - 1 ? T('puz.sleutelletter') : ''), k === r.pos - 1, codeVan[r.antwoord.charAt(k)]);
        r.vakjes.push(v.inp);
        vak.appendChild(v.cel);
      }
      regel.appendChild(vak);
      kaart.appendChild(regel);
      r.melding = el('div', 'fil-melding');
      r.melding.setAttribute('role', 'status');
      kaart.appendChild(r.melding);
      lijst.appendChild(kaart);
    });

    /* ----- tabel Oplossing: de leerling vult zelf de letters van de gele vakjes in ----- */
    var opl = { nr: rijen.length + 1, vakjes: [], kaart: null, melding: null, isOpl: true };
    var oplKader = el('div', 'fil-oplossing');
    opl.kaart = oplKader;
    oplKader.appendChild(el('h3', 'fil-kop', T('puz.oplossing')));
    oplKader.appendChild(el('p', 'fil-opltekst', T('puz.opltekst')));
    var oplRij = el('div', 'fil-oplrij');
    oplRij.setAttribute('role', 'group');
    oplRij.setAttribute('aria-label', T('puz.opl_aria', { n: rijen.length }));
    rijen.forEach(function (r) {
      var kol = el('span', 'fil-oplkolom');
      var v = maakVakje(T('puz.opl_letter_aria', { nr: r.nr, n: rijen.length }), true, codeVan[r.antwoord.charAt(r.pos - 1)]);
      kol.appendChild(v.cel);
      var nr = el('span', 'fil-oplnr', String(r.nr));
      nr.setAttribute('aria-hidden', 'true');
      kol.appendChild(nr);
      opl.vakjes.push(v.inp);
      oplRij.appendChild(kol);
    });
    oplKader.appendChild(oplRij);
    opl.melding = el('p', 'fil-oplmelding');
    opl.melding.setAttribute('role', 'status');
    oplKader.appendChild(opl.melding);
    var groepen = rijen.concat([opl]);

    /* ----- knoppen ----- */
    var onder = el('div', 'kb-controle w3-center');
    var knop = el('button', 'w3-button knop-blauw', T('kb.controleer'));
    knop.type = 'button'; knop.id = 'fil-controleer';
    var uitslag = el('div'); uitslag.id = 'kb-uitslag'; uitslag.setAttribute('role', 'status'); uitslag.setAttribute('aria-live', 'polite');
    onder.appendChild(knop); onder.appendChild(uitslag);

    wortel.appendChild(clues);
    wortel.appendChild(lijst);
    wortel.appendChild(oplKader);
    wortel.appendChild(onder);

    /* raster (breed scherm) of kaartjes (smal scherm): het raster krijgt minstens 30 px per vakje */
    function kiesWeergave() {
      var breedte = wortel.clientWidth || wortel.parentNode.clientWidth;
      var past = (breedte - 44) / kolommen >= 34;
      wortel.classList.toggle('fil-raster', past);
      wortel.classList.toggle('fil-kaarten', !past);
    }
    kiesWeergave();
    window.addEventListener('resize', kiesWeergave);

    /* ----- hulpfuncties ----- */
    function tekstVan(r) { return r.vakjes.map(function (v) { return v.value; }).join(''); }
    function gevuld(r) { return r.vakjes.filter(function (v) { return v.value; }).length; }

    function wisOordeel(r) {
      r.kaart.classList.remove('fil-goed', 'fil-fout');
      r.vakjes.forEach(function (v) { v.removeAttribute('aria-invalid'); v.classList.remove('fil-vgoed', 'fil-vfout'); });
      r.melding.textContent = '';
      r.melding.className = r.isOpl ? 'fil-oplmelding' : 'fil-melding';
    }

    function zet(r, k, tekens) {
      /* zet een of meer letters vanaf vakje k; geeft het eerstvolgende vakje terug */
      var j = k;
      for (var t = 0; t < tekens.length && j < r.vakjes.length; t++, j++) { r.vakjes[j].value = tekens.charAt(t); r.vakjes[j].dataset.v = tekens.charAt(t); }
      return j;
    }

    function focusOp(r, k) {
      var idx = groepen.indexOf(r);
      if (k >= r.vakjes.length) {
        var volgende = groepen[idx + 1];
        if (volgende) { volgende.vakjes[0].focus(); } else { r.vakjes[r.vakjes.length - 1].blur(); }
        return;
      }
      if (k < 0) {
        var vorige = groepen[idx - 1];
        if (vorige) { vorige.vakjes[vorige.vakjes.length - 1].focus(); }
        return;
      }
      r.vakjes[k].focus();
    }

    /* pijl omhoog/omlaag: in het raster naar het vakje er direct boven of onder */
    function buurVakje(r, k, richting) {
      var buur = groepen[groepen.indexOf(r) + richting];
      if (!buur) { return null; }
      var j = k;
      if (wortel.classList.contains('fil-raster') && !r.isOpl && !buur.isOpl) { j = k - (r.pos - 1) + (buur.pos - 1); }
      else if (r.isOpl) { j = k; }
      else if (buur.isOpl) { j = 0; }
      j = Math.max(0, Math.min(j, buur.vakjes.length - 1));
      return buur.vakjes[j];
    }

    groepen.forEach(function (r) {
      r.vakjes.forEach(function (inp, k) {
        inp.addEventListener('focus', function () { try { inp.select(); } catch (e) { /* oudere browsers */ } });
        inp.addEventListener('click', function () { try { inp.select(); } catch (e) { /* idem */ } });
        inp.addEventListener('input', function () {
          wisOordeel(r);
          var tekens = schoon(inp.value);
          if (!tekens) { inp.value = ''; inp.dataset.v = ''; return; }
          /* in een vol vakje typen of plakken: het nieuwste teken telt; bij plakken van een woord vullen we door */
          if (tekens.length > 2) { inp.value = ''; inp.dataset.v = ''; var j = zet(r, k, tekens); focusOp(r, j); return; }
          var vorig = inp.dataset.v || '';
          var teken = tekens.length === 2 ? (tekens.charAt(0) === vorig ? tekens.charAt(1) : tekens.charAt(0)) : tekens;
          inp.value = teken; inp.dataset.v = teken;
          focusOp(r, k + 1);
        });
        inp.addEventListener('keydown', function (e) {
          if (e.key === 'Backspace' && !inp.value) { e.preventDefault(); if (k > 0) { r.vakjes[k - 1].value = ''; r.vakjes[k - 1].dataset.v = ''; wisOordeel(r); } focusOp(r, k - 1); }
          else if (e.key === 'ArrowLeft') { e.preventDefault(); focusOp(r, k - 1); }
          else if (e.key === 'ArrowRight') { e.preventDefault(); focusOp(r, k + 1); }
          else if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
            var buur = buurVakje(r, k, e.key === 'ArrowDown' ? 1 : -1);
            if (buur) { e.preventDefault(); buur.focus(); }
          }
          else if (e.key === 'Enter') { e.preventDefault(); var vol = groepen[groepen.indexOf(r) + 1]; if (vol) { vol.vakjes[0].focus(); } else { inp.blur(); } }
        });
      });
    });

    /* ----- nakijken ----- */
    knop.addEventListener('click', function () {
      var ingevuld = 0, goed = 0, onaf = 0, leeg = 0;
      rijen.forEach(function (r) {
        wisOordeel(r);
        var n = gevuld(r);
        if (n === 0) { leeg++; return; }
        if (n < r.vakjes.length) { onaf++; r.melding.textContent = T('puz.onaf'); return; }
        ingevuld++;
        var juist = tekstVan(r) === r.antwoord;
        if (juist) { goed++; }
        r.kaart.classList.add(juist ? 'fil-goed' : 'fil-fout');
        if (!juist) { r.vakjes.forEach(function (v) { v.setAttribute('aria-invalid', 'true'); }); }
        r.melding.textContent = juist ? T('puz.goed') : T('puz.fout');
        r.melding.className = 'fil-melding uitslag ' + (juist ? 'uitslag-goed' : 'uitslag-fout');
        if (!juist) {
          var toon = el('button', 'fil-toon', T('puz.toon'));
          toon.type = 'button';
          toon.addEventListener('click', function () {
            r.melding.textContent = T('puz.fout_antwoord', { a: r.weergave.toLowerCase() });
          });
          r.melding.appendChild(document.createTextNode(' '));
          r.melding.appendChild(toon);
        }
      });

      /* tabel Oplossing: elk ingevuld vakje wordt nagekeken */
      wisOordeel(opl);
      var oplVol = 0, oplGoed = 0;
      opl.vakjes.forEach(function (v, i) {
        if (!v.value) { return; }
        oplVol++;
        var juist = v.value === sleutel.charAt(i);
        if (juist) { oplGoed++; }
        v.classList.add(juist ? 'fil-vgoed' : 'fil-vfout');
        if (!juist) { v.setAttribute('aria-invalid', 'true'); }
      });
      if (oplVol) {
        if (oplGoed === rijen.length) {
          opl.melding.textContent = T('puz.sleutel_goed', { a: sleutel.toLowerCase() });
          opl.melding.className = 'fil-oplmelding uitslag uitslag-goed';
        } else {
          opl.melding.textContent = (oplGoed === oplVol ? '\u2713 ' : '\u2717 ') + T('puz.opl_deel', { g: oplGoed, v: oplVol });
          opl.melding.className = 'fil-oplmelding uitslag ' + (oplGoed === oplVol ? 'uitslag-goed' : 'uitslag-fout');
        }
      }

      if (!ingevuld && !oplVol) {
        uitslag.innerHTML = '<p class="inline-melding">' + T('puz.eerst') + '</p>';
        return;
      }
      var tekst = ingevuld ? T('puz.n_goed', { g: goed, n: ingevuld }) : T('puz.nog_geen');
      var rest = onaf + leeg;
      if (ingevuld && rest) { tekst += T('puz.rest', { n: rest }); }
      uitslag.textContent = tekst;
    });

    /* ----- zwevende knop (zelfde als bij de andere oefenpagina's) ----- */
    var zweef = el('button', 'zweefknop', T('kb.controleer'));
    zweef.type = 'button'; zweef.id = 'zweefknop';
    zweef.setAttribute('aria-label', T('puz.zweef_aria'));
    zweef.addEventListener('click', function () { knop.click(); });
    document.body.appendChild(zweef);
    document.body.classList.add('heeft-zweefknop');
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (items) { zweef.hidden = items[0].isIntersecting; }).observe(knop);
    }
  }

  function wacht() { if (window.i18nKlaar && window.i18nKlaar.then) { window.i18nKlaar.then(start); } else { start(); } }
  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', wacht); } else { wacht(); }
})();
