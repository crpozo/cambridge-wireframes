/* Nota de crédito por cambio de modalidad o de curso (prototipo): calcula si corresponde
   nota de crédito, cobro adicional o nada, según el valor pagado y el valor nuevo. Sin dependencias. */
(function () {
  if (window.__ajustes) return;
  window.__ajustes = true;

  function campo(box, texto) {
    var ls = box.querySelectorAll('label');
    for (var i = 0; i < ls.length; i++) {
      if (ls[i].textContent.trim().toLowerCase().indexOf(texto) === 0 && ls[i].htmlFor) return box.querySelector('#' + ls[i].htmlFor);
    }
    return null;
  }
  function valor(sel) {
    var m = /\$\s*([\d.,]+)/.exec((sel && sel.options[sel.selectedIndex] ? sel.options[sel.selectedIndex].text : '') || '');
    return m ? parseFloat(m[1].replace(',', '')) : 0;
  }
  function $(n) { return '$' + n.toFixed(2); }
  function set(box, s, t) { var e = box.querySelector(s); if (e) e.textContent = t; }

  function calcular(box) {
    var n = Math.max(+((campo(box, 'módulos afectados') || {}).value) || 1, 1);
    var pagado = valor(campo(box, 'modalidad actual')) * n;
    var nuevo = valor(campo(box, 'nueva modalidad')) * n;
    var dif = Math.round((nuevo - pagado) * 100) / 100;
    var res, monto = 0;
    if (dif < 0) { res = 'Nota de crédito por ' + $(-dif) + ' · se devuelve o queda como saldo a favor'; monto = -dif; box.setAttribute('data-nc-tipo', 'nc'); }
    else if (dif > 0) { res = 'Cobro adicional de ' + $(dif) + ' · no hay nota de crédito'; box.setAttribute('data-nc-tipo', 'cobro'); }
    else { res = 'Sin diferencia · solo se mueve la matrícula'; box.setAttribute('data-nc-tipo', 'igual'); }
    set(box, '[data-nc-pagado]', $(pagado)); set(box, '[data-nc-nuevo]', $(nuevo)); set(box, '[data-nc-resultado]', res);
    // Rellena el monto de la nota de crédito del formulario
    document.querySelectorAll('label').forEach(function (l) {
      if (/^monto de la nota/i.test(l.textContent.trim()) && l.htmlFor) {
        var i = document.getElementById(l.htmlFor); if (i) i.value = monto.toFixed(2);
      }
    });
  }

  function init() {
    document.querySelectorAll('[data-nc]').forEach(function (box) {
      var f = function () { calcular(box); };
      box.addEventListener('input', f); box.addEventListener('change', f); f();
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
