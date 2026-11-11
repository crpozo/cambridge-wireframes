# Informe · qué tenía `main` y qué se agregó al prototipo (rematrícula, facturación, capacidad, pagos, entregas de libros y tablero comercial)

Rama: `prototipo/rematricula-entregas-digitales` (sale de `main`, solo local). Fecha: 10 de noviembre de 2026.
Fuentes: sesión con Secretaría Quito del 5 de nov (transcripción y resumen), métricas del plan estratégico comercial de Dirección Comercial, requerimiento de entrega digital de libros del módulo de Inventario, y `docs/CONTEXTO_PROYECTO_CAMBRIDGE.md`.

**Alcance de este trabajo**: solo mockups HTML (prototipo navegable). No hay backend ni datos reales; las cifras y nombres son ficticios. Lo que se marca "viable" significa "viable de construir en la plataforma real", no que ya funcione.

## 1. Resumen

| # | Requerimiento | En `main` | En esta rama | Viabilidad |
|---|---|---|---|---|
| 1 | Automatizar la rematrícula desde las notas | Parcial | Pantalla `Rematricula.html` | Semi-automática: viable. 100 % automática: depende del Muro (Moodle) |
| 2 | Facturar dentro de la matrícula | Parcial (solo venta nueva) | `RematriculaFactura.html` | Viable |
| 3 | Monitorear capacidad y ocupación | Parcial (cupo, no proyección) | Tabla de ocupación proyectada en Cursos y Rematrícula | Viable (parámetros por confirmar) |
| 4 | Sincronizar pagos por transferencia | No | Vista "Conciliación bancaria" en Facturación → Cobros | Importar extracto: viable. API directa del banco: no, sin convenio |
| 5 | Entrega de libros 100 % digital | No (solo stock y etiquetas) | `EntregasLibros`, `EntregarLibro`, `ReciboEntrega` | Viable; WhatsApp fuera de alcance |
| 6 | Tablero comercial del plan estratégico | Parcial | Pestaña "Plan estratégico" | Viable; 3 indicadores necesitan definición |

## 2. Auditoría detallada de `main`

### 2.1 Rematrícula (Secretaría, 5 nov)
**Dolor**: buscar al estudiante por apellido, copiar el código del curso, ir a matricular, salir a Facturación. Las notas no están conectadas con la matrícula: Secretaría espera a que Académico avise.

**Ya estaba**: protocolo de reaperturas en `Cursos.html` (WhatsApp → llamada → nota de voz al 75 %); `CalificarCurso.html` con reglas de cierre; en el portal, "Rematricularme" se activa con avance 100 % y nota ≥ 7 (propuesta fuera de alcance); `Facturas.html` → Ajustes → "Rematrículas por confirmar"; `MatriculaContinuidad.html` para aplicar saldo a favor.

**Faltaba**: un lugar donde el cierre de notas dispare el aviso y deje la matrícula lista en el siguiente curso; ver quién está bloqueando porque el profesor no pasó notas.

**Agregado**: `Rematricula.html` (nuevo, menú Académico). Franja de resumen viva (esperando notas, alerta enviada, sin factura, por conciliar, confirmadas), flujo automático de 5 pasos, tabla filtrable, pestaña de capacidad y pestaña de reglas (cuándo se dispara, condiciones, qué hace el sistema, reserva de cupo, aviso). Estados: "Sin factura" refleja la matrícula "en rojo" de TeamDesk. En `DetalleCurso.html` se agregó la acción "Rematricular estudiantes".

**Viabilidad**:
- Modo "Sugerir, Secretaría confirma con un clic": **viable**. Las notas se cierran en la plataforma (M3), así que el disparador existe sin depender de nadie.
- Modo "Matricular y facturar sola": **depende del Muro (Moodle)** si la condición es el avance del estudiante. M11 lo contempla "sujeto a lo que exponga", y el contexto del proyecto registra que el cliente lo dejó "requiere más debate". Se deja como opción en las reglas, con aviso, y requiere aprobación de Gerencia.
- Un curso siguiente que aún no existe (módulos pagados por adelantado): se avisa a Coordinación para crearlo; la bolsa de módulos ya cubre el pago.

### 2.2 Facturación integrada a la matrícula
**Ya estaba**: `NuevaVenta.html` ya incluye factura y pago en el mismo asistente (paso 4) para ventas nuevas; vista "Sin vincular" para facturas sueltas.

