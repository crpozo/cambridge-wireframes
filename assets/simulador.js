/* Simulador de comisiones (Reglas de comisión → Simulador).
   Misma regla que sim_calc() del generador: base por sede (a la mitad si cumple la meta),
   matrículas en orden de llegada, monto fijo por venta según módulos, programa y modalidad,
   one to one por horas fuera de la base, summer camp, meses anteriores y bono grupal. */
(function () {
  var root = document.querySelector('[data-sim]');
  if (!root) return;
  var D = JSON.parse(root.querySelector('.sim-data').textContent);
  function money(v) {
    var s = Math.abs(v).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return (v < 0 ? '−$' : '$') + s;
  }
  function params() {
    var p = {};
    root.querySelectorAll('[data-p]').forEach(function (el) {
      var k = el.getAttribute('data-p');
      p[k] = k === 'per' ? el.value : (parseFloat(el.value) || 0);
    });
    return p;
  }
  function modAmount(mod, prog) {
    for (var i = 0; i < D.mod.length; i++) if (D.mod[i][0] === mod && D.mod[i][1] === prog) return D.mod[i][2];
    return 0;
  }
  function calc(a, p) {
    var base0 = a.sede === 'Ambato' ? p.baseA : p.baseQV;
    var base = a.meta ? Math.round(base0 * p.metaPct / 100) : base0;
    var valid = 0, sobre = 0, tot = 0;
    a.ventas.forEach(function (v) {
      var t = v[0];
      if (t === 'm' || t === 'n') {
        valid++;
        if (valid <= base) return;
        sobre++;
        if (t === 'm') tot += modAmount(v[1], v[2]) * (1 + p.ajMod / 100);
        else tot += D.niv[v[1]][v[2]][v[3] - 2] * (1 + p.ajNiv / 100);
      } else if (t === 'o') tot += D.o2o[v[1]][D.o2oH.indexOf(v[2])];
      else if (t === 's') tot += p.summer;
      else if (t === 'a') tot += p.ant;
    });
    if (a.bono) tot += p.bono;
    return { valid: valid, base: Math.max(base, 0), sobre: sobre, tot: Math.round(tot * 100) / 100 };
  }
  function set(key, txt) {
    var el = root.querySelector('[data-s="' + key + '"]');
    if (el) el.textContent = txt;
  }
  function render() {
    var p = params(), vig = {}, k;
    for (k in D.def) vig[k] = D.def[k];
    var lista = D.data[p.per] || [], tv = 0, ts = 0;
    lista.forEach(function (a, i) {
      var cv = calc(a, vig), cs = calc(a, p), dif = Math.round((cs.tot - cv.tot) * 100) / 100;
      tv += cv.tot; ts += cs.tot;
      set(i + '-valid', cs.valid);
      set(i + '-base', cs.base === cv.base ? cs.base : cs.base + ' (antes ' + cv.base + ')');
      set(i + '-sobre', cs.sobre);
      set(i + '-vig', money(cv.tot));
      set(i + '-sim', money(cs.tot));
      set(i + '-dif', (dif > 0 ? '+' : '') + money(dif));
      var d = root.querySelector('[data-s="' + i + '-dif"]');
      if (d) d.className = dif > 0 ? 'sim-up' : (dif < 0 ? 'sim-down' : '');
    });
    var td = Math.round((ts - tv) * 100) / 100;
    set('tv', money(tv));
    set('ts', money(ts));
    set('td', (td > 0 ? '+' : '') + money(td));
    set('tdp', td === 0 ? 'sin cambios' : ((td > 0 ? '+' : '') + (tv ? (td / tv * 100).toFixed(1) : '0') + ' % frente a lo vigente'));
  }
  root.addEventListener('input', function (e) { if (e.target.hasAttribute('data-p')) render(); });
  root.addEventListener('change', function (e) { if (e.target.hasAttribute('data-p')) render(); });
  var reset = root.querySelector('[data-sim-reset]');
  if (reset) reset.addEventListener('click', function () {
    root.querySelectorAll('[data-p]').forEach(function (el) {
      var k = el.getAttribute('data-p');
      if (k in D.def) el.value = D.def[k];
    });
    render();
  });
  render();
})();
