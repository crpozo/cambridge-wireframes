# Cook ledger: diseño general Cambridge

Started: 2026-11-14 23:28 UTC
Time: floor none | cap 1.5h
Bar: jerarquía 8.5 | alineación 8.5 | color 9 | tipografía 8.5 | densidad 8.5 | consistencia 8.5
Calibration offset: none yet
Usage: about 20% per hour, never 100%
Gate: stills approved no | final (publicar) not started
Best so far: round 00, `cook/stills/r00/`

## Decisions
- 23:28 Sin imágenes de referencia: el listón es el design system escrito del repo y la ronda 00 es la base (antes/después), porque el usuario pidió usar la skill sin enviar referencias.
- 23:28 Tope de 1.5 h en lugar de piso de 8 h, porque es un ajuste de componentes de un prototipo, no un build visual largo.
- 23:28 Dos revisores por ronda (mínimo de la skill), para contener el consumo.
- 23:28 Capturas y comparaciones fuera de git (`.gitignore`); BRIEF, SHOTS y ROUNDS sí se versionan para retomar en otra sesión.

## User feedback inbox
- 14 nov "organice mejor la info, no puede verse todo en una sola pagina" | r00 previa | done (vistas en Indicadores y gráficos)
- 14 nov "fix the UI" (pasos horizontales) | r00 previa | done
- 14 nov "IMprove overral design" | round 01 | open

---

## Round 00 (base, sin cambios)

Hallazgos propios de la revisión (self-scored, no decide):
1. S03, S10: color decorativo o mal asignado: "Activa" y "Completado" en rojo, serie "Club de conversación" y "Real" en rojo, medidor multicolor, anillos naranja/celeste.
2. S02: las acciones de página (Nuevo estudiante, Importar/Exportar, Más acciones) caen en una segunda fila bajo los filtros.
3. S06, S10: encabezados de tabla partidos en 2 a 4 líneas ("Fecha de venta", "Pagada por completo", "Virtual / presencial").
4. S07: "Sincronizar con Kommo" queda sola en una fila y deja un hueco grande.
5. S03: la franja de 4 cifras de Rematrícula deja la 4.ª sola en otra fila.
6. S06: los totales de la factura son una línea de texto, no un bloque de totales alineado a la derecha.

## Round 01

Time: 23:28 to 23:35 UTC (reloj del contenedor) | elapsed 0.1 h
Focus: color como estado y orden de acciones, porque eran los hallazgos más visibles de la ronda 00.

Changes:
- Paleta de gráficos sin rojo ni ámbar (`CH` y `assets/plan.js`): azules, pizarra y verde azulado.
- Estados: "Activa" y "Completado" en verde, "En curso" en azul (25 lugares); medidor de Rendimiento de un solo color; filas de curso sin tintes decorativos.
- Acciones de listado: un primario + "Más acciones" en la fila de filtros; el texto de estado y totales nunca se esconde en el menú (`split_actions`).
- Encabezados de tabla con corte equilibrado (`text-wrap:balance`, espaciado .02em): tablas con scroll horizontal a 1280 px bajan de 38 a 36 (medido). Se probó `nowrap` y se descartó: subía a 50 (medido).
- Factura: bloque de totales alineado a la derecha con filete doble (`totals()`). Rematrícula en 2 x 2. Franja de Leads sin hueco.

Stills: `cook/stills/r01/` | Side by side: `cook/compare/r01/` (antes izquierda, después derecha)

Scores, eyeballed: mediana de 2 revisores sin contexto (mismo modelo), sin calibrar

| Shot | Jerarquía | Alineación | Color | Tipografía | Densidad | Consistencia | vs r00 |
|---|---|---|---|---|---|---|---|
| S01 Inicio | 7 | 7 | 7.5 | 8 | 7 | 8 | mejor |
| S02 Estudiantes | 7.5 | 8 | 9 | 8 | 7.5 | 7.5 | mejor |
| S03 Ficha 360 | 6 | 6.5 | 7 | 7 | 6 | 6.5 | mejor |
| S04 Cursos | 7.5 | 7 | 8 | 8 | 7 | 7.5 | mejor |
| S05 Facturas | 6.5 | 7 | 8.5 | 7.5 | 6 | 8 | igual |
| S06 Factura | 7 | 7 | 9 | 8 | 7 | 7 | mejor |
| S07 Leads | 7 | 6.5 | 8 | 7.5 | 6 | 7 | mejor |
| S08 Nueva matrícula | 7 | 6.5 | 9 | 8 | 6.5 | 8 | igual |
| S09 Exámenes | 6.5 | 6 | 8.5 | 7.5 | 6 | 7 | igual |
| S10 Comisiones | 7 | 6 | 8.5 | 7.5 | 7 | 7 | mejor |

