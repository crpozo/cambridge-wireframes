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
        └─ Secretaría abre la entrega en la tablet (busca al estudiante por nombre, cédula o matrícula)
             └─ revisa: libro correcto · completo y en buen estado · datos del estudiante
                  └─ firma: con el dedo en la tablet, o desde su celular con un QR (menor de 18: firma el representante)
                       └─ confirmar → recibo en PDF (estudiante, libro, fecha, hora, quién entregó, firma)
                            ├─ queda en la ficha del estudiante
                            ├─ sale por correo
                            ├─ se descuenta el stock de la sede en ese momento
                            └─ la entrega pasa a "Entregada" y el checklist de bienvenida se marca solo
```

**Estados de una entrega**: Lista para entregar · Sin stock (esperando compra) · Sin retirar (más de 7 días) · Entregada.

**Pantalla de la tablet** (`EntregarLibro.html`): campo grande para buscar al estudiante, tres pasos numerados, casillas de 24 px (objetivo táctil ≥ 44 px), zona de firma de 230 px de alto con trazo real (se puede dibujar en el prototipo), alternativa por QR con simulación de "firma recibida", y el botón de confirmar fijo abajo. Si falta revisar o firmar, avisa qué falta. En el prototipo la firma dibujada **sí aparece en el recibo**.

**Reportes pedidos**:
- *Matriculados que aún no retiran su libro*: pestaña "Sin retirar" con días transcurridos, a quién se contactó y recordatorios.
- *Alertas de stock bajo por nivel y sede*: pestaña "Alertas de stock" con stock, mínimo y entregas por hacer; se apoya en el correo diario de las 07:00 que ya existía.

**Datos que habría que guardar** (para el modelo real): entrega (matrícula, producto, sede, estado, creada, entregada, entregó, receptor, firma, vía de firma, hash del PDF), ligada a la matrícula, la ficha y el movimiento de inventario.

## 4. Lo que no jala, no es viable o necesita adenda

1. **Envío del recibo por WhatsApp** (y recordatorios por WhatsApp): fuera del alcance (punto 12 del contexto). Requiere la API oficial de Meta, plantillas aprobadas y tiene costo por mensaje. Se dejó solo por correo y con etiqueta "Propuesta".
2. **Libros sin código de barras**: los libros de Cambridge no traen código de barras, así que no hay escaneo. La entrega se abre buscando al estudiante (nombre, cédula o matrícula) o desde la lista de pendientes, y la recepción de pedidos se cuenta con botones + y −.
3. **Firma desde el celular con QR**: el QR del prototipo es de ejemplo y no se puede escanear. En la realidad necesita un enlace de un solo uso, con vencimiento, y una página móvil mínima. Es viable pero es una pieza extra de desarrollo.
4. **Firma como evidencia legal**: es firma simple (como la aceptación electrónica del contrato). Si Cambridge necesita firma certificada, es adenda (punto 9).
5. **Rematrícula 100 % automática sin Secretaría**: depende del Muro y de la creación de grupos; no se puede prometer hasta confirmar qué expone Moodle (punto 14).
6. **Conexión directa con el banco, OCR de comprobantes y verificación con Nuvei**: no viables sin terceros; ver 2.4.
7. **Embudo desde Kommo**: viable solo si el plan de Kommo expone la API necesaria (ya figura como pendiente de accesos: plan Advanced).
8. **Si el prototipo se muestra como "ya funciona"**: no. Es una maqueta navegable; la firma y el QR son demostraciones.

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
2. Entrar con cualquier rol (por ejemplo Secretaría, con "Ver como") → Inventario → **Entregas de libros** → "Abrir entrega".
3. En la tablet: buscar la entrega, marcar las tres revisiones, firmar con el dedo (o con el mouse) y confirmar. El recibo muestra la firma que dibujaste.
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


## 15. Stock negativo y recepción de libros físicos (revisión de 10 nov)
**Lo que dijo Secretaría**: el inventario muestra negativos (-1, -4) cuando se venden libros en línea que hay que comprar. Cuando llega la compra, quien recibe verifica los artículos contra el documento, revisa si la entrega está completa, la marca como recibida en el sistema, imprime las etiquetas, las separa a mano y etiqueta cada libro para mantener actualizado el inventario. Si el pedido llega incompleto no se puede marcar como recibido.

**Qué había en `main`**: stock por sede con alerta de negativos y el correo diario de las 07:00, ingresos de proveedor ya registrados con su estado ("Recibido" o "Con pendientes"), pedido sugerido por forecast y los códigos de activación (módulo 7, M7). **Faltaba** explicar qué significa el negativo, armar la lista de compra y, sobre todo, la **pantalla de recepción**: contar lo que llegó, compararlo con el pedido y el documento, y qué pasa al marcarlo recibido.

**Qué se agregó al prototipo**
- **Lista de compra de esta semana** (Inventario): se arma sola con los títulos en negativo, la sede, los libros vendidos sin stock y la cantidad a comprar, con "Crear pedido con esta lista". Aclara que el negativo son libros ya vendidos que aún no están en la sede.
- **Recibir pedido** (`RecepcionPedido.html`, desde Inventario, Movimientos, Pedidos a proveedor "Recibir" y el Inicio de Secretaría): datos del pedido, **documento del proveedor** (número, total y adjunto), **conteo por libro contra lo pedido** con diferencia y estado (completo, faltan, sobran) y botones + y − (o "Marcar todo como recibido") para contar, porque los libros no traen código de barras.
- **Regla de la sesión**: "Marcar como recibido" solo se habilita si el pedido está **completo**; con faltantes o sobrantes avisa qué pasa. Existe "Registrar recepción parcial", que suma lo recibido y deja el pedido "Con pendientes".
- **"Qué pasa al recibirlo"**: el stock de la sede sube, los saldos negativos se cubren y **los libros ya vendidos se asignan solos a su entrega digital** (de "Sin stock" a "Lista para entregar", sección de Entregas de libros) o a su pedido de la tienda en línea. Cada libro muestra para quién es.
- **Sin etiquetas**: el paso de imprimir y pegar etiquetas desaparece; la tablet muestra a quién va cada libro al entregarlo.

**Viabilidad**: **viable y dentro del alcance** (M7 incluye "inventario bajo demanda y tracking de pedidos"). La asignación automática de lo recibido a las entregas pendientes se apoya en el flujo de entregas digitales.

**Por confirmar con el cliente**
- Si **las etiquetas físicas** se pueden eliminar del todo. Si necesitan identificar físicamente el libro de cada estudiante, se puede mantener una etiqueta opcional.
- Si se permite **recibir parcialmente** (el prototipo lo permite, con pendientes) o solo pedidos completos como hoy.
- **Sin código de barras**: el conteo de la recepción es manual (botones + y −). Se retiró el escáner que tenía el prototipo.
- Cómo se vinculan las ventas **en línea** con el stock negativo: depende de la sincronización con la tienda (WooCommerce), que figura como fuera del alcance del contrato (punto 4 del contexto).
- Quién puede registrar una recepción y si hace falta una segunda persona que la valide.


## 16. Exámenes internacionales: factura previa, cédula en PDF y 20 días (revisión de 10 nov)
**Lo que dijo Secretaría**: para que una persona externa rinda un examen internacional hay que emitir primero la factura, verificar los datos y adjuntar obligatoriamente el PDF de la cédula. La política exige hacer el trámite con 20 días de anticipación. Hubo un caso en que el cliente pagó, pero nunca envió la cédula y no se pudo registrar.

**Qué había en `main`**: `NuevaInscripcionExamen.html` con 5 pasos (cliente, examen y pago, datos, fecha del calendario, verificación). La identificación era un adjunto opcional, la regla de 20 días era solo un texto, un paso terminaba en "Imprimir y enviar" y no había forma de saber quién pagó y no completó el trámite. El módulo está marcado como **propuesta fuera del alcance del contrato** (punto 3 del contexto).

**Qué se agregó al prototipo**
- **Factura primero**: el paso del pago pide el **número de factura** como campo obligatorio y explica el orden: factura, datos y cédula, fecha, inscripción.
- **Cédula en PDF obligatoria**: sin el PDF no se puede inscribir. La pantalla lo marca en rojo, rechaza archivos que no sean PDF y se pone verde al adjuntarlo. Se puede **pedir al cliente** la cédula o todos los datos con un botón.
- **Guardar pendiente de cédula**: para el caso del pago hecho sin documento, el candidato queda con el estado **"Falta cédula"** (factura y pago registrados, cupo reservado hasta el cierre de inscripción) en lugar de perderse. En el listado de exámenes hay una cifra y un filtro "Falta cédula" y una acción "Pedir cédula".
- **Regla de 20 días visible**: el calendario muestra la fecha del examen, el cierre de inscripción, los días que faltan y si está disponible; una fecha con menos de 20 días permite **pedir excepción** a Coordinación (queda en Aprobaciones).
- Ya no se imprime: el paso final es **"Enviar resumen al cliente"** por correo.

**Viabilidad**: es viable de construir, pero es un módulo **fuera del alcance del contrato**, así que su construcción y cualquier envío por WhatsApp (plantilla de datos) requieren cotización aparte. El bloqueo sin cédula en el prototipo es una demostración; en la plataforma real debe validarse en el servidor y guardar el documento en el expediente.

**Por confirmar con el cliente**
- Si **siempre** hace falta la cédula (también para estudiantes que ya la tienen en su ficha) o solo para clientes externos.
- Quién puede autorizar una **excepción de la regla de 20 días** y si el centro examinador la acepta.
- Plazo máximo para completar la cédula antes de liberar el cupo y qué pasa con el pago si no se completa.
- Los feriados y el calendario anual se cargan una vez al año (ver sección 13).

## 17. Corrección: los libros no tienen código de barras (10 nov)
Se retiró todo lo relacionado con escanear libros: el campo y botón de escáner de la **entrega** (ahora se busca la entrega por nombre, cédula o matrícula del estudiante, o se elige de la lista de pendientes) y el escáner de la **recepción de pedidos** (ahora el conteo es manual con botones **+** y **−** y un botón "Marcar todo como recibido"). También se corrigieron las referencias en este informe, en `docs/PANTALLAS.md` y en `CLAUDE.md`. No se reintroducirá un escáner salvo que el cliente lo pida.


## 18. Métodos de pago y registro de comprobantes (revisión de 10 nov)
**Lo que dijo Secretaría**: los métodos más comunes son efectivo, tarjeta de débito, tarjeta de crédito, depósito, transferencia, nota de crédito y pago en línea (links generados en la plataforma). Para transferencias y links hay que bajar el comprobante del WhatsApp o del historial de la plataforma, anexarlo, ingresar el número de autorización o de comprobante y la fecha de cierre de caja para que Contabilidad revise. Hoy el sistema solo permite dos métodos de pago por factura.

**Qué había en `main`**: `RegistrarPago.html` con un formulario único (monto, fecha, método entre cuatro opciones, un campo de referencia y un adjunto de texto). La matrícula tenía una lista de métodos más larga, pero sin datos por método. **Faltaba** que cada método pidiera lo suyo, adjuntar el comprobante, la fecha de cierre de caja y permitir más de un método por pago.

**Qué se agregó al prototipo** (en Registrar pago y en Matrícula y factura)
- **Ocho métodos**: efectivo, tarjeta de débito, tarjeta de crédito, depósito, transferencia, nota de crédito, pago en línea (link) y "Otro" (cheque, retención, cruce de cuentas, gift card, que el contrato también menciona).
- **Cada método pide sus datos**: efectivo, recibo de caja; tarjetas, datáfono, lote, número de autorización y si es corriente o diferido; depósito, banco y papeleta; transferencia, banco de origen (con aviso de las interbancarias) y número de comprobante; nota de crédito, cuál se aplica (vigencia de 12 meses); link, código de autorización con "Traer del historial de links".
- **Comprobante adjunto** (PDF, JPG o PNG) en todos los métodos que lo necesitan, y **fecha de cierre de caja** en cada pago.
- **Varios métodos por factura**: se agregan y quitan líneas de pago; una barra verifica la suma (cuadra, faltan o sobran) y deja saldo pendiente si falta. Ya no hay límite de dos.
- Una guía desplegable "Qué se pide según el método" y, en Caja del día, la nota de que cada pago lleva su fecha de cierre y comprobante adjunto.

**Viabilidad**: **viable y dentro del alcance** (M5: "método de pago y estado de cobro"). La conciliación automática con el banco está en la sección 4 (importar el extracto).

**Por confirmar con el cliente**
- **"Traer del historial de links"**: el historial vive en la pasarela de pagos (Datafast o Nuvei). Traerlo automáticamente requiere una integración que no está en el contrato (punto 11 del contexto: verificación con Nuvei); sin ella el número se sigue copiando a mano. En el prototipo es una demostración.
- La lista final de métodos y qué datos exige cada uno (por ejemplo, si se necesita el nombre del titular de la tarjeta).
- Si el **cierre de caja** debe ser un documento digital firmado: hoy Secretaría imprime y entrega la lista de pagos a Contabilidad. Hacerlo digital queda como siguiente mejora.
- Los plazos de diferido y los datáfonos de ejemplo son supuestos.


## 19. Automatizaciones: aperturas, reaperturas, cobranza y notas (revisión de 10 nov)
**Lo que dijo Secretaría**: se pueden programar alertas automáticas y plantillas de WhatsApp para aperturas, reaperturas de cursos y seguimiento de cobranzas a quienes tienen saldos pendientes. La capacidad estándar de las aulas es de 12 estudiantes. Hoy Secretaría revisa a mano, semana a semana, los grupos que terminan y sus notas pendientes para planear la apertura y los procesos comerciales.

**Qué había en `main`**: pedazos sueltos: el protocolo de reaperturas y el botón "Enviar reporte semanal" en Cursos, recordatorios de cuota en la matrícula, la cartera, plantillas en Configuración y alertas en Insights. **No había un lugar** para ver qué avisos salen solos, apagarlos, ver a quién llegaron ni los parámetros (capacidad estándar, mínimo para abrir).

**Qué se agregó al prototipo**: pantalla nueva **Automatizaciones** (menú Dirección; Secretaría, Coordinación y Dirección la ven), con cuatro pestañas:
- **Reglas** (10, por área): aperturas (crear el curso en el LMS a las 72 h, correo informativo a las 48 h, alerta de ocupación baja y curso sin profesor a los 14 días), reaperturas (contacto al 75 % del curso, reporte semanal), cobranza (cuota por vencer, cuota vencida a los 1, 7 y 15 días con escalamiento, saldo con el curso en marcha) y notas pendientes. Cada una con su momento, qué hace, canal y un **interruptor** para activarla o apagarla sin borrarla (el conteo de reglas activas se actualiza).
- **Plantillas**: vista previa con variables ({nombre}, {curso}, {fecha}, {saldo}…) de cinco mensajes (rematrícula, cuota por vencer, cuota vencida, inicio de curso, pocas inscripciones).
- **Registro de envíos**: qué salió, a quién, por qué canal y si se envió, rebotó u fue omitido (por ejemplo, un cobro que se salta porque el estudiante prometió pagar).
- **Resumen semanal y parámetros**: el resumen del lunes con los grupos que terminan, sus notas pendientes y la ocupación del siguiente curso, y los **parámetros** (capacidad estándar 12, mínimo para abrir 6, alerta bajo 50 %, anticipación de 14 días, día y hora del resumen).
- Accesos desde Cursos ("Configurar avisos automáticos") y desde la Cartera ("Automatizar cobranza").

**Viabilidad**
- **Alertas internas y correos: viables y dentro del alcance** (M5 incluye recordatorios de cuota y cobranza; M3 los cursos y M8 los reportes). El resumen semanal y el reporte de reaperturas entran en su versión básica.
- **WhatsApp: fuera del alcance** (punto 12 del contexto): requiere la API oficial de Meta, **plantillas aprobadas una por una por Meta** y tiene costo por mensaje. Las reglas lo marcan como propuesta y hoy salen por correo y notificación.
- **Crear el curso en el LMS** no se puede automatizar sin la API de Cambridge One o Moodle (M11 "sujeto a lo que expongan"); por eso la regla solo recuerda a Coordinación.

**Por confirmar con el cliente**
- La **propuesta externa de automatización** que ya existe (ver sección 6 del contexto): decidir si se absorbe en la plataforma o convive con Kommo, para no duplicar avisos.
- Los **plazos y escalamientos** (3 días antes, días 1, 7 y 15, 72 h) son supuestos tomados de las reuniones y del manual.
- Si la **capacidad estándar de 12** reemplaza a la capacidad por aula (norma SETEC) cuando una aula tiene una propia, o solo se usa si falta.
- Quién puede encender y apagar reglas, y quién recibe cada alerta.


## 20. Envío automático de facturas a Dora y al SRI, con espera de 2 horas (revisión de 10 nov)
**Lo que dijo Secretaría**: la emisión de facturas electrónicas, su carga al SRI y al sistema contable a través de **Dora** está automatizada. Pasan exactamente **2 horas** después de emitir la factura para que el sistema la suba sola y se actualice un **contador numérico** (normalmente en cero). Ese margen sirve para manejar cualquier error o inconveniente técnico. A veces el SRI no autoriza la factura y se queda retenida.

**Qué había en `main`**: la columna "SRI" del listado de facturas (autorizada, sin autorizar, rechazada), el botón "Reintentar autorización" en el detalle y una fila de Dora "por definir" en Integraciones. **No se veía** la espera de 2 horas, el contador ni qué facturas están esperando, ya salieron o fallaron. Además, la factura de ejemplo se autorizaba 1 minuto después de emitirla, lo que contradecía esa espera.

**Qué se agregó al prototipo**
- **Pantalla "Envíos a Dora y al SRI"** (desde el menú "Más acciones" de Facturación y desde el detalle de la factura): cifras (en espera, **sin subir**, autorizadas, rechazadas y con error) y el flujo en cinco pasos: se emite, ventana de corrección de 2 horas, sale sola a Dora, Dora la autoriza en el SRI y la sube a contabilidad, y si falla se avisa.
- **Estado por factura con cuenta regresiva en vivo** ("Sube en 01:17:50"). Dentro de la espera se puede **Corregir** (datos o anular sin dejar rastro en el SRI) o **Enviar ahora**; al salir, el estado cambia a "Enviada", el contador de "sin subir" baja y **Corregir se bloquea** (después se corrige con nota de crédito).
- **Facturas con problemas**: la rechazada por el SRI ("cédula inválida", con "Corregir y reenviar") y la que falló por Dora ("Reintentar envío").
- **Parámetros**: ventana de corrección (sin espera, 1, 2 o 4 horas), reintentos automáticos y alerta si no se autoriza en 24 horas.
- Se corrigió la **factura de ejemplo**: emitida a las 10:11, enviada a Dora a las 12:11, autorizada a las 12:12 y comprobante a las 12:14, con su línea en el historial. El listado de facturas suma el estado "En espera" y un filtro.

**Viabilidad**: **registrar la factura, la espera y el seguimiento: viable** (M5 y M8). **El envío en sí depende de Dora**: M11 contempla Dora "sujeto a lo que exponga" y la **emisión directa al SRI sin Dora es adenda** (punto 10 del contexto). Mientras no haya API de Dora, la plataforma no puede enviar sola y esta pantalla sería solo de seguimiento.

**Por confirmar con el cliente**
- Si **hoy el envío automático lo hace otra herramienta** (la propuesta externa) y cómo convivirá con la plataforma.
- Qué expone Dora (API, estado de la autorización, motivo del rechazo) y si el **contador** es el de Dora o uno propio.
- Si las **2 horas** son una regla del negocio o un límite técnico de la herramienta actual; el prototipo la deja configurable.
- Qué hacer con las facturas que el SRI no autoriza: cuánto tiempo pueden quedar retenidas y quién las corrige.


## 21. Facturas retenidas y problemas de integración con el SRI (revisión de 10 nov)
**Lo que dijo Secretaría**: el sistema del SRI presenta problemas recurrentes de integración automática y algunos comprobantes no se suben de inmediato, por falta de una integración total de la facturación electrónica. Aunque el proceso actual es automático (antes era manual), las facturas con inconvenientes **simplemente no se autorizan y se quedan retenidas**, lo que obliga a una **revisión minuciosa** para evitar inconsistencias.

**Qué había en `main`** (y en la sección 20): la lista de estados de envío, el botón de reintentar y una fila de Dora. **Faltaba** tratar las facturas retenidas como un problema con causa, tiempo y consecuencias, no solo como un estado.

**Qué se agregó al prototipo** (pantalla "Envíos a Dora y al SRI", ahora con cuatro pestañas)
- **Retenidas y revisión**: cuántas hay, desde cuándo, cuántos intentos llevan, el motivo (identificación inválida, Dora no respondió, secuencial ya registrado, servicio del SRI no disponible) y **qué hay que revisar** en cada una (por ejemplo, "pagada y libro entregado sin comprobante autorizado" o "posible duplicado").
- **Antes de reintentar**: una lista de cinco preguntas para no crear inconsistencias: si la factura ya existe en el SRI (**consultar por la clave de acceso para no duplicarla**), si el dato es corregible, si hay un pago cobrado, si hay comisión o entrega de libro asociadas y si hay saltos en la numeración.
- **Inconsistencias detectadas**: pagada y entregada sin autorizar, comisión generada sobre una factura retenida, posible duplicado y saltos de numeración, cada una con su acción ("Marcar como revisada" deja constancia en el audit log).
- **Plan B**: reintentos automáticos (3 veces cada 30 min), aviso a Secretaría y Contabilidad y, pasadas 24 horas, **emisión en contingencia** (a mano en el portal del SRI) registrando la clave de acceso y la fecha, y la factura queda marcada "Emitida fuera de la plataforma".
- **Salud del envío**: autorizadas a la primera, tiempo medio de emisión a autorización, caídas del SRI de la semana y los motivos de retención de 30 días.
- Una **notificación** a Secretaría y Contabilidad cuando una factura queda retenida con riesgo de duplicado, y las acciones nuevas "Consultar estado en el SRI" y "Emitir en contingencia".

**Viabilidad**: el **seguimiento, la revisión y las alertas son viables** (M5 y M8). **Resolver la causa depende de terceros**: la integración total con el SRI no está en la plataforma; M11 contempla Dora "sujeto a lo que exponga" y la emisión directa al SRI es adenda (punto 10 del contexto). La plataforma puede registrar, avisar y ordenar la revisión, pero no puede evitar las caídas del SRI. Las cifras y los motivos de la pantalla son de ejemplo.

**Por confirmar con el cliente**
- Los **motivos de rechazo reales** que devuelve Dora o el SRI, para clasificarlos bien (lo del prototipo son descripciones generales, no códigos oficiales).
- Si el **plan B en contingencia** es aceptable para Contabilidad y el SRI en su forma de registrar la clave de acceso, y quién lo autoriza.
- Qué hacer con la **comisión del asesor y la entrega del libro** mientras la factura está retenida (el prototipo las marca "pendientes de autorización").
- Con qué frecuencia ocurren hoy las retenciones, para dimensionar el tiempo que ahorra la pantalla.
