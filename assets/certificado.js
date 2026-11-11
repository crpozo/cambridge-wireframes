/* Entrega de un certificado internacional (prototipo): la identificación del candidato (foto o PDF) es obligatoria
   y reemplaza la fotocopia. Sin ella no se puede confirmar la entrega. Sin dependencias. */
(function () {
  if (window.__cert) return;
  window.__cert = true;

  var KEY = 'wf-cert-doc';
  var estado = { ok: false };

  function toast(m) {
    var t = document.getElementById('wf-toast');
    if (!t) return;
    t.textContent = m; t.style.display = 'block';
    setTimeout(function () { t.style.display = 'none'; }, 3400);
  }
  function box() { return document.querySelector('[data-cert-doc]'); }
  function guardar(k, v) { try { if (v) localStorage.setItem(k, v); else localStorage.removeItem(k); } catch (e) {} }

  document.addEventListener('change', function (e) {
    var b = box();
    if (!b || !e.target.matches || !e.target.matches('[data-cert-doc] input[type=file]')) return;
    var f = e.target.files && e.target.files[0];
    var st = b.querySelector('[data-doc-status]');
    var esImg = f && /^image\//.test(f.type), esPdf = f && (/pdf$/i.test(f.type) || /\.pdf$/i.test(f.name));
    estado.ok = !!(esImg || esPdf);
    b.classList.toggle('is-ok', estado.ok); b.classList.remove('is-missing');
    if (st) {
      st.innerHTML = !f ? '<b>Falta la identificación del candidato</b><span>Cédula o pasaporte, en foto o PDF</span>'
        : (estado.ok ? '<b>Identificación adjunta: ' + f.name.replace(/</g, '') + '</b><span>Se archiva con el acta en el expediente del candidato</span>'
                     : '<b>El archivo debe ser una foto o un PDF</b><span>' + f.name.replace(/</g, '') + ' no es válido</span>');
    }
    // Guarda una vista previa (solo si es una imagen liviana) para mostrarla en el acta de ejemplo
    if (esImg && f.size < 900000) { var r = new FileReader(); r.onload = function () { guardar(KEY, r.result); }; r.readAsDataURL(f); }
    else guardar(KEY, null);
  });

  // En captura: se ejecuta antes que el botón de confirmar de la entrega
  document.addEventListener('click', function (e) {
    var c = e.target.closest ? e.target.closest('[data-sig-confirm]') : null;
    if (!c || !box()) return;
    if (!estado.ok) {
      e.preventDefault(); e.stopImmediatePropagation();
      box().classList.add('is-missing'); box().scrollIntoView({ block: 'center', behavior: 'smooth' });
      toast('Falta la identificación del candidato: sin ella no se puede entregar el certificado');
    }
  }, true);

  // Acta: muestra la identificación adjunta si existe
  function init() {
    var d = null; try { d = localStorage.getItem(KEY); } catch (e) {}
    document.querySelectorAll('[data-cert-doc-img]').forEach(function (img) { if (d) img.src = d; });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