Top gaps from critics:
1. Tablas: columnas de cifras alineadas a la izquierda (Meta, Real, Cupo, % dcto., Internos), celdas de estado y detalle que parten en 3 líneas, columna Acción con botones, enlaces y chevrones mezclados.
2. Más de un primario por zona (Ficha 360: "Nueva matrícula" dos veces y "Ver todos"; Factura: "Registrar pago" dos veces con saldo 0).
3. Nueva matrícula: el pie fijo tapa una fila del formulario.
4. Tarjetas de una misma fila con alturas distintas (Inicio, Factura, Comisiones).
5. Color residual: medidores de Inicio con colores distintos, texto verde de sincronización en Leads, filete ámbar decorativo en Ficha 360, paso actual sin marcar en Comisiones.

Stop check: bar no | cap no -> round 02
Next focus: disciplina de tablas (global), un primario por zona, pie fijo, alturas iguales, color residual.

## Round 02

Time: 23:35 to 23:40 UTC (reloj del contenedor)
Focus: disciplina de tablas, un primario por zona, color residual, porque eran los huecos que ambos revisores marcaron en la ronda 01.

Changes:
- Tablas: cantidades, porcentajes y fracciones (cupo 12/15) alineadas a la derecha aunque el encabezado no diga "cantidad"; se excluyen identificadores (módulo, nivel, código, año).
- Estados "estado · detalle" largos: el estado queda junto al punto y el detalle debajo en gris (`badge()`); el punto ya no cae solo en una línea.
- Columnas de acción: los botones con borde se ven como enlaces de fila.
- Un primario por zona: Ficha 360 ("Nueva matrícula" del perfil y "Ver todos" pasan a secundarios), Factura ("Registrar pago" de la tarjeta Pagos pasa a enlace).
- Color: filete de la nota de Rendimiento neutro, medidores de Inicio neutros salvo 109 % en verde, nota de sincronización de Leads en gris, paso actual marcado en Comisiones.
- Historial de factura: la columna Evento es la ancha.

Measured: sin errores de JS en 85 páginas a 1280, 768 y 390; los mismos 3 desbordes en 390 de la base (Cursos, RIDE, Reportes); tablas con scroll horizontal a 1280: 33 (base 38); enlaces rotos: 0.

Scores, eyeballed: mediana de 2 revisores nuevos sin contexto, sin calibrar

| Shot | Jerarquía | Alineación | Color | Tipografía | Densidad | Consistencia | vs r00 |
|---|---|---|---|---|---|---|---|
| S01 Inicio | 7.5 | 8 | 7.75 | 8.25 | 7.5 | 8 | mejor |
| S02 Estudiantes | 8.25 | 8.25 | 9 | 8.25 | 8 | 7.75 | mejor |
| S03 Ficha 360 | 7.25 | 7.25 | 7.5 | 8 | 7.25 | 7.25 | mejor |
| S04 Cursos | 8.25 | 8.25 | 8 | 8.25 | 7.25 | 8.25 | mejor |
| S05 Facturas | 7.25 | 8 | 9 | 8.25 | 7.25 | 8 | mejor |
| S06 Factura | 8.25 | 8 | 9 | 8.25 | 8 | 8.25 | mejor |
| S07 Leads | 7.5 | 7.25 | 8.25 | 8 | 6.5 | 7.25 | mejor |
| S08 Nueva matrícula | 7.5 | 8.25 | 8.25 | 8.25 | 7 | 8.25 | igual |
| S09 Exámenes | 7.5 | 7.5 | 8.5 | 8.25 | 7 | 8 | mejor |
| S10 Comisiones | 7.75 | 7.5 | 8 | 7.5 | 7.5 | 7.25 | mejor |

