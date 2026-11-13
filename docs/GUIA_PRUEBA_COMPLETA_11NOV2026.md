# Guía de prueba completa · cambios del 11 nov 2026

Todo está publicado en https://crpozo.github.io/cambridge-wireframes/ y se puede probar igual en local (`http://localhost:8765/`). Los datos son de ejemplo. Estado: **Hecho** = se prueba en el prototipo; **Ya existía** = estaba antes de hoy; **Dependencia** = requiere una integración real; **Propuesta** = fuera del alcance del contrato.

## A. Tablero comercial (Indicadores y gráficos)
Ruta: Comercial → **Tablero comercial** → pestaña **Indicadores y gráficos** (antes "Plan estratégico").
1. Con el filtro por defecto (Este mes) se ven 11 cifras; el ingreso es $21,940 y hay 42 matrículas.
2. **Período**: cambia a Hoy, Esta semana, Este trimestre, Este año. Todas las cifras y gráficos se recalculan. Prueba también "Día específico".
3. **Sede**: arriba, pastillas Quito, Valle, Ambato, combinaciones y Consolidado (Quito + Valle + Ambato; Cuenca va aparte). La línea gris bajo los filtros indica lo que estás viendo.
4. **Asesor, programa, producto, origen del lead y clasificación de walk-in** (Origen = Walk in → elige "Fachada o sector"). "Limpiar filtros" vuelve al inicio.
5. Gráficos: líneas (2026 vs 2025, real vs meta, ticket, conversión y deserción), barras (sede, línea, producto, programa, origen, asesor) y circulares (planes de nivel, one to one, referidos, programa).
6. **Embudo de Kommo**: todas las etapas, % entre etapas, conversión total; "Agrupar por" sede, asesor, canal o mes.
7. **Rol**: menú de usuario → Ver como → Asesor: solo ves lo tuyo (Carla M.). Con Dirección o Administrador ves el consolidado.
8. **Matriz**: marca o desmarca Sede, Asesor, Programa, Producto, Canal; usa el buscador; **Exportar Excel** descarga lo visible.

Cubre: "Sincronizar reportes sedes" (consolidado sin sumar a mano) y el filtro por origen y walk-in. Dependencia: las cifras reales vienen de la API de Kommo. Pendientes de definir con el cliente: deserción, upsell, "lead atendido".

## B. Cambios acordados en la reunión
Ruta base: Comercial → **Nueva matrícula** (`NuevaVenta.html`).

| # | Requerimiento | Cómo probarlo | Estado |
|---|---|---|---|
| 1 | Representante desde los 18 años | Estudiantes → Nuevo estudiante: pon una fecha de nacimiento que dé 17 años (representante obligatorio) y otra que dé 18 o más (opcional). En Nueva matrícula paso 1, "¿Menor de 18 años?" = Sí pide los datos del representante | Hecho (el corte ya era 18; TeamDesk usa 22) |
| 2 | Duplicar datos del estudiante en la factura | Paso 4 → tarjeta "Datos de la factura" → **Usar los datos del estudiante**: se copian nombre, identificación, correo, dirección y teléfono | Hecho |
| 3 | Nivel y horario editables | Paso 2: **Nivel de ingreso (editable)** y **Horario (editable)**, incluye "Otro horario · se acuerda con Académico" | Hecho |
| 4 | Marcar referido al ingresar registros | Paso 1, Registrar walk-in y otros formularios con origen: **¿Es referido?** = Sí muestra **Referido por** | Hecho |
| 5 | No facturar cada módulo por separado | Paso 4, "Ítems de la factura": módulos 7, 8, 9 y 10, material y demás en **una sola factura** | Ya existía |
| 6 | Activo o inactivo según tiempo sin matrícula | Paso 1, **Tiempo sin matrícula**: hasta 2 meses = activo (sin test ni inscripción); 3 a 5 = inactivo, mantiene continuidad, solo repite el test; 6 o más = nuevo, paga inscripción. La **Clasificación** cambia sola | Hecho |
| 7 | Reportería del total facturado sin intervención manual | Reportes → Reportes self-service → "Ventas y facturación": "¿Cuánto facturamos en total este mes?" y "¿Qué matrículas están pagadas por completo y cuáles son abonos?" (ver sección D) | Hecho |
| 8 | Aceptación de términos con registro | Paso 4, tarjeta "Aceptación de términos y condiciones": marca la casilla y aparece fecha, hora y correo del comprobante; **Enviar enlace de compra con aceptación** simula el enlace | Hecho como prototipo; validez legal por consultar con el equipo legal |
| 9 | Editar canal de contacto | Estudiantes → Ficha 360 → pestaña Datos → **Canal de contacto (editable)**: cambia de Walk in a Referencia / Referido; se registra fecha, hora y quién | Hecho |
| 10 | Integrar datos Kommo ↔ plataforma | Comercial → Leads y "Matrícula desde un lead". La conexión real depende de lo que exponga la API de Kommo | Ya existía; dependencia |
| 11 | Sincronizar reportes de sedes | Ver sección A (consolidado) y Dashboard ejecutivo | Hecho (sección A) |

