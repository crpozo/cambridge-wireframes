/* Cierre de caja digital (prototipo): reemplaza imprimir listas y copias para Contabilidad.
   - Cuadre: compara lo del sistema con lo contado y dice si cuadra.
   - Observaciones de Contabilidad: se corrige solo lo observado (no se rehace toda la caja).
   - Reenvío con versión y acuse digital. Sin dependencias. */
(function () {
  if (window.__cierre) return;
  window.__cierre = true;

  function toast(m) {
    var t = document.getElementById('wf-toast');
    if (!t) return;
    t.textContent = m; t.style.display = 'block';
    setTimeout(function () { t.style.display = 'none'; }, 3200);
  }
  function $(n) { return '$' + n.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  function q(s) { return document.querySelector(s); }

  // ---- Cuadre de caja ----
  function cuadre() {
    var sis = 0, con = 0;
    document.querySelectorAll('[data-cuadre-dif]').forEach(function (d) {
      var s = parseFloat(d.getAttribute('data-sis')) || 0;
      var fila = d.closest('.wf-row') || d.parentElement;
      var inp = fila.querySelector('[data-cuadre-in]'), val = fila.querySelector('[data-cuadre-val]');
      var c = inp ? (parseFloat(inp.value) || 0) : (val ? parseFloat(val.getAttribute('data-cuadre-val')) || 0 : 0);
      var dif = Math.round((c - s) * 100) / 100; sis += s; con += c;
      d.textContent = dif === 0 ? 'Cuadra' : (dif > 0 ? 'Sobran ' + $(dif) : 'Faltan ' + $(-dif));
      d.className = 'badge ' + (dif === 0 ? 'badge-ok' : 'badge-bad');
    });
    var r = q('[data-cuadre-res]');
    if (r) {
      var dt = Math.round((con - sis) * 100) / 100;
      r.textContent = dt === 0 ? 'La caja cuadra: ' + $(sis) : 'Diferencia de ' + $(Math.abs(dt)) + ': revísala antes de cerrar';
      r.className = 'cc-res ' + (dt === 0 ? 'is-ok' : 'is-bad');
    }
  }
  document.addEventListener('input', function (e) { if (e.target.matches && e.target.matches('[data-cuadre-in]')) cuadre(); });

  // ---- Observaciones y reenvío ----
  var version = 1;
  function abiertas() { return document.querySelectorAll('[data-obs]:not(.is-done)').length; }
  function log(titulo, detalle) {
    var ol = q('[data-cc-log]'); if (!ol) return;
    var li = document.createElement('li'); li.className = 'is-done';
    li.innerHTML = '<span class="p-t"></span><span class="p-d"></span>';
    li.querySelector('.p-t').textContent = titulo; li.querySelector('.p-d').textContent = detalle;
    ol.insertBefore(li, ol.firstChild);
  }
  function refrescar() {
    var n = abiertas(), tp = window.__tarjPend || 0;
    var c = q('[data-cc-abiertas]'); if (c) c.textContent = n;
    var env = q('[data-cc-enviar]');
    if (env && !env.hasAttribute('data-enviado')) env.setAttribute('aria-disabled', (n || tp) ? 'true' : 'false');
    var est = q('[data-cc-estado]');
    if (est && !q('[data-cc-ver]').hasAttribute('data-enviado')) {
      est.textContent = n ? 'Con observaciones' : (tp ? 'Faltan vouchers de tarjeta' : 'Lista para reenviar');
      est.className = 'badge ' + ((n || tp) ? 'badge-warn' : 'badge-navy');
    }
  }

  document.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target : null; if (!t) return;
    var cor = t.closest('[data-obs-corregir]');
    if (cor) {
      var fila = cor.closest('.wf-row') || cor.parentElement;
      var est = fila.querySelector('[data-obs-estado]'); var ob = fila.querySelector('[data-obs]');
      if (est) { est.textContent = 'Corregida'; est.className = 'badge badge-ok'; }
      if (ob) ob.classList.add('is-done');
      cor.setAttribute('aria-disabled', 'true'); cor.textContent = 'Corregida';
      // La lista de pagos refleja la corrección: el pago observado pasa a conciliado
      document.querySelectorAll('[data-tid="cc_pagos"] .wf-row .badge-bad').forEach(function (b) { b.textContent = 'Conciliado'; b.className = 'badge badge-ok'; });
      var bus = document.querySelector('[data-panel="Lista de pagos"] input[type=search]');
      if (bus) bus.dispatchEvent(new Event('input', { bubbles: true }));
      log('Corregido solo lo observado', 'Secretaría corrigió ' + (fila.getAttribute('data-obs-ref') || 'el ítem') + ' sin rehacer el resto de la caja');
      refrescar(); toast('Corregido: no hace falta rehacer toda la caja');
      return;
    }
    var env = t.closest('[data-cc-enviar]');
    if (env) {
      if (env.getAttribute('aria-disabled') === 'true') { toast(abiertas() ? 'Falta resolver ' + abiertas() + ' observación(es) de Contabilidad' : 'Faltan ' + (window.__tarjPend || 0) + ' vouchers de tarjeta por verificar'); return; }
      version += 1; env.setAttribute('data-enviado', '1');
      var v = q('[data-cc-ver]'); v.textContent = 'v' + version; v.setAttribute('data-enviado', '1');
      var est = q('[data-cc-estado]'); est.textContent = 'Enviada · esperando acuse'; est.className = 'badge badge-navy';
      env.setAttribute('aria-disabled', 'true'); log('Reenviada a Contabilidad (v' + version + ')', 'Solo con la corrección; el resto de la caja no cambió');
      toast('Enviada a Contabilidad: v' + version);
      setTimeout(function () {
        est.textContent = 'Aprobada por Contabilidad'; est.className = 'badge badge-ok';
        var ac = q('[data-cc-acuse]'); if (ac) ac.textContent = '23 oct 18:20 · acuse digital de Contabilidad';
        log('Contabilidad aprobó la caja', 'Acuse digital de recepción: reemplaza la copia que se devolvía firmada');
        toast('Contabilidad aprobó la caja y confirmó la recepción');
      }, 1600);
    }
  });


  // ---- Tarjetas: voucher, referencia y cierre de lote ----
  function vouchers() {
    var pend = 0, sisTotal = 0;
    document.querySelectorAll('[data-vch-res]').forEach(function (rs) {
      var f = rs.closest('.wf-row') || rs.closest('tr') || rs.parentElement.parentElement;
      var sa = f.querySelector('[data-vch-sis-aut]').textContent.trim(), sv = parseFloat(f.querySelector('[data-vch-sis-val]').textContent) || 0;
      var va = (f.querySelector('[data-vch-aut]').value || '').trim(), vv = parseFloat(f.querySelector('[data-vch-val]').value) || 0;
      var adj = f.querySelector('[data-vch-adj]').getAttribute('data-adjunto') === '1';
      var res = f.querySelector('[data-vch-res]'), fix = f.querySelector('[data-vch-fix]');
      var txt, cls, malo = false;
      if (!adj) { txt = 'Falta voucher'; cls = 'badge-warn'; }
      else if (va !== sa) { txt = 'Referencia distinta'; cls = 'badge-bad'; malo = true; }
      else if (Math.abs(vv - sv) > 0.001) { txt = 'Valor distinto'; cls = 'badge-bad'; malo = true; }
      else { txt = 'Coincide'; cls = 'badge-ok'; }
      res.textContent = txt; res.className = 'badge ' + cls;
      if (fix) fix.hidden = !malo;
      if (txt !== 'Coincide') pend++;
      sisTotal += sv;
    });
    var ls = q('[data-lote-sis]'); if (ls) ls.textContent = $(sisTotal);
    var li = q('[data-lote-in]'), ld = q('[data-lote-dif]');
    if (li && ld) {
      var d = Math.round(((parseFloat(li.value) || 0) - sisTotal) * 100) / 100;
      ld.textContent = d === 0 ? 'Cuadra' : (d > 0 ? 'Sobran ' + $(d) : 'Faltan ' + $(-d));
      ld.className = 'badge ' + (d === 0 ? 'badge-ok' : 'badge-bad'); if (d !== 0) pend++;
    }
    var foto = q('[data-lote-adj]'); if (foto && foto.getAttribute('data-adjunto') !== '1') pend++;
    var r = q('[data-vch-resumen]');
    if (r) { r.textContent = pend ? 'Faltan ' + pend + ' por verificar: el cierre no se puede enviar a Contabilidad' : 'Los vouchers y el cierre de lote coinciden: la caja de tarjetas está lista'; r.className = 'cc-res ' + (pend ? 'is-bad' : 'is-ok'); }
    var tab = document.querySelector('[data-tab="Tarjetas y vouchers"]');
    window.__tarjPend = pend; refrescar();
  }
  document.addEventListener('input', function (e) { if (e.target.matches && e.target.matches('[data-vch-aut],[data-vch-val],[data-lote-in]')) vouchers(); });
  document.addEventListener('change', function (e) {
    var f = e.target;
    if (!f.matches || !f.matches('[data-vch-file],[data-lote-file]')) return;
    var fila = f.closest('.wf-row') || f.closest('.card');
    var adj = fila.querySelector('[data-vch-adj],[data-lote-adj]');
    if (adj && f.files && f.files[0]) { adj.textContent = f.files[0].name; adj.setAttribute('data-adjunto', '1'); }
    vouchers();
  });
  document.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('[data-vch-fix]') : null; if (!b) return;
    var f = b.closest('.wf-row');
    f.querySelector('[data-vch-sis-aut]').textContent = f.querySelector('[data-vch-aut]').value.trim();
    f.querySelector('[data-vch-sis-val]').textContent = (parseFloat(f.querySelector('[data-vch-val]').value) || 0).toFixed(2);
    log('Corregida la referencia del voucher', 'El sistema quedó igual al voucher (autorización ' + f.querySelector('[data-vch-aut]').value.trim() + '); la lista de pagos se actualizó sola');
    vouchers(); toast('Corregido en el sistema: ya coincide con el voucher');
  });

  function init() { cuadre(); vouchers(); refrescar(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  setTimeout(init, 500);
})();
