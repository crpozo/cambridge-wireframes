/* Recepción de un pedido al proveedor (prototipo): cuenta lo recibido contra lo pedido con botones + y −,
   marca cada ítem como completo, faltante o sobrante y solo deja marcar el pedido como recibido si está completo.
   Los libros no traen código de barras: el conteo es manual. */
(function () {
  if (window.__recepcion) return;
  window.__recepcion = true;

  function toast(m) {
    var t = document.getElementById('wf-toast');
    if (!t) return;
    t.textContent = m; t.style.display = 'block';
    setTimeout(function () { t.style.display = 'none'; }, 3000);
  }
  function inputs() { return [].slice.call(document.querySelectorAll('input[data-rec]')); }

  function calc() {
    var ped = 0, rec = 0, falta = 0, sobra = 0;
    inputs().forEach(function (i) {
      var p = +i.getAttribute('data-pedido'), r = Math.max(+i.value || 0, 0), d = r - p;
      ped += p; rec += r;
      if (d < 0) falta += -d; else if (d > 0) sobra += d;
      var fila = i.closest('.wf-row') || i.closest('tr') || i.parentElement;
      var dif = fila.querySelector('[data-rec-dif]'), est = fila.querySelector('[data-rec-est]');
      if (dif) dif.textContent = d === 0 ? '0' : (d > 0 ? '+' + d : '' + d);
      if (est) {
        est.textContent = d === 0 ? 'Completo' : (d < 0 ? 'Faltan ' + (-d) : 'Sobran ' + d);
        est.className = 'badge ' + (d === 0 ? 'badge-ok' : (d < 0 ? 'badge-warn' : 'badge-bad'));
      }
    });
    var tot = document.querySelector('[data-rec-total]'); if (tot) tot.textContent = 'Recibidos ' + rec + ' de ' + ped;
    var hint = document.querySelector('[data-rec-hint]');
    var ok = falta === 0 && sobra === 0;
    if (hint) hint.textContent = ok ? 'El pedido está completo: ya puedes marcarlo como recibido.' : (falta ? 'Faltan ' + falta + ' libros: el pedido sigue en camino hasta que llegue completo.' : 'Hay ' + sobra + ' libros de más: revisa el conteo o el documento del proveedor.');
    document.querySelectorAll('[data-rec-confirm]').forEach(function (b) {
      b.setAttribute('aria-disabled', ok ? 'false' : 'true');
      b.title = ok ? '' : 'Completa el conteo para marcarlo como recibido';
    });
    window.__recOk = ok; window.__recFalta = falta; window.__recSobra = sobra;
  }

  document.addEventListener('input', function (e) { if (e.target.matches && e.target.matches('input[data-rec]')) calc(); });
  document.addEventListener('change', function (e) { if (e.target.matches && e.target.matches('input[data-rec]')) calc(); });

  function campoDe(btn) { return btn.parentElement.querySelector('input[data-rec]'); }

  document.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target : null; if (!t) return;
    var mas = t.closest('[data-rec-plus]'), menos = t.closest('[data-rec-minus]'), todo = t.closest('[data-rec-all]');
    if (mas || menos) {
      var i = campoDe(mas || menos); if (!i) return;
      i.value = Math.max((+i.value || 0) + (mas ? 1 : -1), 0); calc(); return;
    }
    if (todo) {
      inputs().forEach(function (i) { i.value = i.getAttribute('data-pedido'); });
      calc(); toast('Todo marcado como recibido: revisa que coincida con el documento del proveedor'); return;
    }
    var c = t.closest('[data-rec-confirm]');
    if (c) {
      if (!window.__recOk) { toast(window.__recFalta ? 'Faltan ' + window.__recFalta + ' libros para marcar el pedido como recibido' : 'Hay libros de más: revisa el conteo'); return; }
      toast('Pedido recibido: el stock se actualizó y los libros se asignaron a sus entregas');
      setTimeout(function () { location.href = c.getAttribute('data-next') || 'Movimientos.html'; }, 1100);
    }
  });

  function init() { calc(); var n = 0, iv = setInterval(function () { calc(); if (++n > 12) clearInterval(iv); }, 250); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