**Faltaba**: el caso real de Secretaría, que es la **rematrícula de un estudiante antiguo**: matricular, generar los ítems, registrar el pago y adjuntar el comprobante sin cambiar de pestaña.

**Agregado**: `RematriculaFactura.html` (nuevo): estudiante y siguiente curso (con cupo), valores y descuento recalculable, factura con servicios educativos y productos en líneas separadas, módulos que paga ahora (el módulo adelantado queda **ligado a la bolsa**, no suelto), pago con comprobante y banco de origen, y resumen lateral. Dos salidas: "Matricular y facturar" o "Matricular sin facturar" (deja la alerta a las 24 h).

**Viabilidad**: **viable**; es composición de M2, M3 y M5.

### 2.3 Capacidad de aulas y ocupación
**Ya estaba**: cupo por grupo con bloqueo al llenarse; capacidad por aula (criterio SETEC) en Configuración; un insight de ocupación por aula.

**Faltaba**: el porcentaje de ocupación **proyectado** de los cursos por abrir, para decidir si abren, se refuerzan o se divide el grupo.

**Agregado**: tabla "Capacidad y ocupación de los cursos por abrir" en `Cursos.html` y en la pestaña de capacidad de `Rematricula.html`. Fórmula: inscritos + (estudiantes que terminan × índice de retención) sobre la capacidad del aula. Estados: riesgo de no abrir (< 6 inscritos), por llenar, buena ocupación (≥ 80 %), sobrecupo.

**Viabilidad**: **viable**. Parámetros a confirmar con el cliente: el índice de retención usado (71 %, del tablero) y el mínimo para abrir (6, de la nota del propio prototipo).

### 2.4 Sincronizar pagos por transferencia
**Ya estaba**: "Pagos por validar" (asesor registra y sube comprobante → Contabilidad valida en el banco → Secretaría confirma). Todo manual; el número de comprobante se digita.

**Agregado**: vista **"Conciliación bancaria"** en Facturación → Cobros: se importa el extracto, la plataforma busca cada ingreso por monto, fecha y referencia, y valida sola lo que coincide. Maneja el caso real de las transferencias interbancarias (referencia distinta a la del comprobante del cliente → "Revisar", coincidencia por monto, fecha y nombre) y los ingresos sin pago registrado.

**Viabilidad**:
- **Importar el extracto (Excel o CSV) y conciliar: viable** y entra en M5.
- **Conexión directa con el banco por API: no es viable por ahora**. Depende de que el banco ofrezca una API empresarial y de un convenio; no es algo que la plataforma controle. Se marca como propuesta.
- **Lectura automática de comprobantes (OCR) y verificación con Nuvei**: ya están listadas como fuera de alcance (punto 11 del contexto).
- Pagos en línea (links Datafast/Nuvei) se conciliarían contra el historial de la pasarela, no contra el banco; es otra integración.

### 2.5 Entrega de libros 100 % digital (módulo Inventario)
**En `main`**: stock por sede, ingresos del proveedor, códigos de activación (`Inventario.html`, `Movimientos.html`, pestaña "Códigos de libros" de la matrícula), y un botón "Imprimir etiquetas de libros" en la matrícula. **No existía** ningún flujo de entrega, firma, recibo ni reporte de quien no retiró.

**Agregado** (ver sección 3 para el diseño):
- `EntregasLibros.html` (menú Inventario → Entregas de libros): lista de entregas con estados, reporte de matriculados sin retirar, alertas de stock bajo por nivel y sede, y explicación del flujo.
- `EntregarLibro.html`: pantalla pensada para la tablet.
- `ReciboEntrega.html`: recibo en PDF.
- Cambios en pantallas existentes: `NuevaVenta` ya no ofrece imprimir etiquetas; al confirmar se crea la entrega pendiente; la pestaña "Códigos de libros" de la matrícula enlaza al recibo y a la entrega pendiente; el Inicio de Secretaría suma el pendiente.

