# Documentación del cliente · 18 nov 2026

Cinco documentos enviados por Cambridge (R-02, R-09, R-12 ×2, R-13). Este resumen no copia nombres ni correos: los originales quedan fuera del repo.

## R-02 · Área e interlocutor

Validadores por área para el levantamiento. Interlocutor general: Dirección Administrativa.

| Área | Validador (cargo) | Enfoque | Rol en la plataforma |
|---|---|---|---|
| Contable - Financiero | Contadora General | compras, facturación y retenciones (SRI y Dora), tesorería, cajas, inventario y proyecciones, notas de crédito, conciliación bancaria, nómina | `CON` Contabilidad |
| Comercial | Directora Comercial | B2C y B2B, KPIs, CRM, pagos, facturación y matriculación, cartera | `DIR` Director Comercial |
| Marketing | Directora de Marketing | captura de leads, campañas, performance, analítica, redes, CRM | **`MKT` Marketing (nuevo)** |
| Administración | Directora Administrativa | presupuesto, sucursales, comunicación, pagos al personal, operación general | `ADM` Administrador General |
| Académico / Secretaría | Dirección General Académica | docentes, seguimiento y retención, plataformas, aperturas y reaperturas, inventario de libros | `COO` y `SEC` |

**En la plataforma**: rol `MKT` en `ROLES` ("Ver como" → Marketing). Ve Inicio (leads del mes, leads sin sede u origen, conversión, canales en meta), Programas, Cursos, Leads, Tablero comercial (sin Cobros, Metas por asesor ni Consolidado), Reportes e Insights. No ve estudiantes, facturación, comisiones ni inventario.

## R-09 · Cálculo de comisiones (tabla de julio 2026, videos del proceso y propuesta para Dirección Comercial)

Primero llegó un documento que solo tenía dos enlaces a Loom. Después llegaron la tabla de cálculo de julio, las transcripciones de los videos y la propuesta de comisiones de la Dirección Comercial. Los originales contienen nombres y ventas reales y no se suben al repo. En el prototipo solo se usan los montos y las reglas.

**Asesores** (Quito, Valle y Ambato; Cuenca lleva otro proceso):
- Se paga el mes siguiente: en octubre se pagan las matrículas nuevas de septiembre.
- **Base**: las primeras 30 matrículas del mes en Quito y Valle, y 12 en Ambato, no comisionan. Se cuentan módulos y niveles en orden de llegada. Si el asesor cumple la meta comercial, la base baja a la mitad (15 y 6).
- **Módulo suelto**: monto fijo por matrícula de 1 módulo. Presencial: Preschool y Kids $12, Teens y Adults $10. Virtual: Teens $10, Adults $10.14. Online: $8.10.
- **Niveles**: monto fijo por venta según cuántos módulos tiene (de 2 a 13), el programa (Preschool, Kids, Teens, Adults) y la modalidad (presencial/híbrido, virtual, online). Ejemplos: 1 nivel de Adults presencial $22, 2 niveles $44; 1 nivel de Adults virtual $18.72.
- **One to one**: por horas vendidas (20 a 90 h), en cuatro columnas: presencial normal, presencial preparatoria, virtual normal y virtual preparatoria. No suma a la base. El de menos de 20 horas sí suma a la base.
- **Otros**: summer camp $6 por matrícula; matrículas de meses anteriores cobradas en el mes, $10 cada una; bono grupal de $100 si Quito y Valle llegan juntos a la meta. Business corporativo no comisiona.
- **Control**: la exportación del sistema se cruza con el reporte comercial manual; las que no cruzan se revisan una por una.

**Dirección Comercial**:
- La base comercial es el ingreso por matrículas nuevas del mismo mes, promedio de los últimos tres años, por sede.
- Se paga un porcentaje sobre el excedente (venta real − base), nunca sobre la venta total.
- Tramos: menos de 5 % de crecimiento, sin comisión; 5–9.99 %, 1 %; 10–14.99 %, 2 %; 15–19.99 %, 3 %; 20 % o más, 4 %.

**En la plataforma**:
- `ReglasComision.html` tiene seis pestañas con las tablas reales (`COM_NIV`, `COM_MOD`, `COM_O2O_V`): Niveles por venta, Módulo suelto, One to one por horas, Base y bonos, Dirección Comercial y Simulador.
- `DetalleComision.html` ("Mi comisión") muestra el cálculo paso a paso de Carla M. y la lista de matrículas en orden de llegada (de la 1 a la 15 es base). Total: $32.14 + $163.72 + $19.80 + $22 + $100 = **$337.66**.
- En `Comisiones.html` la tabla del equipo muestra sede, matrículas válidas, base, cantidad sobre la base y comisión.
- La venta de María Andrade comisiona $39.00 (2 niveles de Adults virtual).
- Las cifras son ficticias.

## R-12 · Descriptivo de métricas e indicadores comerciales

