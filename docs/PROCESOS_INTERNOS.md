# Procesos internos de Cambridge y cómo los refleja la plataforma

Resumen (sin datos personales) del **Manual de Procesos** y los documentos de contratación docente que el cliente entregó el 23 oct 2026. Los archivos originales (contrato de servicios, formatos, checklists, hojas de cálculo de activos y de conteo de horas) contienen datos reales de estudiantes y profesores y **no se suben al repo**; aquí va solo su estructura y sus reglas. Este documento complementa `PROCESO_ECOMMERCE.md` (tienda en línea).

## Académico

### 1. Contratación de profesores (servicios profesionales) → `ContratacionProfesores.html`, `DetalleCandidato.html`, `AltaProfesor.html`
Fuentes: Manual de contratación de servicios profesionales 2026, diagrama BPMN, banco de preguntas (D-SGC-001), informe de entrevista (FT-SGC-002), rúbrica de clase demostrativa (D-SGC-002), formato de referencias de empleo, checklists de hoja de ruta y de finalización de contrato.

Etapas y responsables (carriles del BPMN: Coordinación Académica, Asistente de Gerencia, Dirección General Académica, Coordinación Administrativa, Dirección Administrativa):
1. Vacante aprobada (Coord. Académica detecta; DGA aprueba abrir el proceso).
2. Anuncio en LinkedIn y web; los CV llegan a la carpeta compartida de la sede (Asistente de Gerencia).
3. Revisión de CV y entrevista telefónica.
4. Referencias: 2 laborales + 1 personal (cargo, período, motivo de salida, ¿lo volvería a contratar?).
5. Entrevista de contratación con informe FT-SGC-002: trayectoria profesional, intereses personales, conocimiento docente, preguntas para docentes sin experiencia, manejo de clase, enseñanza virtual, desarrollo profesional, expectativas; cierra con "¿Continúa el proceso? Sí/No". El banco D-SGC-001 sugiere 2 o 3 preguntas por área.
6. Clase demostrativa con rúbrica D-SGC-002: seis aspectos (planificación, ambiente de aprendizaje, recursos, lenguaje y destrezas, manejo de clase, evaluación y retroalimentación) de 1 "necesita mejorar" a 5 "excelente"; retroalimentación escrita.
7. MOCK C1: resultado mínimo B2 para dictar.
8. Entrevista formal con Dirección General Académica.
9. Pay scale según sede, título y MOCK; lo aprueba Coordinación Administrativa.
10. Validación de documentos habilitantes y aprobación de la contratación por Dirección Administrativa.
11. Alta del profesor (crea el perfil Coordinación Académica), correo de bienvenida e inducción.
12. Hoja de ruta de inducción (Coord. Académica / Asistencia Académica / Coord. Administrativa) y Moodle New Edge.

Documentos habilitantes: hoja de vida, cédula, título o certificación docente, antecedentes penales, resultado del MOCK, rúbrica de la demo, pay scale firmado, RUC activo, certificaciones internacionales (opcional), contrato civil firmado. Sin aprobación final el profesor no cobra.

Finalización de contrato (checklist): desvincular de cursos, baja en plataformas (Moodle, Cambridge One, GradeKeeper, Teams), retiro de correo/Drive/WhatsApp, entrega de reportes finales, encuesta de salida, saldo por facturar y última payment sheet, devolución de locker y credencial, pago final.

**Decisión**: el cliente pidió que "el coordinador académico pueda crear un profesor sin autorización". El manual exige aprobaciones de DGA, Coord. Administrativa (pay scale) y Dirección Administrativa. Se concilian así: las aprobaciones viven en el **pipeline de contratación**; el **alta del profesor** es el último paso y Coordinación la hace sin pedir otra autorización. Solo una tarifa distinta al pay scale aprobado vuelve a aprobación.

### 2. Apertura y seguimiento de un curso → `DetalleCurso.html` (tarjeta "Seguimiento del curso")
- 72 h antes: crear el curso en Cambridge One y GradeKeeper.
- 48 h antes: correo informativo a estudiantes (YAMM) con horario, aula o enlace, libro y profesor.
- Grupo de WhatsApp solo informativo; ningún estudiante inicia sin contrato firmado; listado de aulas.
- Primera clase: recepción y bienvenida. Segunda clase: checklist de bienvenida (libros, códigos, Teams).
- 20 % del curso: observación de clase con rúbrica y retroalimentación al profesor.
- 50 %: follow up (asistencia, notas parciales, saldos; llamada a los que están en riesgo).
- 75 %: mensaje de próximo módulo (reapertura) y agendar Mock Test.
- Última semana: encuesta de satisfacción. Cierre.

