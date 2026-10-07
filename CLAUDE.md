# CLAUDE.md · Wireframes Plataforma Cambridge

Repo de wireframes estáticos (HTML/CSS puro, sin build) para la **Plataforma Cambridge**, el sistema administrativo a medida que Orkesta construye para Cambridge School of Languages (Quito, Valle de los Chillos, Ambato). Se publica con GitHub Pages desde `main` / root.

## Antes de tocar nada, lee
- `docs/PROYECTO.md`: qué es el proyecto, el cliente, los dolores, los 11 módulos del contrato, fases y plazos.
- `docs/PANTALLAS.md`: las 44 pantallas, qué muestra cada una, a qué módulo pertenece y cómo se enlazan (flujos).
- `docs/DECISIONES.md`: decisiones y supuestos tomados en los wireframes, y el **mapeo TeamDesk → Plataforma** (tablas, vistas y campos del sistema actual y a qué pantalla van). Al modelar una pantalla, respeta ese mapeo y los identificadores legados (código de curso 0001-AAAA-NNNN, matrícula 001-AAAANNNNN).
- `docs/fuentes/`: propuesta comercial, análisis técnico-comercial y contrato (PDF). Fuente de verdad del alcance.

## Estructura
```
index.html              redirige a Main.html (login): la URL principal abre el mockup
Mapa.html               mapa de pantallas por área (hub)
<Pantalla>.html         una página por pantalla (Main.html = login)
style.css               tema completo (generado desde `css` en el generador)
tools/generar_pantallas.py   generador en Python de TODAS las páginas (fuente de verdad del HTML)
docs/                   documentación de contexto
.nojekyll               para que Pages sirva tal cual
```

