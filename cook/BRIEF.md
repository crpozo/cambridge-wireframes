# Brief: mejora del diseño general del prototipo Cambridge

Target: mejorar el diseño general de la plataforma (85 pantallas generadas por `tools/generar_pantallas.py`) corrigiendo los componentes compartidos, sin cambiar flujos ni contenido. Stack: HTML/CSS/JS estático generado con Python.
References: no references (imágenes). La referencia escrita es el design system del repo, "Mesa de trabajo con sello académico" (`docs/DECISIONES.md` y `CLAUDE.md`): Mercury (cifra protagonista), Attio (etapas), Linear (filetes, estados, chips), Stripe (resumen vivo), GOV.UK (pasos). La ronda 00 (estado actual) es la base de comparación: antes a la izquierda, después a la derecha.
Bar (escala 0-10, mediana de revisores): jerarquía 8.5, alineación y espaciado 8.5, color como estado 9, tipografía 8.5, densidad y legibilidad 8.5, consistencia 8.5.
Calibration offset: none yet.
Rules: el color solo comunica estado (verde ok, ámbar parcial, rojo alerta, azul en curso, gris anulado); nada de gradientes, sombras salvo flotantes, emojis ni color decorativo. No cambiar textos de negocio, flujos ni roles. Editar solo el generador y `assets/*.js`; regenerar. Sin scroll horizontal a 1280, 768 y 390. Extra bans: la lista anti-slop de la skill.
Time: cap 1.5h (trabajo acotado). Started: 2026-11-14T23:28Z.
Usage: about 20% per hour, never 100%.
Hardware: no aplica (capturas con Chromium headless, 1366 px).
Deliverable: capturas aprobadas; luego commit en la rama y publicación en `main` (el usuario ya autorizó publicar en esta conversación).
Permissions: download no, push yes (rama de trabajo), publish yes (main, autorizado).
User's words: "IMprove overral design" · "improve overral design using that skill I just upload" · antes: "mejora las interfaces de toda la plataforma", "organice mejor la info, no puede verse todo en una sola pagina", "fix the UI".
