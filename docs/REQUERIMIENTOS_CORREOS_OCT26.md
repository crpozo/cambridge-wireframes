# Requerimientos recibidos por correo (26 oct 2026) y cómo los refleja la plataforma

Dos correos del cliente reenviados por Orkesta el 29 oct 2026. Los adjuntos (matriz de KPIs en Excel, reporte general consolidado, auditoría y propuesta del hub de secretaría) **no llegaron en el ZIP** (traía el Manual de Procesos ya reflejado en `PROCESOS_INTERNOS.md` más el flujograma de contratación en PNG); este resumen se basa en el texto de los correos. El hub de secretaría (`cambridge.plugin.agency`) tiene credenciales en el correo: no se guardan en este repo y el sitio no se pudo abrir desde el entorno de trabajo.

## 1. Dirección Comercial · KPIs, seguimiento diario y orígenes de lead

### Indicadores mensuales (Quito, Valle y Ambato; Cuenca lleva un reporte distinto)
Matrículas y facturación total · ticket promedio · cantidad y valor de servicios vendidos · matrículas por referidos · niveles y One to One vendidos · certificaciones, traducciones y cursos de español · variación porcentual y cumplimiento de metas · proyección de crecimiento del 15 % frente al mismo período del año anterior (matrículas y facturación).
→ `TableroComercial.html` pestaña **Matriz KPI mensual** (Oct 2025 · Oct 2026 · variación · proyección +15 % · meta · cumplimiento) con filtro por mes y asesor y exportación a Excel; **Consolidado por sede** incluye la fila Consolidado (Quito + Valle + Ambato) y Cuenca aparte.

### Seguimiento diario
Número de ventas y matrículas, facturación, servicios y productos vendidos, origen de cada venta y resultado por asesor y sede.
→ Pestañas **Hoy y acumulado** y **Ventas** (columnas Origen, Producto o servicio, Pagada por completo, Asesor · sede).

### Filtros
Día, mes, trimestre o año; asesor; producto o servicio; origen del lead; sede. Elegir una sede, combinar dos o tres, o ver el consolidado.
→ Barra de filtros del tablero: Período (hoy, semana, mes, trimestre, año, mes anterior, rango), Asesor, Programa, Modalidad, Origen (incluye los sub-orígenes de walk-in), Producto o servicio; **sedes como chips combinables** (Quito, Valle, Ambato, Cuenca, Consolidado).

### Orígenes de lead (catálogo único)
Facebook, Instagram, TikTok, Facebook Forms, WhatsApp, Contacto web, Test online, Exalumno, Referido, Convenio empresarial, Alianza, Feria, Walk-in, Otro.
- Estrategias pagadas (Facebook, Instagram, TikTok, Facebook Forms): segundo campo **Canal de la estrategia pagada** (Meta Ads Facebook / Instagram, TikTok Ads, Google Ads, Facebook Forms, orgánico).
- **Walk-in**: segundo desplegable **¿Cómo nos conoció?**: Fachada o sector · Redes sociales orgánicas · Google o IA orgánica · Pauta digital visualizada · Activaciones o ferias · Prensa o medios · Conocía la marca SOL · Asociación de marca · Otros. Se conserva al pasar a Ganado (hoy es una etiqueta en Kommo); si el lead entró solo como Walk-in, el asesor lo completa a mano.
→ `origen_fields()` en Nueva matrícula, Matrícula desde lead y Nuevo estudiante (campos dependientes por JS); filtro Origen en Leads; `RegistrarWalkIn.html` crea el lead **en Kommo por la API** (regla: todo lead entra a Kommo y de Kommo a la plataforma) y lo muestra en Leads; el catálogo se comparte con Kommo (Integraciones).

### Reporte por fuente
Seleccionar una fuente y ver cuántos leads, matrículas, servicios y facturación generó en el período (base del informe individual del asesor y del consolidado).
→ Pestaña **Por origen** del tablero (fuente + período → KPIs y tabla por sede y asesor).