### 3. Reapertura de cursos → `Cursos.html` (tarjeta "Reaperturas")
Filtrar cursos al 75 %; crear los cursos de continuidad como *upcoming*; reunión de revisión los jueves; cuadro de reaperturas (estudiantes, contactados, confirmados, perdidos y motivo); protocolo de contacto WhatsApp → llamada → nota de voz; 10 % de descuento al pagar 2 módulos; excepciones con autorización; reporte semanal a Dirección Académica; auditoría del 10 al 20 % de los contactos.

### 4. Cierre de cursos → `CalificarCurso.html` (tarjeta "Reglas del proceso de cierre")
72 h después de la última clase: speaking mock, notas en GradeKeeper en 48 h, End of level report. Reglas: ≥ 7.00 aprueba (Student Report PDF al expediente); 6.50–6.99 tutorías y recuperación; ≤ 6.49 pierde el módulo y repite con descuento; con deuda no se envía nota ni certificado; nota menor a 7 se comunica por llamada antes de publicar. Portafolio, encuestas e informe trimestral por sede.

### 5. Payment sheets de docentes → `PaymentSheet.html`
Sesiones generadas al crear el curso descontando feriados; one to one se liquida desde 10 h; actividades sin código de curso van a payment sheet manual; reemplazos con 48 h de aviso (las horas se pagan a quien cubre); atrasos desde el reloj de asistencia (tablet CAMB-CLOCK, "Minutes Late"); cancelaciones con "Cancelled" + "Remarks"; revisión mensual; correo al profesor con plantilla (nombres, horas, valor hora, descuentos, subtotal, factura requerida según régimen RIMPE o general, cuenta); 3 días para observar; consolidación; Teacher of the Month +5 %; facturas de los docentes.

### 6. Política de indexados → `DetalleCurso.html` (tarjeta "Indexados")
Regular con 48 h o más de anticipación; urgente con menos de 24 h solo con autorización de Coordinación. Correo con asunto `|REGULAR|` o `|URGENTE| INDEXO ESTUDIANTES …`; aviso en el grupo `|IMPORTANTE| INDEXADOS CAMBRIDGE SOL`; quien entra en la primera semana rinde nivelación.

### 7. Contrato de servicios educativos (estudiante) → `NotaCredito.html` (tarjeta "Reglas del contrato")
La inscripción no se devuelve; devolución antes de iniciar con retención del 10 % y pago en hasta 45 días; curso iniciado: cambio de horario o modalidad o nota de crédito (vigencia 12 meses); interrupción de 2 meses puede retomar con esas opciones; 6 meses o más: nuevo contrato y prueba de ubicación; reclamos por escrito a Coordinación Administrativa; cláusulas de protección de datos (LOPDP).

## Administrativo

### 8. Compra y traspaso de activos fijos → `Inventario.html` (tarjeta "Activos fijos por sede", **propuesta fuera del alcance**)
Solicitud de activo → aprobación de Gerencia → 2 o 3 cotizaciones con cuadro comparativo → orden de compra → acta de entrega y recepción (A.E.R.) → factura y registro contable → inventario (código tipo `XX.NN.ACCO.NNNNNN`, descripción, fecha, valor, ubicación, custodio, vida útil) → etiqueta y asignación. Traspaso interno entre sedes con acta C.T.I. (fecha de salida, fecha de ingreso, nueva ubicación, custodio). No está en los 11 módulos del contrato: se muestra como propuesta.

### 9. Reclutamiento de personal administrativo → `ReclutamientoAdministrativo.html` (**propuesta fuera del alcance**)
Proceso de contratación de nuevo personal (ISO 9001), 12 etapas: vacante aprobada por Gerencia General → perfil del cargo (manual de funciones) → publicación en LinkedIn, Indeed y web con presupuesto aprobado (Anexo 1) → filtración y pre-screen telefónico de 10 minutos (Anexo 2) → entrevistas → documentación habilitante (CV, cédula, papeleta, certificados, 2 cartas personales + 2 laborales, antecedentes, planilla) → verificación de referencias → evaluación psicológica y exámenes médicos con profesional externo (Anexo 5) → oferta laboral (cargo, horario, remuneración menos IESS, décimos, fondos de reserva, utilidades; Anexo 6) → inducción con acta de entrega → firma del contrato bajo relación de dependencia → comunicación institucional. Roles: Gerencia General (aprueba y firma), Administración / Talento Humano (ejecuta), Área solicitante (perfil, entrevistas, inducción). Correos tipo: aviso de no selección, propuesta laboral, solicitud de exámenes, inicio de labores. Los docentes no pasan por aquí sino por el proceso de servicios profesionales (punto 1).

## Qué queda fuera de este resumen a propósito
Nombres, cédulas, correos, cuentas bancarias y montos reales que aparecen en los documentos originales. Toda la data del mockup es ficticia.