Top gaps from critics:
1. Celdas que todavía parten en 3-4 líneas en listados (Leads, Exámenes, Facturas, Cursos).
2. El primario de la página vive en la fila de filtros en unas pantallas y junto al h1 en otras.
3. Colores de categoría en gráficos (gris se lee como anulado, verde de "Ausencias" como ok); tarjetas estiradas con paneles vacíos.
4. Textos de ayuda de 2-3 líneas en Nueva matrícula; notas de reunión impresas en Comisiones.

Stop check: bar no | cap no -> round 03

## Round 03

Time: 23:40 to 23:41 UTC
Focus: huecos 3 de la ronda 02 y formato de Comisiones.

Changes:
- Se revierte el estirado de tarjetas (dejaba paneles vacíos).
- Gráficos en una sola escala de azul marino (`CH`, `--ch1..4`, `assets/plan.js`): sin gris ni verde para categorías.
- Comisiones: montos con dos decimales, "por nivel" en el encabezado de la tabla de rangos, la nota "pasa a noviembre" va en el estado, no en la cifra.
- Franja de etapas de Leads a todo el ancho.

Measured: mismos resultados que la ronda 02 (0 errores de JS, 3 desbordes previos, 33 tablas con scroll, 0 enlaces rotos).
Scores: not measured. Esta ronda no pasó por revisores, para contener el consumo; la verificación fue mía sobre `cook/compare/r03/` (self-checked, no decide).

Stop check: bar no (mediana 7.25 a 9 por dimensión en la ronda 02) | cap no | stills approved no -> stop por consumo y gate: se envían las comparaciones al usuario; no se publica en `main` sin su aprobación.
Next focus si se aprueba seguir: mover el primario de cada listado junto al h1 (global en `shell()`), celdas de una línea + detalle en Leads, Exámenes, Facturas y Cursos, ayudas de una línea en Nueva matrícula, sacar notas de reunión de Comisiones a docs.

## Round 04

Time: 23:45 a 23:52 UTC (reloj del contenedor)
Focus: acción principal junto al h1, celdas de una línea, ayudas de formulario, notas de reunión en pantalla (huecos de la ronda 02). El usuario aprobó publicar las rondas 01-03 en `main` y pidió esta ronda con publicación automática.

Changes:
- `shell()`: el primario de los filtros de la página sube junto al h1 (Estudiantes, Cursos, Exámenes, Leads, Facturas y demás listados); conserva los roles (COO y PRO no ven "Nuevo estudiante", medido).
- Comisiones: sin la nota de reunión "Pendiente…"; tabla de rangos con encabezados cortos ("por nivel" en el título).
- Las razones con espacios ("6 / 8") ya no se alinean como cifra; el cupo "12/15" sí.

Probado y revertido en esta ronda (los revisores lo marcaron como retroceso):
- Ayudas de formulario cortadas en una línea con "…": escondían información.
- Ocultar Interés en Leads y Sede en Exámenes: quitaba datos útiles.

Scores, eyeballed: mediana de 2 revisores nuevos sin contexto (antes de revertir los retrocesos)

| Shot | Jerarquía | Alineación | Color | Tipografía | Densidad | Consistencia | vs r00 |
|---|---|---|---|---|---|---|---|
| S01 Inicio | 7.25 | 7.75 | 8.75 | 8.5 | 7.5 | 8 | mejor |
| S02 Estudiantes | 8.5 | 8 | 9 | 8.5 | 8 | 8.5 | mejor |
| S03 Ficha 360 | 6.75 | 7.25 | 8.5 | 7.75 | 7 | 7.25 | mejor |
| S04 Cursos | 8.5 | 7.75 | 8 | 8.25 | 7.25 | 8.25 | mejor |
| S05 Facturas | 7.5 | 7.5 | 8.75 | 8.25 | 7 | 8 | mejor / igual |
| S06 Factura | 7.5 | 8 | 9 | 8.5 | 8 | 7.75 | mejor |
| S07 Leads | 8.25 | 7.75 | 8.25 | 8.5 | 8 | 7.5 | mejor |
| S08 Nueva matrícula | 7.75 | 8 | 9 | 8 | 7.25 | 8 | igual |
| S09 Exámenes | 7.75 | 7.75 | 8.75 | 8.25 | 7.5 | 7.75 | mejor |
| S10 Comisiones | 7 | 7.25 | 9 | 8 | 7.25 | 7.25 | mejor |

