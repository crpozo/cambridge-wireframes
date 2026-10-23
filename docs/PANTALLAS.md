# Pantallas de la Plataforma Cambridge (45 · 41 visibles en el hub)

Todas comparten la misma **shell**: barra superior con nombre de la plataforma, selector de sede global (Todas / Quito / Valle / Ambato), notificaciones, asistente y usuario con rol; menú lateral: Inicio, Estudiantes, Cursos, Profesores, Facturación, Comisiones, Inventario, Reportes, Aprobaciones, Configuración. Lo que cada rol ve depende del RBAC (M1).

Formato: **archivo** · qué muestra · de dónde se llega / a dónde va.

El hub y el menú lateral están agrupados por áreas (Académico, Comercial, Inventario, Dirección, Administración) y cada ítem se muestra según el tipo de usuario elegido en "Ver como".

Regla: ninguna acción queda muerta. Los botones de navegación llevan a su pantalla; los botones de acción (guardar, aprobar, rechazar, exportar, confirmar…) abren un diálogo que explica qué pasaría al confirmar y, si aplica, llevan a la siguiente pantalla.

## Acceso y navegación
1. **Main.html · Login** (M1). Email, contraseña, recuperar contraseña, 2FA opcional. → Home.
2. **Home.html · Inicio por rol** (M1/M8). KPIs del rol, pendientes de aprobación, accesos rápidos (nueva venta, nuevo estudiante, payment sheet, comisiones), actividad reciente del audit log. → cualquier módulo.
3. **Notificaciones.html** (M1). Centro de avisos: aprobaciones pendientes, stock negativo, payment sheet lista, profesor aprobado. Cada aviso enlaza a su pantalla.
4. **Chatbot.html · Asistente interno** (M9). Chat sobre datos de la plataforma respetando permisos y sede del usuario.

## Estudiantes (M2)
5. **Estudiantes.html · Listado**. Búsqueda por nombre/cédula/email, filtros sede/estado/nivel, tabla consolidada de las 3 sedes, nuevo estudiante, importar/exportar. → Ficha360, NuevoEstudiante, ImportExport.
6. **NuevoEstudiante.html**. Formulario único, bloque de representante si es menor, marcadores de dato sensible, validación de duplicados por cédula. → Ficha360.
7. **Ficha360.html · Ficha 360°**. Cabecera (sede, estado, asesor, nivel/módulo, ID legado TeamDesk), tabs: Datos, Matrículas y notas (número de matrícula, código de curso, saldo, asistencia, pass/fail), Niveles/crédito, Facturas y pagos, Archivos y certificados, Historial. Botón Nueva matrícula. → NuevaVenta, DetalleMatricula.
8. **ImportExport.html**. Carga CSV/Excel con vista previa y detección de duplicados; exportación filtrada y auditada.

## Flujo comercial (M5 + M1 aprobaciones)
9. **NuevaVenta.html · Nueva matrícula** (M5). Sigue el flujo del Enrollment de TeamDesk en 5 pasos numerados: (1) estudiante y origen (buscar o crear, tipo nuevo/antiguo, asesor, canal de contacto, ¿paga la empresa?); (2) programa, nivel y curso **por módulo** (una matrícula por módulo, solo cursos con cupo y sin choque); (3) valores y descuentos (derecho de matrícula, valor del curso y libros, cada uno con su %; motivo de lista cerrada; observaciones; matrícula firmada adjunta); (4) factura y pago (cliente CED/RUC/PAS, RUC especial, plan de pago 1 a 3 cuotas, pagos mixtos con comprobante, etiquetas de libros); (5) confirmación (matrículas creadas, factura multi-módulo al SRI, cuotas en cartera, libros, Teams, comisión pendiente). → SolicitudDescuento, DetalleMatricula.
10. **SolicitudDescuento.html**. Porcentaje, monto resultante, motivo de lista cerrada, justificación. Regla ilustrativa: >10% requiere Director Comercial. → Aprobaciones.
11. **Aprobaciones.html · Bandeja de aprobaciones** (M1). Tabs: descuentos, profesores, asignaciones. Aprobar/rechazar con trazabilidad y notificación al solicitante.
12. **Facturas.html · Facturación**. KPIs (facturado hoy, cobrado, por cobrar a crédito, sin autorizar SRI); pestañas Facturas (filtros estado, SRI, asesor, crédito; enviar comprobantes pendientes, descargar XML), Calendario de crédito (vencimientos), Por estudiante (elegir un estudiante, ver sus facturas con saldo y descargarlas en ZIP o enviárselas por correo con el total adeudado) y Notas de crédito. → DetalleFactura, NuevaVenta, NotaCredito.
13. **DetalleFactura.html**. Cabecera (número, estado de cobro, estado SRI, matrícula, venta multi-módulo, crédito y vencimiento), datos de facturación del cliente (CED/RUC/PAS, RUC especial), autorización SRI (clave de acceso, comprobante enviado), ítems (servicio/producto, % descuento, IVA), pagos múltiples, efecto en el saldo de la matrícula e historial. Acciones: registrar pago, enviar comprobante, PDF, XML, nota de crédito, anular.

