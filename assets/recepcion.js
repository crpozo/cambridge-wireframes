/* Recepción de un pedido al proveedor (prototipo): cuenta lo recibido contra lo pedido, marca cada ítem
   como completo, faltante o sobrante y solo deja marcar el pedido como recibido si está completo. */
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

  function sumar(isbn) {
    var fila = inputs().filter(function (i) { return i.getAttribute('data-isbn') === isbn; })[0];
    if (!fila) { toast('Ese ISBN no está en este pedido'); return; }
    var p = +fila.getAttribute('data-pedido'), r = (+fila.value || 0) + 1;
    fila.value = r; calc();
    toast((fila.getAttribute('data-nombre') || isbn) + ': ' + r + ' de ' + p);
  }

  document.addEventListener('click', function (e) {
    var sim = e.target.closest ? e.target.closest('[data-rec-scan-btn]') : null;
    if (sim) {
      var pend = inputs().filter(function (i) { return (+i.value || 0) < +i.getAttribute('data-pedido'); })[0];
      var inp = document.querySelector('[data-rec-scan]');
      var isbn = pend ? pend.getAttribute('data-isbn') : (inputs()[0] || {}).getAttribute('data-isbn');
      if (inp) inp.value = isbn;
      sumar(isbn); return;
    }
    var c = e.target.closest ? e.target.closest('[data-rec-confirm]') : null;
    if (c) {
      if (!window.__recOk) { toast(window.__recFalta ? 'Faltan ' + window.__recFalta + ' libros para marcar el pedido como recibido' : 'Hay libros de más: revisa el conteo'); return; }
      toast('Pedido recibido: el stock se actualizó y los libros se asignaron a sus entregas');
      setTimeout(function () { location.href = c.getAttribute('data-next') || 'Movimientos.html'; }, 1100);
    }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && e.target.matches && e.target.matches('[data-rec-scan]')) {
      e.preventDefault(); var v = e.target.value.trim(); if (v) { sumar(v); e.target.value = ''; }
    }
  });

  function init() { calc(); setTimeout(calc, 400); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
