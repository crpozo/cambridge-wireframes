# Guía de prueba · Cambios de la reunión (matrícula, factura, referidos, estados y mensajes)

Servidor local: http://localhost:8765/ (o abre los `.html` de la carpeta). Datos de ejemplo ficticios.

## 1. Representante desde los 18 años
1. Estudiantes → **Nuevo estudiante** (`NuevoEstudiante.html`). En "Fecha de nacimiento" pon una fecha que dé 17 años: la tarjeta pasa a "Representante · obligatorio (17 años)".
2. Pon una fecha que dé 18 años o más: pasa a "opcional (mayor de edad)". La regla de TeamDesk era 22; aquí el corte es 18.
3. En **Nueva matrícula**, paso 1, "¿Menor de 18 años?" = Sí pide nombre, teléfono y correo del representante.

## 2. Datos de la factura copiados del estudiante
1. Comercial → **Nueva matrícula** → avanza hasta el paso 4 "Factura y pago".
2. En la tarjeta "Datos de la factura" pulsa **Usar los datos del estudiante**: se llenan nombre, identificación, correo, dirección y teléfono. Edítalos si la factura va a otra persona.

## 3. Nivel y horario editables al matricular
Paso 2 "Programa y cursos": cambia **Nivel de ingreso (editable)** (por ejemplo a B2) y **Horario (editable)** (incluye "Otro horario · se acuerda con Académico"). El curso se elige después.

## 4. Referidos
En cualquier formulario con origen del lead (Nueva matrícula paso 1, Registrar walk-in, Nuevo lead): elige "¿Es referido?" = Sí y aparece **Referido por**. Sirve aunque el lead haya entrado como Walk in o por WhatsApp.

## 5. Una sola factura por venta
En el paso 4 de Nueva matrícula la tabla "Ítems de la factura" trae los módulos 7, 8, 9 y 10, el material y lo demás en **una sola factura**; ya no hay facturas separadas por módulo ni una factura manual extra.

## 6. Activo, inactivo o nuevo según el tiempo sin matrícula
Paso 1 de Nueva matrícula: cambia **Tiempo sin matrícula**.
- Hasta 2 meses: Activo, continúa sin test ni inscripción.
- 3 a 5 meses: Inactivo; mantiene su continuidad, solo repite el test y no paga inscripción.
- 6 meses o más: se trata como nuevo, paga inscripción. La **Clasificación** se ajusta sola.

## 7. Aceptación de términos con registro
Paso 4: marca **El estudiante acepta los términos…**. Aparece la fecha, la hora y el correo del comprobante. "Enviar enlace de compra con aceptación" simula el enlace por correo. Está marcado como requerimiento por validar con el equipo legal.

## 8. Canal de contacto editable
Estudiantes → **Ficha 360** → pestaña **Datos**: cambia "Canal de contacto (editable)" (por ejemplo de Walk in a Referencia / Referido). Debajo aparece el cambio con fecha, hora y quién lo hizo.

## 9. Mensajes de bienvenida y avisos (WhatsApp)
Automatizaciones (`Automatizaciones.html`):
- Pestaña **Reglas**: nuevas reglas "Bienvenida al matricularse", "Grupo y mensaje de apertura" (48 h antes) y "Fin de módulo: aviso del siguiente curso". Enciende o apaga una y mira el contador.
- Pestaña **Plantillas** → "Bienvenida", "Recordatorio al grupo" y "Fin de módulo": vista previa y variables.
WhatsApp está marcado como propuesta fuera del alcance del contrato (requiere la API de WhatsApp Business y que Meta apruebe cada plantilla). Los correos sí están dentro del alcance. Pendiente: el flujo con Cris.

## 10. Reportería automática del total facturado
Reportes → **Constructor de reportes** → área "Ventas y facturación": "¿Cuánto facturamos en total este mes?" y "¿Qué matrículas están pagadas por completo y cuáles son abonos?". Para sedes consolidadas, Tablero comercial → Plan estratégico (ver la otra guía).

## Ya estaba o es dependencia
- **Integrar Kommo con la plataforma** (sin registros manuales): ya existe Leads → Matrícula desde un lead; la conexión real depende de lo que exponga la API de Kommo.
- **Sincronizar reportes de sedes**: Tablero comercial → "Consolidado por sede" y el Plan estratégico.

## 11. WhatsApp simulado (como se vería con la API de WhatsApp Business)
Automatizaciones → pestaña **WhatsApp**:
1. Revisa "Conexión" (número, estado, calidad) y "Plantillas aprobadas por Meta" (aprobada, en revisión, rechazada).
2. En "Probar el envío" elige estudiante y plantilla; ves el texto con sus variables y pulsas **Enviar mensaje de prueba**.
3. En el teléfono aparece el mensaje y pasa de Enviando a Enviado, Entregado y Leído; unos segundos después llega una respuesta de ejemplo. El registro de la izquierda y los contadores se actualizan.
Todo es simulación: no se envía nada real. Sigue siendo propuesta fuera del alcance del contrato.