### 2.6 Tablero comercial (métricas del plan estratégico)
| Indicador pedido | En `main` | Ahora |
|---|---|---|
| Ingreso mensual total | Sí (total facturado) | Tarjeta + tendencia vs 2025 |
| Ingresos por línea de negocio | Parcial (tabla por concepto) | Barras |
| Certificados / traducciones vendidos | Solo en la matriz KPI de Valle | Tarjetas y barras, todas las sedes |
| Ingresos por productos | Parcial | Barras por línea de negocio |
| Ticket promedio mensual | Sí (matriz Valle) | Tarjeta + tendencia |
| % estudiantes en planes de nivel | **No** | Medidor |
| % one to one vs regulares | Solo conteo | Barra porcentual |
| Ingresos por tipo de programa | Parcial | Barras por programa |
| % upsell por asesor | **No** | Tabla y barras |
| % conversión lead → matrícula | Sí (Leads) | Tarjeta y evolución mensual |
| % deserción mensual | **No** | Evolución mensual (definición pendiente) |
| % matrículas por referidos | Parcial | Medidor |
| % leads atendidos | **No** | Medidor |
| Conversión por canal | Parcial | Barras |

Además: 11 tarjetas principales (ingreso, matrículas, niveles, ticket, one to one, certificados, traducciones, total de servicios, ticket de servicios, cumplimiento de la meta, variación vs año anterior), líneas para evolución y comparativos (ingresos y matrículas, ticket, real vs meta, año anterior, conversión y deserción), barras para comparar (sede, línea, programa, asesor, origen, canal), circulares para porcentajes, **embudo de Kommo** con porcentaje entre etapas y conversión total, y una **matriz consultable y exportable** por sede, asesor, producto, programa y canal. Los filtros por período, sede, asesor, programa, producto y origen ya existían en la parte superior del tablero; el walk-in se abre por '¿cómo nos conoció?' en la pestaña Por origen. Falta confirmar si se necesita un filtro propio de clasificación de walk-in.

**Viabilidad**: **viable** en general. Tres indicadores necesitan definición (sección 5). El embudo depende de la API de Kommo (M11), traería solo totales agrupados y el lead individual solo al ganarse, como ya estaba decidido.

## 3. Diseño del flujo de entrega digital de libros

**Principio**: no se imprime nada. Ni recibo en impresora de facturas, ni cinta, ni firma a mano, ni etiquetas.

```
Matrícula confirmada
   └─ se crea sola la entrega pendiente (libro del nivel, solo el del primer nivel)
        └─ Secretaría abre la entrega en la tablet (busca al estudiante o escanea el código de barras)
             └─ revisa: libro correcto · completo y en buen estado · datos del estudiante
                  └─ firma: con el dedo en la tablet, o desde su celular con un QR (menor de 18: firma el representante)
                       └─ confirmar → recibo en PDF (estudiante, libro, fecha, hora, quién entregó, firma)
                            ├─ queda en la ficha del estudiante
                            ├─ sale por correo
                            ├─ se descuenta el stock de la sede en ese momento
                            └─ la entrega pasa a "Entregada" y el checklist de bienvenida se marca solo
```

**Estados de una entrega**: Lista para entregar · Sin stock (esperando compra) · Sin retirar (más de 7 días) · Entregada.

**Pantalla de la tablet** (`EntregarLibro.html`): campo grande para escanear, tres pasos numerados, casillas de 24 px (objetivo táctil ≥ 44 px), zona de firma de 230 px de alto con trazo real (se puede dibujar en el prototipo), alternativa por QR con simulación de "firma recibida", y el botón de confirmar fijo abajo. Si falta revisar o firmar, avisa qué falta. En el prototipo la firma dibujada **sí aparece en el recibo**.

**Reportes pedidos**:
- *Matriculados que aún no retiran su libro*: pestaña "Sin retirar" con días transcurridos, a quién se contactó y recordatorios.
- *Alertas de stock bajo por nivel y sede*: pestaña "Alertas de stock" con stock, mínimo y entregas por hacer; se apoya en el correo diario de las 07:00 que ya existía.

**Datos que habría que guardar** (para el modelo real): entrega (matrícula, producto, sede, estado, creada, entregada, entregó, receptor, firma, vía de firma, hash del PDF), ligada a la matrícula, la ficha y el movimiento de inventario.

## 4. Lo que no jala, no es viable o necesita adenda