## Flujo académico (M3)
14. **Cursos.html · Listado**. Filtros programa/nivel/modalidad/estado, ocupación, profesor. → DetalleCurso, NuevoCurso.
15. **NuevoCurso.html**. Programa, nivel, modalidad, tipo, sede, aula, fechas, horario, horas, cupo; selección de profesor con validación de contrato activo (si no, va a aprobación). Al crear se compromete stock de libros. → DetalleCurso.
16. **DetalleCurso.html**. Horario y progreso, profesor asignado, sesiones (automáticas/manuales/pendientes), estudiantes con asistencia, nota y estado. → Sesiones.
17. **Sesiones.html · Registro de sesiones**. Vista semanal tipo calendario, confirmar o marcar no dictada, alertas (fuera de horario, contrato vencido, curso sin sesiones). Alimenta progreso y payment sheet.

## Flujo profesores (M4)
18. **Profesores.html · Listado**. Contrato, tarifa, cursos activos, estado. Alta de profesor y acceso a payment sheet. → AltaProfesor, FichaProfesor, PaymentSheet.
19. **AltaProfesor.html · Alta con aprobación**. Datos, contrato, tarifa, vigencia, archivo firmado. Queda "pendiente de aprobación" hasta que Dirección apruebe; recién entonces puede recibir cursos y pagos. → Aprobaciones.
20. **FichaProfesor.html · Ficha del profesor** (M4). Perfil con foto, contacto, educación y certificaciones, tarifa y datos de pago (roles administrativos), indicadores (carga, asistencia, pass rate) y pestañas: Agenda y carga, Desempeño (gauges, evolución, comparación con la sede, reconocimientos/observaciones), Datos y educación, Contrato tarifa y pago, Cursos, Sesiones, Historial de pagos. → AltaProfesor, PaymentSheet, DetalleCurso.
21. **PaymentSheet.html**. Mes, sede, estado (borrador/aprobado). Por profesor: sesiones, horas, tarifa, a pagar, factura del profesor, alerta de diferencia o contrato vencido. Aprobar pagos, exportar.

## Comisiones (M6)
22. **Comisiones.html · Período**. Estado draft → revisión → aprobado; tabla por asesor (niveles, modalidad, meta, real, comisión); gráfico meta vs real; reglas activas. → DetalleComision, ReglasComision. Pestaña **Descuentos otorgados** (solo Admin, Gerencia, Dir. Comercial, Admin. de sucursal): cada venta con descuento, asesor, % y monto, motivo y estado de aprobación; KPIs y promedio por asesor.
23. **DetalleComision.html · Mi comisión** (M6). Cálculo paso a paso para el asesor: niveles vendidos y rango, % por modalidad, bono por meta, retenido hasta cobro, total y fecha de pago; meta del mes y cuánto ganaría con una venta más; ventas del mes con su comisión; historial y preguntas frecuentes. ← Comisiones, Inicio (asesor).
24. **ReglasComision.html**. Tabla de reglas (rangos, modalidad, bono meta, vigencia), nueva regla, simulador contra ventas pasadas. Cambios al audit log.

## Inventario (M7)
25. **Inventario.html · Stock por sede**. Libro × sede, comprometido por cursos abiertos, alertas de pedido. → Movimientos.
26. **Movimientos.html**. Tabs: movimientos, pedidos a proveedor (Books & Bits), notas de crédito; registrar ingreso; forecast por cursos próximos.