Measured: 0 errores de JS en 85 páginas a 1280, 768 y 390; mismos 3 desbordes previos en 390; 33 tablas con scroll a 1280 (base 38); 0 enlaces rotos.

Top gaps from critics (para la próxima ronda):
1. Pantallas de detalle sin primario junto al h1 y con acciones repetidas: Ficha 360 ("Nueva matrícula" dos veces), Factura ("Registrar pago" como primario de una factura ya pagada), Comisiones ("Aprobar período" en la fila del período), Inicio.
2. Subtítulos de celdas que parten en 3-4 líneas: Cursos (código · sede · aula · horario · modalidad), Facturas, Exámenes, Comisiones.
3. Bloque de capacidad en Cursos: barra rayada, porcentaje con fondo y tres cajitas repiten el mismo estado.
4. Tarjetas en pares con alturas distintas (Inicio, Factura) y datos de cliente/SRI en texto corrido en vez de lista de definición.

Stop check: bar no (S02 llega a 8.5 en 4 de 6 dimensiones; el resto entre 6.75 y 9) | cap: se corta aquí por consumo | publicación: automática, autorizada por el usuario -> publicado en `main`.

## Round 05

Focus: los 4 huecos de la ronda 04 y el pedido del usuario "mejora el side menu".

Changes:
- Cabeceras de detalle: las acciones de `hero()` suben junto al h1 (Factura, Matrícula, Curso y demás detalles). Factura pagada: "Enviar comprobante" es el primario y "Registrar pago" queda como secundario; SRI autorizada en verde. Ficha 360: "Nueva matrícula" una sola vez. Inicio: "Nueva matrícula" junto al h1.
- Cursos: el subtítulo de 13 cursos deja de repetir sede y modalidad (ya están en sus columnas). Efecto medido: Cursos ya no desborda a 390 px (quedan RIDE y Reportes, previos).
- Capacidad: barra de un solo azul (oscuro inscritos, claro esperados, rojo solo en sobrecupo), sin rayas, sin porcentaje con fondo y sin cajitas.
- Factura: datos del cliente como lista de definición.
- Menú lateral: buscador "Ir a…" (filtra, Enter abre, Esc limpia, respeta roles); solo se abre el área de la pantalla actual (en Inicio, Académico y Comercial) y cada área recuerda si la abriste; filas compactas, títulos de área más legibles y separadores entre áreas.
- Pasos: el hecho lleva check en verde y el actual queda como anillo.

Measured: 0 errores de JS en 85 páginas a 1280, 768 y 390; desbordes a 390: 2 (base 3); 33 tablas con scroll a 1280 (base 38); 0 enlaces rotos; roles: COO y PRO no ven "Nuevo estudiante" ni encuentran "Facturación" en el buscador del menú.

Scores, eyeballed: mediana de 2 revisores nuevos sin contexto (antes de los últimos ajustes de menú, factura y pasos)

| Shot | Jerarquía | Alineación | Color | Tipografía | Densidad | Consistencia | vs r00 |
|---|---|---|---|---|---|---|---|
| S01 Inicio | 8 | 7.5 | 8.75 | 8.5 | 7.75 | 8.25 | mejor |
| S02 Estudiantes | 8.75 | 8.25 | 9 | 8.5 | 8.25 | 8.5 | mejor |
| S03 Ficha 360 | 7.5 | 7.5 | 8.75 | 8.25 | 7.5 | 8 | mejor |
| S04 Cursos | 8.25 | 7.5 | 8.75 | 8.5 | 8 | 8 | mejor |
| S05 Facturas | 7.5 | 7.75 | 9 | 8.5 | 7.5 | 8 | igual |
| S06 Factura | 7.75 | 8.25 | 8.5 | 8.5 | 8 | 7.75 | mejor |
| S07 Leads | 8.5 | 7.5 | 9 | 8.5 | 7.5 | 7.5 | mejor |
| S08 Nueva matrícula | 8 | 7.75 | 9 | 8.5 | 7.25 | 8.5 | igual |
| S09 Exámenes | 8 | 7.5 | 9 | 8.5 | 7.75 | 8 | mejor |
| S10 Comisiones | 7.25 | 7.75 | 9 | 8.5 | 8 | 7.75 | mejor |
| Menú lateral | 7.5 (mediana de 8 y 7) | | | | | | mejor |

