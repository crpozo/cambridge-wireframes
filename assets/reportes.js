/* Arma tu reporte (prototipo): "Ver resultado" lee la pregunta, el período, la sede, la vista y las columnas elegidas
   y redibuja el resultado (texto, gráfico y tabla) con datos de ejemplo. Sin dependencias. */
(function () {
  if (window.__reportes) return;
  window.__reportes = true;
  var body = document.querySelector('[data-rep-body]'); if (!body) return;
  var CH = ['#2F55B5', '#D62839', '#2E8BC9', '#C9900A', '#7A5BC0'];
  var SEDES = ['Quito', 'Valle', 'Ambato'], PESO = { Quito: 1, Valle: .55, Ambato: .35 };
  var ASES = { Quito: ['Carla M.', 'Andrea S.', 'Luis P.'], Valle: ['Diego R.'], Ambato: ['Sofía L.'] };
  var PROGS = ['Adults', 'Teens', 'Kids', 'Business'];
  var NOMBRES = ['María Andrade', 'Pedro Mora', 'Camila Sánchez', 'Martín Ortega', 'Gabriela Núñez', 'Luis Torres', 'Sofía Herrera', 'Mateo Salazar', 'Renata Salazar', 'Daniel Pozo'];
  var MES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct'];
  function q(s, r) { return (r || document).querySelector(s); }
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
  function sel(label) {
    var rows = document.querySelectorAll('.pill-row');
    for (var i = 0; i < rows.length; i++) if (rows[i].firstChild.textContent.trim() === label) return [].slice.call(rows[i].querySelectorAll('.pill.on')).map(function (p) { return p.textContent.trim(); });
    return [];
  }
  function hash(s) { var h = 7; for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) % 9973; return h; }
  function rnd(seed, i) { var x = Math.sin(seed * 12.9898 + i * 78.233) * 43758.5453; return x - Math.floor(x); }
  function fmt(v, dinero) { return dinero ? '$' + Math.round(v).toLocaleString('en-US') : String(Math.round(v)); }

  function periodos(p) {
    if (p === 'Este mes' || p === 'Mes pasado') return { lab: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'], f: p === 'Este mes' ? 1 : 1.1, txt: p === 'Este mes' ? 'este mes' : 'el mes pasado' };
    if (p === 'Últimos 3 meses') return { lab: ['Ago', 'Sep', 'Oct'], f: 3, txt: 'en los últimos 3 meses' };
    if (p === 'Este año') return { lab: MES, f: 10, txt: 'este año' };
    return { lab: ['T1', 'T2', 'T3'], f: 9, txt: 'en las fechas elegidas' };
  }
  function vbars(grupos, series) {
    var mx = 1; grupos.forEach(function (g) { g[1].forEach(function (v) { if (v > mx) mx = v; }); });
    var h = '<div class="chart"><div class="vbars">' + grupos.map(function (g) {
      return '<div class="vgroup"><div class="vbars-stack" style="height:160px">' + g[1].map(function (v, i) { return '<div class="vbar" title="' + esc(series[i]) + ': ' + v + '" style="height:' + Math.max(Math.round(v / mx * 160), 4) + 'px;background:' + CH[i % 5] + '"><span>' + v + '</span></div>'; }).join('') + '</div><span class="vlabel">' + esc(g[0]) + '</span></div>';
    }).join('') + '</div>' + (series.length > 1 ? '<div class="legend">' + series.map(function (n, i) { return '<span class="leg"><i style="background:' + CH[i % 5] + '"></i>' + esc(n) + '</span>'; }).join('') + '</div>' : '') + '</div>';
    return h;
  }
  function hbars(items) {
    var mx = Math.max.apply(null, items.map(function (i) { return i[1]; })) || 1;
    return '<div class="hbars">' + items.map(function (i) { return '<div class="hbar"><span>' + esc(i[0]) + '</span><div class="hbar-track"><div class="hbar-fill" style="width:' + Math.round(i[1] / mx * 100) + '%"></div></div><b>' + i[2] + '</b></div>'; }).join('') + '</div>';
  }
  function tabla(cols, rows) {
    var num = function (i) { return i > 0 && rows.every(function (r) { return /^[\$\d,.%]+$/.test(String(r[i])); }); };
    var tpl = cols.map(function (c, i) { return i === 0 ? 'minmax(160px,2fr)' : 'minmax(min-content,1fr)'; }).join(' ');
    var h = '<div class="tbl-wrap"><div class="wf-table tbl" data-cols=\'' + JSON.stringify(cols).replace(/'/g, '&#39;') + '\' style="grid-template-columns:' + tpl + '">';
    h += cols.map(function (c, i) { return '<div class="th' + (num(i) ? ' th-num' : '') + '" role="columnheader">' + esc(c) + '</div>'; }).join('');
    rows.forEach(function (r) { h += '<div class="wf-row">' + r.map(function (c, i) { return '<div class="td' + (i === 0 ? ' td-wide' : '') + (num(i) ? ' is-num' : '') + '" data-label="' + esc(cols[i]) + '">' + esc(c) + '</div>'; }).join('') + '</div>'; });
    return h + '</div></div>';
  }

  function armar() {
    var pregunta = (q('.pick.on b') || {}).textContent || 'Estudiantes nuevos';
    var per = sel('Período')[0] || 'Este mes', sedeSel = sel('Sede')[0] || 'Todas', vista = sel('Vista')[0] || 'Por mes', extra = sel('Agregar');
    var dinero = /factur|cobr|dinero|deben|descuento|caja|ventas/i.test(pregunta);
    var unidad = dinero ? 'USD' : (/curso|aula/i.test(pregunta) ? 'cursos' : 'estudiantes');
    var P = periodos(per), seed = hash(pregunta), sedes = sedeSel === 'Todas' ? SEDES : [sedeSel];
    var base = dinero ? 9000 : 18;
    function valor(sede, i) { return base * PESO[sede] * (0.8 + rnd(seed, i + sede.length) * .5); }
    var grupos = P.lab.map(function (l, i) { return [l, sedes.map(function (s) { return Math.round(valor(s, i) * (per === 'Este año' ? 1 : (P.lab.length === 4 ? .3 : 1))); })]; });
    var totalSede = sedes.map(function (s, j) { return grupos.reduce(function (a, g) { return a + g[1][j]; }, 0); });
    var total = totalSede.reduce(function (a, b) { return a + b; }, 0);
    var delta = Math.round((rnd(seed + hash(per + sedeSel), 99) * 18 - 4));
    var lugar = sedeSel === 'Todas' ? 'todas las sedes' : sedeSel;
    var texto = '<p class="plain"><b>' + fmt(total, dinero) + (dinero ? '' : ' ' + unidad) + '</b> ' + P.txt + ' en ' + lugar + '. Es <b>' + Math.abs(delta) + '% ' + (delta >= 0 ? 'más' : 'menos') + '</b> que el período anterior.';
    var grafico, cols, filas;
    var progs = PROGS.map(function (p, i) { return [p, Math.round(total * (.5 / (i + 1)) * (.9 + rnd(seed, 40 + i) * .2))]; });
    if (vista === 'Por mes') {
      grafico = vbars(grupos, sedes);
      cols = ['Período'].concat(sedes, sedes.length > 1 ? ['Total'] : []);
      filas = grupos.map(function (g) { var t = g[1].reduce(function (a, b) { return a + b; }, 0); return [g[0]].concat(g[1].map(function (v) { return fmt(v, dinero); }), sedes.length > 1 ? [fmt(t, dinero)] : []); });
    } else if (vista === 'Por sede') {
      if (sedes.length > 1) { grafico = hbars(sedes.map(function (s, i) { return [s, totalSede[i], fmt(totalSede[i], dinero)]; })); cols = ['Sede', 'Total', 'Participación']; filas = sedes.map(function (s, i) { return [s, fmt(totalSede[i], dinero), Math.round(totalSede[i] / total * 100) + '%']; }); }
      else { grafico = hbars(progs.map(function (p) { return [p[0], p[1], fmt(p[1], dinero)]; })); cols = ['Programa', 'Total']; filas = progs.map(function (p) { return [p[0], fmt(p[1], dinero)]; }); texto += ' Con una sola sede el detalle se abre por programa.'; }
    } else if (vista === 'Por asesor') {
      var lista = []; sedes.forEach(function (s, j) { ASES[s].forEach(function (a, k) { lista.push([a, s, totalSede[j] * (k === 0 ? .5 : .3) / (ASES[s].length > 1 ? 1 : 1.6) * (0.9 + rnd(seed, k) * .2)]); }); });
      lista.sort(function (a, b) { return b[2] - a[2]; });
      grafico = hbars(lista.map(function (a) { return [a[0], a[2], fmt(a[2], dinero)]; })); cols = ['Asesor', 'Sede', 'Total']; filas = lista.map(function (a) { return [a[0], a[1], fmt(a[2], dinero)]; });
      texto += ' ' + lista[0][0] + ' lidera.';
    } else {
      var n = Math.min(8, Math.max(4, Math.round(total / (dinero ? 2000 : 6))));
      cols = ['Estudiante', 'Sede'].concat(extra);
      filas = NOMBRES.slice(0, n).map(function (nm, i) {
        var s = sedes[i % sedes.length];
        return [nm, s].concat(extra.map(function (e) { return e === 'Teléfono de contacto' ? '099 000 0' + (100 + i * 7) : e === 'Asesor' ? ASES[s][0] : e === 'Programa y nivel' ? PROGS[i % 4] + ' · ' + ['A1', 'A2', 'B1', 'B2'][i % 4] : '$' + (i % 3 === 0 ? 0 : 120 + i * 35); }));
      });
      grafico = hbars(progs.map(function (p) { return [p[0], p[1], fmt(p[1], dinero)]; }));
      texto += ' Abajo está la lista, con las columnas que elegiste.';
    }
    extra = extra.filter(function (e) { return cols.indexOf(e) < 0; });
    if (vista !== 'Lista de estudiantes' && extra.length) {
      var adds = { 'Teléfono de contacto': ['099 000 0100'], 'Asesor': null, 'Programa y nivel': null, 'Saldo': null };
      cols = cols.concat(extra); filas = filas.map(function (r, i) { return r.concat(extra.map(function (e) { return e === 'Asesor' ? 'Carla M.' : e === 'Programa y nivel' ? 'Adults · B1' : e === 'Saldo' ? '$' + (80 + i * 40) : '099 000 0' + (100 + i * 7); })); });
    }
    texto += '</p>';
    var tit = 'Resultado · ' + pregunta.replace(/^¿|\?$/g, '') + ' · ' + per.toLowerCase() + ' · ' + lugar + ' · ' + vista.toLowerCase();
    var card = body.closest('.card'); var h2 = card && card.querySelector('h2'); if (h2) h2.textContent = tit;
    body.innerHTML = texto + '<div class="grid grid-2"><div class="g-cell">' + grafico + '</div><div class="g-cell">' + tabla(cols, filas) + '</div></div>';
    body.classList.add('rep-flash'); setTimeout(function () { body.classList.remove('rep-flash'); }, 900);
    if (card) card.scrollIntoView({ behavior: 'smooth', block: 'start' });
    var t = document.getElementById('wf-toast'); if (t) { t.textContent = 'Reporte armado con tus filtros'; t.style.display = 'block'; setTimeout(function () { t.style.display = 'none'; }, 2200); }
  }
  document.addEventListener('click', function (e) { if (e.target.closest && e.target.closest('[data-rep-run]')) armar(); });
})();
