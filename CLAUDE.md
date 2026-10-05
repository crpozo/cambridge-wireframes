# CLAUDE.md · Wireframes Plataforma Cambridge

Repo de wireframes estáticos (HTML/CSS puro, sin build) para la **Plataforma Cambridge**, el sistema administrativo a medida que Orkesta construye para Cambridge School of Languages (Quito, Valle de los Chillos, Ambato). Se publica con GitHub Pages desde `main` / root.

## Antes de tocar nada, lee
- `docs/PROYECTO.md`: qué es el proyecto, el cliente, los dolores, los 11 módulos del contrato, fases y plazos.
- `docs/PANTALLAS.md`: las 33 pantallas, qué muestra cada una, a qué módulo pertenece y cómo se enlazan (flujos).
- `docs/DECISIONES.md`: decisiones y supuestos tomados en los wireframes.
- `docs/fuentes/`: propuesta comercial, análisis técnico-comercial y contrato (PDF). Fuente de verdad del alcance.

## Estructura
```
index.html              mapa de pantallas por flujo (hub)
<Pantalla>.html         una página por pantalla (Main.html = login)
style.css               estilos del hub y la barra amarilla de wireframe
tools/generar_pantallas.py   generador en Python de TODAS las páginas (fuente de verdad del HTML)
docs/                   documentación de contexto
.nojekyll               para que Pages sirva tal cual
```

## Cómo trabajar
- **Las páginas se generan**: edita `tools/generar_pantallas.py` y corre `python3 tools/generar_pantallas.py` desde la raíz del repo (escribe en `ROOT`; ajusta esa constante a la ruta del repo si hace falta). No edites los `.html` a mano si vas a regenerar, se pierden.
- Nivel de fidelidad: **alto nivel / lo-fi**. Cajas grises con etiqueta, tablas con 3-4 filas de ejemplo, sin diseño visual. El objetivo es validar flujo y contenido con el cliente (Estefanía), no la estética.
- Toda pantalla usa la misma shell: barra superior (selector de sede global, notificaciones, asistente, usuario/rol) + menú lateral por módulo. Nueva pantalla = nueva llamada a `page(...)` + agregarla a `rows` para que aparezca en el hub y, si aplica, un enlace en el menú `nav()`.
- Pestañas: `tabs(items, active, panels)`. `panels` es un dict etiqueta → HTML y cada pestaña muestra su panel en la misma página (JS mínimo en `page()`). Una pestaña que es otra pantalla se pasa como tupla `("Etiqueta","Pantalla.html")` y navega. Toda pestaña debe tener panel o href, nunca quedar muerta.
- Nombres de archivo en PascalCase sin acentos ni espacios (`NuevaVenta.html`). Idioma de la UI: español.
- Botones y enlaces deben apuntar a la siguiente pantalla del flujo (no dejar `href` rotos; verificar con el grep del final).
- Accesibilidad mínima aunque sea wireframe: `<button>`, `<a href>`, `<input>` con `<label>`.
- No inventar funcionalidades fuera del contrato (Cláusula Tercera). Si algo no está en los 11 módulos, va como "fuera de alcance" o se pregunta.

## Verificación rápida
```
python3 tools/generar_pantallas.py
grep -o 'href="[A-Za-z0-9]*\.html"' *.html | sed 's/.*href="//;s/"//' | sort -u | while read f; do [ -f "$f" ] || echo "ROTO $f"; done
```

## Publicación
GitHub Pages: Settings → Pages → Deploy from a branch → `main` / `/ (root)`. URL: https://crpozo.github.io/cambridge-wireframes/
