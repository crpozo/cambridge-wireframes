# Contexto completo de la sesión · Wireframes Plataforma Cambridge

Documento de traspaso para continuar el trabajo en otra sesión o con otra persona. Resume qué es el proyecto, todo lo que pidió el cliente y el usuario a lo largo de la sesión, cómo se resolvió, cómo está el repo hoy y qué queda pendiente.

Fecha de corte: 2026-10-19. Repo: `crpozo/cambridge-wireframes`, rama `main`. Publicado en https://crpozo.github.io/cambridge-wireframes/

---

## 1. Qué es esto

Mockup navegable (HTML/CSS puro, sin build) de la **Plataforma Cambridge**: el sistema administrativo a medida que Orkesta construye para Cambridge School of Languages (sedes Quito, Valle de los Chillos, Ambato). Reemplaza TeamDesk. Sirve para validar flujo, contenido y look & feel con la cliente (Estefanía) antes de desarrollar.

- 52 pantallas + login + índice + mapa (54 archivos HTML).
- Todo se genera desde `tools/generar_pantallas.py` (fuente de verdad). `style.css` también sale del generador.
- GitHub Pages desde `main` / root, con workflow `.github/workflows/pages.yml` (enablement automático).
- Documentación de contexto en `docs/`: `PROYECTO.md` (cliente, dolores, 11 módulos del contrato), `PANTALLAS.md` (las 52 pantallas y sus flujos), `DECISIONES.md` (decisiones y mapeo TeamDesk → Plataforma), `fuentes/` (propuesta, análisis y contrato en PDF).
- Reglas de trabajo en `CLAUDE.md` (leerlo primero; es la guía operativa del generador).

## 2. Los 11 módulos del contrato (alcance)

M1 Core + Auth + RBAC + Audit log · M2 Gestión de estudiantes (Ficha 360°) · M3 Cursos y sesiones · M4 Profesores y pagos (payment sheet) · M5 Facturación por niveles · M6 Motor de comisiones · M7 Inventario de libros · M8 Dashboards y reportería · M9 Chatbot interno · M10 Dashboard ejecutivo · M11 APIs de integración (Kommo, Moodle, Dora).

Lo que no está en los 11 módulos se marca como **propuesta fuera de alcance** (hoy: el portal del estudiante).

## 3. Cronología de lo que se pidió y cómo se resolvió

### 3.1 Arranque y publicación (5 oct)
- Subir los wireframes a GitHub Pages; todo en `main`. Pages daba 404 hasta habilitarlo con el workflow (`enablement: true`) y guardar en Settings.
- Selector de sede más pequeño; todas las pestañas funcionales (panel por pestaña en la misma página, y cuando una pestaña es otra pantalla, la destino repite la barra); crear todas las pantallas de alto nivel; cada botón lleva a algún lado (dict `ACTIONS`: navega o abre diálogo de confirmación + toast).
- Más detalle en todas las pantallas, sin recuadros grises; el selector de sede cambia los datos (`sv()` y `table(..., sede=)`); filtros funcionales con más datos de ejemplo.

### 3.2 Alineación con TeamDesk y contrato (6 oct)
- Ocultar Facturación (set `HIDDEN`); luego se volvió a mostrar (12 oct).
- Se pidió entrar a TeamDesk con credenciales: la red del entorno bloquea `teamdesk.net`, no fue posible. Las credenciales se pegaron en el chat (no se guardaron en el repo); se recomendó cambiar la contraseña. Se trabajó con capturas de TeamDesk: Students, Enrollments, Courses, Invoices, Credit Notes, Teachers, Products/Services, Inventory Management, Classrooms, Programs, Companies. El mapeo está en `docs/DECISIONES.md`. Identificadores legados: curso `0001-AAAA-NNNN`, matrícula `001-AAAANNNNN`, factura `0000NNNNN`.
- Tipos de usuario (RBAC): ADM, GER, DIR, SUC, COO, ASE, SEC, PRO. Un académico no ve nada comercial; un asesor no ve profesores, inventario, configuración ni payment sheet. Selector "Ver como" para probar roles.
- Menú por áreas: Académico, Comercial, Inventario, Dirección, Administración.
- Perfiles de profesores más ricos con ayuda de IA.

