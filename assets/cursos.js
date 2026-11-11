/* Calendario del curso (prototipo): calcula la fecha de fin saltando feriados de Ecuador.
   Entradas: fecha de inicio, días de clase, horas por sesión y total de horas. Sin dependencias. */
(function () {
  if (window.__calCurso) return;
  window.__calCurso = true;

  // Feriados de ejemplo (los carga el calendario oficial; los móviles dependen de decretos)
  var FER = {
    '2026-11-02': 'Día de Difuntos', '2026-11-03': 'Independencia de Cuenca', '2026-12-25': 'Navidad',
    '2027-01-01': 'Año Nuevo', '2027-02-08': 'Carnaval', '2027-02-09': 'Carnaval', '2027-03-26': 'Viernes Santo',
    '2027-05-01': 'Día del Trabajo', '2027-05-24': 'Batalla de Pichincha', '2027-08-10': 'Primer Grito de Independencia',
    '2027-10-09': 'Independencia de Guayaquil', '2027-11-02': 'Día de Difuntos', '2027-11-03': 'Independencia de Cuenca', '2027-12-25': 'Navidad'
  };
  var MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  var DIAS = ['dom', 'lun', 'mar', 'mié', 'jue', 'vie', 'sáb'];

  function pad(n) { return ('0' + n).slice(-2); }
  function iso(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function fmt(d) { return DIAS[d.getDay()] + ' ' + d.getDate() + ' ' + MESES[d.getMonth()] + ' ' + d.getFullYear(); }
  function parse(v) { var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(v || ''); return m ? new Date(+m[1], +m[2] - 1, +m[3]) : null; }

  function campo(box, texto) {
    var ls = box.querySelectorAll('label');
    for (var i = 0; i < ls.length; i++) {
      if (ls[i].textContent.trim().toLowerCase().indexOf(texto) === 0 && ls[i].htmlFor) return box.querySelector('#' + ls[i].htmlFor);
    }
    return null;
  }
  function set(box, sel, v) { var e = box.querySelector(sel); if (e) e.textContent = v; }

  function calcular(box) {
    var ini = parse((campo(box, 'fecha de inicio') || {}).value);
    var hps = +((campo(box, 'horas por sesión') || {}).value) || 2;
    var tot = +((campo(box, 'total de horas') || {}).value) || 0;
    var dias = [].slice.call(box.querySelectorAll('[data-cal-day]:checked')).map(function (c) { return +c.value; });
    if (!ini || !tot || !dias.length) {
      ['[data-cal-first]', '[data-cal-end]', '[data-cal-sessions]', '[data-cal-skipped]'].forEach(function (s) { set(box, s, '—'); });
      return;
    }
    var need = Math.ceil(tot / hps), n = 0, d = new Date(ini), first = null, last = null, saltados = [], guard = 0;
    while (n < need && guard++ < 800) {
      if (dias.indexOf(d.getDay()) >= 0) {
        var k = iso(d);
        if (FER[k]) saltados.push(d.getDate() + ' ' + MESES[d.getMonth()] + ' · ' + FER[k]);
        else { n++; if (!first) first = new Date(d); last = new Date(d); }
      }
      d.setDate(d.getDate() + 1);
    }
    set(box, '[data-cal-first]', first ? fmt(first) : '—');
    set(box, '[data-cal-end]', last ? fmt(last) : '—');
    set(box, '[data-cal-sessions]', n + ' sesiones de ' + hps + ' h');
    set(box, '[data-cal-skipped]', saltados.length ? saltados.join(', ') : 'ninguno');
    box.classList.toggle('has-skipped', saltados.length > 0);
    // Rellena el campo "Fecha fin" de solo lectura del formulario, si existe
    if (last) {
      document.querySelectorAll('label').forEach(function (l) {
        if (/^fecha fin/i.test(l.textContent.trim()) && l.htmlFor) { var inp = document.getElementById(l.htmlFor); if (inp) inp.value = iso(last); }
      });
    }
  }

  function init() {
    document.querySelectorAll('[data-cal]').forEach(function (box) {
      var f = function () { calcular(box); };
      box.addEventListener('input', f); box.addEventListener('change', f); f();
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