1. **Envío del recibo por WhatsApp** (y recordatorios por WhatsApp): fuera del alcance (punto 12 del contexto). Requiere la API oficial de Meta, plantillas aprobadas y tiene costo por mensaje. Se dejó solo por correo y con etiqueta "Propuesta".
2. **Escaneo con la cámara de la tablet**: en el prototipo está **simulado**. En la plataforma real la lectura por cámara en el navegador es inconsistente (iOS y algunos navegadores); lo seguro es una librería de lectura (por ejemplo ZXing) o un **lector USB**, que se comporta como teclado y ya funciona con el campo de la pantalla. Conviene confirmar qué tablet usarán.
3. **Firma desde el celular con QR**: el QR del prototipo es de ejemplo y no se puede escanear. En la realidad necesita un enlace de un solo uso, con vencimiento, y una página móvil mínima. Es viable pero es una pieza extra de desarrollo.
4. **Firma como evidencia legal**: es firma simple (como la aceptación electrónica del contrato). Si Cambridge necesita firma certificada, es adenda (punto 9).
5. **Rematrícula 100 % automática sin Secretaría**: depende del Muro y de la creación de grupos; no se puede prometer hasta confirmar qué expone Moodle (punto 14).
6. **Conexión directa con el banco, OCR de comprobantes y verificación con Nuvei**: no viables sin terceros; ver 2.4.
7. **Embudo desde Kommo**: viable solo si el plan de Kommo expone la API necesaria (ya figura como pendiente de accesos: plan Advanced).
8. **Si el prototipo se muestra como "ya funciona"**: no. Es una maqueta navegable; la firma, el QR y el escáner son demostraciones.

## 5. Preguntas abiertas para el cliente
- **Deserción mensual**: ¿cómo se define? Propuesta: estudiantes que terminan un módulo y no se rematriculan en 30 días, sobre los que terminaron.
- **% estudiantes en planes de nivel**: ¿sobre qué base? Propuesta: matriculados activos que compraron nivel completo (2 módulos o más) sobre el total de activos.
- **% upsell**: ¿qué cuenta como upsell? Propuesta: venta que incluye un servicio adicional (examen, tutoría, simulador, niveles extra).
- **Leads atendidos**: ¿qué etapa de Kommo significa "atendido"? Propuesta: los que tienen al menos un contacto del asesor.
- **Rematrícula**: índice de retención de referencia, mínimo para abrir un curso (¿6?), horas de reserva del cupo (¿72?), y si Gerencia aprueba el modo automático.
- **Entrega de libros**: ¿qué tablet y qué lector? ¿Cuántos días sin retirar antes del recordatorio? ¿Quién firma por un menor?
- **Cuenca**: sigue fuera del consolidado de Quito, Valle y Ambato, como estaba decidido; se muestra aparte.

## 6. Cosas que salieron en la sesión y no se tocaron (siguiente iteración)
- **Cierre de caja digital**: hoy se imprimen la lista de pagos, de ventas y de matrículas, y se pegan comprobantes físicos. Es el mayor consumo de papel y tiempo de Secretaría; una lista de pagos con casillas de verificación y exportación firmada lo reemplazaría.
- **Facturas autorizadas por el SRI a las 2 horas**: el prototipo ya tiene el estado de autorización; falta el contador y la alerta de las rechazadas.
- **Cálculo automático de fecha de fin de un curso** con feriados cargados (el módulo 3, 4 y siguientes se crean a mano).

## 7. Cómo probar el prototipo
1. `python -m http.server 8765` dentro de la carpeta del repo, y abrir `http://localhost:8765/`.
2. Entrar con cualquier rol (por ejemplo Secretaría, con "Ver como") → Inventario → **Entregas de libros** → "Abrir entrega con escáner".
3. En la tablet: escanear, marcar las tres revisiones, firmar con el dedo (o con el mouse) y confirmar. El recibo muestra la firma que dibujaste.
4. Académico → **Rematrícula** → "Matricular y facturar" en un estudiante con alerta enviada.
5. Facturación → Cobros → **Conciliación bancaria**. Cursos → "Capacidad y ocupación". Tablero comercial → **Plan estratégico**.

## 8. Archivos
Nuevos: `EntregasLibros.html`, `EntregarLibro.html`, `ReciboEntrega.html`, `Rematricula.html`, `RematriculaFactura.html`, `assets/entregas.js`, este informe. Modificados: `tools/generar_pantallas.py` (todo se genera desde ahí) y las páginas que reflejan el nuevo menú.

## 9. Datos del curso nuevo y creación de módulos (revisión de fuentes, 10 nov)
Pregunta: ¿alguna fuente dice que la plataforma debe contener docente, aula, fecha de fin, horas totales, progreso y código del LMS, y debe permitir crear un módulo nuevo?