## Reportes y dashboards (M8 + M10)
27. **Reportes.html · Dashboard por rol**. KPIs (ventas por nivel real, matrículas, cobros, ocupación), gráficos por sede/modalidad y pipeline comercial, bloque de reportes self-service. → ConstructorReportes, DashboardEjecutivo.
28. **ConstructorReportes.html · Arma tu reporte** (M8). Flujo guiado en 3 pasos para usuarios no técnicos: (1) ¿Qué quieres saber? (preguntas en lenguaje natural por área: estudiantes y matrículas, cursos y profesores, ventas y facturación incl. estado SRI y XML, inventario, otra pregunta al asistente), (2) período y sede, (3) vista y datos extra. Resultado en una frase + gráfico + tabla, con exportar Excel/PDF, enviar por correo (programable) y guardar. Reportes guardados como tarjetas con quién los usa y la vista TeamDesk que reemplazan. ← Reportes. → Estudiantes, Facturas.
29. **DashboardEjecutivo.html** (M10). Ingresos YTD, estudiantes activos, ticket promedio, margen por sede; ingresos por mes/sede, mix programa/modalidad, funnel comercial, retención por nivel.

## Administración y gobierno (M1 + M11)
30. **Usuarios.html · Usuarios y roles**. Listado de usuarios con rol y sedes visibles; matriz de permisos por rol.
31. **Configuracion.html**. Tabs: sedes, catálogo de niveles y precios, tarifas de profesores, reglas de aprobación, parámetros.
32. **AuditLog.html**. Filtros por usuario/acción/entidad/fecha/sede; registro de quién hizo qué, cuándo y desde dónde; alertas por exportaciones masivas, cambios de tarifa y descuentos fuera de regla.
33. **Integraciones.html** (M11). Estado de Kommo, Moodle y Dora; API keys, webhooks, documentación; log de sincronización.

## Flujos principales (para validar con el cliente)
- **Matrícula (como TeamDesk)**: Leads / Estudiantes → NuevaVenta (una matrícula por módulo, factura multi-módulo, plan de cuotas) → (SolicitudDescuento → Aprobaciones si > 10%) → DetalleMatricula → DetalleFactura → Facturas › Cartera → DetalleCurso → CalificarCurso → certificado → rematrícula al terminar lo comprado.
- **Curso**: Cursos → NuevoCurso (valida profesor) → DetalleCurso → Sesiones.
- **Profesor**: Profesores → AltaProfesor → Aprobaciones → FichaProfesor → PaymentSheet.
- **Cierre de mes**: Sesiones → PaymentSheet; ventas → Comisiones → DetalleComision; todo → Reportes / DashboardEjecutivo.

## Pantallas agregadas en la revisión contra TeamDesk (oct 2026)
51. **CalificarCurso.html · Calificar curso** (M3). Cierre de módulo: notas por estudiante (participación 40%, quiz 30%, examen 30%, escala 0–10, aprueba con 7), bloqueo por asistencia < 75%, importar notas del Muro, cerrar módulo y emitir certificados con código de verificación. ← DetalleCurso. → DetalleCurso.
52. **ExamenesInternacionales.html · Exámenes internacionales** (propuesta, fuera de los 11 módulos). Candidatos Cambridge/Oxford/TOEFL/Anglia, factura, estado (inscrito → esperando resultados → listo para retirar → entregado), puntaje y nivel. Reemplaza la tabla International Exams de TeamDesk.
- Facturas suma las pestañas **Cartera** (cuotas vencidas y por vencer con días y seguimiento; reemplaza Portfolio), **Caja del día** (cobros por método, recibos, cierre de caja; reemplaza 1. Cash / List of Payments) y **Sin vincular** (facturas sin matrícula; reemplaza Unlinked invoices / LINK UP).
- Otros agregados: walk-ins en Leads, correo masivo en Estudiantes y Profesores, profesores Standby y Anteriores, papelera en Audit log, multisucursal y tarifa especial en Nuevo curso, tipo de sesión / profesor sustituto / minutos de atraso en Sesión manual, calificar profesor en Detalle de curso, reportes guardados con el nombre de las vistas de TeamDesk, progreso general del programa en el Portal.

