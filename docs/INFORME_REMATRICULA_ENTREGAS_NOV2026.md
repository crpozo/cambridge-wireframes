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
