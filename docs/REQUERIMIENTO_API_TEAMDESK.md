# Pedido a Cambridge · acceso a TeamDesk para la migración

La migración contratada consolida las bases TeamDesk de cada sede en una sola base con el campo Sede (ver `docs/DECISIONES.md` → Mapeo TeamDesk → Plataforma). Para extraer los datos por la API REST de TeamDesk necesitamos lo siguiente.

## 1. Accesos (uno por cada base)

| # | Qué | Detalle |
|---|---|---|
| 1 | Lista de bases | Nombre y sede de cada base TeamDesk (Quito, Valle de los Chillos, Ambato; confirmar si Cuenca tiene base propia y si entra en la migración). |
| 2 | ID de cada base | El número que aparece en la URL al abrir la base (`teamdesk.net/secure/db/<ID>/…`). |
| 3 | Token de API de solo lectura por base | Se crea en Setup → Integraciones → REST API (tokens de autorización). Debe estar asociado a un usuario o rol que pueda **leer todas las tablas, columnas (incluidas las ocultas o restringidas) y archivos adjuntos**. Sin permisos de escritura. |
| 4 | Vigencia del token | Hasta el cierre de la migración (go-live, feb 2027). Después Cambridge lo revoca. |
| 5 | Plan y límites | Plan contratado de TeamDesk y límite de llamadas a la API; confirmar que la API REST está habilitada en ese plan. |
| 6 | Restricción por IP | Si los tokens tienen restricción por IP, autorizar las IP que Orkesta indique. |
| 7 | Usuario de consulta | Un usuario de solo lectura en la interfaz de cada base, para revisar fórmulas, vistas, listas desplegables y automatizaciones. |

**Envío seguro**: los tokens no se mandan por correo ni por WhatsApp en texto plano; se comparten por un gestor de contraseñas o un enlace de un solo uso.

## 2. Tablas que se van a extraer

Confirmar por base cuáles están en uso y cuáles son obsoletas:

- **Núcleo**: Students, Enrollments, Courses, Invoices, Credit Notes, Portfolio (cuotas), Teachers, Companies.
- **Catálogo e inventario**: Products/Services, Programs, Classrooms, Inventory Management, Purchased Book Codes.
- **Usuarios y plantillas**: Employees, Email Templates.
- **Por aclarar** (no están en los 11 módulos; se migran como histórico si se confirma): International Exams, Microsoft Accounts, Pacients, Jotform Webhooks, Indexes, pruebases.

Para cada base indicar si tiene tablas o columnas propias (sabemos que Valle tiene más campos y automatizaciones que las otras).

## 3. Datos y archivos

| # | Qué | Por qué |
|---|---|---|
| 8 | Desde qué año se migra | Todo el histórico o desde un año de corte. |
| 9 | Adjuntos | Comprobantes de pago, contratos (Enroll Doc), cédulas, facturas y guías de proveedor: confirmar que se migran y el volumen aproximado (GB). Se descargan por la API. |
| 10 | Historial de cambios | Si necesitan conservar quién cambió qué en TeamDesk, o basta con el estado final de cada registro. |
| 11 | Listas de valores | Valores vigentes de los desplegables: estados de matrícula y factura, programas, modalidades, motivos de descuento, Contact Channel, categorías de producto. |
| 12 | Fórmulas y automatizaciones | Cómo se calculan los campos clave (saldos, Vendor's commission PENDING/PAID/NA, % de avance del curso) y qué avisos automáticos tienen hoy (por ejemplo, notify de stock). |

## 4. Reglas para consolidar las sedes

| # | Qué |
|---|---|
| 13 | Criterio para detectar al mismo estudiante en dos sedes: cédula o pasaporte, correo, teléfono. ¿Cuál manda si los datos difieren? |
| 14 | Significado de los estados y tipos (status de matrícula, type of student, indexed, cross-checked). |
| 15 | Qué hacer con registros de prueba, duplicados o incompletos (se depuran o se migran marcados). |

## 5. Operación de la migración

| # | Qué |
|---|---|
| 16 | Persona de contacto que conoce TeamDesk, con unas horas a la semana para resolver dudas. |
| 17 | Ventana de congelamiento: fecha y hora en que se deja de registrar en TeamDesk para la extracción final. |
| 18 | Validación: quién de cada área revisa los conteos y muestras después del ensayo de migración (estudiantes, matrículas, facturas, saldos, inventario). |
| 19 | Confidencialidad: acuerdo de tratamiento de datos personales (LOPDP) para el manejo de la información de estudiantes. |

## Plan B si la API no está disponible

Exportación CSV de cada tabla **con el ID interno de cada registro y las columnas de relación**, más un ZIP de los adjuntos por tabla. Con eso se puede reconstruir el modelo, aunque con más trabajo manual.
