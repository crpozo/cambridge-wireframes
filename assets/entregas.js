/* Entrega digital de libros (prototipo): firma en canvas, firma por QR simulada, validaciones y recibo.
   Sin dependencias. Guarda la firma en localStorage solo para que el recibo de ejemplo la muestre. */
(function () {
  var KEY = 'wf-entrega-firma';
  function toast(m) {
    var t = document.getElementById('wf-toast');
    if (!t) return;
    t.textContent = m; t.style.display = 'block';
    setTimeout(function () { t.style.display = 'none'; }, 2600);
  }
  function save(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function load(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }

  // Firma de ejemplo que "llega" del celular (trazo vectorial)
  var QR_SIGN = 'data:image/svg+xml;utf8,' + encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 90"><path d="M14 60 C 30 12, 50 10, 60 54 S 94 86, 114 36 S 152 12, 166 48 S 198 64, 226 28" fill="none" stroke="#16181D" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>');

  var CANAL = 'wf-entrega-canal';
  var CORREO = 'maria.andrade@ejemplo.com', CEL = '099 000 0001';
  var texto = {
    'Correo': { resumen: 'por correo · ' + CORREO, titulo: 'Enviado por correo', detalle: CORREO + ' · 10:42' },
    'WhatsApp': { resumen: 'por WhatsApp · ' + CEL + ' (propuesta)', titulo: 'Enviado por WhatsApp (propuesta)', detalle: CEL + ' · 10:42' },
    'Correo y WhatsApp': { resumen: 'por correo y por WhatsApp (propuesta)', titulo: 'Enviado por correo y WhatsApp', detalle: CORREO + ' y ' + CEL + ' · 10:42' }
  };
  function setText(sel, v) { document.querySelectorAll(sel).forEach(function (e) { e.textContent = v; }); }
  function canalActual() {
    var r = document.querySelector('[data-canal-wrap] [role=radio][aria-checked=true]');
    return r ? r.textContent.trim() : 'Correo';
  }
  document.addEventListener('click', function (e) {
    var r = e.target.closest ? e.target.closest('[data-canal-wrap] [role=radio]') : null;
    if (r) setText('[data-canal-resumen]', (texto[r.textContent.trim()] || texto['Correo']).resumen);
  });
  // Recibo y ficha: reflejan el canal elegido al confirmar
  var elegido = load(CANAL);
  if (elegido && texto[elegido]) {
    setText('[data-canal-titulo]', texto[elegido].titulo);
    setText('[data-canal-detalle]', texto[elegido].detalle);
    setText('[data-recibo-canal]', elegido);
  }

  var pad = document.querySelector('[data-sigpad]');
  var state = { signed: false, via: null, data: null };

  function setStatus(msg, ok) {
    document.querySelectorAll('[data-sig-status]').forEach(function (s) {
      s.textContent = msg; s.classList.toggle('is-ok', !!ok);
    });
  }

  if (pad) {
    var cv = pad.querySelector('canvas'), ctx = cv.getContext('2d'), drawing = false, fitted = false;
    var fit = function () {
      var r = cv.getBoundingClientRect(), d = window.devicePixelRatio || 1;
      if (!r.width) return;
      cv.width = Math.round(r.width * d); cv.height = Math.round(r.height * d);
      ctx.setTransform(d, 0, 0, d, 0, 0);
      ctx.lineWidth = 2.6; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.strokeStyle = '#16181D';
      fitted = true;
    };
    var pos = function (e) { var r = cv.getBoundingClientRect(); return { x: e.clientX - r.left, y: e.clientY - r.top }; };
    cv.addEventListener('pointerdown', function (e) {
      if (!fitted) fit();
      drawing = true; try { cv.setPointerCapture(e.pointerId); } catch (x) {}
      var p = pos(e); ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(p.x + .1, p.y + .1); ctx.stroke(); e.preventDefault();
    });
    cv.addEventListener('pointermove', function (e) {
      if (!drawing) return;
      var p = pos(e); ctx.lineTo(p.x, p.y); ctx.stroke(); e.preventDefault();
    });
    var end = function () {
      if (!drawing) return; drawing = false;
      state.signed = true; state.via = 'tablet'; state.data = cv.toDataURL('image/png');
      pad.classList.add('is-signed'); setStatus('Firma capturada en esta tablet', true);
    };
    ['pointerup', 'pointercancel', 'pointerleave'].forEach(function (n) { cv.addEventListener(n, end); });
    window.addEventListener('resize', function () { if (!state.signed) fitted = false; });
    document.querySelectorAll('[data-sig-clear]').forEach(function (b) {
      b.addEventListener('click', function () {
        if (!fitted) fit();
        ctx.clearRect(0, 0, cv.width, cv.height);
        state = { signed: false, via: null, data: null };
        pad.classList.remove('is-signed'); setStatus('Sin firma todavía', false);
      });
    });
  }

  // Firma desde el celular (QR) simulada
  document.querySelectorAll('[data-qr-sim]').forEach(function (b) {
    b.addEventListener('click', function () {
      state = { signed: true, via: 'celular', data: QR_SIGN };
      var q = document.querySelector('[data-qr-status]');
      if (q) { q.textContent = 'Firma recibida desde el celular · 10:42'; q.classList.add('is-ok'); }
      setStatus('Firma recibida desde el celular', true);
      toast('Firma recibida desde el celular del estudiante');
    });
  });

  // Escáner de código de barras simulado
  document.querySelectorAll('[data-scan]').forEach(function (b) {
    b.addEventListener('click', function () {
      var i = document.querySelector('[data-scan-input]');
      if (i) i.value = '9781108961516';
      toast('Libro identificado: Empower B1 Combo A. Coincide con la entrega EN-2026-0431');
    });
  });

  // Confirmar entrega
  // Delegado: el botón vive en el pie de página, que se dibuja después de este script
  document.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('[data-sig-confirm]') : null;
    if (!b) return;
    var falta = [];
    var ok = true; document.querySelectorAll('[data-check]').forEach(function (c) { if (!c.checked) ok = false; });
    if (!ok) falta.push('revisar el libro');
    if (!state.signed) falta.push('la firma');
    if (falta.length) { toast('Falta ' + falta.join(' y ') + ' para confirmar la entrega'); return; }
    save(KEY, state.data); save(KEY + '-via', state.via || ''); save(CANAL, canalActual());
    var sg = document.querySelector('[data-signer-wrap] select');
    save(KEY + '-por', sg ? sg.value : '');
    location.href = b.getAttribute('data-next') || 'ReciboEntrega.html';
  });

  // Recibo: muestra la firma capturada si existe
  document.querySelectorAll('[data-sig-img]').forEach(function (img) {
    var d = load(KEY); if (d) img.src = d;
    var via = load(KEY + '-via'), por = load(KEY + '-por');
    var v = document.querySelector('[data-sig-via]');
    if (v && via) v.textContent = via === 'celular' ? 'Firmado desde el celular del estudiante' : 'Firmado en la tablet de la sede';
    var p = document.querySelector('[data-sig-por]');
    if (p && por) p.textContent = por;
  });
})();
