/* Cambio de curso, horario o modalidad (prototipo): la matrícula se conserva; según la clasificación, el avance del curso y el tipo de cambio
   se decide quién lo autoriza (Comercial o Académico), quién mueve al estudiante y quién emite la nota de crédito. Sin dependencias. */
(function () {
  if (window.__cambio) return;
  window.__cambio = true;
  var form = document.querySelector('[data-cambio]'); if (!form) return;
  var ACTUAL = { modalidad: 'Virtual', precio: 250 };
  var COMERCIAL = ['ASE', 'SUC', 'ADM', 'DIR', 'GER'], ACADEMICO = ['COO', 'ADM', 'GER', 'DIR'];
  function q(s) { return document.querySelector(s); }
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
  function rol() { var r = document.getElementById('rol'); return r ? r.value : 'ADM'; }
  function toast(m) { var t = document.getElementById('wf-toast'); if (!t) return; t.textContent = m; t.style.display = 'block'; setTimeout(function () { t.style.display = 'none'; }, 3400); }
  function ahora() {
    var d = new Date(), m = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'][d.getMonth()];
    return d.getDate() + ' ' + m + ' ' + d.getFullYear() + ' · ' + ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2);
  }
  var NOMBRE = { ASE: 'Asesor', SUC: 'Administración de sucursal', ADM: 'Administrador', DIR: 'Dirección Comercial', GER: 'Gerencia', COO: 'Coordinación Académica', SEC: 'Secretaría', PRO: 'Profesor', CON: 'Contabilidad' };

  function estado() {
    var opt = q('[data-cb-curso]').selectedOptions[0];
    var nuevo = { modalidad: opt.getAttribute('data-mod'), diff: +opt.getAttribute('data-diff'), texto: opt.value };
    var avance = q('[data-cb-avance]').selectedIndex, clas = q('[data-cb-clas]').value;
    var cambiaMod = nuevo.modalidad !== ACTUAL.modalidad;
    var iniciado = avance > 0;
    var comercial = clas === 'Nueva' && !iniciado;
    var decide = comercial ? 'Comercial' : 'Académico';
    var motivoDecide = comercial ? 'El estudiante es nuevo y el curso no ha iniciado: Comercial puede gestionarlo.'
      : (!iniciado ? 'El estudiante no es nuevo: lo autoriza Académico.' : (avance === 3 ? 'El curso ya avanzó 80 % o más: lo autoriza solo Académico, con su justificación.' : 'El curso ya inició: lo autoriza Académico, con su justificación.'));
    var nc = cambiaMod || nuevo.diff !== 0;
    return { nuevo: nuevo, cambiaMod: cambiaMod, decide: decide, motivoDecide: motivoDecide, nc: nc, avance: avance, clas: clas };
  }

  function pintar() {
    var s = estado();
    q('[data-cb-tipo]').innerHTML = '<span class="badge badge-' + (s.cambiaMod ? 'warn' : 'navy') + '">' + (s.cambiaMod ? 'Cambio de modalidad: Virtual → ' + s.nuevo.modalidad : 'Cambio de horario o de curso (misma modalidad)') + '</span>';
    q('[data-cb-decide]').innerHTML = '<span class="badge badge-' + (s.decide === 'Comercial' ? 'ok' : 'navy') + '">Lo autoriza ' + s.decide + '</span> <span>' + esc(s.motivoDecide) + '</span>';
    q('[data-cb-mueve]').textContent = 'Académico (Coordinación) mueve al estudiante al nuevo grupo y actualiza la asistencia.';
    q('[data-cb-nc]').innerHTML = s.nc ? 'Facturación (Secretaría) emite la nota de crédito y la refactura' + (s.nuevo.diff ? ' por la diferencia de <b>' + (s.nuevo.diff > 0 ? '+' : '-') + '$' + Math.abs(s.nuevo.diff) + '</b>' : '') + '. <a href="NotaCredito.html">Ir a Nota de crédito</a>' : 'No hace falta nota de crédito: el precio no cambia y la modalidad es la misma.';
    q('[data-cb-justif]').hidden = s.decide !== 'Académico';
    q('[data-cb-ant]').textContent = 'Virtual · Lu-Ma-Mi-Ju 19:00–21:00 · 0001-2026-0767';
    q('[data-cb-des]').textContent = s.nuevo.texto;
    var roles = s.decide === 'Comercial' ? COMERCIAL : ACADEMICO, ok = roles.indexOf(rol()) >= 0;
    var b = q('[data-cb-aprobar]'); b.setAttribute('aria-disabled', ok ? 'false' : 'true');
    b.title = ok ? '' : 'Con tu rol no puedes autorizar este cambio';
    q('[data-cb-rol]').textContent = ok ? 'Entraste como ' + (NOMBRE[rol()] || rol()) + ': puedes autorizar este cambio.' : 'Entraste como ' + (NOMBRE[rol()] || rol()) + ': este cambio lo autoriza ' + (s.decide === 'Académico' ? 'Coordinación Académica' : 'Comercial') + '. Usa "Ver como" en el menú de usuario para probarlo.';
  }

  document.addEventListener('change', function (e) { if (e.target.matches && (e.target.matches('[data-cambio] select') || e.target.id === 'rol')) pintar(); });
  document.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('[data-cb-aprobar]') : null; if (!b) return;
    if (b.getAttribute('aria-disabled') === 'true') { toast('Con tu rol no puedes autorizar este cambio; lo hace ' + (estado().decide === 'Académico' ? 'Coordinación Académica' : 'Comercial')); return; }
    var s = estado();
    if (s.decide === 'Académico') { var j = q('[data-cb-justif] textarea'); if (!j.value.trim()) { j.classList.add('is-invalid'); j.focus(); toast('Escribe la justificación académica'); return; } j.classList.remove('is-invalid'); }
    var li = document.createElement('li'); li.className = 'is-done'; li.innerHTML = '<span class="p-t"></span><span class="p-d"></span>';
    li.querySelector('.p-t').textContent = 'Cambio registrado: ' + s.nuevo.texto;
    li.querySelector('.p-d').textContent = ahora() + ' · ' + (NOMBRE[rol()] || rol()) + ' · matrícula 001-202602794 conservada' + (s.nc ? ' · pendiente nota de crédito' : '');
    var lst = q('[data-cb-hist]'); lst.insertBefore(li, lst.firstChild);
    toast('Cambio registrado: la matrícula se conserva y el reporte de nuevos estudiantes no cambia');
  });
  document.addEventListener('input', function (e) { if (e.target.classList && e.target.classList.contains('is-invalid')) e.target.classList.remove('is-invalid'); });
  function init() { pintar(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  setTimeout(init, 500);
})();