## C. Mensajes de bienvenida y recordatorios (WhatsApp)
Ruta: Automatizaciones.
1. Pestaña **Reglas**: busca "Bienvenida al matricularse" (al confirmar la matrícula), "Grupo y mensaje de apertura" (48 h antes; si entra con el curso iniciado avisa de inmediato) y "Fin de módulo: aviso del siguiente curso". Apágalas y enciéndelas: el contador cambia.
2. Pestaña **Plantillas**: Bienvenida, Inicio de curso, Recordatorio al grupo, Fin de módulo, con vista previa y variables.
3. Pestaña **WhatsApp** (simulación): ve la conexión y las plantillas "aprobadas por Meta"; en "Probar el envío" elige estudiante y plantilla y pulsa **Enviar mensaje de prueba**. El mensaje pasa de Enviando a Enviado, Entregado y Leído, llega una respuesta de ejemplo y se actualizan el registro y los contadores.

WhatsApp es **propuesta fuera del alcance** (requiere la API de WhatsApp Business y que Meta apruebe cada plantilla). El correo sí está dentro. Pendiente: el flujo con Cris.

## D. Arma tu reporte
Ruta: Reportes → **Reportes self-service**.
1. Elige una pregunta; en "¿De cuándo y de dónde?" cambia **Período** y **Sede**; en "¿Cómo lo quieres ver?" cambia **Vista** (por mes, por sede, por asesor, lista de estudiantes) y marca columnas en **Agregar**.
2. Pulsa **Ver resultado**: el título, el texto, el gráfico y la tabla se redibujan con esos filtros. Con una sola sede, "Por sede" se abre por programa.

## E. Ficha 360
Ruta: Estudiantes → María Andrade. Bajo "Nueva matrícula" y "Editar" está el botón **Ver portal del estudiante** (con la línea "lo que ve María al ingresar · propuesta"); lleva al portal. Es una propuesta fuera del alcance.

## F. Otros puntos de la reunión (ya estaban en el prototipo antes de hoy)
Se revisan con las guías anteriores; hoy no se modificaron.

| Tema de la reunión | Dónde verlo |
|---|---|
| Descuentos con comentario justificativo y aprobación de administración | Nueva matrícula, paso 3 (motivo obligatorio y "Aprobado por") |
| Cursos indexados entre sedes | Nueva matrícula, paso 1 ("¿Indexado?") y Cursos |
| Exámenes internacionales y certificaciones (factura, cédula, entrega) | Exámenes |
| Comisión solo con el pago completo (abonos) | Tablero comercial → pestaña Ventas ("Pagada por completo") y Comisiones |
| Notas de crédito y refacturación al cambiar de modalidad | Facturación → Nota de crédito |
| Reemplazo de PandaDoc por aceptación electrónica del contrato | Nueva matrícula, paso 3 ("Contrato y Reglamento del Estudiante") |
| Cierre de caja y envío al SRI | Facturación → Cierre de caja y Envíos al SRI |

## G. Pendientes de la reunión, ahora en el prototipo
**G1. Plazo de crédito editable (Nueva matrícula, paso 4).** Cambia **Días entre cuotas** (por ejemplo 45) y **Número de cuotas**: el plan pasa a "Personalizado" y abajo se lee el valor de cada cuota y sus fechas. Menos de 15 días marca error; de 31 a 60 avisa que solo va con convenio de crédito (el caso de Farma, hasta 2 meses); más de 60 pide aprobación de Dirección Comercial. Elegir un plan de la lista llena los días y las cuotas.

