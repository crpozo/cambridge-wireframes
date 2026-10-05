# Plataforma Cambridge · contexto del proyecto

## Partes
- **Cliente**: Cambridge School of Languages, instituto de idiomas con 30+ años. Sedes: Quito (centro), Valle de los Chillos, Ambato; Quito Norte en expansión. ~800 estudiantes activos, ~100 profesores (36 activos).
- **Contacto principal / Product Owner**: Estefanía (rol administrativo y financiero, dueña de datos y reportería).
- **Proveedor**: Orkesta S.A.S. (Quito). Da una sola cara al cliente. El trabajo técnico lo ejecuta el arquitecto de software de Orkesta (Carlos, MindfulTech).
- **Contrato**: USD 18,600 + IVA (producto + migración de datos). 20 semanas. Kickoff 21-sep-2026, go-live estimado febrero 2027. Pagos por hitos 25% / 15% / 30% / 30%. Hypercare 30 días post go-live. Fase B (extensión, $2,800) fuera de este alcance. Código fuente pasa al cliente al pago total.

## Situación actual (diagnóstico)
Cambridge opera sobre **TeamDesk** (low-code) con **3 bases de datos independientes, una por sede**, sin cruce de información. Además usa un CRM (Kommo), Moodle (en desarrollo con otra consultora) y Excel/Drive para cálculos.

Problemas identificados en la llamada de diagnóstico (ver `fuentes/Ana_lisis_Tecnico_Comercial_Cambridge.pdf`):

| # | Problema | Severidad |
|---|----------|-----------|
| 1 | 3 bases aisladas, sin vista consolidada ni dashboards unificados | Crítico |
| 2 | Reportería manual y poco confiable: cada reporte nuevo se pide al desarrollador; el reporte de ventas no refleja la venta por niveles | Crítico |
| 3 | Modelo de facturación incompatible: venden por niveles (1 nivel = 2 módulos) pero facturan 1:1 por módulo (4 niveles = 8 facturas) | Crítico |
| 4 | Comisiones de asesores calculadas a mano en Excel, 2 días/mes, sin auditoría | Alto |
| 5 | Sin permisos ni aprobaciones: descuentos del 42% sin autorizar, cualquier coordinador crea profesores. Ya hubo fraude: profesor falso facturando horas | Alto |
| 6 | Pago a profesores manual (sesiones × tarifa en Excel/Drive), no uniforme entre sedes | Alto |
| 7 | Sin integración entre TeamDesk, CRM y Moodle | Medio-alto |
| 8 | Inventario de libros básico (stock negativo, email diario de alertas, sin forecast) | Medio |
| 9 | Sin trazabilidad ni auditoría: cualquiera exporta la base completa; datos de menores (LOPDP) | Medio-alto |
| 10 | Dependencia de una sola persona técnica que conoce TeamDesk | Medio |

## Objetivo
Una plataforma administrativa a medida, multi-sede, que reemplace TeamDesk: base única con filtro global por sede, RBAC y flujos de aprobación, audit log, facturación por niveles con factura consolidada, comisiones automáticas, payment sheet de profesores, inventario, reportes self-service, dashboard ejecutivo, chatbot interno de consultas y APIs de integración. Más la migración de datos desde las 3 bases.

## Alcance contractual (Cláusula Tercera del contrato)
| Módulo | Contenido |
|--------|-----------|
| M1 Core + Auth + RBAC + Audit log | Base unificada multi-sede, login (2FA opcional), roles (Admin General, Director Comercial, Coordinador Académico, Asesor Comercial, Secretaría, Profesor consulta, Gerente General), permisos por acción, trazabilidad completa, control de exportación |
| M2 Gestión de estudiantes | Ficha 360°, búsqueda avanzada, estados, marcadores de datos sensibles (menor, discapacidad), importación/exportación, historial |
| M3 Cursos y sesiones | Creación de cursos (programa, nivel, modalidad, horario, aula), asignación de profesor con validación de contrato activo, registro de sesiones, progreso, notas pass/fail |
| M4 Profesores y pagos | Ficha, alta con aprobación obligatoria, payment sheet automática (sesiones × tarifa), comparativa vs factura del profesor, alertas, historial |
| M5 Facturación por niveles | Venta por paquete de niveles con factura consolidada, tracking de crédito (niveles pagados vs consumidos), descuentos con justificación y aprobación, método de pago y estado de cobro, notas de crédito |
| M6 Motor de comisiones | Reglas configurables sin código (niveles vendidos, modalidad, meta, rango), cálculo mensual, flujo draft → review → approved, meta vs real, exportación |
| M7 Inventario de libros | Stock por sede, alertas, pedidos a proveedor (Books & Bits), ingresos, notas de crédito, forecast básico |
| M8 Dashboards y reportería | Dashboards por rol, reportes self-service con filtros y exportación |
| M9 Chatbot interno | Asistente conversacional para el personal, sobre la base unificada, respetando RBAC |
| M10 Dashboard ejecutivo | Visualizaciones e indicadores gerenciales, complementario a M8 |
| M11 APIs de integración | API REST para Kommo, Moodle y Dora, sujeto a lo que expongan esos proveedores |
| Migración de datos | Extracción de las 3 bases TeamDesk, deduplicación entre sedes, transformación, validación y reconciliación |

Todo lo no listado está fuera de alcance (cambios por adenda).

## Fases
- **Fase 0 · Discovery y diseño** (semanas 1-4): requerimientos, modelo de datos, UX/UI y prototipo, validación con stakeholders. **Los wireframes de este repo son el entregable de esta fase.**
- **Fase 1 · Desarrollo** (semanas 5-16): construcción de los módulos.
- **Fase 2 · QA y go-live** (semanas 17-20): testing, UAT con el equipo de Cambridge, capacitación, despliegue.

## Volumetría para migración
Estudiantes ~800 (3 sedes), profesores ~100, cursos cientos, enrollments e invoices miles, inventario 1,491+ registros, más items, notas de crédito, leads, adjuntos. Valle tiene más campos y automatizaciones que las otras bases. Hay estudiantes duplicados entre sedes.

## Stack sugerido (análisis técnico, no contractual)
React / Next.js, Tailwind, Node.js o Python, PostgreSQL, AWS, GitHub. Dominio por definir.

## Preguntas abiertas con el cliente
- ¿TeamDesk da acceso para exportar las 3 bases completas?
- Modelo de "créditos" por nivel: regla exacta de consumo y vencimiento.
- ¿Qué CRM es Kommo y qué expone su API? ¿Dora qué es exactamente?
- Facturación electrónica SRI: ¿la plataforma emite o solo registra?
- Volumen real de leads y stakeholders que participan en la validación de diseño.
