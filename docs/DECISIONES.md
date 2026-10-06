# Decisiones y supuestos en los wireframes

- **Fidelidad**: mockup v1 con la identidad de Cambridge (azul marino, rojo, amarillo y celeste del sitio cambridgesol.edu.ec), menú lateral oscuro por áreas, tarjetas, KPIs, gráficos (barras apiladas, tendencia, medidores, anillos de progreso) y datos de ejemplo realistas. La URL principal abre directamente el login; el mapa de pantallas queda en Mapa.html. Todos los datos de personas son ficticios.
- **Una sola shell** para toda la plataforma (barra superior + menú lateral agrupado por áreas: Académico, Comercial, Inventario, Dirección, Administración). El selector de sede es global.
- **Tipos de usuario**: Administrador General, Gerente General, Director Comercial, Administrador de Sucursal, Coordinador Académico, Asesor Comercial, Secretaría, Profesor (consulta). El selector "Ver como" de la barra superior simula cada rol: cambian el menú, las pestañas, los accesos de Inicio y las tarjetas del asistente. Un académico no ve nada comercial (venta/matrícula, comisiones, facturación); un asesor no ve profesores, inventario ni configuración. La matriz detallada está en Usuarios y roles y se valida con el cliente.
- **Asistente (M9) proactivo**: además del chat, cada pantalla clave muestra "lo que vale la pena mirar": observaciones generadas sobre la base unificada (sesiones sin confirmar, cursos sin calificar, profesores con horas libres para un curso sin asignar, saldos por cobrar antes del fin de curso, stock negativo). Son de solo lectura y respetan el rol. Supuesto: cabe en el Módulo 9 (consulta ágil de información operativa); si el cliente quiere que el asistente ejecute acciones (asignar, cobrar), eso es una extensión fuera del contrato.
- **Ficha 360 como dashboard** (referencia del cliente): tarjeta de perfil con avatar, ID, estado, contacto, logros y certificados; actividad de aprendizaje semanal por curso; rendimiento con medidor, desglose (participación, tareas, quiz, examen) y tendencia de 6 meses; cursos matriculados con anillo de progreso, estado, nota y certificado. Las pestañas de detalle siguen debajo.
- **Perfil del profesor**: agenda del día, carga semanal vs. máximo del contrato, cursos que dicta con asistencia y avance, pass histórico, disponibilidad para cubrir cursos sin profesor.
- **Rol de ejemplo**: Estefanía · Admin. Los datos de las tablas (nombres, montos) son ficticios.
- **Regla de descuento ilustrativa**: hasta 10% lo aplica el asesor, más de 10% requiere aprobación del Director Comercial. Se confirma con el cliente.
- **Aprobaciones centralizadas** en una bandeja (descuentos, alta de profesores, asignación de profesor sin contrato activo). Toda decisión queda en el audit log y notifica al solicitante.
- **Venta por paquete de niveles** (1 nivel = 2 módulos) con una sola factura consolidada; el crédito del estudiante (niveles pagados vs consumidos) vive en la ficha 360°.
- **Payment sheet** se calcula desde las sesiones confirmadas en Cursos (sesiones × tarifa) y se compara contra la factura que entrega el profesor.
- **Comisiones** se calculan desde las ventas del período con reglas configurables; estados draft → revisión → aprobado.
- **Inventario** se compromete al crear un curso (cupo) y se revierte con notas de crédito.
- **Integraciones** (Kommo, Moodle, Dora) se muestran como pantalla de estado/configuración; el alcance real depende de las APIs de esos proveedores.
- **Fuera de este set**: pantallas de facturación electrónica SRI, portal para estudiantes/padres, app móvil, migración de datos (es un servicio, no una pantalla; podría necesitar un panel de reconciliación en Fase 1).
- Los 12 primeros wireframes se publicaron también como canvas en Claude (Design); la fuente de verdad desde ahora es este repo.

## Mapeo TeamDesk → Plataforma Cambridge (revisado con capturas del sistema actual, oct 2026)

Hoy cada sede es una base TeamDesk independiente ("Cambridge Los Chillos", etc.). La migración las consolida en una sola base con el campo Sede. Se conservan los identificadores legados para reconciliar: código de curso `0001-AAAA-NNNN`, número de matrícula `001-AAAANNNNN`, número de ingreso de inventario `IM AAAAMM-NN`.

| Tabla / vista TeamDesk | En la plataforma | Módulo |
|---|---|---|
| Students (alumnos indexados activos / inactivos / x cruzar) | Estudiantes + vistas guardadas; deduplicación entre sedes en la migración | M2 |
| Enrollments (uno por módulo; level = module N; vendor's commission PAID; cross-checked) | **Matrícula por paquete de niveles** (`DetalleMatricula.html`): un registro cubre 1+ niveles (2 módulos c/u), con cargos (tuition / course fee / libros), descuento con motivo, plan de pago, saldo, asistencia, códigos de libros, certificados y estado de comisión | M5 / M2 |
| Courses (código, programa, level, schedule, elapsed %, end date; vistas Matrículas con saldos, Disponibilidad, Finished courses with ungraded students, Open courses grouped by schedule) | Cursos con código, horario, aula, avance, estado "Terminado sin calificar" y vistas guardadas; Detalle de curso con matriculados, saldos y acción Calificar (pass/fail) | M3 |
| Invoices, Credit Notes | Facturas y notas de crédito consolidadas por matrícula (módulo oculto por ahora en el hub a pedido del cliente; las pantallas existen) | M5 |
| Teachers | Profesores con alta aprobada y payment sheet | M4 |
| Products/Services (código, ISBN, ítem, precio) | Configuración → Productos y materiales | M7 |
| Inventory Management (ingreso por proveedor con factura, comprobante PDF, ítems, pending books / pending codes) | Inventario → Ingresos de proveedor + Códigos de activación | M7 |
| Purchased Book Codes | Códigos de activación por matrícula | M7 |
| Classrooms (capacidad SETEC, dimensiones, sesiones por día) | Configuración → Aulas; validación de cupo y choque de horario al crear curso | M3 |
| Programs | Configuración → Programas y niveles (regla 1 nivel = 2 módulos) | M3 / M5 |
| Employees (Administrador de Sucursal, etc.) | Usuarios y roles (RBAC); se agregan roles Administrador de Sucursal y Gerente General | M1 |
| Companies (RUC, razón social, dirección fiscal) | Configuración → Empresas y convenios; "Facturar a" en la matrícula | M5 |
| Email Templates | Plantillas de notificación (Integraciones / Notificaciones) | M1 |
| Commissions Report, Current month vs last month, New students report, Inscripciones por año, Aprobación vs pérdida de niveles, Saldos negativos… | Reportes guardados del constructor self-service | M8 |
| International Exams, Microsoft Accounts, Portfolio, pruebases | **No están en los 11 módulos del contrato** (Cláusula Tercera 3.2). Se migran como datos históricos; su gestión se decide con el cliente o va por adenda | — |

Reglas confirmadas por los datos actuales: programas English for Adults / Teens / Kids / Tailored; modalidad Virtual / Onsite (presencial); descuentos con motivo (p. ej. "Beneficio cancela 2 módulos"); comisión del asesor se registra por matrícula y se paga al cobrar.