Top gaps from critics (próxima ronda):
1. Columnas angostas que parten en 3-4 líneas: Facturas (factura, SRI, cobro), Leads (origen, quién estudia), Exámenes (examen), Reaperturas en Cursos.
2. Acciones fuera del h1 cuando viven en una pestaña o tarjeta: Comisiones ("Aprobar período"), Exámenes (tarjeta de contexto con 3 botones), Ficha 360 (sin acción junto al h1; pestañas lejos del título).
3. Facturas: cuatro capas de controles antes de la tabla (pestañas, vista, filtros rápidos, filtros).
4. Inicio: tarjetas en pares con alturas distintas, "Pendientes de aprobación" repite la lista de pendientes, medidores grandes para tres cifras.

Stop check: bar no (S02 en 8.25-9; el resto entre 7.25 y 9) | publicación automática autorizada -> publicado en `main`.

## Round 06

Focus: los 4 huecos de la ronda 05.

Changes:
- Facturas: una capa menos de controles (los cuatro botones de vista rápida pasan a un selector "Vista" en la fila de filtros; filtra igual, medido: 8 todas, 4 por cobrar, 2 sin autorizar SRI) y sin la línea suelta de envío masivo; "Nueva factura" con el mismo ícono de menú que el resto.
- Acciones junto al h1: Comisiones ("Aprobar período" + "Reglas de comisión" + "Más acciones"; el estado y los totales quedan en la fila del período), Ficha 360 ("Nueva matrícula"), Exámenes (las acciones de la tarjeta de contexto se suman a "Más acciones" junto a "Nuevo candidato").
- Inicio: sin la tarjeta que repetía los pendientes de aprobación; los bloques de abajo se apilan a todo el ancho (`stack()`), sin hueco.

Probado y descartado (medido):
- Columnas secundarias a su largo natural (`max-content`): tablas con scroll a 1280 suben de 33 a 51.
- Columna principal más angosta (1.3 partes): celdas de 4+ líneas suben de 198 a 249.

Measured: 0 errores de JS en 85 páginas a 1280, 768 y 390; desbordes a 390: 2 (RIDE, Reportes; base 3); 33 tablas con scroll a 1280 (base 38); 0 enlaces rotos; roles intactos.

Scores, eyeballed: mediana de 2 revisores nuevos sin contexto (antes de corregir el hueco de Inicio)

| Shot | Jerarquía | Alineación | Color | Tipografía | Densidad | Consistencia | vs r00 |
|---|---|---|---|---|---|---|---|
| S01 Inicio | 8 | 7 | 9 | 8.5 | 7.75 | 8.5 | mejor |
| S02 Estudiantes | 8.5 | 8.5 | 9.25 | 8.5 | 8.25 | 8.5 | mejor |
| S03 Ficha 360 | 7.5 | 7.25 | 9 | 8 | 7.5 | 8 | mejor |
| S04 Cursos | 8.25 | 7.5 | 8.75 | 8.25 | 7.75 | 8 | mejor |
| S05 Facturas | 7.75 | 8 | 8.75 | 8 | 8 | 7.75 | mejor |
| S06 Factura | 7.75 | 8.25 | 9.25 | 8.5 | 8.25 | 7.75 | mejor |
| S07 Leads | 8.5 | 8 | 8 | 8.5 | 7.75 | 7.5 | mejor |
| S08 Nueva matrícula | 8 | 8 | 9.25 | 8.25 | 7.5 | 8.5 | igual |
| S09 Exámenes | 8.25 | 8 | 8.75 | 8.25 | 7.5 | 8.25 | mejor |
| S10 Comisiones | 8.5 | 7.5 | 9.25 | 8.5 | 8.25 | 8 | mejor |
| Menú lateral | 8 (7.5 y 8.5) | | | | | | mejor |

