/* Mejoras de la matrícula y la ficha (prototipo): copiar datos del estudiante a la factura, estado por tiempo sin matrícula,
   aceptación de términos con fecha y hora, y cambio del canal de contacto con historial. Sin dependencias. */
(function () {
  if (window.__matricula) return;
  window.__matricula = true;

  function toast(m) {
    var t = document.getElementById('wf-toast');
    if (!t) return;
    t.textContent = m; t.style.display = 'block';
    setTimeout(function () { t.style.display = 'none'; }, 3200);
  }
  function campo(txt) {
    var ls = document.querySelectorAll('label');
    for (var i = 0; i < ls.length; i++) {
      if (ls[i].textContent.trim().toLowerCase().indexOf(txt.toLowerCase()) === 0 && ls[i].htmlFor) return document.getElementById(ls[i].htmlFor);
    }
    return null;
  }
  function ahora() {
    var d = new Date(), m = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'][d.getMonth()];
    return d.getDate() + ' ' + m + ' ' + d.getFullYear() + ' · ' + ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2);
  }

  /* 1. Usar los datos del estudiante en la factura */
  var EST = { 'Nombre o razón social': 'María Andrade', 'Número de identificación': '1712345678', 'Correo para la factura': 'maria.andrade@ejemplo.com', 'Dirección': 'Quito · La Carolina', 'Teléfono de la factura': '099 000 0001' };

  /* 2. Estado según el tiempo sin matrícula */
  function estado() {
    var s = campo('Tiempo sin matrícula'), out = document.querySelector('[data-estado-out]'), cl = campo('Clasificación');
    if (!s || !out) return;
    var v = s.selectedIndex, txt, cls, clas;
    if (v === 0) { txt = 'Paga la inscripción y rinde el test de ubicación.'; cls = 'badge-navy'; clas = 'Nueva'; }
    else if (v <= 2) { txt = 'Continúa con su nivel, sin test y sin inscripción.'; cls = 'badge-ok'; clas = 'Continuidad'; }
    else if (v <= 4) { txt = '3 a 5 meses sin matrícula: mantiene su continuidad. Solo vuelve a rendir el test y no paga inscripción.'; cls = 'badge-warn'; clas = 'Reingreso (exestudiante)'; }
    else { txt = '6 meses o más sin matrícula: el sistema lo trata como estudiante nuevo, paga la inscripción y rinde el test.'; cls = 'badge-bad'; clas = 'Nueva'; }
    out.innerHTML = '<span class="badge ' + cls + '">' + (v === 0 ? 'Nuevo' : v <= 2 ? 'Activo' : v <= 4 ? 'Inactivo' : 'Nuevo por ausencia') + '</span> ' + txt;
    if (cl) { for (var i = 0; i < cl.options.length; i++) if (cl.options[i].text === clas) cl.selectedIndex = i; }
  }

  document.addEventListener('change', function (e) {
    var t = e.target;
    if (t.matches && t.matches('[data-acepta]')) {
      var o = document.querySelector('[data-acepta-out]');
      if (o) o.textContent = t.checked ? 'Aceptado el ' + ahora() + ' · enlace enviado a maria.andrade@ejemplo.com · IP y dispositivo guardados con el comprobante' : 'Sin aceptación: no se puede confirmar la matrícula por canales digitales';
    }
    if (t.tagName === 'SELECT') {
      var lab = t.id && document.querySelector('label[for="' + t.id + '"]');
      var tx = lab ? lab.textContent.trim() : '';
      if (/^Tiempo sin matrícula/i.test(tx)) estado();
      if (/^Canal de contacto \(editable\)/i.test(tx)) {
        var log = document.querySelector('[data-canal-log]');
        if (log) { log.hidden = false; log.textContent = 'Canal cambiado a «' + t.value + '» · ' + ahora() + ' · Carla M. · el cambio queda en el historial y el reporte de orígenes se actualiza'; }
        toast('Canal actualizado: queda registrado en el historial');
      }
    }
  });

  document.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('[data-copy-est]') : null;
    if (!b) return;
    Object.keys(EST).forEach(function (k) { var i = campo(k); if (i) { i.value = EST[k]; i.dispatchEvent(new Event('input', { bubbles: true })); } });
    var o = document.querySelector('[data-copy-out]'); if (o) o.textContent = 'Datos copiados desde la ficha del estudiante. Puedes editarlos si la factura va a otra persona.';
    toast('Datos del estudiante copiados a la factura');
  });

  /* 3. Plazo de crédito editable (paso 4): días entre cuotas y número de cuotas, con aviso si pasa de 30 días */
  var PLANES = { 'Contado': [1, 0], '2 cuotas · cada 15 días': [2, 15], '2 cuotas · cada 30 días': [2, 30], '3 cuotas · cada 30 días': [3, 30] };
  function dias(f, n) { var d = new Date(); d.setDate(d.getDate() + f * n); var m = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'][d.getMonth()]; return d.getDate() + ' ' + m + ' ' + d.getFullYear(); }
  function credito(origen) {
    var plan = campo('Plan de pago'), dd = campo('Días entre cuotas'), nn = campo('Número de cuotas'), out = document.querySelector('[data-credito-out]');
    if (!plan || !dd || !nn || !out) return;
    if (origen === 'plan' && PLANES[plan.value]) { nn.value = PLANES[plan.value][0]; dd.value = PLANES[plan.value][1]; }
    else if (origen === 'dias' || origen === 'n') { for (var i = 0; i < plan.options.length; i++) if (/^Personalizado/.test(plan.options[i].text)) plan.selectedIndex = i; }
    var d = +dd.value || 0, n = Math.max(1, Math.min(12, +nn.value || 1));
    var totalEl = document.querySelector('[data-total-for="lgv"]'), total = totalEl ? parseFloat(totalEl.textContent.replace(/[^\d.]/g, '')) || 980 : 980;
    var cr = campo('Crédito'); if (cr) cr.value = n > 1 ? 'Sí · ' + d + ' días entre cuotas' : 'No · contado';
    var aviso = '', cls = 'is-ok';
    if (n > 1 && d < 15) { aviso = 'El mínimo entre cuotas es 15 días.'; cls = 'is-bad'; }
    else if (d > 60) { aviso = 'El máximo es 60 días entre cuotas; por encima necesita aprobación de Dirección Comercial.'; cls = 'is-bad'; }
    else if (d > 30) { aviso = 'Más de 30 días: solo con convenio de crédito (por ejemplo, la empresa del paso 1, como Farma que pide hasta 2 meses).'; cls = 'is-warn'; }
    var porCuota = (total / n).toFixed(2), fechas = [];
    for (var k = 0; k < n; k++) fechas.push(dias(k, d));
    out.className = 'plan-nota ' + cls;
    out.textContent = n + (n === 1 ? ' pago' : ' cuotas') + ' de $' + porCuota + ' · vencen ' + fechas.join(', ') + (aviso ? ' · ' + aviso : '');
  }
  document.addEventListener('change', function (e) {
    var t = e.target; if (t.tagName !== 'SELECT' && t.tagName !== 'INPUT') return;
    var lab = t.id && document.querySelector('label[for="' + t.id + '"]'), tx = lab ? lab.textContent.trim() : '';
    if (/^Plan de pago/i.test(tx)) credito('plan');
    if (/^Días entre cuotas/i.test(tx)) credito('dias');
    if (/^Número de cuotas/i.test(tx)) credito('n');
  });
  document.addEventListener('input', function (e) {
    var t = e.target, lab = t.id && document.querySelector('label[for="' + t.id + '"]'), tx = lab ? lab.textContent.trim() : '';
    if (/^Días entre cuotas/i.test(tx)) credito('dias');
    if (/^Número de cuotas/i.test(tx)) credito('n');
    // 4. Nombres y apellidos de la ficha: siempre en mayúsculas
    if (t.tagName === 'INPUT' && /^(Nombres|Apellidos)/i.test(tx)) { var p = t.selectionStart; t.value = t.value.toLocaleUpperCase('es'); try { t.setSelectionRange(p, p); } catch (_) {} }
    if (t.classList && t.classList.contains('is-invalid')) t.classList.remove('is-invalid');
  });

  /* 5. Campos obligatorios de la ficha: no deja guardar si falta alguno */
  var OBLIG = ['Nombres', 'Apellidos', 'Cédula / ID', 'Fecha de nacimiento', 'Ocupación', 'Lugar de estudio o trabajo', 'Provincia', 'Cantón', 'Parroquia', 'Calle principal', 'Calle secundaria', 'Email', 'Teléfono'];
  document.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('a,button') : null; if (!b || !campo('Calle secundaria') || !campo('Cédula / ID')) return;
    if (!/^(Guardar estudiante|Guardar y matricular)/i.test(b.textContent.trim())) return;
    var faltan = [];
    OBLIG.forEach(function (n) {
      var i = campo(n); if (!i) return;
      var v = (i.value || '').trim(), mal = !v || /^Otra parroquia/.test(v);
      if (n === 'Cédula / ID' && v && !/^\d{10}$/.test(v) && !/^[A-Za-z0-9]{6,}$/.test(v)) mal = true;
      i.classList.toggle('is-invalid', mal); if (mal) faltan.push(n);
    });
    if (faltan.length) {
      e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
      toast('Faltan datos obligatorios: ' + faltan.join(', '));
      var f = document.querySelector('.is-invalid'); if (f) f.focus();
    }
  }, true);

  function init() { estado(); credito(''); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  setTimeout(init, 500);
})();
