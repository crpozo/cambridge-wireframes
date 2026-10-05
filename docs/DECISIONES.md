# Decisiones y supuestos en los wireframes

- **Fidelidad**: lo-fi a propósito. Cajas grises, texto de ejemplo, sin colores de marca. Objetivo: validar flujo y contenido con Estefanía antes del diseño UX/UI.
- **Una sola shell** para toda la plataforma (barra superior + menú lateral). El selector de sede es global y lo que se ve depende del rol (RBAC). El Admin ve todas las sedes; un asesor solo la suya.
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