Top gaps from critics (próxima ronda):
1. Tablas angostas que parten en 3-4 líneas: Reaperturas en Cursos (la peor), Exámenes (examen), Facturas (SRI, cobro), Leads, Comisiones (estado pendiente).
2. Ficha 360: pestañas lejos del título; Rematrícula en 2 x 2 con huecos; columna del perfil corta.
3. Nueva matrícula: ayudas de 2-3 líneas, búsqueda del estudiante al final del paso, paso actual poco marcado.
4. Tarjetas en pares con alturas distintas (Inicio, Factura, Comisiones); Facturas con dos enlaces subrayados por fila.

Stop check: bar no (S02 y S10 cerca: 8-9.25; el resto entre 7 y 9.25) | publicación automática autorizada -> publicado en `main`.

## Round 07

Focus: contenido de las tablas (celdas que parten en 3-4 líneas), porque era el hueco que ambos revisores repetían; más los pendientes de Nueva matrícula.

Changes:
- Cursos · Reaperturas: el curso que termina y su continuidad en una sola columna; 6 columnas en vez de 7; motivo de pérdida corto; sin el primario duplicado en la tarjeta.
- Rematrícula: "Curso que terminó → siguiente" en una sola columna ancha. Automatizaciones: la descripción de la regla es la columna ancha.
- Exámenes: el examen en la primera línea y el centro con la fecha debajo; factura con su estado en la segunda línea; encabezado "Puntaje"; Examen es la columna ancha.
- Facturas, Leads, Comisiones: detalles cortos ("$475 pendiente", "Hijo · Tomás · 9 años", "Pendiente · cuota 2, 16 nov").
- Nueva matrícula: "Buscar estudiante / Nuevo estudiante" al comienzo del paso 1; paso actual relleno en azul; sin referencias a TeamDesk en las ayudas.
- Cabecera de página: las acciones quedan a la altura del h1 aunque el subtítulo sea largo (en tablet y celular bajan debajo).

Measured: celdas con 4+ líneas de texto en tablas visibles a 1366 px: 169 (inicio de la ronda 198); tablas con scroll a 1280: 32 (base 38); 0 errores de JS; desbordes a 390: 2 (RIDE, Reportes; base 3); un desborde nuevo de 6 px en Detalle de matrícula a 768 px apareció y se corrigió en la misma ronda; 0 enlaces rotos; roles intactos.

Scores, eyeballed: mediana de 2 revisores nuevos sin contexto (antes de los dos últimos ajustes: Examen ancho y acciones junto al h1 con subtítulo largo)

| Shot | Jerarquía | Alineación | Color | Tipografía | Densidad | Consistencia | vs r00 |
|---|---|---|---|---|---|---|---|
| S01 Inicio | 8.25 | 7.5 | 8.5 | 8.75 | 7.75 | 8.25 | mejor |
| S02 Estudiantes | 8.5 | 8.25 | 9.25 | 8.75 | 8.25 | 8.25 | mejor |
| S03 Ficha 360 | 7.5 | 7.25 | 9 | 8 | 7 | 7.5 | mejor |
| S04 Cursos | 8.25 | 8 | 8.75 | 8.25 | 7.75 | 8.25 | mejor |
| S05 Facturas | 7.75 | 7.25 | 9 | 8 | 6.75 | 7.25 | mejor |
| S06 Factura | 7.25 | 8 | 9.25 | 8.25 | 8 | 7.5 | mejor |
| S07 Leads | 8.25 | 7.25 | 8.5 | 8 | 6.5 | 7.25 | mejor |
| S08 Nueva matrícula | 8.25 | 8 | 9.25 | 8.75 | 7.25 | 8.25 | mejor |
| S09 Exámenes | 8.25 | 7.25 | 8.5 | 8 | 6.5 | 8.25 | mejor |
| S10 Comisiones | 8.5 | 7.25 | 9 | 8.25 | 7.5 | 8 | mejor |
| Menú lateral | 7.75 (7 y 8.5) | | | | | | mejor |

