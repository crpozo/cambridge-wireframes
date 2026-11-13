/* Plan estratégico del Tablero comercial (prototipo): todos los indicadores se recalculan con los filtros.
   Los datos de ejemplo vienen incrustados en la página (#plan-data): ventas, embudo de Kommo por etapa y deserción.
   Sin dependencias. */
(function () {
  if (window.__plan) return;
  window.__plan = true;
  var node = document.getElementById('plan-data');
  if (!node) return;
  var D = JSON.parse(node.textContent), S = D.S, L = D.L, DS = D.D, dim = D.dim;
  var CH = ['#2F55B5', '#D62839', '#2E8BC9', '#C9900A', '#7A5BC0', '#2E9E6B', '#8A93A6', '#B45309', '#16A34A'];
  var HOY = 20261023, MESES = ['Jun', 'Jul', 'Ago', 'Sep', 'Oct'], MES_N = [6, 7, 8, 9, 10];
  var DIAS = { 6: 30, 7: 31, 8: 31, 9: 30, 10: 23 };
  var ORIG_REF = dim.origs.indexOf('Referencia / Referido');
  var F = { periodo: 'Este mes', dia: '', ase: 'Todos', prog: 'Todos', prod: 'Todos', orig: 'Todos', walk: 'Todas' };
  var root = document.querySelector('[data-plan]');
  if (!root) return;

  function q(s, r) { return (r || document).querySelector(s); }
  function qa(s, r) { return [].slice.call((r || document).querySelectorAll(s)); }
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
  function money(n) { return '$' + Math.round(n).toLocaleString('en-US'); }
  function miles(n) { return (Math.round(n / 100) / 10).toFixed(1) + 'k'; }
  function pct(n, d) { return d > 0 ? (Math.round(n / d * 1000) / 10).toFixed(1).replace(/\.0$/, '') + '%' : '—'; }
  function num(n) { var r = Math.round(n * 10) / 10; return String(r); }
  function ymd(y, m, d) { return y * 10000 + m * 100 + d; }
  function fecha(r) { return (2025 + r[0]) * 10000 + r[1] * 100 + r[2]; }

  /* ---------- Contexto: rol, sedes, asesor, período ---------- */
  function rol() { var r = document.getElementById('rol'); return r ? r.value : 'ADM'; }
  function sedesSel() {
    if (rol() === 'ASE') return [0];
    if (rol() === 'SUC') return [1];
    if (window.wfSedes && window.wfSedes.length) return window.wfSedes.map(function (n) { return dim.sedes.indexOf(n); }).filter(function (i) { return i >= 0; });
    var s = document.getElementById('sede'), v = s ? s.value : 'Todas';
    if (v && v !== 'Todas') { for (var i = 0; i < dim.sedes.length; i++) { if (v.indexOf(dim.sedes[i]) === 0) return [i]; } }
    return [0, 1, 2]; // consolidado Quito + Valle + Ambato; Cuenca lleva un reporte distinto
  }
  function aseNombre() { return rol() === 'ASE' ? 'Carla M.' : F.ase; }
  function rango() {
    if (F.dia) { var p = F.dia.split('-'); var v = ymd(+p[0], +p[1], +p[2]); return { a: v, b: v, t: 'el ' + F.dia }; }
    var p = F.periodo;
    if (p.indexOf('Hoy') === 0) return { a: HOY, b: HOY, t: 'hoy · 23 oct 2026' };
    if (p.indexOf('Ayer') === 0) return { a: 20261022, b: 20261022, t: 'ayer · 22 oct 2026' };
    if (p.indexOf('Esta semana') === 0) return { a: 20261019, b: HOY, t: 'esta semana · 19 a 23 oct' };
    if (p.indexOf('Mes anterior') === 0) return { a: 20260901, b: 20260930, t: 'septiembre 2026' };
    if (p.indexOf('Este trimestre') === 0) return { a: 20261001, b: HOY, t: 'este trimestre · oct a hoy' };
    if (p.indexOf('Trimestre anterior') === 0) return { a: 20260701, b: 20260930, t: 'trimestre anterior · jul a sep' };
    if (p.indexOf('Este año') === 0) return { a: 20260101, b: HOY, t: 'este año · datos desde junio' };
    return { a: 20261001, b: HOY, t: 'octubre 2026 · al 23 oct' };
  }
  function prodIdx() { return F.prod === 'Todos' ? -1 : dim.prod.indexOf(F.prod); }

  /* ---------- Selección de datos ---------- */
  function selS(a, b) {
    var sd = sedesSel(), an = aseNombre(), ai = an === 'Todos' ? -1 : dim.ases.indexOf(an), pi = prodIdx();
    return S.filter(function (r) {
      var f = fecha(r); if (f < a || f > b) return false;
      if (sd.indexOf(r[3]) < 0) return false;
      if (ai >= 0 && r[4] !== ai) return false;
      if (F.prog !== 'Todos' && dim.progs[r[5]] !== F.prog) return false;
      if (pi >= 0 && r[8] !== pi) return false;
      if (F.orig !== 'Todos' && dim.origs[r[6]] !== F.orig) return false;
      if (F.walk !== 'Todas' && dim.walk[r[7]] !== F.walk) return false;
      return true;
    });
  }
  function peso(r, a, b) {
    var Y = 2025 + r[0], M = r[1], s = ymd(Y, M, 1), e = ymd(Y, M, DIAS[M]);
    var lo = Math.max(a, s), hi = Math.min(b, e); if (lo > hi) return 0;
    return ((hi % 100) - (lo % 100) + 1) / DIAS[M];
  }
  // Embudo y deserción vienen por mes: para períodos cortos se prorratean
  function selL(a, b) {
    var sd = sedesSel(), an = aseNombre(), ai = an === 'Todos' ? -1 : dim.ases.indexOf(an);
    var out = [];
    L.forEach(function (r) {
      if (sd.indexOf(r[2]) < 0) return;
      if (ai >= 0 && r[3] !== ai) return;
      if (F.orig !== 'Todos' && dim.origs[r[4]] !== F.orig) return;
      if (F.walk !== 'Todas' && dim.walk[r[5]] !== F.walk) return;
      var w = peso(r, a, b); if (w > 0) out.push({ r: r, w: w });
    });
    return out;
  }
  function selD(a, b) {
    var sd = sedesSel(), out = [];
    DS.forEach(function (r) { if (sd.indexOf(r[2]) < 0) return; var w = peso(r, a, b); if (w > 0) out.push({ r: r, w: w }); });
    return out;
  }

  function agg(rows) {
    var o = { ing: 0, mat: 0, niv: 0, one: 0, cert: 0, trad: 0, ups: 0, ref: 0, planes: 0, n: rows.length, lin: [0, 0, 0, 0, 0, 0] };
    rows.forEach(function (r) {
      var p = r[8], t = 0;
      for (var k = 0; k < 6; k++) { o.lin[k] += r[10 + k]; t += r[10 + k]; }
      o.ing += t;
      if (p < 3) { o.mat++; if (r[9]) o.ups++; if (r[6] === ORIG_REF) o.ref++; if (p === 0) { o.niv += 1; o.planes++; } else if (p === 1) o.niv += 0.5; }
      if (p === 2) o.one++;
      if (p === 3) o.cert++;
      if (p === 4) o.trad++;
    });
    o.serv = o.cert + o.trad;
    o.ingServ = o.lin[3] + o.lin[4];
    return o;
  }
  function funnel(ls) {
    var f = { pros: 0, asig: 0, aten: 0, cot: 0, gan: 0, perd: 0 };
    ls.forEach(function (x) { f.pros += x.r[6] * x.w; f.asig += x.r[7] * x.w; f.aten += x.r[8] * x.w; f.cot += x.r[9] * x.w; f.gan += x.r[10] * x.w; f.perd += x.r[11] * x.w; });
    f.rec = f.pros + f.asig + f.aten + f.cot + f.gan + f.perd;
    f.pAsig = f.rec - f.pros;            // salieron de prospección
    f.pAten = f.aten + f.cot + f.gan + f.perd; // fueron atendidos
    f.pCot = f.cot + f.gan;              // llegaron a cotización
    return f;
  }

  /* ---------- Piezas visuales ---------- */
  function card(t, inner, badge) { return '<section class="card"><div class="card-head"><h2>' + t + '</h2>' + (badge || '') + '</div>' + inner + '</section>'; }
  function dos(a, b) { return '<div class="grid grid-2"><div class="g-cell">' + a + '</div><div class="g-cell">' + b + '</div></div>'; }
  function vacio() { return '<p class="plan-empty">Sin datos con estos filtros</p>'; }
  function hb(items, fmt) {
    items = items.filter(function (i) { return i.v > 0 || i.cero; });
    if (!items.length) return vacio();
    var mx = Math.max.apply(null, items.map(function (i) { return i.v; })) || 1;
    return '<div class="hbars">' + items.map(function (i) { return '<div class="hbar"><span>' + esc(i.l) + '</span><div class="hbar-track"><div class="hbar-fill" style="width:' + Math.round(i.v / mx * 100) + '%"></div></div><b>' + fmt(i.v) + '</b></div>'; }).join('') + '</div>';
  }
  function pie(items, fmt) {
    var tot = items.reduce(function (s, i) { return s + i.v; }, 0);
    if (!tot) return vacio();
    var acc = 0, g = [];
    items.forEach(function (it, i) { var p = it.v / tot * 100; g.push(CH[i % CH.length] + ' ' + acc.toFixed(2) + '% ' + (acc + p).toFixed(2) + '%'); acc += p; });
    return '<div class="pie-wrap"><div class="pie" style="background:conic-gradient(' + g.join(',') + ')" role="img" aria-label="Gráfico circular"></div><ul class="pie-leg">' +
      items.map(function (it, i) { return '<li><i style="background:' + CH[i % CH.length] + '"></i>' + esc(it.l) + ' <b>' + pct(it.v, tot) + '</b>' + (fmt ? ' <small>' + fmt(it.v) + '</small>' : '') + '</li>'; }).join('') + '</ul></div>';
  }
  function linea(labels, series, fmt) {
    var W = 600, H = 170, names = Object.keys(series), mx = 0;
    names.forEach(function (k) { series[k].forEach(function (v) { if (v > mx) mx = v; }); });
    if (!mx) return vacio();
    mx = mx * 1.08; var n = labels.length, xs = labels.map(function (_, i) { return 44 + i * (W - 70) / (n - 1); });
    var y = function (v) { return H - 24 - (v / mx) * (H - 48); };
    var grid = [0, 0.5, 1].map(function (f) { var yy = H - 24 - (H - 48) * f; return '<line x1="44" x2="' + (W - 20) + '" y1="' + yy + '" y2="' + yy + '" stroke="#D6DCEA"/><text x="40" y="' + (yy + 4) + '" font-size="12" text-anchor="end" fill="#5B6B8A">' + fmt(mx * f / 1.08) + '</text>'; }).join('');
    var lines = names.map(function (k, j) {
      var pts = series[k].map(function (v, i) { return xs[i].toFixed(0) + ',' + y(v).toFixed(0); }).join(' ');
      var dots = series[k].map(function (v, i) { return '<circle cx="' + xs[i].toFixed(0) + '" cy="' + y(v).toFixed(0) + '" r="3.5" fill="' + CH[j % CH.length] + '"><title>' + esc(k) + ' · ' + labels[i] + ': ' + fmt(v) + '</title></circle>'; }).join('');
      return '<polyline fill="none" stroke="' + CH[j % CH.length] + '" stroke-width="2.5" stroke-linejoin="round" points="' + pts + '"' + (/anterior|2025|meta/i.test(k) ? ' stroke-dasharray="6 4"' : '') + '/>' + dots;
    }).join('');
    var ax = labels.map(function (l, i) { return '<text x="' + xs[i].toFixed(0) + '" y="' + (H - 6) + '" font-size="12" text-anchor="middle" fill="#5B6B8A">' + l + '</text>'; }).join('');
    var leg = names.map(function (k, j) { return '<span class="leg"><i style="background:' + CH[j % CH.length] + ';height:3px"></i>' + esc(k) + '</span>'; }).join('');
    return '<div class="chart"><svg viewBox="0 0 ' + W + ' ' + H + '" style="width:100%;height:auto" role="img" aria-label="Gráfico de líneas">' + grid + lines + ax + '</svg><div class="legend">' + leg + '</div></div>';
  }
  function tarjetas(items) {
    return '<div class="summary">' + items.map(function (i) { return '<div class="sum-item"><span class="sum-label">' + i[0] + '</span><span class="sum-value">' + i[1] + '</span><span class="sum-sub' + (i[3] ? ' ' + i[3] : '') + '">' + i[2] + '</span></div>'; }).join('') + '</div>';
  }
  function variacion(a, b) { if (!b) return 'sin base'; var v = (a - b) / b * 100; return (v >= 0 ? '+' : '') + (Math.round(v * 10) / 10) + '%'; }

  /* ---------- Series mensuales (respetan todos los filtros menos el período) ---------- */
  function serie(yr, fn) { return MES_N.map(function (m) { var rows = selS(ymd(yr, m, 1), ymd(yr, m, 31)); return fn(agg(rows), m, rows); }); }
  function convMes(yr, m) { var ls = selL(ymd(yr, m, 1), ymd(yr, m, 31)); var f = funnel(ls); return f.rec ? f.gan / f.rec * 100 : 0; }
  function deserMes(yr, m) { var ds = selD(ymd(yr, m, 1), ymd(yr, m, 31)), t = 0, n = 0; ds.forEach(function (x) { t += x.r[3] * x.w; n += x.r[4] * x.w; }); return t ? n / t * 100 : 0; }

  /* ---------- Dibujo de secciones ---------- */
  function render() {
    var R = rango(), P = { a: R.a - 10000, b: R.b - 10000 };
    var cur = agg(selS(R.a, R.b)), prv = agg(selS(P.a, P.b));
    var sd = sedesSel(), sedeTxt = sd.length === 3 && sd.indexOf(3) < 0 ? 'Quito + Valle + Ambato' : sd.map(function (i) { return dim.sedes[i]; }).join(' + ');
    var an = aseNombre();
    var ctx = '<b>' + esc(R.t) + '</b> · ' + esc(sedeTxt) + ' · ' + (an === 'Todos' ? 'todos los asesores' : esc(an));
    if (rol() === 'ASE') ctx += ' · <b>reporte individual</b>: solo ves tus ventas';
    else if (rol() === 'DIR' || rol() === 'GER' || rol() === 'ADM') ctx += ' · vista consolidada';
    q('[data-plan-ctx]').innerHTML = ctx;

    var meta = prv.ing * 1.15;
    var kp1 = tarjetas([
      ['Ingreso total', money(cur.ing), 'todos los conceptos'],
      ['Matrículas', cur.mat, 'nuevas, reingresos y continuidad'],
      ['Niveles vendidos', num(cur.niv), '1 nivel = 2 módulos'],
      ['Ticket promedio', cur.mat ? money(cur.ing / cur.mat) : '—', 'ingreso total / matrículas'],
      ['One to one vendidos', cur.one, 'programas de horas'],
      ['Cumplimiento de la meta', meta ? pct(cur.ing, meta) : 'sin base', 'meta: mismo período del año anterior + 15 %', meta && cur.ing < meta ? 'is-warn' : '']]);
    var kp2 = tarjetas([
      ['Certificados vendidos', cur.cert, 'exámenes internacionales'],
      ['Traducciones vendidas', cur.trad, 'las registra Secretaría'],
      ['Total de servicios', cur.serv, 'certificados + traducciones'],
      ['Ticket de servicios', cur.serv ? money(cur.ingServ / cur.serv) : '—', 'servicios / servicios vendidos'],
      ['Variación vs año anterior', variacion(cur.ing, prv.ing), 'ingreso del mismo período · matrículas ' + variacion(cur.mat, prv.mat), prv.ing && cur.ing < prv.ing ? 'is-bad' : '']]);
    var h = '<div class="plan-sec">' + card('Indicadores principales', kp1 + kp2, '<span class="badge badge-navy">Se recalculan con los filtros</span>');

    // Líneas
    var ing26 = serie(1, function (a) { return a.ing; }), ing25 = serie(0, function (a) { return a.ing; });
    var mat26 = serie(1, function (a) { return a.mat; }), mat25 = serie(0, function (a) { return a.mat; });
    var tk26 = serie(1, function (a) { return a.mat ? a.ing / a.mat : 0; }), tk25 = serie(0, function (a) { return a.mat ? a.ing / a.mat : 0; });
    var metaS = ing25.map(function (v) { return v * 1.15; });
    h += dos(card('Ingresos mensuales · 2026 frente a 2025', linea(MESES, { '2026': ing26, '2025 (mismo período)': ing25 }, miles)),
             card('Matrículas mensuales · 2026 frente a 2025', linea(MESES, { '2026': mat26, '2025 (mismo período)': mat25 }, function (v) { return Math.round(v); })));
    h += dos(card('Resultado real frente a la meta proyectada', linea(MESES, { 'Real 2026': ing26, 'Meta (2025 + 15 %)': metaS }, miles)),
             card('Ticket promedio mensual', linea(MESES, { '2026': tk26, '2025 (mismo período)': tk25 }, function (v) { return money(v); })));
    var cv26 = MES_N.map(function (m) { return convMes(1, m); }), dz26 = MES_N.map(function (m) { return deserMes(1, m); });
    var cv25 = MES_N.map(function (m) { return convMes(0, m); }), dz25 = MES_N.map(function (m) { return deserMes(0, m); });
    h += card('Evolución de la conversión y la deserción (%)', linea(MESES, { 'Conversión lead → matrícula 2026': cv26, 'Deserción mensual 2026': dz26, 'Conversión 2025': cv25, 'Deserción 2025': dz25 }, function (v) { return (Math.round(v * 10) / 10) + '%'; })
      + '<p class="plan-nota">Deserción: estudiantes que terminan un módulo y no se rematriculan en 30 días (definición propuesta, por confirmar). Se filtra por sede.</p>');

    // Barras
    var rows = selS(R.a, R.b);
    var porSede = dim.sedes.map(function (n, i) { return { l: n, v: agg(rows.filter(function (r) { return r[3] === i; })).ing }; });
    var lineas = dim.lineas.map(function (n, k) { return { l: n, v: cur.lin[k] }; });
    var porProd = dim.prod.map(function (n, k) { return { l: n, v: agg(rows.filter(function (r) { return r[8] === k; })).ing }; });
    var porProg = dim.progs.map(function (n, k) { return { l: n, v: agg(rows.filter(function (r) { return r[5] === k; })).ing }; });
    var porOrigM = dim.origs.map(function (n, k) { return { l: n, v: agg(rows.filter(function (r) { return r[6] === k; })).mat }; });
    var porOrigI = dim.origs.map(function (n, k) { return { l: n, v: agg(rows.filter(function (r) { return r[6] === k; })).ing }; });
    var ls = selL(R.a, R.b), fu = funnel(ls);
    var porCanal = dim.origs.map(function (n, k) { var f = funnel(ls.filter(function (x) { return x.r[4] === k; })); return { l: n, v: f.rec ? f.gan / f.rec * 100 : 0 }; }).sort(function (a, b) { return b.v - a.v; });
    var sorted = function (a) { return a.slice().sort(function (x, y) { return y.v - x.v; }); };
    var $f = function (v) { return money(v); }, nf = function (v) { return String(Math.round(v)); }, pf = function (v) { return (Math.round(v * 10) / 10) + '%'; };
    h += dos(card('Ingresos por sede', hb(sorted(porSede), $f)), card('Ingresos por línea de negocio', hb(sorted(lineas), $f)));
    h += dos(card('Ingresos por producto', hb(sorted(porProd), $f)), card('Ingresos por tipo de programa', hb(sorted(porProg), $f)));
    h += dos(card('Certificaciones, traducciones y servicios vendidos', hb([{ l: 'Certificaciones (exámenes)', v: cur.cert, cero: true }, { l: 'Traducciones', v: cur.trad, cero: true }, { l: 'Total de servicios', v: cur.serv, cero: true }], nf)),
             card('Matrículas por origen del lead', hb(sorted(porOrigM), nf)));
    h += dos(card('Ingresos por origen del lead', hb(sorted(porOrigI), $f)), card('Conversión por canal (lead → ganado)', hb(porCanal, pf)));

    // Asesores
    var ases = dim.ases.map(function (n, i) { var rr = rows.filter(function (r) { return r[4] === i; }); var a = agg(rr); var f = funnel(ls.filter(function (x) { return x.r[3] === i; })); return { n: n, a: a, conv: f.rec ? f.gan / f.rec * 100 : 0 }; }).filter(function (x) { return x.a.n || x.conv; });
    var asB = function (fn, fmt) { return hb(ases.map(function (x) { return { l: x.n, v: fn(x) }; }).sort(function (a, b) { return b.v - a.v; }), fmt); };
    h += card('Resultado por asesor',
      dos(card('Matrículas', asB(function (x) { return x.a.mat; }, nf)), card('Facturación', asB(function (x) { return x.a.ing; }, $f)))
      + dos(card('Conversión lead → matrícula', asB(function (x) { return x.conv; }, pf)), card('Matrículas por referidos', asB(function (x) { return x.a.ref; }, nf)))
      + card('Upsell (% de matrículas con un servicio adicional)', asB(function (x) { return x.a.mat ? x.a.ups / x.a.mat * 100 : 0; }, pf)),
      '<span class="badge badge-neutral">Cada asesor ve el suyo</span>');

    // Porcentuales
    var regulares = cur.mat - cur.one;
    var porProgM = dim.progs.map(function (n, k) { return { l: n, v: agg(rows.filter(function (r) { return r[5] === k; })).mat }; }).filter(function (x) { return x.v > 0; });
    h += dos(card('Estudiantes en planes de nivel', pie([{ l: 'Plan de nivel completo', v: cur.planes }, { l: 'Módulos sueltos y horas', v: cur.mat - cur.planes }])),
             card('Ventas one to one frente a programas regulares', pie([{ l: 'One to one', v: cur.one }, { l: 'Programas regulares', v: regulares }])));
    h += dos(card('Matrículas provenientes de referidos', pie([{ l: 'Referidos', v: cur.ref }, { l: 'Otros orígenes', v: cur.mat - cur.ref }])),
             card('Distribución de matrículas por programa', pie(porProgM, nf)));
    h += card('Upsell por asesor (%)', asB(function (x) { return x.a.mat ? x.a.ups / x.a.mat * 100 : 0; }, pf));
    h += '</div>';
    q('[data-plan-out="todo"]').innerHTML = h;

    embudo(R, ls, fu);
    matriz(R, rows, ls);
  }

  /* ---------- Embudo de Kommo ---------- */
  function embudo(R, ls, fu) {
    var etapas = [['Leads recibidos', fu.rec], ['Asignados a un asesor', fu.pAsig], ['Atendidos por los asesores', fu.pAten], ['Cotizados', fu.pCot], ['Ganados · matrícula o servicio', fu.gan]];
    var mx = etapas[0][1] || 1, out = '';
    etapas.forEach(function (e, i) {
      var conv = i ? ' · ' + pct(e[1], etapas[i - 1][1]) + ' del paso anterior' : '';
      out += '<div class="funnel-row"><div class="funnel-bar" style="width:' + Math.max(Math.round(e[1] / mx * 100), 4) + '%;background:' + CH[0] + '">' + Math.round(e[1]).toLocaleString('en-US') + '</div><span>' + e[0] + conv + '</span></div>';
    });
    var actuales = [['En prospección', fu.pros], ['Asignados, sin atender', fu.asig], ['Atendidos, sin cotizar', fu.aten], ['Cotizados, sin cerrar', fu.cot], ['Ganados', fu.gan], ['Perdidos', fu.perd]];
    var html = fu.rec ? '<div class="funnel">' + out + '</div>'
      + '<div class="plan-kv"><span><b>' + pct(fu.gan, fu.rec) + '</b> conversión total lead → matrícula</span><span><b>' + pct(fu.pAten, fu.rec) + '</b> leads atendidos</span><span><b>' + Math.round(fu.perd) + '</b> perdidos</span><span><b>' + Math.round(fu.pros) + '</b> en prospección</span></div>'
      + '<h4 class="section-title">Dónde está hoy cada lead (todas las etapas)</h4>' + hb(actuales.map(function (e) { return { l: e[0], v: e[1], cero: true }; }), function (v) { return String(Math.round(v)); }) : vacio();
    q('[data-plan-out="embudo"]').innerHTML = html;
    var g = (q('[data-pf="egrupo"]') || {}).value || 'Sede';
    var clave = { Sede: function (r) { return dim.sedes[r[2]]; }, Asesor: function (r) { return dim.ases[r[3]]; }, Canal: function (r) { return dim.origs[r[4]]; }, Mes: function (r) { return MESES[MES_N.indexOf(r[1])] + ' ' + (2025 + r[0]); } }[g];
    var m = {};
    ls.forEach(function (x) { var k = clave(x.r); (m[k] = m[k] || []).push(x); });
    var filas = Object.keys(m).map(function (k) {
      var f = funnel(m[k]);
      return [k, Math.round(f.rec), Math.round(f.pros), Math.round(f.pAsig), Math.round(f.pAten), Math.round(f.pCot), Math.round(f.gan), Math.round(f.perd), pct(f.gan, f.rec)];
    }).sort(function (a, b) { return b[1] - a[1]; });
    tabla(q('[data-plan-etbl] .wf-table'), [g, 'Recibidos', 'En prospección', 'Asignados', 'Atendidos', 'Cotizados', 'Ganados', 'Perdidos', 'Conversión'], filas, 1);
  }

  /* ---------- Matriz consultable y exportable ---------- */
  function matriz(R, rows, ls) {
    var dimsOn = qa('[data-mdim]').filter(function (c) { return c.checked; }).map(function (c) { return +c.getAttribute('data-mdim'); });
    var names = ['Sede', 'Asesor', 'Programa', 'Producto', 'Canal'];
    var val = [function (r) { return dim.sedes[r[3]]; }, function (r) { return dim.ases[r[4]]; }, function (r) { return dim.progs[r[5]]; }, function (r) { return dim.prod[r[8]]; }, function (r) { return dim.origs[r[6]]; }];
    var leadVal = [function (r) { return dim.sedes[r[2]]; }, function (r) { return dim.ases[r[3]]; }, null, null, function (r) { return dim.origs[r[4]]; }];
    var conLeads = dimsOn.every(function (d) { return d !== 2 && d !== 3; });
    var m = {};
    rows.forEach(function (r) { var k = dimsOn.map(function (d) { return val[d](r); }).join('|'); (m[k] = m[k] || []).push(r); });
    var lm = {};
    if (conLeads) ls.forEach(function (x) { var k = dimsOn.map(function (d) { return leadVal[d](x.r); }).join('|'); (lm[k] = lm[k] || []).push(x); });
    var filas = Object.keys(m).map(function (k) {
      var a = agg(m[k]), f = conLeads && lm[k] ? funnel(lm[k]) : null;
      return { k: k, a: a, f: f };
    }).sort(function (x, y) { return y.a.ing - x.a.ing; });
    var cols = dimsOn.map(function (d) { return names[d]; }).concat(['Ventas', 'Matrículas', 'Facturación', 'Ticket', 'Referidos', 'Upsell']);
    if (conLeads) cols.push('Conversión');
    var tot = agg(rows), ft = conLeads ? funnel(ls) : null;
    var data = filas.slice(0, 300).map(function (x) {
      var base = x.k.split('|');
      var r = base.concat([x.a.n, x.a.mat, money(x.a.ing), x.a.mat ? money(x.a.ing / x.a.mat) : '—', x.a.ref, x.a.mat ? pct(x.a.ups, x.a.mat) : '—']);
      if (conLeads) r.push(x.f ? pct(x.f.gan, x.f.rec) : '—');
      return r;
    });
    if (data.length) {
      var t = dimsOn.map(function (d, i) { return i === 0 ? 'Total' : ''; }).concat([tot.n, tot.mat, money(tot.ing), tot.mat ? money(tot.ing / tot.mat) : '—', tot.ref, tot.mat ? pct(tot.ups, tot.mat) : '—']);
      if (conLeads) t.push(ft ? pct(ft.gan, ft.rec) : '—');
      data.push(t);
    }
    window.__planMatriz = { cols: cols, data: data, nd: dimsOn.length };
    pintarMatriz();
    var info = q('[data-plan-minfo]');
    if (info) info.textContent = (filas.length ? filas.length + ' filas' : 'Sin filas') + (conLeads ? '' : ' · la conversión solo se muestra por sede, asesor y canal') ;
  }
  function pintarMatriz() {
    var M = window.__planMatriz; if (!M) return;
    var bus = ((q('[data-pf-mbus]') || {}).value || '').toLowerCase();
    var data = M.data.filter(function (r) { return !bus || r.join(' ').toLowerCase().indexOf(bus) >= 0 || r[0] === 'Total'; });
    tabla(q('[data-plan-mtbl] .wf-table'), M.cols, data, 0, M.nd);
  }
  function tabla(el, cols, rows, wide, nd) {
    if (!el) return;
    nd = nd === undefined ? 1 : nd;
    el.setAttribute('data-cols', JSON.stringify(cols));
    el.style.gridTemplateColumns = cols.map(function (c, i) { return i === wide ? 'minmax(140px,1.6fr)' : 'minmax(min-content,1fr)'; }).join(' ');
    var h = cols.map(function (c, i) { return '<div class="th' + (i >= nd ? ' th-num' : '') + '" role="columnheader">' + esc(c) + '</div>'; }).join('');
    rows.forEach(function (r) {
      var total = r[0] === 'Total';
      h += '<div class="wf-row">' + r.map(function (c, i) { return '<div class="td' + (i === wide ? ' td-wide' : '') + (i >= nd ? ' is-num' : '') + '" data-label="' + esc(cols[i]) + '">' + (total ? '<b>' + esc(c) + '</b>' : esc(c)) + '</div>'; }).join('') + '</div>';
    });
    if (!rows.length) h += '<div class="wf-empty" style="grid-column:1/-1">Sin resultados con estos filtros</div>';
    el.innerHTML = h;
  }

  /* ---------- Eventos ---------- */
  function leer() {
    qa('[data-pf]').forEach(function (e) { var k = e.getAttribute('data-pf'); if (k in F) F[k] = e.value; });
  }
  function bloquear() {
    var asesor = q('[data-pf="ase"]');
    if (asesor) { if (rol() === 'ASE') { asesor.value = 'Carla M.'; asesor.disabled = true; } else { if (asesor.disabled) asesor.value = 'Todos'; asesor.disabled = false; } }
  }
  function todo() { bloquear(); leer(); render(); }
  document.addEventListener('change', function (e) {
    var t = e.target; if (!t.matches) return;
    if (t.matches('[data-pf]') || t.matches('[data-mdim]') || t.id === 'sede' || t.id === 'rol') { if (t.matches('[data-pf="dia"]') && t.value) { /* el día específico manda */ } todo(); }
  });
  document.addEventListener('input', function (e) { if (e.target.matches && e.target.matches('[data-pf-mbus]')) pintarMatriz(); });
  document.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target : null; if (!t) return;
    if (t.closest('[data-pf-reset]')) {
      qa('[data-pf]').forEach(function (s) { if (s.tagName === 'SELECT') s.selectedIndex = s.hasAttribute('data-def') ? +s.getAttribute('data-def') : 0; else s.value = ''; });
      todo(); return;
    }
    if (t.closest('.pills[data-sede-pills] .pill')) setTimeout(todo, 60);
  });
  // La barra de filtros de la página solo mueve la tabla de ventas: en el Plan estratégico se oculta para no duplicar filtros
  function barraPagina() {
    var tab = q('[role=tab].on'), plan = tab && tab.getAttribute('data-tab') === 'Indicadores y gráficos';
    var f = q('.wf-filters[data-target="ventas"]'); if (f) { f.hidden = plan; var k = f.nextElementSibling; if (k && k.classList.contains('summary')) k.hidden = plan; }
  }
  document.addEventListener('click', function (e) { if (e.target.closest && e.target.closest('[role=tab]')) setTimeout(barraPagina, 30); });
  function init() { todo(); barraPagina(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  setTimeout(init, 700);
})();
