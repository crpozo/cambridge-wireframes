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

  function init() { estado(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  setTimeout(init, 500);
})();