Top gaps from critics (próxima ronda):
1. Celdas que todavía parten: Facturas (factura, cobro), Leads (origen, interés), Ficha 360 (curso en la pestaña de matrículas).
2. Ficha 360: la columna del perfil termina corta y "Cursos matriculados" repite la tabla de la pestaña.
3. Capacidad en Cursos: leyenda repetida en cada fila; rojo usado para sobrecupo y para "no abre".
4. Facturas: "Vista" más pestañas más control segmentado siguen siendo tres niveles; dos enlaces subrayados por fila.

Stop check: bar no (S02 8.25-9.25; el resto entre 6.5 y 9.25) | publicación automática autorizada -> publicado en `main`.

## Round 08

Focus: los 4 huecos de la ronda 07.

Changes:
- Celdas: factura sin la sede repetida en el detalle; cursos de la Ficha 360 con nombre corto ("Adults · virtual · B1"); enlaces dentro de tablas sin subrayado (subrayado al pasar el cursor).
- Ficha 360: el perfil acompaña el scroll en escritorio (en tablet y celular queda normal, medido).
- Capacidad: cifras en una línea ("4 inscritos · 9 esperados · 2 libres") en vez de una leyenda por fila; sobrecupo en ámbar (requiere acción), rojo solo para "no abre"; barras siempre azules, el color lo lleva el estado.
- Facturas: el selector "Vista" pasa al panel de filtros (filtra igual, medido).
- Menú: el difuminado "Más opciones" ya no tapa el último título.

Revertido en esta ronda (los dos revisores lo marcaron como retroceso de la ronda 07):
- Exámenes con "Examen" como columna ancha: angostaba "Candidato" a 4-5 líneas. Vuelve a ser ancha la columna del candidato.

Measured: celdas con 4+ líneas a 1366 px: 156 (ronda 07: 169; inicio de la ronda 07: 198); tablas con scroll a 1280: 32 (base 38); 0 errores de JS; desbordes a 390: 2 (RIDE, Reportes); 0 enlaces rotos.

Scores, eyeballed: mediana de 2 revisores nuevos sin contexto (antes de revertir Exámenes y de los ajustes de capacidad y menú)

| Shot | Jerarquía | Alineación | Color | Tipografía | Densidad | Consistencia | vs r00 |
|---|---|---|---|---|---|---|---|
| S01 Inicio | 8 | 7.75 | 8.75 | 8.5 | 8 | 8.25 | mejor |
| S02 Estudiantes | 8.5 | 8.25 | 9 | 8.5 | 8.25 | 8.5 | mejor |
| S03 Ficha 360 | 7.5 | 7.25 | 8.5 | 8 | 7.25 | 7.5 | mejor |
| S04 Cursos | 8.5 | 8.5 | 8.5 | 8.5 | 8.25 | 8.25 | mejor |
| S05 Facturas | 7.75 | 8.25 | 8.5 | 8.5 | 8.25 | 8 | mejor |
| S06 Factura | 8.25 | 8.25 | 9 | 8.5 | 8.5 | 7.75 | mejor |
| S07 Leads | 8.25 | 7.5 | 8.5 | 8 | 7.25 | 7.5 | mejor |
| S08 Nueva matrícula | 8.25 | 8 | 8.75 | 8.5 | 7.75 | 8.5 | mejor |
| S09 Exámenes | 8.25 | 6.75 | 8.5 | 7.75 | 6.5 | 8 | igual / mejor (retroceso por la columna ancha, revertido) |
| S10 Comisiones | 8 | 7.75 | 9 | 8.5 | 8 | 8 | mejor |
| Menú lateral | 8 (8 y 8) | | | | | | mejor |

Top gaps from critics (próxima ronda):
1. Leads: 7 columnas; origen, interés y quién estudia todavía parten en 2-3 líneas.
2. Ficha 360: pestañas debajo de las tarjetas; nombres de curso distintos entre la lista y la tabla.
3. Factura y Comisiones: tarjetas con datos en texto corrido (SRI, Efecto en la matrícula) y alturas desparejas; resumen del período de Comisiones como texto suelto.
4. Inicio: "Accesos rápidos" con 8 botones repite el menú.

Stop check: bar no (S04 y S06 llegan a 8.25-9 salvo una dimensión; el resto entre 6.5 y 9) | publicación automática autorizada -> publicado en `main`.