### 3.3 Identidad visual y UX (7 oct)
- Mockup con colores Cambridge (azul marino #1D3F8F, rojo #D62839, amarillo #F6C21C, celeste #4FA3DC), tipografía Poppins, barra lateral clara con íconos SVG, tarjetas de 16 px, logo oficial (`assets/logo.webp`), dashboard siguiendo la referencia del cliente (gauges, filas de curso, actividad).
- La URL principal abre el mockup directamente (no el mapa). Se corrigieron: medidores rotos, texto invisible en hover, densidad y desbordes a 1330 px, tablas apretadas (celdas de dos líneas `c2()`, columnas ocultas, máx. ~7 columnas), botones de acción que parecían texto, cajas de alerta eliminadas (`note()` devuelve vacío), notificaciones como popover, sin botón atrás en Inicio, sin enlace al mapa.
- Asistente tipo Clippy: botón flotante en todas las pantallas internas que sabe en qué pantalla estás (`AI_CTX`), más `Insights.html` con todas las observaciones por área y prioridad. El acordeón "Asistente" por pantalla se quitó después a pedido del cliente.

### 3.4 Cabeceras, formularios, tablas, menú (8–12 oct)
- Cabecera de páginas de detalle como tarjeta `hero()` (datos clave en cuadrícula, acciones a la derecha).
- Formularios inteligentes `form()/field()`: placeholders, selects deducidos, fecha/hora/email/teléfono/número/archivo, obligatorios, campos automáticos; pie fijo `foot()`.
- Filas de listado clicables; tablas que no parten palabras.
- Menú lateral: áreas plegables con estado guardado, filas compactas, degradado "Más opciones" cuando hace falta scroll; selector de sede en la barra superior; "Ver como" en el menú del usuario; restauración de grupos antes de pintar (sin parpadeo). Etiqueta "Comisiones" corta con su ícono.
- Chat del asistente interno a ancho completo. Chevrones de texto reemplazados por ícono SVG. Buscador con placeholder "Buscar…".

### 3.5 Facturación como el módulo Invoice de TeamDesk (12 oct)
- Listado con KPIs, pestañas Facturas / Rematrículas por confirmar / Calendario de crédito / Por estudiante / Notas de crédito; filtros estado, SRI, asesor, crédito; acciones enviar comprobantes pendientes y descargar XML.
- Detalle con términos, cliente (CED/RUC/PAS, RUC especial), autorización SRI (clave de acceso, comprobante enviado), ítems con tipo, % descuento e IVA, pagos múltiples, efecto en la matrícula e historial.
- "Por estudiante": elegir un estudiante y descargar (ZIP) o enviar por correo todas sus facturas pendientes; también desde la Ficha 360°.

### 3.6 Portal del estudiante (12–13 oct)
- `PortalEstudiante.html` (propuesta fuera de alcance, etiquetada): curso actual, próxima clase, avance, asistencia, notas y certificados, pagos y facturas, datos. Primero tuvo login propio; luego el cliente pidió **login único** con redirección por rol, así que `LoginEstudiante.html` se eliminó y `Main.html` quedó como único ingreso (con enlace "Demo" para ver el portal).

### 3.7 Reportes, descuentos, comisiones, profesores, catálogo, inventario (12 oct)
- Constructor de reportes guiado para usuarios no técnicos: preguntas en lenguaje natural por área (incluida facturación/SRI, inventario, B2B, retención), período y sede con chips, vista, resultado en palabras + gráfico + tabla, exportar Excel/PDF, enviar por correo, guardar. Reportes guardados como tarjetas con quién los usa y la vista TeamDesk que reemplazan.
- Descuentos: el asesor aplica hasta 10 % sin aprobación (motivo obligatorio); más de 10 % va a Dirección Comercial; Dirección ve todo en Comisiones → "Descuentos otorgados".
- Comisiones claras para el asesor: cálculo paso a paso (niveles, rango, % por modalidad, bono por meta, retenido hasta cobro, total y fecha de pago), meta y "cuánto ganarías con una venta más"; el asesor solo ve lo suyo.
- Alta de profesor sin autorización (Coordinación Académica lo crea; solo la tarifa fuera de tabla va a aprobación). Nota: el contrato M4 decía "alta con aprobación obligatoria"; el cambio está documentado en DECISIONES.
- Ficha del profesor completa: foto, contacto, educación y certificaciones, tarifa y datos de pago, desempeño (asistencia, pass rate, comparación con la sede, reconocimientos/observaciones), cursos, sesiones, historial de pagos.
- Configuración → Productos y servicios: catálogo completo (niveles, matrícula, clases individuales, club, exámenes internacionales, Summer Camp, libros físicos y digitales, merchandising) y `DetalleProducto.html` (precio e IVA, stock por sede, parámetros de matrícula, códigos de activación, historial de precios, movimientos).
- Inventario: correo diario de stock negativo a las 07:00 (destinatarios, últimos envíos, "Enviar resumen ahora"), configurable en Parámetros.

### 3.8 Feedback de la sesión con el cliente (13 oct)
- Login único con redirección por rol; menú con Académico primero.
- `Programas.html`: jerarquía Programa → Modalidad → Tipo de clase → Curso; programas Preescolar, Kids, Teens, Adults (ESL), Business; modalidades virtual/presencial; tipos de clase grupal, one to one, one to one reducido, one to one Business; horas por sesión (regular 2 h, sábados 4 h, one to one en paquetes de 20/40 h); plantillas de horario y horario personalizado; calendario de feriados de Ecuador automático y configurable (p. ej. EE. UU.); grupos de Microsoft Teams por curso.
- Nuevo curso con esa jerarquía, fecha fin que salta feriados y equipo de Teams automático.
- Estudiante: dirección sectorizada (provincia/ciudad, sector, referencia, ubicar en el mapa); rematrícula conectada con el Muro (avance 100 % + nota ≥ 7 activa "Rematricularme" en el portal; queda pendiente de pago; Secretaría confirma en Facturación); recordatorios "te faltan X días"; certificados con programa + modalidad + curso por módulo; próximos cursos con fecha y profesor.
- `Leads.html`: flujo Kommo → contacto → cotización → matrícula.
- `Empresas.html`: vista B2B consolidada por empresa (ejemplo ficticio "Grupo Nova").
- Dashboard: retención por cohorte, cursos por abrir, alertas de información escondida (sin grupo, Teams sin profesor, cursos sin profesor, sin calificar, rematrículas sin pago), conteos, exportar PDF.

## 4. Estado actual del repo

- 33 commits en `main`; último despliegue de Pages en verde.
- Verificación que se corre siempre: regenerar, grep de `href` rotos, cobertura del hub (`Mapa.html`), y Playwright (Chromium en `/opt/pw-browsers/chromium`) para errores de JS y desbordes horizontales a 1330 px en todas las páginas. Todo en verde al cierre.
- Commits con `git -c user.name="crpozo" -c user.email="crpozo95@gmail.com"` y las líneas de atribución al final del mensaje.

## 5. Reglas que hay que respetar al continuar

- Editar solo el generador y regenerar; nunca los HTML a mano.
- Datos siempre ficticios (nunca copiar nombres, cédulas, teléfonos o correos reales de TeamDesk).
- No inventar funcionalidades fuera de los 11 módulos; si algo no está, marcarlo como propuesta fuera de alcance.
- Nada de cajas grises ni notas explicativas en el mockup; la explicación vive en `docs/`.
- Toda pantalla nueva: `page(...)` + entrada en `rows` (hub) + `NAV` con roles si va en el menú + `ACTIONS` para cada botón nuevo (una etiqueta sin entrada hace fallar el generador a propósito).
- Tablas: máx. ~7 columnas visibles, celdas de dos líneas con `c2()`, nada de tablas de 12 columnas.

### 23 oct 2026 · Manual de Procesos del cliente
El usuario subió el manual de ecommerce (ya reflejado en `Pedidos.html`), el contrato de servicios del estudiante, el formato de referencias, el BPMN de contratación docente, dos checklists (hoja de ruta y finalización) y el ZIP "MANUAL DE PROCESOS" (académico y administrativo). Resultado: `ContratacionProfesores.html` + `DetalleCandidato.html` (pipeline con aprobaciones y alta al final), tarjetas de seguimiento e indexados en DetalleCurso, reaperturas en Cursos, reglas de cierre en CalificarCurso, novedades/Teacher of the Month/correo en PaymentSheet, reglas del contrato en NotaCredito, activos fijos (propuesta) en Inventario y, a pedido del usuario, `ReclutamientoAdministrativo.html` (propuesta, menú Administración). Resumen en `docs/PROCESOS_INTERNOS.md`; los originales con datos personales no se subieron. La carpeta de Drive compartida sigue sin poder leerse desde el entorno (el conector ve la carpeta pero no sus archivos); el usuario subió los documentos directamente.

## 6. Pendientes y temas abiertos

- Acceso a TeamDesk desde el entorno (bloqueado por política de red). Alternativas: permitir `teamdesk.net` en la política del entorno o exportar el esquema/vistas.
- Validar con la cliente: portal del estudiante (fuera de alcance), alta de profesor sin aprobación (difiere del texto del contrato), reglas de descuento (10 %) y de comisión (rangos y bono), calendario de feriados y vínculo con Teams (depende de M11).
- Ideas no implementadas: Nueva matrícula iniciada desde la Ficha 360° con datos cargados; aprobar/rechazar desde la notificación; acceso rápido "Registrar sesión de hoy" en Inicio para el rol Profesor.

## 7. Índice rápido de pantallas (archivo → qué es)

Acceso: `Main` (login único), `RecuperarContrasena`, `Home` (inicio por rol), `Notificaciones`, `Chatbot`, `Insights`, `PortalEstudiante` (propuesta).
Académico: `Programas`, `Cursos`, `NuevoCurso`, `DetalleCurso`, `Estudiantes`, `NuevoEstudiante`, `Ficha360`, `DetalleMatricula`, `Sesiones`, `RegistrarSesion`, `Profesores`, `AltaProfesor`, `FichaProfesor`, `PaymentSheet`, `ImportExport`.
Comercial: `Leads`, `NuevaVenta`, `SolicitudDescuento`, `Empresas`, `Facturas`, `DetalleFactura`, `RegistrarPago`, `NotaCredito`, `Comisiones`, `DetalleComision`, `ReglasComision`, `Aprobaciones`.
Inventario: `Inventario`, `Movimientos`, `NuevoPedido`, `RegistrarMovimiento`, `DetalleProducto`.
Dirección: `Reportes`, `ConstructorReportes`, `DashboardEjecutivo`.
Administración: `Usuarios`, `NuevoUsuario`, `Configuracion`, `NuevaSede`, `NuevoNivel`, `NuevaRegla`, `AuditLog`, `Integraciones`.
Interno: `Mapa` (hub por URL), `index` (redirige a Main).

## 8. Revisión contra TeamDesk (19 oct 2026, rama `revision-teamdesk`)
- Se recorrió TeamDesk en vivo (solo lectura): 25 tablas, vistas, dashboards, botones de cada ficha y formularios de Enrollment e Invoice. Resultado en `revision-teamdesk-vs-mockup.md` (fuera del repo).
- Matrícula rehecha como en TeamDesk: una por módulo, factura multi-módulo, cuotas, valores con descuento por concepto, canal de contacto, matrícula firmada, acciones de TeamDesk.
- Caso María Andrade coherente en todas las pantallas (ver DECISIONES). Rematrícula ya no cobra módulos pagados.
- Nuevas pantallas: CalificarCurso, ExamenesInternacionales (propuesta). Nuevas pestañas en Facturas: Cartera, Caja del día, Sin vincular. Portal: sección "Mi progreso general" con la ruta A1 → C1.
- Un agente revisó el mockup por rol; quedan pendientes los de la lista en DECISIONES (revisión automática).
- Para regenerar en Windows: `python -X utf8 tools/generar_pantallas.py`.
