/* Aprobación de descuentos (prototipo): muestra "Aprobado por" cuando el descuento lo exige y
   bloquea el guardado de la matrícula mientras no se registre quién lo aprobó. Sin dependencias. */
(function () {
  if (window.__descuentosAprob) return;
  window.__descuentosAprob = true;

  function toast(m) {
    var t = document.getElementById('wf-toast');
    if (!t) return;
    t.textContent = m; t.style.display = 'block';
    setTimeout(function () { t.style.display = 'none'; }, 3200);
  }

  function requiere(sel) {
    var pct = +sel.value, lim = +(sel.getAttribute('data-limit') || 10);
    var txt = (sel.options[sel.selectedIndex] || {}).text || '';
    if (pct > lim) return 'El descuento pasa del ' + lim + '% que puede aplicar el asesor';
    if (/aprobaci|autorizaci|hermano/i.test(txt)) return 'Este tipo de descuento siempre necesita aprobación';
    return '';
  }

  function actualizar(sel) {
    var lid = sel.getAttribute('data-disc');
    var box = document.querySelector('[data-appr-for="' + lid + '"]');
    if (!box) return;
    var why = requiere(sel);
    box.hidden = !why;
    box.setAttribute('data-appr-required', why ? '1' : '0');
    var m = box.querySelector('[data-appr-msg]');
    if (m) m.textContent = why ? why + '. Registra quién lo aprobó antes de guardar la matrícula.' : '';
  }

  function pendientes() {
    return [].filter.call(document.querySelectorAll('[data-appr-required="1"]'), function (box) {
      var s = box.querySelector('select');
      return !box.hidden && s && s.selectedIndex <= 0;
    });
  }

  function init() {
    document.querySelectorAll('select[data-disc]').forEach(function (sel) {
      actualizar(sel);
      sel.addEventListener('change', function () { actualizar(sel); });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();

  // En captura: se ejecuta antes que el diálogo de confirmación de la página
  document.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('[data-action]') : null;
    if (!b || !/^(Confirmar matrícula|Matricular y facturar|Matricular sin facturar)/.test(b.textContent.trim())) return;
    var p = pendientes();
    if (!p.length) return;
    e.preventDefault(); e.stopImmediatePropagation();
    p[0].scrollIntoView({ block: 'center', behavior: 'smooth' });
    var s = p[0].querySelector('select'); if (s) s.focus();
    p[0].classList.add('is-missing');
    toast('Falta registrar quién aprobó el descuento para guardar la matrícula');
  }, true);

  document.addEventListener('change', function (e) {
    var box = e.target.closest ? e.target.closest('[data-appr-for]') : null;
    if (box && e.target.tagName === 'SELECT' && e.target.selectedIndex > 0) box.classList.remove('is-missing');
  });
})();