| Dato | ¿Lo piden las fuentes? | Estado |
|---|---|---|
| Docente | Sí. `docs/PROYECTO.md` (M3): "asignación de profesor con validación de contrato activo". | En alcance |
| Aula | Sí. M3: "creación de cursos (programa, nivel, modalidad, horario, aula)". | En alcance |
| Progreso del curso | Sí, literal. Contrato, Cláusula Tercera, M3: "gestión, seguimiento (tracking) y progreso". | En alcance |
| Fecha de finalización y horas totales | No literal. Son parte del horario del curso; ya estaba decidido calcular la fecha de fin saltando feriados (`docs/DECISIONES.md`). | En alcance como detalle de M3 |
| Código y plataforma LMS | **No**. Ni el contrato ni la propuesta lo piden como campo. Solo existe como proceso manual (crear el curso en Cambridge One y GradeKeeper 72 h antes, `docs/PROCESOS_INTERNOS.md`) y Moodle figura en M11 "sujeto a la API que expongan". Nació en la sesión del 5 nov. | Requerimiento nuevo |

- **Código LMS**: guardarlo como campo informativo es trivial y cabe en M3; **sincronizarlo con el LMS** depende de M11 y de lo que Moodle o Cambridge One expongan. Se dejó como campo de texto con esa advertencia. Conviene confirmarlo con el cliente.
- **Crear un módulo nuevo**: sí debe permitirlo. M3 incluye la creación de cursos y `NuevoCurso.html` ya existía. En la sesión, Secretaría crea a mano cada módulo siguiente (módulo 3, 4…) y la plataforma calcula el fin con los feriados cargados. Falta decidir si algún día se crean solos los módulos que quedan en la bolsa; hoy no está pedido.

**Cambios en el prototipo**: en `RematriculaFactura.html` la nueva tarjeta "2 · Curso nuevo" muestra el curso con programa, módulo, docente, aula, plataforma LMS, días y horario, inicio, fin, horas totales, cupo, valor y progreso. Si el módulo aún no tiene curso, la segunda opción permite **crearlo sin salir de la matrícula** (docente, aula, código LMS, horario, fecha de inicio, fin calculado, horas y cupo) o abrir el formulario completo. `NuevoCurso.html` y el detalle del curso suman el campo "Código en el LMS".



## 10. Notas académicas → matrícula: aviso automático al cerrar las notas (revisión de 10 nov)
**Dolor**: el sistema actual no conecta la aprobación de notas con la matrícula. Secretaría espera a que Académico termine y le avise; cada correo y cada matrícula se hacen a mano.

**Qué había en `main`**: `CalificarCurso.html` con reglas de cierre (≥ 7 aprueba, 6.50–6.99 recuperación, deuda bloquea la nota), el protocolo manual de reaperturas y, desde esta rama, `Rematricula.html` con los estados y las reglas. Faltaba **mostrar qué se dispara al cerrar las notas**, el **correo** que recibe el estudiante y el **registro** de lo enviado.

**Qué se agregó al prototipo**
- `CalificarCurso.html`: tarjeta "Qué se dispara solo al cerrar las notas" con cuatro grupos (aprobados sin deuda, aprobados con deuda, bloqueados por asistencia, reprobados), qué recibe cada uno y qué queda en el sistema.
- `Rematricula.html`, pestaña **Avisos automáticos**: vista previa del correo en tres variantes (aprobado, recuperación, con deuda), cifras de envío (confirmaron, abiertos, sin abrir, rebotaron) y registro por estudiante. Reglas: reenvío a las 48 h; a las 72 h se libera el cupo y se avisa a Secretaría.
- Secretaría recibe una **notificación** y una **tarea** en su Inicio ("Notas cerradas: A1 Sábados · 8 listos para rematricular"): ya no espera a que Académico le avise.
- Los aprobados con deuda no reciben la nota hasta regularizar; los de recuperación o bloqueados por asistencia no se rematriculan solos (decide Coordinación).

