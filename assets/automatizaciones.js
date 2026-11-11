/* Automatizaciones (prototipo): activa o apaga reglas y mantiene el conteo de reglas activas. Sin dependencias. */
(function () {
  if (window.__auto) return;
  window.__auto = true;

  function toast(m) {
    var t = document.getElementById('wf-toast');
    if (!t) return;
    t.textContent = m; t.style.display = 'block';
    setTimeout(function () { t.style.display = 'none'; }, 2600);
  }

  function contar() {
    var todas = document.querySelectorAll('input[data-regla]');
    var act = [].filter.call(todas, function (i) { return i.checked; }).length;
    var a = document.querySelector('[data-reglas-activas]'), t = document.querySelector('[data-reglas-total]');
    if (a) a.textContent = act; if (t) t.textContent = todas.length;
  }

  document.addEventListener('change', function (e) {
    var i = e.target.closest ? e.target.closest('input[data-regla]') : null;
    if (!i) return;
    var fila = i.closest('.wf-row') || i.parentElement;
    var est = fila.querySelector('[data-regla-estado]');
    if (est) { est.textContent = i.checked ? 'Activa' : 'Apagada'; est.className = 'badge ' + (i.checked ? 'badge-ok' : 'badge-neutral'); }
    contar();
    toast(i.checked ? 'Regla activada: se aplicará desde ahora' : 'Regla apagada: dejará de enviar avisos');
  });

  function init() { contar(); setTimeout(contar, 500); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
