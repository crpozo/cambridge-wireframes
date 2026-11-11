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

  function init() { document.querySelectorAll('[data-pagos]').forEach(resumen); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  setTimeout(init, 500);
})();
