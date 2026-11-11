/* Envío de facturas a Dora y al SRI (prototipo): cuenta regresiva de la ventana de corrección de 2 horas.
   Al llegar a cero la factura "sale" sola; "Enviar ahora" la adelanta. Sin dependencias. */
(function () {
  if (window.__envios) return;
  window.__envios = true;

  function toast(m) {
    var t = document.getElementById('wf-toast');
    if (!t) return;
    t.textContent = m; t.style.display = 'block';
    setTimeout(function () { t.style.display = 'none'; }, 2800);
  }
  function pad(n) { return ('0' + n).slice(-2); }
  function fmt(s) { return pad(Math.floor(s / 3600)) + ':' + pad(Math.floor((s % 3600) / 60)) + ':' + pad(s % 60); }

  function fila(el) { return el.closest('.wf-row') || el.parentElement; }

  function enviar(el) {
    el.setAttribute('data-cd', '0');
    el.textContent = 'Enviada a Dora · ahora';
    el.classList.add('is-sent');
    var f = fila(el), est = f.querySelector('[data-cd-estado]');
    if (est) { est.textContent = 'Enviada'; est.className = 'badge badge-navy'; }
    f.querySelectorAll('[data-envio-ahora],[data-envio-corregir]').forEach(function (b) { b.setAttribute('aria-disabled', 'true'); });
    actualizarContador();
  }

  function actualizarContador() {
    var n = [].filter.call(document.querySelectorAll('[data-cd]'), function (e) { return (+e.getAttribute('data-cd')) > 0; }).length;
    var c = document.querySelector('[data-cd-total]'); if (c) c.textContent = n;
  }

  setInterval(function () {
    document.querySelectorAll('[data-cd]').forEach(function (el) {
      var s = +el.getAttribute('data-cd'); if (!(s > 0)) return;
      s -= 1; el.setAttribute('data-cd', s);
      if (s <= 0) { enviar(el); toast('Una factura salió sola a Dora al terminar la espera'); }
      else el.textContent = 'Sube en ' + fmt(s);
    });
  }, 1000);

  document.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target : null; if (!t) return;
    var ya = t.closest('[data-envio-ahora]');
    if (ya) {
      if (ya.getAttribute('aria-disabled') === 'true') return;
      var el = fila(ya).querySelector('[data-cd]'); if (el && +el.getAttribute('data-cd') > 0) { enviar(el); toast('Factura enviada ahora a Dora sin esperar las 2 horas'); }
      return;
    }
    var co = t.closest('[data-envio-corregir]');
    if (co) {
      if (co.getAttribute('aria-disabled') === 'true') { toast('Esta factura ya salió: para corregirla se emite una nota de crédito'); e.preventDefault(); return; }
      toast('Dentro de la espera puedes corregir los datos o anular la factura sin dejar rastro en el SRI');
    }
  });

  function init() { actualizarContador(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  setTimeout(init, 500);
})();