**Viabilidad y condiciones**
- **El disparador funciona solo si las notas se registran en la plataforma** (M3 incluye "notas pass/fail"). El proceso actual del cliente registra las notas en **GradeKeeper** (`docs/PROCESOS_INTERNOS.md`) y el contrato solo contempla integraciones con Kommo, Moodle y Dora (M11). Si las notas siguen viviendo en GradeKeeper, esta automatización necesita una integración que **no está en el contrato**. Es la pregunta clave para el cliente.
- **"Sin intervención manual" total**: el aviso y la matrícula propuesta sí son automáticos. La confirmación final depende del pago del estudiante y de que exista el curso siguiente con cupo; si no existe, se avisa a Coordinación para crearlo.
- **Correo al estudiante**: la plataforma ya necesita enviar correos por el contrato (aceptación del contrato, recordatorios de cuotas), pero las notificaciones a estudiantes "más allá de las internas" figuran como fuera de alcance (punto 17 del contexto) y dependen de un proveedor de correo transaccional. Conviene **confirmar si el aviso de rematrícula entra en ese correo ya contratado**. **WhatsApp**: propuesta aparte (punto 12).
- **Enlace "Confirmar mi matrícula y pagar"**: apunta al portal del estudiante, que es una propuesta fuera del alcance. Sin portal, el enlace llevaría a una página de pago simple o el estudiante respondería al correo.
- El texto de los correos, los plazos (48 h, 72 h) y quién puede cerrar notas son supuestos por confirmar con Coordinación Académica.


## 11. Descuentos, políticas de módulos y aprobador (revisión de 10 nov)
**Lo que dijo Secretaría**: al crear la matrícula se aplican descuentos por pagar dos módulos o el nivel completo (la política más común), y otros casos como hermanos que necesitan revisión y aprobación administrativa. Antes de guardar la matrícula en estado pendiente de facturación se debe registrar el nombre de quien aprobó el descuento.

**Qué había en `main`**
- Tabla de descuentos con motivos (referido, hermanos, promoción, convenio, "Beneficio cancela 2 módulos", indexado) y regla "hasta 10 % lo aplica el asesor; más pasa a aprobación" (`docs/DECISIONES.md`).
- Bandeja de Aprobaciones y `SolicitudDescuento.html`.
- **Faltaba**: dónde se registra **quién aprobó**. En la rematrícula era un campo de texto libre y opcional; en Nueva matrícula no existía. Los hermanos entraban como "10 %" sin aprobación.

**Qué se agregó al prototipo**
- **Bloque "Aprobación del descuento"** (aprobado por, referencia, fecha y hora automática) en Nueva matrícula, Matrícula desde lead y Matrícula y factura. **Solo aparece cuando hace falta**: descuento por encima del límite del asesor, hermanos o beneficios por pago de módulos.
- **Bloqueo al guardar**: mientras no se elija quién aprobó, los botones de confirmar o guardar la matrícula no avanzan y avisan qué falta. Con aprobador registrado, se abre la confirmación normal.
- "Hermano o familiar matriculado" ahora figura "requiere aprobación".
- Tarjeta desplegable **"Ver políticas de descuento"** junto al selector, con cada motivo, su porcentaje y si necesita aprobación.
- `DetalleMatricula.html` muestra "Aprobado por" (en el ejemplo, "No requerido · dentro del límite del asesor").
- "Matricular sin facturar" deja la matrícula en **estado pendiente de facturación** con el aprobador registrado.

**Por confirmar con el cliente**
- **Los porcentajes reales.** Hay una inconsistencia que ya existía: el manual de procesos habla de **10 %** por pagar 2 módulos (reaperturas) y la tabla de ejemplo del prototipo dice **20 % y pasa a aprobación**. La tabla real la deben enviar Dirección Comercial y Administración. Hasta entonces los valores son ilustrativos.
- **Quién puede aprobar** cada tipo (el prototipo ofrece Dirección Comercial, Administración General y Gerencia General) y si la aprobación se pide dentro de la plataforma (bandeja de Aprobaciones) o se registra después de aprobarla por fuera.
- **Hermanos**: ¿siempre requieren aprobación, o solo a partir de cierto porcentaje?
- **Validación real**: en el prototipo el bloqueo es una demostración en el navegador. En la plataforma debe validarse en el servidor y quedar en el audit log (aprobador, fecha, descuento, matrícula).


## 12. Facturación vinculada a la matrícula, sin cambiar de pestaña (revisión de 10 nov)
**Lo que dijo Secretaría**: hoy hay que pasar de cursos a matrículas y de ahí a facturas, lo cual es tedioso. Al estar matriculado el estudiante, la matrícula se vincula y genera los ítems de la factura, con **servicios educativos** y **productos** (materiales) claramente diferenciados. Hoy, al registrarse todo como "producto", no se puede saber cuántos módulos se facturan realmente.

**Qué había en `main`**: Nueva matrícula ya incluía factura y pago en un solo asistente para ventas nuevas; la factura ya tenía columna "Tipo" (servicio o producto); la vista "Sin vincular" cubre las facturas sin matrícula. Faltaba el camino inverso y el caso real de Secretaría: **partir de una matrícula o de un curso y facturar desde ahí**.

