/* Pagos con varios métodos (prototipo): agrega y quita líneas de pago y verifica que la suma cuadre con el valor a cobrar.
   Cada línea muestra los datos que pide su método (la lógica de mostrar u ocultar campos la hace la página). Sin dependencias. */
(function () {
  if (window.__pagos) return;
  window.__pagos = true;

  function dinero(n) { return '$' + n.toFixed(2); }

  function monto(line) {
    var ls = line.querySelectorAll('label');
    for (var i = 0; i < ls.length; i++) {
      if (/^monto/i.test(ls[i].textContent.trim()) && ls[i].htmlFor) {
        var e = document.getElementById(ls[i].htmlFor);
        return e ? e : null;
      }
    }
    return null;
  }
  function visibles(box) { return [].filter.call(box.querySelectorAll('[data-pago-line]'), function (l) { return !l.hidden; }); }

  function resumen(box) {
    var total = parseFloat(box.getAttribute('data-total')) || 0, suma = 0;
    visibles(box).forEach(function (l) { var m = monto(l); suma += m ? (parseFloat(m.value) || 0) : 0; });
    suma = Math.round(suma * 100) / 100;
    var dif = Math.round((total - suma) * 100) / 100;
    var out = box.querySelector('[data-pagos-sum]'); if (!out) return;
    out.classList.remove('is-ok', 'is-warn', 'is-bad');
    if (dif === 0) { out.textContent = 'Pagos ' + dinero(suma) + ' de ' + dinero(total) + ' · cuadra'; out.classList.add('is-ok'); }
    else if (dif > 0) { out.textContent = 'Pagos ' + dinero(suma) + ' de ' + dinero(total) + ' · faltan ' + dinero(dif) + ': quedará saldo pendiente'; out.classList.add('is-warn'); }
    else { out.textContent = 'Pagos ' + dinero(suma) + ' de ' + dinero(total) + ' · sobran ' + dinero(-dif) + ': revisa los montos'; out.classList.add('is-bad'); }
    var add = box.querySelector('[data-pago-add]');
    if (add) add.hidden = !box.querySelector('[data-pago-line][hidden]');
  }

  document.addEventListener('input', function (e) {
    var box = e.target.closest ? e.target.closest('[data-pagos]') : null; if (box) resumen(box);
  });
  document.addEventListener('change', function (e) {
    var box = e.target.closest ? e.target.closest('[data-pagos]') : null; if (box) resumen(box);
  });
  document.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target : null; if (!t) return;
    var add = t.closest('[data-pago-add]'), del = t.closest('[data-pago-del]');
    if (add) {
      var box = add.closest('[data-pagos]'); var next = box.querySelector('[data-pago-line][hidden]');
      if (!next) return;
      var total = parseFloat(box.getAttribute('data-total')) || 0, suma = 0;
      visibles(box).forEach(function (l) { var m = monto(l); suma += m ? (parseFloat(m.value) || 0) : 0; });
      var m2 = monto(next); if (m2) m2.value = Math.max(total - suma, 0).toFixed(2);
      next.hidden = false; resumen(box);
      var f = next.querySelector('select'); if (f) f.focus();
    }
    if (del) {
      var line = del.closest('[data-pago-line]'); var b = del.closest('[data-pagos]');
      line.hidden = true; var mm = monto(line); if (mm) mm.value = '0.00'; resumen(b);
    }
  });


  // Elegir un link del historial: llena autorización, link y monto del pago en línea
  document.addEventListener('change', function (e) {
    var t = e.target;
    if (!t || !t.tagName || t.tagName !== 'SELECT') return;
    var lab = t.id && document.querySelector('label[for="' + t.id + '"]');
    if (!lab || !/^traer del historial/i.test(lab.textContent.trim())) return;
    var m = /(LP-\d+).*\$([\d.,]+).*aut\.\s*(\d+)/.exec(t.options[t.selectedIndex].text);
    if (!m) return;
    var grupo = t.closest('.dep-group') || t.closest('[data-pago-line]');
    function poner(txt, val) {
      [].forEach.call(grupo.querySelectorAll('label'), function (l) {
        if (new RegExp('^' + txt, 'i').test(l.textContent.trim()) && l.htmlFor) { var i = document.getElementById(l.htmlFor); if (i) i.value = val; }
      });
    }
    poner('código de autorización', m[3]); poner('link de pago', m[1] + ' · Datafast');
    var linea = t.closest('[data-pago-line]');
    if (linea) { var mo = monto(linea); if (mo) { mo.value = parseFloat(m[2].replace(',', '')).toFixed(2); var box = linea.closest('[data-pagos]'); if (box) resumen(box); } }
    var tt = document.getElementById('wf-toast'); if (tt) { tt.textContent = 'Traído del historial: autorización ' + m[3] + ' y su comprobante'; tt.style.display = 'block'; setTimeout(function () { tt.style.display = 'none'; }, 2800); }
  });

  function init() { document.querySelectorAll('[data-pagos]').forEach(resumen); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  setTimeout(init, 500);
})();