- **VerificarCertificado.html** (público, desde el login): verificar un certificado por su código (reemplaza la validación de Issued Certificates de TeamDesk).
- Flujos cerrados en la segunda pasada: ciclo de vida de la matrícula (congelar, reactivar, cambio de curso, retiro, transferencia de saldo) en Detalle de matrícula; lista de espera en Nueva matrícula y Detalle de curso; alta completa en Nuevo estudiante (identificación, facturación, examen de ubicación, consentimiento LOPDP, representante) con "Guardar y matricular"; firma digital de la matrícula; plantillas de correo en Configuración; en el Portal, rematrícula con pago en línea o comprobante, justificar ausencia, pedir reposición y cambiar contraseña.

## Procesos comerciales (oct 2026)
- **TableroComercial.html**, **DetalleVenta.html**, **MatriculaContinuidad.html**, **NuevaInscripcionExamen.html**, **VentaMercaderia.html**, **InformeComisiones.html**. Ver DECISIONES → Procesos comerciales.
- Facturas suma "Pagos por validar" y "Continuidades"; Inventario suma Mercadería; Configuración suma Metas comerciales; Detalle de empresa suma condiciones e historial.

## Pantallas de formulario y acción (agregadas para cerrar todos los flujos)
34. **RecuperarContrasena.html** (M1). Envío de enlace temporal al correo. ← Main. → Main.
35. **RegistrarSesion.html · Sesión manual** (M3). Curso, profesor con validación de contrato, fecha y horas, asistencia por estudiante; alerta si está fuera de horario. ← Sesiones, DetalleCurso, FichaProfesor. → Sesiones.
36. **RegistrarPago.html** (M5). Monto, fecha, método, comprobante; actualiza el estado de cobro de la factura. ← DetalleFactura, Ficha360. → DetalleFactura.
37. **NotaCredito.html** (M5/M7). Factura origen, motivo, monto, devolución de libro al stock. ← DetalleFactura, Movimientos. → DetalleFactura.
38. **RegistrarMovimiento.html** (M7). Ingreso / salida / traslado / devolución con vínculo a factura, curso o pedido. ← Movimientos. → Movimientos.
39. **NuevoPedido.html** (M7). Pedido a Books & Bits con cantidades sugeridas por el forecast de cursos. ← Inventario. → Movimientos.
40. **NuevoUsuario.html** (M1). Datos, rol, sedes visibles, 2FA; muestra los permisos del rol. ← Usuarios. → Usuarios.
41. **NuevaSede.html** (M10). Alta de sede: aparece en selector global, filtros y visibilidad por rol. ← Configuración. → Configuración.
42. **NuevoNivel.html** (M10). Programa, nivel, módulos, horas, precios con vigencia, libro asociado. ← Configuración. → Configuración.
43. **NuevaRegla.html** (M1/M10). Regla de aprobación: entidad, condición, rol aprobador, notificación, vigencia. ← Configuración. → Configuración.
44. **DetalleMatricula.html · Detalle de matrícula** (M5/M2). Equivalente al Enrollment de TeamDesk: **una matrícula por módulo** (nivel = módulo N). Cabecera con estudiante, curso, programa, módulo, horario, asesor y plan de pago; acciones de TeamDesk (cambio de curso, enviar enlace de clase, hoja de asistencia, imprimir matrícula, comentario, reversar y anular). Resumen (subtotal, descuento, total, pagado, saldo, venta multi-módulo, canal, matrícula firmada) y valores con descuento por concepto. Pestañas: Matrículas de la venta, Facturas y pagos, Cartera (cuotas), Códigos de libros, Asistencia, Certificados, Comisión, Historial.

`index.html` redirige al login; el hub es `Mapa.html`. Pantallas ocultas del hub (set `HIDDEN`): Facturas, DetalleFactura, RegistrarPago, NotaCredito.