Tarjetas, líneas, barras, participación y glosario de variables (matrícula efectiva, lead asignado, upsell, activo frente a retirado). Criterios transversales: valores netos, fórmulas que se recalculan con los filtros, comparación interanual sobre el mismo rango de días.

**En la plataforma**: casi todo ya existía en Tablero comercial → "Indicadores y gráficos" (`assets/plan.js`). Nueva pestaña **"Diccionario de métricas"** (`diccionario_metricas()`, datos en `DICC`): cada indicador con qué mide, fórmula, formato y enlace a la pestaña donde se ve, más los criterios y el glosario. Se busca también desde la barra superior.

## R-12 · Descriptivo de mediciones mensuales (informe de sede)

Informe mensual por sede con **cuadre único**: el total de matrículas (65 en el corte de referencia) debe coincidir en condición de pago, estrategia, descuento, modalidad y grupo etario.

**En la plataforma**: nueva pestaña **"Informe mensual de sede"** (`informe_mensual()`, reparto con `_reparto()` para que cada desglose sume el total). Control por sede: Quito, Valle de los Chillos (65, como el documento), Ambato y Consolidado. Contenido:

- Matrículas: completas, en cuotas, con abono y con descuento.
- Embudo de Kommo: recibidos, sin contactabilidad, SQL, perdidos y ganados (ganados = matrículas), con la conversión global.
- Servicios adicionales aparte: pruebas internacionales, summer, traducciones y español.
- Matrículas por canal y forma de pago.
- Embudo por medio, separado en estrategias digitales y directas.
- Participación por condición de pago, estrategia y descuento.
- Modalidad: presencial, virtual, online puro, one to one y summer.
- Grupo etario: Pre-School, Kids, Teens y Adults.
- Motivos del walk-in ganado.
- Evolución mensual.
- Línea de verificación "Cuadra" / "No cuadra".

Otros cambios:
- **Leads**: las etapas pasan a los estados de Kommo del informe: sin contactabilidad, calificados (SQL), perdidos y ganados. En cada sede suman los leads recibidos.
- **Nueva matrícula** y **Matrícula desde lead**: el plan de pago agrega "Abono · pago parcial que separa el cupo", así las tres condiciones de pago salen de la matrícula.

## R-13 · Manual de procesos de Marketing (MP-MKT-01 a 06)

| Requerimiento | Clasificación | Dónde |
|---|---|---|
| Sede obligatoria y origen trazable en todo lead y venta | Dentro (M2, M8, M11 Kommo) | catálogo de orígenes, Leads, Tablero |
| Venta con canal de origen y condición comercial (precio lleno o descuento y tipo) | Dentro (M5, M8) | Informe mensual → "Ventas por canal frente a la meta" |
| Matriz de metas por canal y sede; alerta con cumplimiento < 80 % o más del 50 % de ventas con descuento (propuesta a validar) | Dentro (M8, metas del tablero) | Informe mensual |
| Tablero B2B: convenios, estudiantes comprometidos frente a inscritos, plan de activación < 70 % | Dentro (M5 convenios, M8) | Empresas → columna "Inscritos frente a comprometidos" |
| Tasa de cierre calculada con datos de matrícula | Dentro (M8) | Informe mensual, Indicadores |
| Reporte semanal automático los lunes | Dentro como aviso interno (M8 / automatizaciones); envío por correo a externos no | Automatizaciones (resumen semanal) |
| Deduplicación, reglas de asignación y SLA de primer contacto | En Kommo, no en la plataforma | — |
| Costo por matrícula y ROAS por canal, campaña y sede; conectores a Meta, Google, TikTok y LinkedIn; envío de conversiones offline | **Fuera del alcance** (M11 solo incluye Kommo, Moodle y Dora) | tarjeta "Propuesta · fuera del alcance" en el Informe mensual |
| Flujo de aprobación de campañas, checklist de marca, calendario de campañas, banco de medios con autorizaciones, tickets de crisis, biblioteca de respuestas | **Fuera del alcance** (no está en los 11 módulos) | — |

## Preguntas para Cambridge

1. Comisiones: ¿el bono grupal tiene rangos según cuánto se supera la meta (el video dice "según el rango que hayan llegado")? ¿Cuál es la meta comercial por asesor que baja la base a la mitad?
2. Estados de Kommo: ¿"sin contactabilidad" y "SQL" existen como etapas en su pipeline? El informe depende de que la API los exponga.
3. "Online puro": ¿es una modalidad distinta de virtual en el catálogo?
4. Abono: ¿cuál es el monto mínimo para separar el cupo y cuánto tiempo lo reserva?
5. Las reglas de alerta (80 % de cumplimiento, 50 % con descuento, 70 % de inscritos en convenios) están marcadas como propuesta a validar en el manual: ¿quedan así?
6. Costo por matrícula y ROAS: si los quieren, se cotiza aparte (conectores de pauta), o se carga la inversión a mano por canal y sede.
