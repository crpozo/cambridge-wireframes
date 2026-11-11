/* Inscripción a un examen internacional (prototipo): la cédula del candidato en PDF es obligatoria.
   Sin ella no se puede inscribir, aunque el pago ya esté hecho; se puede guardar como pendiente. Sin dependencias. */
(function () {
  if (window.__examenDoc) return;
  window.__examenDoc = true;

  function toast(m) {
    var t = document.getElementById('wf-toast');
    if (!t) return;
    t.textContent = m; t.style.display = 'block';
    setTimeout(function () { t.style.display = 'none'; }, 3400);
  }
  var box = function () { return document.querySelector('[data-exam-doc]'); };
  var estado = { ok: false };

  document.addEventListener('change', function (e) {
    var b = box();
    if (!b || !e.target.matches || !e.target.matches('[data-exam-doc] input[type=file]')) return;
    var f = e.target.files && e.target.files[0];
    var st = b.querySelector('[data-doc-status]');
    var esPdf = f && (/pdf$/i.test(f.type) || /\.pdf$/i.test(f.name));
    estado.ok = !!esPdf;
    b.classList.toggle('is-ok', !!esPdf); b.classList.remove('is-missing');
    if (st) {
      st.innerHTML = f
        ? (esPdf ? '<b>Cédula adjunta: ' + f.name.replace(/</g, '') + '</b><span>Lista para contrastar con nombres y fecha de nacimiento</span>'
                 : '<b>El archivo debe ser un PDF</b><span>' + f.name.replace(/</g, '') + ' no es un PDF</span>')
        : '<b>Falta el PDF de la cédula</b><span>Se contrasta con los nombres y la fecha de nacimiento</span>';
    }
  });

  document.addEventListener('click', function (e) {
    var s = e.target.closest ? e.target.closest('[data-exam-submit]') : null;
    if (!s) return;
    var b = box();
    if (!estado.ok) {
      e.preventDefault();
      if (b) { b.classList.add('is-missing'); b.scrollIntoView({ block: 'center', behavior: 'smooth' }); }
      toast('Falta el PDF de la cédula: sin él no se puede registrar el examen. Puedes guardarlo como pendiente de cédula.');
      return;
    }
    toast('Candidato inscrito: factura, datos y cédula completos');
    setTimeout(function () { location.href = s.getAttribute('data-next') || 'ExamenesInternacionales.html'; }, 1000);
  });
})();