**Qué se agregó al prototipo**
- **Matrícula y factura** (`RematriculaFactura.html`): la factura muestra "Ítems generados desde la matrícula 001-…", vinculada a ella, con botón "Volver a generar ítems". Los ítems se separan en **Servicios educativos** (módulos, inscripción, con su código y origen: matrícula o bolsa de módulos) y **Productos** (libros y materiales), cada uno con su subtotal y un botón "Agregar producto". Se muestra cuántos módulos se facturan.
- **Detalle de curso**: en la lista de estudiantes aparece el estado "Matriculada · sin factura" (en rojo, como en TeamDesk) con la acción **Facturar** directa, y un filtro "Sin factura". El saldo del curso se actualiza.
- **Detalle de matrícula**: botón "Generar factura" (aquí deshabilitado porque la matrícula ya está facturada, con el motivo) y, en la pestaña de facturas, la vinculación: "la factura 000021090 está ligada a esta matrícula: servicios educativos $900 y productos $80".
- **Facturación**: nueva vista **"Matrículas sin factura"** (cifras: cuántas, valor por facturar, más de 24 h, con acción Facturar por fila) y la opción **"Desde una matrícula existente"** en el menú "Nueva factura".

**Viabilidad**: **viable y dentro del alcance** (M5, con M2 y M3): el contexto del proyecto ya dice "factura con varios ítems con código y material sugerido editable" y "una factura por venta con todos los ítems". La separación entre servicios y productos permite contar módulos facturados, lo que hoy no se puede; depende de definir bien los códigos de los ítems en el catálogo (Configuración).

**Por confirmar**: si el **IVA** o las reglas del SRI son distintos entre servicios educativos y productos (el prototipo muestra servicios con IVA 0 %); el catálogo real de códigos por módulo y por libro; y si la factura puede editarse una vez generada o solo regenerarse. Las pantallas de Facturar de cursos y matrículas apuntan a una misma pantalla de ejemplo (la de Camila Sánchez); en la plataforma real cargarían los datos de cada matrícula.


## 13. Cursos futuros sin crear, fechas de fin con feriados y multimódulos (revisión de 10 nov)
**Lo que dijo Secretaría**: cuando un estudiante paga varios módulos por adelantado, los cursos futuros (por ejemplo los de febrero) todavía no existen y se crean a mano, calculando la fecha de fin y los feriados. En la primera factura se usa la sección de multimódulos para registrar cuántos módulos se pagaron; cuando no hay matrícula vinculada, hay que buscar a mano el producto del módulo (el 5 o el 6) y agregarlo a una factura suelta para asignarlo después a un curso.

**Qué había en `main`**: `NuevoCurso.html` con una fecha de fin "calculada" (solo un texto), un calendario de feriados 2026 en Programas, y la bolsa de módulos visible solo en la ficha y el portal del estudiante. **Faltaba**: calcular la fecha de fin de verdad, ver **qué cursos hay que crear** según lo que ya se pagó y **asignar** esos módulos sin una factura suelta.

**Qué se agregó al prototipo**
- **Calendario del curso con cálculo real** (Nuevo curso y la creación de un curso dentro de la matrícula): se elige fecha de inicio, días de clase, horas por sesión y total de horas, y la pantalla calcula la **primera clase, el fin, el número de sesiones y los feriados saltados**. Ejemplo: desde el 1 de febrero de 2027, con Lu-Ma-Mi-Ju y 36 h, salta el Carnaval (8 y 9 feb) y termina el 4 de marzo. El resultado llena el campo "Fecha fin".
- **Bolsa de módulos** (`Rematricula.html`, nueva pestaña): "Cursos que faltan por crear" (cuántos estudiantes ya pagaron cada módulo, fecha sugerida y cuántos faltan para el mínimo de 6) y "Quién pagó qué módulo" (estudiante, módulo, factura y fecha de pago). Cada fila lleva a **Crear curso**, y hay una acción **"Matricular a los que ya pagaron"**.
- **Nuevo curso** suma "Estudiantes con este módulo ya pagado": al crear el curso se matriculan con su módulo, **sin emitir otra factura**.
- **Sin factura suelta**: el módulo adelantado queda guardado en la factura original y en la bolsa (ver sección 12); ya no hay que buscar el producto del módulo y agregarlo a mano.

**Viabilidad**: **viable y dentro del alcance** (M3 creación de cursos, M5 bolsa de módulos y factura multi-módulo).