### Comisiones: fecha de venta vs fecha de pago completo
La comisión se genera solo cuando la matrícula está totalmente pagada: una venta de agosto pagada por completo en octubre es venta de agosto y comisión de octubre.
→ `Comisiones.html`: regla en "Reglas activas" y tabla **Ventas que entran a la comisión del mes** (fecha de venta · pagada por completo · comisión); columna "Pagada por completo" en Ventas del tablero.

## 2. Contrato de matrícula con Reglamento del Estudiante · aceptación electrónica
Hoy se pide la firma después de la matrícula y a veces no se completa. Debe firmar/aceptar el representante si el estudiante es menor de 18 años, o el propio estudiante si es mayor. Se pide integrarlo a la ficha y enviarlo automáticamente al matricular (correo o mensaje), con aceptación electrónica sencilla y respaldo en el expediente.
→ Nueva matrícula paso 3, campo **Contrato y Reglamento del Estudiante** (aceptación electrónica al estudiante o al representante, o PDF en papel); al confirmar se envía por correo y WhatsApp; `DetalleMatricula.html` muestra el estado del contrato (Aceptado · fecha · quién · código · IP) y la acción "Reenviar contrato para aceptación"; Integraciones lista la pieza "Firma electrónica del contrato".

**Recomendación técnica (para responder al cliente):**
1. **Aceptación electrónica simple con evidencia** (recomendada para el volumen de Cambridge): al confirmar la matrícula la plataforma genera el contrato en PDF con los datos de la matrícula y el Reglamento, lo envía por correo y WhatsApp con un enlace único; la persona (representante o estudiante según la edad calculada desde la fecha de nacimiento) lo lee, marca "Acepto" y confirma con un código de un solo uso enviado a su correo o teléfono. Se guarda el PDF sellado con hash, fecha y hora, nombre y cédula, correo/teléfono verificado, IP y el texto aceptado, y queda en el expediente del estudiante y en el audit log. En Ecuador la Ley de Comercio Electrónico reconoce la firma electrónica y los mensajes de datos con estos elementos de prueba; es suficiente para un contrato de servicios educativos. Recordatorios automáticos si no acepta en 24 h y 72 h; la matrícula queda marcada "Contrato pendiente" y Secretaría lo ve en su lista.
2. **Firma electrónica certificada** (certificado de firma del BCE, Security Data, Uanataca, etc.) solo si Legal exige firma avanzada: exige que el firmante tenga certificado o pase por verificación de identidad; añade costo por firma y fricción, no se recomienda para todos los estudiantes.
3. **Proveedor de firma (DocuSign, Zoho Sign, Docusign eSignature, Firmar.ec)**: experiencia pulida y auditoría, con costo mensual por sobre; viable si prefieren no construir la pieza, integrable por API con la misma lógica de quién firma.
Lo que no se recomienda: seguir con Jotform o pedir la firma después de la matrícula sin bloqueo ni recordatorio.

## 3. Secretaría académica · continuidad y rematrículas
Secretaría atiende al estudiante actual y genera las rematrículas de módulos y niveles; hubo una auditoría con una solución parche (hub de secretaría) que debe considerarse. Visión: una cuenta de Kommo por secretaría de sede (hoy solo Quito). Se sugiere una sesión (idealmente presencial) con el equipo de secretarías.
→ Ya cubierto: Facturación → Rematrículas por confirmar, rematrícula desde el Muro, Cursos → Reaperturas, Inicio por rol SEC con pendientes; Integraciones: Kommo con un usuario por secretaría de sede. **Pendiente**: recibir la auditoría y la propuesta del hub para contrastar sus procesos con las pantallas; agendar la sesión con secretarías.

## Pendientes para el cliente
- Enviar la matriz de KPIs (Excel), el reporte consolidado y los archivos de la auditoría/hub de secretaría (no estaban en el ZIP).
- Confirmar la opción de aceptación del contrato (1, 2 o 3).
- Confirmar si las metas por asesor y sede se cargan desde el Excel actual o se editan en la plataforma (hoy: "Editar metas").