**G2. Campos obligatorios de la ficha (Estudiantes → Nuevo estudiante).** Nombres y apellidos se convierten solos a mayúsculas. La dirección ahora pide **Calle principal** y **Calle secundaria**. Borra la calle secundaria, la cédula (o pon menos de 10 dígitos), la ocupación o el lugar de estudio o trabajo y pulsa **Guardar estudiante** o **Guardar y matricular**: no guarda, marca en rojo los campos y avisa cuáles faltan. Con todo completo guarda y sigue.

**G3 y G4. Cambio de curso, horario o modalidad (Estudiantes → Detalle de matrícula → "Cambio de curso, horario o modalidad").**
1. Elige el nuevo curso. Si pasa de Virtual a Presencial, es cambio de modalidad y se calcula la diferencia de precio.
2. Cambia **Avance del curso actual** y **Clasificación**. Comercial solo lo autoriza si el estudiante es **Nuevo** y el curso **no ha iniciado**; en cualquier otro caso (o con 80 % o más de avance) lo autoriza **Académico**, con justificación obligatoria.
3. Arriba a la derecha, "Ver como": con Asesor y un cambio académico, el botón queda bloqueado; con Coordinador Académico se habilita. Quien mueve al estudiante es Académico; la nota de crédito y la refactura las emite Facturación (Secretaría) cuando cambia el precio o la modalidad.
4. **Registrar el cambio** deja el movimiento en el historial. La matrícula se conserva (mismo código y fecha de venta, misma comisión): el reporte de nuevos estudiantes no baja (68, no 67), que era la causa de la discrepancia 64 frente a 68.

**G5. RIDE en PDF (Facturación → Detalle de factura → "Ver RIDE (PDF)").** Se abre la factura con su diseño: emisor, número, clave de acceso, autorización del SRI, cliente, ítems con código, totales y forma de pago. **Descargar RIDE en PDF** abre la impresión para guardarla como PDF; **Enviar RIDE por correo** simula el envío con el XML. Reemplaza el envío en Word.

## H. Lo que sigue pendiente
- **Integración real con Dora, Kommo y WhatsApp**: es dependencia externa; el prototipo solo la simula.
- **Código de barras del RIDE**: el RIDE oficial del SRI lleva el código de barras de la clave de acceso; el prototipo muestra la clave en texto y Dora lo genera al emitir.
- **Por confirmar con el cliente**: desde cuándo se cuentan los 3 y 6 meses, si 3 meses basta para repetir el test, el texto legal de la aceptación, el plazo máximo de crédito por convenio y a partir de qué avance solo decide Académico (se usó 80 %).

## I. Tiempos de trabajo del 11 nov 2026
Salen de las horas reales de los commits y del reflog de git. Cada tramo va desde el hito anterior hasta el suyo, así que incluye pruebas y las pausas entre mensajes.

| Parte | Desde | Hasta | Duración |
|---|---|---|---|
| Tablero comercial: filtros reales, embudo y matriz | 12:57 | 13:08 | 11 min |
| Cambios de la reunión (factura copiable, nivel y horario, referido, estados, aceptación, canal, mensajes) | 13:08 | 13:36 | 28 min |
| Simulación de WhatsApp | 13:36 | 13:45 | 9 min |
| Botón "Ver portal del estudiante" en la Ficha 360 | 13:45 | 13:54 | 9 min |
| Arma tu reporte con filtros que cambian el resultado | 13:54 | 13:57 | 3 min |
| Merge a main y publicación | 13:57 | 14:04 | 7 min |
| Guía completa de pruebas y aclaraciones | 14:04 | 14:21 | 17 min |
| Pendientes: crédito editable, campos de la ficha, cambio de matrícula, RIDE | 14:21 | 14:25 | 4 min |
| **Total** | 12:57 | 14:25 | **88 min** |

El análisis y diseño del tablero antes de crear su rama (12:57) no está contado: no hay una hora de inicio confiable.
