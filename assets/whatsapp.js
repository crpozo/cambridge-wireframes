/* Simulación del canal de WhatsApp (propuesta fuera del alcance): muestra cómo se vería el envío con una API de WhatsApp Business.
   No se conecta a nada: el chat, los estados y el registro son de ejemplo. Sin dependencias. */
(function () {
  if (window.__whatsapp) return;
  window.__whatsapp = true;
  var EST = {
    'María Andrade': { nombre: 'María', curso: 'English for Adults B1 Virtual', horario: 'Lu-Ma-Mi-Ju 19:00–21:00', fecha: '3 nov', hora: '19:00', aula: 'Zoom 2', contacto: 'secretaria@cambridge.example', siguiente: 'Módulo 8 · B1', enlace: 'cambridge.example/rematricula', saldo: '$490', cel: '+593 99 000 0001' },
    'Pedro Mora': { nombre: 'Pedro', curso: 'English for Adults B1+ Sábados', horario: 'Sábados 09:00–13:00', fecha: '14 nov', hora: '09:00', aula: 'Aula 3 · Valle', contacto: 'valle@cambridge.example', siguiente: 'Módulo 10 · B1+', enlace: 'cambridge.example/rematricula', saldo: '$250', cel: '+593 99 000 0002' }
  };
  var PLAN = {
    'Bienvenida al matricularse': '¡Hola {nombre}! Bienvenido(a) a Cambridge. Te matriculaste en {curso}. Horario: {horario}. Inicia el {fecha}. Si tienes dudas escribe a {contacto}.',
    'Mensaje de apertura (48 h antes)': 'Hola {nombre}, mañana empieza {curso} a las {hora}. Ya te agregamos al grupo de tu clase. Tu enlace o aula: {aula}. Recuerda tu libro y tu licencia digital.',
    'Fin de módulo': 'Hola {nombre}, terminaste {curso}. Tu siguiente módulo es {siguiente} y empieza el {fecha}. Puedes matricularte aquí: {enlace}.',
    'Cuota por vencer': 'Hola {nombre}, te recordamos que tu cuota de {saldo} vence el {fecha}. Puedes pagar por transferencia o con el link de pago. Gracias.'
  };
  function q(s) { return document.querySelector(s); }
  function hora() { var d = new Date(); return ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2); }
  function llenar(t, e) { return t.replace(/\{(\w+)\}/g, function (_, k) { return e[k] || '{' + k + '}'; }); }
  var chat = q('[data-wa-chat]'); if (!chat) return;
  var n = 0;

  function estado(el, txt) { el.querySelector('[data-wa-st]').textContent = txt; }
  function agregarLog(e, plantilla, st) {
    var tb = q('[data-wa-log]'); if (!tb) return null;
    var li = document.createElement('li'); li.className = 'is-done';
    li.innerHTML = '<span class="p-t"></span><span class="p-d"></span>';
    li.querySelector('.p-t').textContent = plantilla + ' · ' + e.nombre + ' (' + e.cel + ')';
    li.querySelector('.p-d').textContent = hora() + ' · ' + st;
    tb.insertBefore(li, tb.firstChild); return li;
  }
  function enviar() {
    var e = EST[q('[data-wa-est]').value], p = q('[data-wa-plan]').value, txt = llenar(PLAN[p], e);
    n++;
    var b = document.createElement('div'); b.className = 'wa-msg wa-out';
    b.innerHTML = '<p></p><small><span>' + hora() + '</span> · <span data-wa-st>Enviando…</span></small>';
    b.querySelector('p').textContent = txt;
    chat.appendChild(b); chat.scrollTop = chat.scrollHeight;
    var li = agregarLog(e, p, 'enviando a la API');
    var set = function (s) { estado(b, s); if (li) li.querySelector('.p-d').textContent = hora() + ' · ' + s; };
    setTimeout(function () { set('Enviado'); }, 600);
    setTimeout(function () { set('Entregado'); }, 1500);
    setTimeout(function () { set('Leído'); b.classList.add('is-read'); }, 2800);
    setTimeout(function () {
      var r = document.createElement('div'); r.className = 'wa-msg wa-in';
      r.innerHTML = '<p></p><small>' + hora() + '</small>';
      r.querySelector('p').textContent = /Fin de módulo/.test(p) ? 'Gracias, quiero matricularme al siguiente' : (/Cuota/.test(p) ? 'Listo, pago hoy' : 'Gracias, nos vemos en clase');
      chat.appendChild(r); chat.scrollTop = chat.scrollHeight;
      var c = q('[data-wa-resp]'); if (c) c.textContent = String((+c.textContent || 0) + 1);
    }, 4200);
    var s = q('[data-wa-sent]'); if (s) s.textContent = String((+s.textContent || 0) + 1);
  }
  function vista() {
    var e = EST[q('[data-wa-est]').value], p = q('[data-wa-plan]').value, v = q('[data-wa-prev]');
    if (v) v.textContent = llenar(PLAN[p], e);
  }
  document.addEventListener('click', function (ev) {
    if (ev.target.closest && ev.target.closest('[data-wa-send]')) enviar();
    if (ev.target.closest && ev.target.closest('[data-wa-clear]')) { chat.innerHTML = ''; }
  });
  document.addEventListener('change', function (ev) { if (ev.target.matches && ev.target.matches('[data-wa-est],[data-wa-plan]')) vista(); });
  vista();
})();