**Por confirmar con el cliente**
- **Feriados**: los de 2027 del prototipo son de ejemplo. Los feriados móviles y los "puentes" los fija el Gobierno por decreto, así que el calendario debe cargarse cada año y poder editarse; también los locales (por ejemplo, el 6 de diciembre en Quito).
- **Creación automática**: hoy la persona crea el curso a mano con la ayuda de la bolsa. Crear automáticamente los cursos cuando se junte la demanda no está pedido ni contratado; es una posible mejora.
- **Mínimo para abrir (6)** y la **regla de una o dos semanas** que mencionó Secretaría sobre la duración según el horario: hay que confirmarlas.
- La fecha de fin depende de las sesiones regulares; **reposiciones, recuperaciones o cambios de profesor** no se reflejan en el cálculo.


## 14. Facturas sueltas y notas de crédito por cambio de modalidad o de curso (revisión de 10 nov)
**Lo que dijo Secretaría**: los servicios adicionales (tutorías, simuladores) generan facturas sueltas sin matrícula, y para encontrar la factura del módulo siguiente hay que revisarlas todas a mano. Además, cuando hay un cambio de modalidad o de curso que modifica el valor se hace una **nota de crédito**, y la factura original queda en el historial.

**Qué había en `main`**: una vista "Sin vincular" con tres casos y un botón de vincular sin contexto; `NotaCredito.html` como formulario simple con las reglas del contrato de servicios; y un listado de notas de crédito. **Faltaba** distinguir las facturas que de verdad hay que revisar de las que no, sugerir a dónde pertenece cada una, y **calcular** qué corresponde cuando cambia el valor.

**Qué se agregó al prototipo**
- **Facturas sueltas clasificadas por concepto** (Facturación → Facturas → "Sin vincular"): cada factura lleva su concepto (módulo adelantado, matrícula, convenio, tutoría, simulador, traducción, libro) y un estado: **"Requiere acción"** (módulos o matrículas sin vincular) o **"Servicio independiente"** (tutorías, simuladores, traducciones y libros, que se ligan a la ficha del estudiante y no necesitan matrícula). Con cifras y filtros, solo las que requieren acción quedan pendientes (en el ejemplo, 4 de 8).
- **Sugerencia del sistema** por cada una ("Bolsa de módulos · módulo 5, coincide valor y fecha", "Matrícula 001-202603265, misma persona y valor") y acciones: vincular a la bolsa, vincular a matrícula, asignar estudiantes de un convenio.
- **Nota de crédito con cálculo** (`NotaCredito.html`): motivos "Cambio de modalidad" y "Cambio de curso u horario". Al elegir modalidad actual, modalidad nueva y número de módulos, la pantalla dice si corresponde **nota de crédito** (el valor baja), **cobro adicional** (sube) o **solo mover la matrícula** (igual), y llena el monto. Ejemplo: presencial $275 a virtual $250 da una nota de crédito de $25. Incluye la decisión de **volver a facturar** y el flujo "qué pasa con la factura original".
- **Historial**: la factura original **no se borra**: queda con el estado **"Ajustada · NC-…"** en el listado y la nota de crédito enlaza a la factura nueva (listado de notas con el nuevo caso).

**Viabilidad**: **viable y dentro del alcance** (M5 incluye "notas de crédito" y el contexto del proyecto ya describe la factura con ítems con código). Clasificar las facturas depende de que cada ítem del catálogo (Configuración) tenga su tipo: módulo, tutoría, simulador, traducción, libro.

**Por confirmar con el cliente**
- Los **precios por modalidad** del cálculo ($250 virtual y $275 presencial por módulo) salen de los datos de ejemplo; deben venir del catálogo real.
- **Devoluciones en dinero**: el contrato de servicios retiene el 10 % antes de iniciar y no devuelve inscripción; la calculadora cubre solo el cambio de valor, no esas devoluciones.
- **SRI**: la nota de crédito debe autorizarse en el SRI. La plataforma la registra, pero emitirla directamente al SRI no está contratado (depende de Dora, módulo 11, o es adenda).
- **Facturas ya pagadas**: si la factura original está pagada y la nota de crédito deja saldo a favor, hay que decidir si se devuelve o se aplica al siguiente módulo (hoy el prototipo ofrece "queda como saldo a favor").
- Hasta cuándo se puede ajustar una factura (cierre contable del mes) y quién puede emitir la nota de crédito.