## Cómo trabajar
- **Las páginas se generan**: edita `tools/generar_pantallas.py` y corre `python3 tools/generar_pantallas.py` desde la raíz del repo (escribe en `ROOT`; ajusta esa constante a la ruta del repo si hace falta). No edites los `.html` a mano si vas a regenerar, se pierden.
- Nivel de fidelidad: **mockup con identidad Cambridge** siguiendo la referencia de dashboard del cliente: tipografía Poppins, barra lateral clara con íconos SVG lineales (`SVG`/`ico()`), fondo #F6F7FB, tarjetas de 16px de radio con sombra suave, tintes pastel (`--tint-*`) para chips y estados, breadcrumb con flecha atrás en la barra superior (se calcula desde `NAV`). Colores de marca: azul marino #1D3F8F, rojo #D62839, amarillo #F6C21C, celeste #4FA3DC; paleta de gráficos validada `CH`. Los helpers emiten clases CSS (`.card`, `.btn`, `.tbl`, `.kpi`, `.badge`, …) definidas en `style.css` (generado desde `css` en el generador); no agregar estilos en línea nuevos. Componentes de dashboard: `gauge()`, `ring()`, `areachart()`, `stackbars()`, `avatar()`, `course_item()`, `.profile`. Nada de cajas grises con etiqueta: KPIs con cifra (`kpis([(label, valor, sub)])`), filtros con `sel()/search()/dates()` dentro de `filters()`, textos explicativos con `note()`, pares clave-valor con `kv()`, estados con `badge()`, gráficos simples con `vbars()/hbars()/linechart()/funnel()/stacked()/progress()`, procesos con `flow()`, carga de archivos con `upload()`, paginación con `pager()`. Tablas con 4-7 filas de ejemplo. El objetivo es validar flujo, contenido y look & feel con el cliente (Estefanía).
- Filtros funcionales: un bloque `filters(...)` filtra la primera `table(...)` que lo sigue. `search()` busca en todas las celdas; `sel("Etiqueta", opciones)` filtra por la columna que se llama igual que la etiqueta (o `col="Columna"`; `col=False` para un selector decorativo como "Semana"). Las opciones deben coincidir con el texto de las celdas ("Todos"/"Todas" no filtra). La tabla muestra "Sin resultados con estos filtros" si nada coincide y el `pager()` indica cuántas filas quedan en pantalla. Los listados tienen 6-10 filas de ejemplo que cubren los distintos escenarios (estados, sedes, alertas).
- Selector de sede global: filtra los datos de la página. Una cifra que varía por sede se escribe `sv(todas, quito, valle, ambato)`; una tabla con columna de sede se pasa `table(..., sede=<índice de columna>)` y sus filas se ocultan según la sede elegida. La selección se guarda en `localStorage` y se mantiene entre pantallas.
- Toda pantalla usa la misma shell: barra superior (selector de sede, selector de rol "Ver como", notificaciones, asistente, usuario) + menú lateral agrupado por áreas (`NAV`: Académico, Comercial, Inventario, Dirección, Administración). Nueva pantalla = nueva llamada a `page(...)` + agregarla a `rows` (hub, agrupado por las mismas áreas) y, si aplica, a `NAV` con sus roles.
- Tipos de usuario (RBAC): códigos en `ROLES` (ADM, GER, DIR, SUC, COO, ASE, SEC, PRO) y conjuntos `ALL`, `COMERCIAL`, `ACADEMICO`, `APROBADORES`. Cada ítem de `NAV` lleva los roles que lo ven; `only(roles, html, inline=False)` oculta cualquier bloque para los demás roles; `tabs(..., roles={"Pestaña": roles})` oculta pestañas y su panel (si la activa queda oculta se abre la primera visible). El rol elegido se guarda en `localStorage` y se mantiene entre pantallas. Regla: un académico (COO, PRO) no ve nada comercial (matrícula/venta, comisiones, facturación); un asesor no ve Profesores, Inventario, Configuración ni payment sheet.
- Asistente (M9): `ai([(observación, texto del enlace, href)], pregunta_sugerida)` pinta la tarjeta "Asistente · lo que vale la pena mirar" con observaciones generadas sobre la base unificada. Son de solo lectura, deben derivarse de datos visibles en la plataforma y respetar el rol (envolver con `only` cuando el contenido es de un área). El botón "Preguntar" lleva al chat.
- Pestañas: `tabs(items, active, panels)`. `panels` es un dict etiqueta → HTML y cada pestaña muestra su panel en la misma página (JS mínimo en `page()`). Una pestaña que es otra pantalla se pasa como tupla `("Etiqueta","Pantalla.html")` y navega; en ese caso la pantalla destino debe mostrar la misma barra con su pestaña activa (ver `rep_tabs()` en Reportes), para que el usuario nunca "pierda" las pestañas. Toda pestaña debe tener panel o href, nunca quedar muerta.
- Nombres de archivo en PascalCase sin acentos ni espacios (`NuevaVenta.html`). Idioma de la UI: español.
- Botones y enlaces deben apuntar a la siguiente pantalla del flujo (no dejar `href` rotos; verificar con el grep del final).
- Ningún botón queda muerto. `btn(label, href)` navega. `btn(label)` sin href busca la etiqueta en el dict `ACTIONS`: si el valor es un `.html` navega; si es `(descripción, siguiente)` abre el diálogo de confirmación (inyectado en `page()`) que explica qué pasaría y, tras confirmar, muestra un toast y navega a `siguiente` si lo hay. También se puede pasar `btn(label, None, primary, action="…", next="X.html")`. Una etiqueta nueva sin entrada en `ACTIONS` hace fallar el generador a propósito.
- El hub (`rows`) numera solo; toda pantalla nueva debe estar en `rows`.
- Pantallas ocultas: el set `HIDDEN` del generador (hoy: el módulo de Facturación: Facturas, DetalleFactura, RegistrarPago, NotaCredito) quita esas pantallas del menú lateral y del hub, pero se siguen generando para que ningún enlace se rompa. Para volver a mostrarlas, vaciar el set.
- Accesibilidad mínima aunque sea wireframe: `<button>`, `<a href>`, `<input>` con `<label>`.
- Datos de ejemplo siempre ficticios: nunca copiar nombres, cédulas, teléfonos ni correos reales de capturas de TeamDesk u otros sistemas del cliente.
- No inventar funcionalidades fuera del contrato (Cláusula Tercera). Si algo no está en los 11 módulos, va como "fuera de alcance" o se pregunta.

## Verificación rápida
```
python3 tools/generar_pantallas.py
grep -o 'href="[A-Za-z0-9]*\.html"' *.html | sed 's/.*href="//;s/"//' | sort -u | while read f; do [ -f "$f" ] || echo "ROTO $f"; done
for f in *.html; do grep -q "href=\"$f\"" Mapa.html || echo "FUERA DEL HUB $f"; done   # solo debe listar index.html, Mapa.html y las de HIDDEN
```

## Publicación
GitHub Pages: Settings → Pages → Deploy from a branch → `main` / `/ (root)`. URL: https://crpozo.github.io/cambridge-wireframes/
