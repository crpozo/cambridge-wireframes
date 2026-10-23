# Procedimiento · Pedidos de la tienda virtual (WooCommerce)

Fuente: procedimiento interno de Cambridge School of Languages compartido por el cliente (oct 2026). Se refleja en la pantalla `Pedidos.html` (menú Comercial → Tienda en línea) y en `ExamenesInternacionales.html`.

## Objetivo y alcance
Gestionar, seguir y atender los pedidos de la tienda en línea (https://cambridgesol.edu.ec/tienda-virtual-cambridge-sol/) desde que se reciben hasta la entrega del servicio, con respuesta oportuna al cliente, control administrativo y coordinación interna.

## Roles
- **Usuario validador de tienda · Secretaría Académica**: revisa pedidos en WooCommerce (My Account → Sign In), valida pagos, confirma la compra, asigna el caso a coordinación, contacta al cliente, gestiona la prestación del servicio, coordina con el área académica y confirma fechas y horarios.
- **Contabilidad**: confirma la recepción del pago.
- Pedidos cancelados con datos del cliente: llamar para conocer el inconveniente e intentar recuperar la venta.

## Flujo
1. **Recepción automática**: WooCommerce genera el pedido y envía correo al validador. Revisión en máximo 4 horas laborales.
2. **Validación**: pago confirmado en Nuvei (sin rechazo), datos del cliente, producto, correo y teléfono; estado del pedido Pagado/Completado. Máximo 12 horas.
3. **Registro interno**: la factura se registra en el sistema (hoy TeamDesk; en la plataforma, Facturación) según el proceso de ingreso de facturas.
4. **Contacto con el cliente**: explicar los pasos y agendar el servicio si aplica. Máximo 24 horas. Canales: WhatsApp, correo, llamada.
5. **Gestión del servicio** según el producto (Mock Test, traducciones, SIELE/TOEFL; la hoja de productos y procedimientos vive en Drive del cliente).
6. **Control y seguimiento semanal**: número de pedidos, tiempo de respuesta, pedidos sin gestionar, cancelados. Reporte semanal a Dirección Administrativa.

## Indicadores
- Tiempo promedio de contacto con el cliente: meta < 24 h.
- Pedidos atendidos correctamente: meta 99 %.
- Pedidos abandonados: meta < 5 %.
- Conversión ecommerce.

## Incidencias
Pago no registrado, cliente no responde, error en producto, error en precio, duplicación de pedido. Procedimiento: registrar, notificar a Dirección Administrativa y resolver en máximo 48 horas.

## Correos informativos al cliente (Anexo 1)
- **Mock Test Internacional**: pago → contacto de un asesor en 24 h → fecha con 15 días de anticipación → respaldo de inscripción por correo (confirmar) → horarios 3 días antes del examen; disponibilidad todo el día; presencial. Contactos: Secretaría Quito, Valle de los Chillos y Ambato.
- **Traducciones**: hasta 4 páginas ≈ 3 días laborables; más de 5 páginas, tiempo proporcional informado por correo; urgentes con recargo (infoquito@cambridgesol.edu.ec); entrega en PDF por correo; si no adjuntó el documento, enviarlo al mismo correo.
- **SIELE y TOEFL ITP**: contacto en 24 h; inscripción con 15 días de anticipación; respaldo por correo; horarios flexibles, presencial en el instituto. TOEFL ITP: resultados en la institución y certificado físico en ~1 semana. SIELE: certificado digital en la plataforma oficial, con código de verificación y validez de 5 años.

## Certificaciones internacionales (Anexo 2)
Cambridge, Oxford y Anglia se compran en la URL exclusiva de Books and Bits para Cambridge (https://exams.booksandbits.ec/csol). Books and Bits gestiona transacción, información y citas. Llega un correo de confirmación por registro y un correo diario con el cierre de registros. En la plataforma, ese cierre diario alimenta la lista de candidatos de Exámenes internacionales.

## Qué hace la plataforma con esto
- Pantalla **Tienda en línea · pedidos WooCommerce**: pedidos sincronizados con su estado de pago (Nuvei), etapa y semáforo de SLA (4 h / 12 h / 24 h); acciones Validar pedido, Registrar factura, Marcar contactado, Enviar correo informativo (plantillas por producto), Registrar incidencia, Llamar para recuperar venta; pestañas de Incidencias (48 h), Correos al cliente, Certificaciones internacionales (Books and Bits) y Control semanal con reporte a Dirección Administrativa.
- Los productos que se venden en la tienda no se cobran en la plataforma: los botones "Ir a la tienda" y "Abrir WooCommerce" redirigen a la tienda; la plataforma registra el pedido, la factura y el servicio.
- Depende de M11 (integración): WooCommerce (pedidos y estados), Nuvei (resultado del pago) y el correo de cierre diario de Books and Bits.
