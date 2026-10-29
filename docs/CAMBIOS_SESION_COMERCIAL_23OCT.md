# Cambios al prototipo tras la revisión del módulo comercial (23 oct 2026)

Fuente: "Cambios al prototipo y próximos pasos" y "Análisis de sesión: revisión del módulo comercial" (Orkesta, 29 oct 2026). Estado de cada cambio en el prototipo.

| Pantalla | Cambio pedido | Estado · dónde |
|---|---|---|
| Leads | Embudo de Kommo solo como resumen de consulta (contactado, cotizado, matriculado, perdido) | Hecho · franja de etapas sin "Nuevo", con nota "el trabajo diario sigue en Kommo" |
| Leads | Lista de trabajo solo con leads ganados que vienen de Kommo | Hecho · tabla "Lead ganado" con columna "Quién estudia" y "Ganado en Kommo"; filtro Etapa reemplazado |
| Leads → matrícula | Editar la ficha o agregar un estudiante dependiente (papá lead, hijo estudiante) | Hecho · `MatriculaLead.html` paso 1 "¿Quién estudia?" (la misma persona / dependiente con sus datos y relación) |
| Nueva matrícula · paso 1 | Selector de tipo de transacción: regular, examen internacional (cédula escaneada, fecha de nacimiento, correo), solo facturación | Hecho · primer campo, con campos dependientes |
| Paso 1 | Correo del estudiante obligatorio | Hecho |
| Paso 1 | Menor de 18 → representante (nombre, teléfono, correo) | Hecho · "¿Menor de 18 años?" muestra los campos |
| Paso 1 | "Paga la empresa" separa alianza (paga el estudiante con descuento) de convenio (paga la empresa: factura individual en $0 + factura global) | Hecho · con nota "validar la factura en $0 con el contador" |
| Paso 2 | "N módulos desde el módulo X", empezar en módulo par | Hecho · "Qué compra" → desde el módulo (1–14) + cantidad |
| Paso 2 | Opción por horas con cantidad (one to one o personalizado) | Hecho |
| Paso 2 | Mostrar cuántos módulos u horas compró (comercial y secretaría) | Hecho · "Lo que compra / se matricula ahora / quedan en la bolsa" en el paso, en el resumen lateral, en la confirmación y en la Ficha 360° (bolsa de módulos) |
| Paso 2 | Cupo disponible por grupo y bloqueo al llenarse | Hecho · cupo en cada grupo y opción "LLENO · 15/15 · bloqueado" en el selector |
| Paso 2 | Virtuales compartidos: ocupación total sumando sedes | Hecho · "12 de 15 · Quito 7 · Valle 3 · Ambato 2" |
| Paso 3 | Cargar la tabla real de descuentos | Parcial · el selector usa una tabla de descuentos (`DESCUENTOS`) de ejemplo; la real la envían Dayana y Estefanía |
| Paso 3 | Aplicar el descuento de la empresa cuando corresponda | Hecho · opciones de convenio/alianza en la tabla y nota de que no se suma a otro |
| Paso 4 | Varios ítems en una factura, cada uno con código | Hecho · tabla de ítems (módulos, material, horas extra, merch) + "Agregar ítem" |
| Paso 4 | Material sugerido editable: solo el del primer nivel; quitar, físico ↔ licencia, medio material en pares | Hecho · tabla "Material sugerido · editable" con selector por módulo |
| Paso 4 | Recordatorios automáticos de cuotas a estudiante/representante con copia al asesor + campanita | Hecho · tarjeta "Pagos y cuotas" |
| Empresas | Solo un rol con permiso edita el descuento; aplica a matrículas nuevas | Hecho · "Editar descuento del convenio" solo ADM/GER/DIR |
| Empresas | Contadores: vinculados, activos, en curso, finalizados | Hecho · franja por empresa |
| Empresas | Convenio: factura global a crédito y estado del cobro | Hecho · factura global con vencimiento, estado y "Conciliar pago de la empresa" |
| Tablero | Filtros por sede y período: hoy, ayer, 1–15, mes, rango libre | Hecho · período con "Del 1 al 15" y "Del 16 a fin de mes"; sedes combinables |
| Tablero | Matrículas y montos por origen, detalle de referidos, servicio educativo vs total | Hecho · pestaña "Por origen" |
| Tablero | Ventas nuevas y de continuidad con índice de retención | Hecho · indicadores de "Hoy y acumulado" |
| Tablero | Metas por asesor: cuánto lleva y cuánto falta | Hecho · pestaña "Metas por asesor" |
| Comisiones | Tablas de rangos por módulos/niveles, modalidad, base por sede y one to one; Estefanía configura, el asesor consulta y exporta | Hecho · `ReglasComision.html` con pestañas por producto y sede; Comisiones muestra la tabla vigente y "Exportar Excel" |
| Comisiones | Reporte mensual en tres grupos: 2 módulos o más, sueltos, horas | Hecho · tabla en Comisiones |
| Portal | "Rematricularme" con el saldo de módulos pagados; aviso con contacto si hay saldo pendiente | Hecho · bolsa de módulos en la tarjeta de rematrícula y texto del aviso |
| Datos de ejemplo | Listas reales (orígenes, programas, precios, catálogo, libros) | Pendiente de Cambridge · orígenes ya con el catálogo de Dayana; programas con los 12 de TeamDesk |

## Pendientes de Cambridge (del documento)
Métricas del tablero con su cálculo e informe mensual (Dayana) · catálogo de cursos con libros, precios y códigos (Estefanía) · listas desplegables reales y disponibilidad para la sesión con secretaría (Estefanía) · tabla de descuentos (Dayana y Estefanía) · revisión del prototipo (Majo y Andrea).

## Pendientes de Orkesta (del documento)
Resumen escrito MVP vs Fase B · estimación de horas (comisiones, bolsa de módulos con rematrícula, facturación a crédito, notas de crédito) · revisar la tabla de comisiones enviada por Estefanía (las tablas del prototipo son de ejemplo) · diseñar el webhook de Kommo al pasar a "ganado" y el modelo de datos de la bolsa de módulos · validación del contador (factura en $0, ingreso diferido, notas de crédito) · sesión con secretaría con una matrícula completa hecha por Majo.

## Propuesta de clasificación de alcance (para el resumen a Cambridge; decide Orkesta)
- **MVP**: tipo de transacción, correo obligatorio, representante, alianza vs convenio, N módulos desde X u horas, cupos con bloqueo, factura con varios ítems, material sugerido editable, recordatorios de cuotas, filtros del tablero por sede y período, origen de las matrículas, ventas de continuidad, leads ganados desde Kommo (webhook), contrato con aceptación electrónica.
- **Fase B o cambio de alcance (estimar)**: motor de comisiones por tablas de rangos, bolsa de módulos con rematrícula automática (depende de Moodle y de la creación de grupos por académico), facturación corporativa a crédito con conciliación, notas de crédito emitidas directo al SRI, ocupación consolidada entre sedes en tiempo real, metas por asesor con histórico.
