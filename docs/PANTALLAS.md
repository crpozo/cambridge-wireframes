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
9. **NuevaVenta.html · Nueva venta por niveles**. Wizard: Estudiante → Niveles → Descuento → Pago → Factura. Reemplaza la facturación por módulo; genera una factura consolidada. → SolicitudDescuento, Aprobaciones, Ficha360.
10. **SolicitudDescuento.html**. Porcentaje, monto resultante, motivo de lista cerrada, justificación. Regla ilustrativa: >10% requiere Director Comercial. → Aprobaciones.
11. **Aprobaciones.html · Bandeja de aprobaciones** (M1). Tabs: descuentos, profesores, asignaciones. Aprobar/rechazar con trazabilidad y notificación al solicitante.
12. **Facturas.html · Listado de facturas**. KPIs de facturado/cobrado/pendiente, tabla con estado de cobro. → DetalleFactura, NuevaVenta.
13. **DetalleFactura.html**. Líneas por nivel, descuento aprobado, libros, total, método y estado; notas de crédito y cambio de curso; registrar pago.

## Flujo académico (M3)
14. **Cursos.html · Listado**. Filtros programa/nivel/modalidad/estado, ocupación, profesor. → DetalleCurso, NuevoCurso.
15. **NuevoCurso.html**. Programa, nivel, modalidad, tipo, sede, aula, fechas, horario, horas, cupo; selección de profesor con validación de contrato activo (si no, va a aprobación). Al crear se compromete stock de libros. → DetalleCurso.
16. **DetalleCurso.html**. Horario y progreso, profesor asignado, sesiones (automáticas/manuales/pendientes), estudiantes con asistencia, nota y estado. → Sesiones.
17. **Sesiones.html · Registro de sesiones**. Vista semanal tipo calendario, confirmar o marcar no dictada, alertas (fuera de horario, contrato vencido, curso sin sesiones). Alimenta progreso y payment sheet.

## Flujo profesores (M4)
18. **Profesores.html · Listado**. Contrato, tarifa, cursos activos, estado. Alta de profesor y acceso a payment sheet. → AltaProfesor, FichaProfesor, PaymentSheet.
19. **AltaProfesor.html · Alta con aprobación**. Datos, contrato, tarifa, vigencia, archivo firmado. Queda "pendiente de aprobación" hasta que Dirección apruebe; recién entonces puede recibir cursos y pagos. → Aprobaciones.
20. **FichaProfesor.html · Perfil del profesor**. KPIs (dictando ahora, horas de la semana vs. contrato, asistencia de sus cursos, pass), tabs: Agenda y carga (clases de hoy, carga semanal, cursos que dicta, asistente), Datos, Contrato y tarifa, Cursos (histórico con asistencia y pass), Sesiones, Historial de pagos. Acción Asignar a curso. → PaymentSheet, DetalleCurso.
21. **PaymentSheet.html**. Mes, sede, estado (borrador/aprobado). Por profesor: sesiones, horas, tarifa, a pagar, factura del profesor, alerta de diferencia o contrato vencido. Aprobar pagos, exportar.

## Comisiones (M6)
22. **Comisiones.html · Período**. Estado draft → revisión → aprobado; tabla por asesor (niveles, modalidad, meta, real, comisión); gráfico meta vs real; reglas activas. → DetalleComision, ReglasComision.
23. **DetalleComision.html · Detalle por asesor**. Cada venta con la regla que la generó, bonos, historial, exportar.
24. **ReglasComision.html**. Tabla de reglas (rangos, modalidad, bono meta, vigencia), nueva regla, simulador contra ventas pasadas. Cambios al audit log.

## Inventario (M7)
25. **Inventario.html · Stock por sede**. Libro × sede, comprometido por cursos abiertos, alertas de pedido. → Movimientos.
26. **Movimientos.html**. Tabs: movimientos, pedidos a proveedor (Books & Bits), notas de crédito; registrar ingreso; forecast por cursos próximos.

## Reportes y dashboards (M8 + M10)
27. **Reportes.html · Dashboard por rol**. KPIs (ventas por nivel real, matrículas, cobros, ocupación), gráficos por sede/modalidad y pipeline comercial, bloque de reportes self-service. → ConstructorReportes, DashboardEjecutivo.
28. **ConstructorReportes.html**. Entidad, columnas, filtros, rango; reportes guardados (reemplazo del "New Students Report"); resultado y exportación.
29. **DashboardEjecutivo.html** (M10). Ingresos YTD, estudiantes activos, ticket promedio, margen por sede; ingresos por mes/sede, mix programa/modalidad, funnel comercial, retención por nivel.

## Administración y gobierno (M1 + M11)
30. **Usuarios.html · Usuarios y roles**. Listado de usuarios con rol y sedes visibles; matriz de permisos por rol.
31. **Configuracion.html**. Tabs: sedes, catálogo de niveles y precios, tarifas de profesores, reglas de aprobación, parámetros.
32. **AuditLog.html**. Filtros por usuario/acción/entidad/fecha/sede; registro de quién hizo qué, cuándo y desde dónde; alertas por exportaciones masivas, cambios de tarifa y descuentos fuera de regla.
33. **Integraciones.html** (M11). Estado de Kommo, Moodle y Dora; API keys, webhooks, documentación; log de sincronización.

## Flujos principales (para validar con el cliente)
- **Venta**: Estudiantes → Ficha360 → NuevaVenta → (SolicitudDescuento → Aprobaciones) → DetalleFactura.
- **Curso**: Cursos → NuevoCurso (valida profesor) → DetalleCurso → Sesiones.
- **Profesor**: Profesores → AltaProfesor → Aprobaciones → FichaProfesor → PaymentSheet.
- **Cierre de mes**: Sesiones → PaymentSheet; ventas → Comisiones → DetalleComision; todo → Reportes / DashboardEjecutivo.

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
44. **DetalleMatricula.html · Detalle de matrícula** (M5/M2). Equivalente al Enrollment de TeamDesk pero por paquete de niveles: estudiante, curso (código), horario, asesor, plan de pago; resumen (subtotal, descuento, total, pagado, saldo); cargos (tuition, niveles, libros); tabs Facturas y pagos, Códigos de libros, Asistencia, Certificados, Comisión. Acciones: cambio de curso, enviar enlace de clase, hoja de asistencia, anular (con aprobación). ← Ficha360, DetalleCurso, NuevaVenta.

`index.html` redirige al login; el hub es `Mapa.html`. Pantallas ocultas del hub (set `HIDDEN`): Facturas, DetalleFactura, RegistrarPago, NotaCredito.

45. **Insights.html · Insights de IA** (M9/M8). Tablero con todas las observaciones del asistente por área y prioridad: KPIs, distribución por área, evolución semanal y lista de insights con acción directa, marcar como atendido o descartar. En todas las pantallas hay además un asistente flotante contextual (sabe en qué pantalla estás y sugiere preguntas).