45. **Insights.html · Insights de IA** (M9/M8). Tablero con todas las observaciones del asistente por área y prioridad: KPIs, distribución por área, evolución semanal y lista de insights con acción directa, marcar como atendido o descartar. En todas las pantallas hay además un asistente flotante contextual (sabe en qué pantalla estás y sugiere preguntas).
46. **PortalEstudiante.html · Portal del estudiante** (propuesta, fuera del alcance de los 11 módulos). Vista de solo lectura para el estudiante: curso actual y próxima clase, avance del nivel, asistencia, puntaje y certificados descargables, paquete de niveles y facturas, datos personales con solicitud de cambio. ← Main ("Soy estudiante"), Ficha360 ("Ver como estudiante"). → Main.
47. **DetalleProducto.html · Detalle de producto o servicio** (M7/M5). Equivale al registro Product/Service de TeamDesk: tipo, categoría, ISBN, precio e IVA, costo del último ingreso, stock por sede con mínimos y pedido en camino, parámetros de matrícula (programa, nivel, módulos, modalidades), códigos de activación comprados, historial de precios y movimientos. ← Configuración → Productos y servicios, Inventario. → NuevoPedido, Movimientos.
48. **Programas.html · Programas, modalidades y tipos de clase** (M3). Jerarquía Programa → Modalidad → Tipo de clase → Curso (Preescolar, Kids, Teens, Adults/ESL, Business); tipos de clase y horas por sesión (grupal 2 h, sábados 4 h, one to one en paquetes de 20/40 h, reducido, Business); plantillas de horario estándar y horario personalizado; calendario de feriados de Ecuador automático y configurable (p. ej. EE. UU.); grupos de Microsoft Teams por curso. ← menú Académico. → NuevoCurso, DetalleCurso, Integraciones.
49. **Leads.html · Leads y conversión** (M11/M5). Flujo Kommo → contacto → cotización → matrícula; KPIs, tabla de leads por etapa, asesor y origen; "Matricular" abre Nueva matrícula con el lead cargado. ← menú Comercial. → NuevaVenta, Ficha360.
50. **Empresas.html · Empresas y grupos B2B** (M2/M5). Vista consolidada por empresa: convenio, estudiantes, cursos, facturación y saldo; detalle del grupo con asistencia, aprobación y rematrícula; exportar PDF y estado de cuenta. ← menú Comercial. → Ficha360, Facturas.
53. **Pedidos.html · Tienda en línea (WooCommerce)** (M5/M11). Pedidos de la tienda virtual con pago Nuvei, etapa y SLA (revisión 4 h, validación 12 h, contacto 24 h); flujo del procedimiento; acciones validar, registrar factura, contactar, correo informativo por producto, incidencia, recuperar venta cancelada; pestañas Incidencias (48 h), Correos al cliente, Certificaciones internacionales (Books and Bits) y Control semanal. Ver `docs/PROCESO_ECOMMERCE.md`. ← menú Comercial, Exámenes. → Facturas, ExamenesInternacionales.
54. **ContratacionProfesores.html · Contratación de profesores** (M3/M10). Pipeline del manual de contratación de servicios profesionales: franja de etapas (selección, evaluación, aprobaciones, alta e inducción), candidatos con etapa, último paso y responsable; pestañas Etapas del proceso (12 pasos del BPMN con responsable), Documentos habilitantes, Hoja de ruta de inducción y Finalización de contrato (checklists). ← Profesores. → DetalleCandidato, AltaProfesor.
55. **DetalleCandidato.html · Detalle de candidato** (M3). Expediente: etapas, informe de entrevista FT-SGC-002, referencias, rúbrica de clase demostrativa D-SGC-002 (6 aspectos de 1 a 5), pay scale propuesto (aprobación de Coord. Administrativa) y documentos habilitantes. ← ContratacionProfesores. → AltaProfesor.

Cambios en pantallas existentes (procesos internos, ver `docs/PROCESOS_INTERNOS.md`): DetalleCurso con "Seguimiento del curso" (72 h / 48 h / bienvenida / 20 % / 50 % / 75 % / encuesta / cierre) e "Indexados" (regular 48 h, urgente 24 h); Cursos con "Reaperturas" (cuadro semanal y protocolo de contacto); CalificarCurso con reglas de cierre (≥ 7.00, 6.50–6.99, ≤ 6.49, deuda); PaymentSheet con novedades (atrasos, cancelaciones, reemplazos), Teacher of the Month y correo al profesor; NotaCredito con reglas del contrato de servicios; Inventario con "Activos fijos por sede" (propuesta fuera del alcance); AltaProfesor y Profesores explican que la alta es el último paso del pipeline.
