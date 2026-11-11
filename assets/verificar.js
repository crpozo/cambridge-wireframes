/* Verificación de transferencias (prototipo): compara lo registrado en el sistema, la lista de pagos y la confirmación
   de Contabilidad, campo por campo, y deja corregir solo el dato que no coincide. Sin dependencias. */
(function () {
  if (window.__verificar) return;
  window.__verificar = true;

  var node = document.getElementById('vt-data');
  if (!node) return;
  var data = JSON.parse(node.textContent);
  var sel = document.querySelector('[data-vt-select]');

  function toast(m) {
    var t = document.getElementById('wf-toast');
    if (!t) return;
    t.textContent = m; t.style.display = 'block';
    setTimeout(function () { t.style.display = 'none'; }, 3400);
  }
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
  function q(s) { return document.querySelector(s); }

  function campos(d) {
    return [
      ['Número de comprobante', d.sistema, d.lista, d.conf],
      ['Valor', d.valor, d.valor, d.valor],
      ['Fecha', d.fecha, d.fecha, d.conf_fecha],
      ['Banco', d.banco, d.banco, d.banco],
      ['Factura', d.factura, d.factura, d.factura]
    ];
  }
  function coincide(r) { return r[1] === r[2] && r[2] === r[3]; }
  function todoCoincide(d) { return campos(d).every(coincide); }

  function render() {
    var d = data[sel.value]; if (!d) return;
    var filas = campos(d);
    var html = '<div class="vt-row vt-head"><span>Campo</span><span>En el sistema</span><span>En la lista de pagos</span><span>En la confirmación de Contabilidad</span><span>¿Coincide?</span></div>';
    filas.forEach(function (r) {
      var ok = coincide(r);
      html += '<div class="vt-row' + (ok ? '' : ' is-diff') + '"><b>' + esc(r[0]) + '</b><span>' + esc(r[1]) + '</span><span>' + esc(r[2]) + '</span><span>' + esc(r[3]) + '</span><span><span class="badge badge-' + (ok ? 'ok' : 'bad') + '">' + (ok ? 'Coincide' : 'Distinto') + '</span></span></div>';
    });
    q('[data-vt-detalle]').innerHTML = html;
    var ok = todoCoincide(d);
    var res = q('[data-vt-resultado]');
    res.textContent = ok ? 'Todo coincide: el pago queda verificado' : 'Hay diferencias: corrige solo el dato que no coincide';
    res.className = 'cc-res ' + (ok ? 'is-ok' : 'is-bad');
    var btn = q('[data-vt-corregir]');
    btn.setAttribute('aria-disabled', ok ? 'true' : 'false');
    btn.textContent = ok ? 'Sin diferencias' : 'Corregir en el sistema';
    // Vista previa de la confirmación de Contabilidad
    q('[data-vt-mail-factura]').textContent = d.factura;
    q('[data-vt-mail-valor]').textContent = d.valor;
    q('[data-vt-mail-pago]').textContent = 'Transferencia · ' + d.banco;
    q('[data-vt-mail-detalle]').textContent = d.estudiante + ' · ' + d.fecha;
    q('[data-vt-mail-comprobante]').textContent = d.conf;
    q('[data-vt-mail-asunto]').textContent = 'Confirmación de pago · comprobante ' + d.conf;
  }

  function actualizarTabla(id, d) {
    var c = document.querySelector('[data-vt-sis="' + id + '"]'); if (c) c.textContent = d.sistema;
    var r = document.querySelector('[data-vt-res="' + id + '"]');
    if (r) { var ok = todoCoincide(d); r.textContent = ok ? 'Coincide' : 'Diferencia'; r.className = 'badge badge-' + (ok ? 'ok' : 'bad'); }
    var bus = document.querySelector('input[type=search]'); if (bus) bus.dispatchEvent(new Event('input', { bubbles: true }));
  }

  document.addEventListener('change', function (e) { if (e.target === sel) render(); });
  document.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('[data-vt-corregir]') : null; if (!b) return;
    var d = data[sel.value];
    if (b.getAttribute('aria-disabled') === 'true') { toast('Este pago ya coincide en todo'); return; }
    // El número oficial reemplaza al del cliente, que queda como referencia; la fecha toma la de la confirmación
    var ref = d.sistema;
    d.sistema = d.conf; d.lista = d.conf; d.fecha = d.conf_fecha;
    d.referencia = ref;
    render(); actualizarTabla(sel.value, d);
    var li = q('[data-vt-log]');
    if (li) { var x = document.createElement('li'); x.className = 'is-done'; x.innerHTML = '<span class="p-t"></span><span class="p-d"></span>'; x.querySelector('.p-t').textContent = 'Corregido el comprobante de ' + d.estudiante; x.querySelector('.p-d').textContent = 'Número oficial ' + d.conf + ' (referencia del cliente: ' + ref + '). La lista de pagos y el cierre de caja se actualizaron solos.'; li.insertBefore(x, li.firstChild); }
    toast('Corregido: la lista de pagos y el cierre de caja se actualizan solos; no hay que reimprimir nada');
  });

  function init() {
    if (sel) { var idx = [].findIndex ? [].findIndex.call(sel.options, function (o) { return !todoCoincide(data[o.value]); }) : 0; if (idx >= 0) sel.selectedIndex = idx; render(); }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  setTimeout(init, 500);
})();
