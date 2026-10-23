import re
import json, os
import sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W,H=1280,820

INK="#0F1E40"; MUTE="#5B6B8A"; LINE="#D6DCEA"; FILL="#E8EDF7"; FILL2="#F4F6FB"; ACC="#1D3F8F"

def box(label, h=120, extra="", dashed=True, w="100%"):
    b = f"2px {'dashed' if dashed else 'solid'} {LINE}"
    return f'<div style="width:{w};height:{h}px;box-sizing:border-box;border:{b};background:{FILL2};display:flex;align-items:center;justify-content:center;color:{MUTE};font-size:14px;text-align:center;padding:8px;{extra}">{label}</div>'

# Destino o comportamiento de cada botón sin href explícito.
# Valor str que termina en .html → navega. Tupla (descripción, siguiente) → diálogo de confirmación y, si hay siguiente, navega.
AUDIT="Queda registrado en el audit log con tu usuario, fecha y sede."
ACTIONS={
 "Enviar comprobantes seleccionados":("Se envían por correo el PDF y el XML autorizados de las facturas marcadas con la casilla. "+AUDIT,None),
 "Salir sin guardar":("Sales de la matrícula sin guardar los cambios de este borrador. Lo que ya estaba guardado se conserva.","Ficha360.html"),
 "Cambiar módulos":("Se abre la lista de módulos del programa para agregar o quitar módulos de esta venta.",None),
 "Corregir clasificación":("Se elige la clasificación correcta (nueva, reingreso o continuidad) con un motivo. El indicador de nuevas matrículas se recalcula y el cambio queda trazado con usuario y fecha. "+AUDIT,None),
 "Eliminar matrícula":("Solo antes de facturar: la matrícula se elimina con un motivo (queda en la papelera y el audit log) y el asesor puede crearla de nuevo con los datos corregidos. "+AUDIT,None),
 "Validar pago":("Contabilidad confirma que el depósito o la transferencia llegó al banco. El pago pasa a 'Validado' y Secretaría recibe el aviso para confirmarlo. "+AUDIT,None),
 "Observar pago":("Contabilidad indica qué no cuadra (monto, fecha, cuenta) y el asesor recibe el aviso para corregir o subir otro comprobante.",None),
 "Confirmar en sistema":("Secretaría confirma el pago ya validado por Contabilidad; la factura y el saldo de la venta se actualizan. "+AUDIT,None),
 "Aplicar saldo a favor":("Se aplica el saldo a favor de la venta a la nueva matrícula de continuidad. No es una nueva venta ni un nuevo cobro: queda como aplicación con fecha, monto y saldo restante. "+AUDIT,"DetalleVenta.html"),
 "Emitir factura del módulo":("Se emite la factura de este módulo con el valor y descuento de la venta original, pagada con el saldo a favor. Queda relacionada con la misma compra y el mismo pago. "+AUDIT,None),
 "Inscribir candidato":("Se crea la inscripción con el candidato, el examen y la fecha; queda vinculada a la factura y al pago. Si faltan menos de 20 días para el examen, el sistema no deja guardar.",None),
 "Imprimir y enviar":("Se envía al candidato (y al destinatario de la factura si es otra persona) la información de inscripción: examen, fecha, sede y requisitos.",None),
 "Cargar calendario anual":("Se sube el calendario de exámenes del año (Excel o PDF del centro autorizado); las fechas quedan disponibles para elegir al inscribir.",None),
 "Registrar venta y entregar":("Se emite la factura de mercadería, se registra el pago y se descuenta el artículo del stock de la sede. Al guardar se marca como entregado.",None),
 "Enviar a Dirección Comercial":("Tu informe del mes pasa a revisión de Dirección Comercial con el detalle de ventas y cobros que lo respalda.",None),
 "Aprobar y enviar a Administración":("Dirección Comercial aprueba el informe y lo envía a Administración para su revisión y asignación del pago. "+AUDIT,None),
 "Asignar pago de comisión":("Administración revisa el informe y asigna el pago de la comisión según las reglas vigentes. El asesor recibe el aviso. "+AUDIT,None),
 "Devolver con observaciones":("El informe vuelve al asesor con las observaciones para corregir.",None),
 "Editar metas":("Se editan las metas por indicador (matrículas, servicios educativos, niveles, ventas) y por período y sede. "+AUDIT,None),
 "Ver detalle":"TableroComercial.html",
 "Congelar matrícula":("Se pide el motivo (viaje, salud, trabajo) y la fecha de regreso (máximo 3 meses). Se libera el cupo del grupo, los módulos pagados y el saldo quedan guardados y se programa un recordatorio de reactivación. Si supera 1 mes lo aprueba Coordinación. "+AUDIT,None),
 "Reactivar matrícula":("Se elige un curso con cupo del mismo programa y módulo; la matrícula vuelve a 'En curso' con los módulos que tenía pagados.","NuevaVenta.html"),
 "Retirar estudiante":("Se pide el motivo de retiro (lista cerrada). Se calcula lo no consumido según la política: nota de crédito, devolución o saldo a favor. El estudiante sale del grupo y de Teams, las cuotas pendientes se cancelan y la comisión del asesor se ajusta. Lo aprueba Administración de sucursal. "+AUDIT,"NotaCredito.html"),
 "Transferir saldo":("Se elige el estudiante que recibe el saldo (por ejemplo un hermano) y el monto. Se emite la nota de crédito en esta matrícula y queda el saldo a favor en la otra. Lo aprueba Administración de sucursal. "+AUDIT,None),
 "Agregar a lista de espera":("El curso está lleno: el estudiante queda en la lista de espera del curso con su asesor. Cuando se libera un cupo se le avisa y tiene 48 h para confirmar.",None),
 "Ofrecer cupo":("Se avisa al primero de la lista por WhatsApp y correo. Si confirma en 48 h, el asesor abre Nueva matrícula con ese curso; si no, se ofrece al siguiente.","NuevaVenta.html"),
 "Agendar examen de ubicación":("Se agenda el examen de ubicación (en línea o en la sede). El resultado define el programa y el módulo de inicio y queda en la ficha del estudiante.",None),
 "Pagar en línea":("Se abre el pago con tarjeta. Al aprobarse se registra el pago, se emite la factura y la rematrícula queda confirmada sin esperar a Secretaría.",None),
 "Subir comprobante":("Subes la foto o PDF de la transferencia o depósito. Secretaría lo valida en Facturación → Rematrículas por confirmar y te avisa cuando quede confirmada.",None),
 "Justificar ausencia":("Eliges la sesión, el motivo y adjuntas un respaldo si lo tienes. Tu profesor y Coordinación lo ven; una ausencia justificada no cuenta para el mínimo de asistencia.",None),
 "Pedir reposición":("Se envía la solicitud a Coordinación con la sesión perdida; te proponen fecha y hora de reposición y te llega el enlace.",None),
 "Cambiar contraseña":("Se pide tu contraseña actual y la nueva (mínimo 8 caracteres). Se cierra la sesión en otros dispositivos.",None),
 "Nueva plantilla":("Se crea una plantilla con categoría, asunto, cuerpo y campos que se completan solos (nombre, curso, enlace de clase, saldo, fecha). Se usa en avisos automáticos y en el correo masivo.",None),
 "Verificar":("Se busca el código: si existe, se muestran el titular, el nivel, el programa y la fecha de emisión; si no, aparece 'Certificado no encontrado'.",None),
 "Imprimir recibo":("Se imprime el recibo de caja con número, estudiante, método y monto.",None),
 "Cerrar caja":("Se cierra la caja del día: se cuadran efectivo, tarjetas y transferencias contra los recibos y se genera el reporte de cierre en PDF. "+AUDIT,None),
 "Vincular a matrícula":("Se elige la matrícula a la que pertenece la factura; el saldo de la matrícula y la comisión del asesor se recalculan. "+AUDIT,None),
 "Correo masivo":("Se elige una plantilla de correo (o se escribe uno nuevo) y se envía a todos los registros filtrados en pantalla. Queda el envío con destinatarios en el historial. "+AUDIT,None),
 "Registrar walk-in":("Se registra la visita en la sede con cédula y nombre; queda como lead con origen Walk-in asignado al asesor de turno.",None),
 "Restaurar":("El registro vuelve a su lugar con todos sus datos y queda en el audit log quién lo restauró.",None),
 "Calificar profesor":("Coordinación califica al profesor en este curso (1 a 5) con un comentario; alimenta el desempeño de su ficha.",None),
 "Registrar resultado":("Se registra el puntaje y el nivel obtenido; el certificado pasa a 'Listo para retirar' y se avisa al candidato.",None),
 "Nuevo candidato":("Se inscribe un candidato: datos personales, examen, fecha y sede; se emite la factura del examen.",None),
 "Importar notas del Muro":("Se traen las notas de participación, quiz y examen registradas en el Muro (Moodle) para este módulo.",None),
 "Guardar borrador de notas":("Las notas se guardan sin cerrar el módulo; puedes seguir editándolas.",None),
 "Cerrar módulo y emitir certificados":("Se cierran las notas del módulo 7: los aprobados avanzan al módulo 8 de su compra y, al cerrar el nivel, reciben su certificado con código único de verificación. Los bloqueados por asistencia van a Coordinación. "+AUDIT,"DetalleCurso.html"),
 "Confirmar mi cupo":("Confirmas que sigues en el mismo grupo para el módulo 8. No hay pago: ya está incluido en tu compra. Te llega el enlace de clase el día anterior.",None),
 "Enviar solicitud":("La solicitud va a la bandeja de Dirección Comercial. La venta queda en espera; verás aprobado o rechazado en Notificaciones y en tus pendientes de Inicio, y al aprobarse retomas la venta. "+AUDIT,"Home.html"),
 "Nuevo estudiante":"NuevoEstudiante.html","Importar / Exportar":"ImportExport.html","Nuevo curso":"NuevoCurso.html","Editar curso":"NuevoCurso.html",
 "Registrar sesión":"RegistrarSesion.html","Registrar sesión manual":"RegistrarSesion.html","Reglas de comisión":"ReglasComision.html",
 "Nuevo usuario":"NuevoUsuario.html","Nueva sede":"NuevaSede.html","Nuevo nivel":"NuevoNivel.html","Nueva regla":"NuevaRegla.html",
 "Ver PDF":("Se abre el documento adjunto.",None),
 "Validar pedido":("Se marca el pedido como validado: pago aprobado en Nuvei, datos del cliente, producto, correo y teléfono. Sigue el registro de la factura y el contacto con el cliente (24 h). "+AUDIT,None),
 "Marcar contactado":("Se registra el contacto (canal, fecha y resultado) y, si aplica, la fecha agendada del servicio. "+AUDIT,None),
 "Enviar correo informativo":("Se envía al cliente el correo informativo según el producto (Mock Test, traducción, SIELE/TOEFL) y queda en su historial.",None),
 "Registrar incidencia":("Se registra la incidencia (pago no registrado, cliente no responde, error en producto o precio, duplicación), se notifica a Dirección Administrativa y corre el plazo de 48 h. "+AUDIT,None),
 "Resolver incidencia":("Se registra la resolución y se cierra la incidencia; si pasó de 48 h queda marcada como vencida en el reporte semanal. "+AUDIT,None),
 "Llamar para recuperar venta":("Se abre el marcador con el teléfono del cliente y se registra el resultado de la llamada (recuperada, perdida, volver a llamar).",None),
 "Enviar reporte a Dirección Administrativa":("Se envía el reporte semanal (pedidos, tiempos de respuesta, sin gestionar, cancelados, incidencias) a Dirección Administrativa.",None),
 "Seleccionar":("El profesor queda asignado al curso; se valida contrato activo y que no tenga otra clase en ese horario.",None),
 "Rematricularme":("Se crea tu matrícula del siguiente nivel en estado 'Pendiente de pago' con el mismo horario y modalidad; Secretaría te confirma cuando registre el pago. Recibirás el enlace de pago por correo.",None),
 "Confirmar pago":("Se confirma el pago recibido, la rematrícula pasa a 'Activa', se emite la factura y el estudiante entra al grupo (y al equipo de Teams si es virtual). "+AUDIT,None),
 "Enviar recordatorio":("Se envía al estudiante el recordatorio de rematrícula por correo y WhatsApp con los días que le quedan y el enlace de pago. "+AUDIT,None),
 "Ubicar en el mapa":("Se abre el mapa para fijar la ubicación; provincia, cantón y parroquia se asignan automáticamente desde el punto elegido.",None),
 "Usar mi ubicación actual":("El navegador pide permiso de ubicación y el pin se coloca en la posición actual del dispositivo (útil cuando el asesor visita al estudiante). Provincia, cantón, parroquia y calle se completan por geocodificación inversa.",None),
 "Enviar resumen ahora":("Se envía ahora mismo por correo el resumen de stock negativo y bajo mínimo por sede a los destinatarios configurados. "+AUDIT,None),
 "Editar destinatarios y hora":"Configuracion.html",
 "Guardar profesor":("El profesor queda activo de inmediato (Coordinación Académica no necesita autorización). Si la tarifa está fuera de la tabla vigente, solo la tarifa pasa a aprobación de Dirección. "+AUDIT,"FichaProfesor.html"),
 "Registrar pago":"RegistrarPago.html","Emitir nota de crédito":"NotaCredito.html","Nueva nota de crédito":"NotaCredito.html",
 "Registrar movimiento":"RegistrarMovimiento.html","Nuevo pedido a proveedor":"NuevoPedido.html","Atrás":"Ficha360.html","Emitir factura y matricular":"DetalleMatricula.html",
 "Aprobar":("Se aprueba la solicitud y se notifica al solicitante. "+AUDIT,None),
 "Rechazar":("Se pide un motivo de rechazo (obligatorio) y se notifica al solicitante. "+AUDIT,None),
 "Exportar":("Se genera el archivo (Excel o PDF) con los filtros aplicados. "+AUDIT,None),
 "Exportar log":("Se genera el archivo del audit log con los filtros aplicados. "+AUDIT,None),
 "Exportar detalle":("Se genera el detalle de comisiones del asesor en Excel. "+AUDIT,None),
 "Exportar Excel":("Se genera el reporte en Excel. "+AUDIT,None),
 "Exportar PDF":("Se genera el reporte en PDF. "+AUDIT,None),
 "Exportar CSV":("Se exportan los estudiantes filtrados en CSV. Si incluye datos de menores se marca como exportación sensible. "+AUDIT,None),
 "Descargar PDF":("Se descarga la factura en PDF.",None),
 "Descargar certificado":("Se descarga el certificado del nivel en PDF con código de verificación.",None),
 "Descargar factura":("Se descarga la factura electrónica (PDF + XML) autorizada por el SRI.",None),
 "Actualizar mis datos":("Se envía la solicitud de cambio a Secretaría de tu sede; verás el cambio aplicado cuando lo validen.",None),
 "Unirse a la clase":("Se abre el enlace de la sesión virtual (Zoom) del curso en una pestaña nueva.",None),
 "Escribir a mi asesor":("Se abre un mensaje por WhatsApp a tu asesor comercial.",None),
 "Descargar XML":("Se descarga el XML autorizado por el SRI de la factura.",None),
 "Descargar facturas pendientes":("Se descarga un ZIP con el PDF y el XML de todas las facturas con saldo del estudiante seleccionado, más un resumen con el total adeudado.",None),
 "Enviar facturas pendientes al estudiante":("Se envía al correo del estudiante (y del representante si es menor) un mensaje con sus facturas pendientes adjuntas (PDF + XML) y el total a pagar. "+AUDIT,None),
 "Enviar estado de cuenta":("Se envía al estudiante un estado de cuenta con sus facturas pendientes adjuntas (PDF + XML) y el total a pagar. "+AUDIT,None),
 "Descargar XML del día":("Se descargan en un ZIP los XML autorizados de las facturas del período filtrado.",None),
 "Enviar comprobante":("Se envía por correo al cliente el PDF y el XML autorizados por el SRI y la factura queda marcada como enviada. "+AUDIT,None),
 "Enviar comprobantes pendientes":("Se envían por correo los comprobantes (PDF + XML) de todas las facturas autorizadas que aún no se enviaron. "+AUDIT,None),
 "Reintentar autorización":("Se vuelve a enviar la factura al SRI para su autorización. Si vuelve a fallar se muestra el motivo. "+AUDIT,None),
 "Anular factura":("Se anula la factura (si está autorizada se emite la nota de crédito por el total) y el saldo de la matrícula se recalcula. "+AUDIT,"Facturas.html"),
 "Descargar plantilla":("Se descarga la plantilla CSV con las columnas esperadas y un ejemplo.",None),
 "Guardar cambios":("Se validan los campos obligatorios y se guarda. "+AUDIT,None),
 "Guardar regla":("La regla queda activa desde su vigencia y se aplica en el próximo cálculo. "+AUDIT,None),
 "Guardar como reporte":("El reporte se guarda con sus filtros y columnas para volver a ejecutarlo desde 'Reportes guardados'.",None),
 "Generar":("Se ejecuta el reporte con los filtros elegidos y el resultado se muestra abajo.",None),
 "Ver resultado":("Se arma el reporte con la pregunta, el período y la sede elegidos y se muestra abajo en palabras, gráfico y tabla.",None),
 "Enviar por correo":("Se envía el reporte (Excel + PDF) por correo a quien elijas; puedes dejarlo programado para que llegue cada semana o cada mes.",None),
 "Importar":("Se importan las filas válidas. Duplicados y errores se descartan y se muestran en un resumen. "+AUDIT,None),
 "Enviar":("El asistente responde solo con datos que tu rol y sede permiten ver.",None),
 "Confirmar sesión":("La sesión queda confirmada: suma horas a la payment sheet del profesor y avance a los estudiantes.",None),
 "Marcar no dictada":("Se pide un motivo. La sesión no suma horas ni avance y se notifica a Coordinación.",None),
 "Aprobar período":("El período pasa a Aprobado, deja de recalcularse y se notifica a los asesores. "+AUDIT,None),
 "Aprobar pagos":("La payment sheet pasa a Aprobada. Las diferencias y contratos vencidos deben estar resueltos antes. "+AUDIT,None),
 "Registrar ingreso":("Se suma la cantidad recibida al stock de la sede y el pedido pasa a Recibido.",None),
 "Subir archivo":("Se adjunta el archivo a la ficha y queda registrado quién lo subió y cuándo.",None),
 "Editar precios":("Se habilita la edición en la tabla. El cambio requiere Guardar y queda en el audit log.",None),
 "Cambio de curso":("Se elige el nuevo curso. Se genera el ajuste o nota de crédito, se actualiza la matrícula y el stock de libros.",None),
 "Configurar":("Credenciales, mapeo de campos y frecuencia de sincronización del sistema.",None),
 "Editar":("Se habilita la edición de los datos de esta ficha. Los cambios requieren Guardar.",None),
 "Enviar enlace de clase":("Se envía por email y WhatsApp el enlace de la clase virtual (Zoom/Teams) a los estudiantes matriculados con saldo al día.",None),
 "Hoja de asistencia":("Se genera la hoja de asistencia del curso en PDF para la sesión de hoy.",None),
 "Calificar curso":"CalificarCurso.html",
 "Anular matrícula":("Requiere aprobación. Se revierte la matrícula, se genera nota de crédito por el saldo pagado y el libro vuelve al stock.",None),
 "Emitir certificado":("Se genera el certificado del nivel aprobado en PDF y queda en Archivos del estudiante.",None),
 "Ver matrícula":"DetalleMatricula.html","Ver curso":"DetalleCurso.html","Nueva matrícula":"NuevaVenta.html",
 "Registrar ingreso de proveedor":"NuevoPedido.html",
 "Asignar código":("Se asigna el código de activación del material digital al estudiante y se marca como entregado.",None),
 "Marcar como atendido":("El insight pasa a 'atendido' con tu usuario y fecha; deja de aparecer en Inicio y en el asistente.",None),
 "Descartar":("El insight se descarta con un motivo; el asistente aprende a no repetirlo para este caso.",None),
 # contratación de profesores
 "Nuevo candidato":("Se registra el candidato con su CV, la vacante y la sede; entra en la etapa 'Revisión de CV' y Coordinación Académica recibe el aviso.",None),
 "Publicar vacante":("Se genera el texto del anuncio (perfil, horario, sede, tipo de contrato) para publicar en LinkedIn y la web; la carpeta de CV de la sede queda enlazada al proceso.",None),
 "Registrar resultado de clase demostrativa":("Se llena la rúbrica D-SGC-002 (6 aspectos de 1 a 5) con observaciones. Si el promedio es 3.5 o más, el candidato pasa al MOCK; si no, queda descartado con la retroalimentación escrita.",None),
 "Agendar MOCK":("Se agenda el MOCK C1 (fecha, sede y evaluador). El resultado mínimo para dictar es B2.",None),
 "Descartar candidato":("El candidato sale del proceso con un motivo (perfil, referencias, demo, MOCK, no acepta la oferta). Se envía el correo de aviso y el expediente se conserva 12 meses. "+AUDIT,"ContratacionProfesores.html"),
 "Reprogramar demo":("Se elige nueva fecha y hora para la clase demostrativa y se avisa al candidato.",None),
 "Descargar expediente":("Se descarga un PDF con el informe de entrevista, referencias, rúbrica de la demo, resultado del MOCK, pay scale y documentos habilitantes.",None),
 "Aprobar pay scale":("Coordinación Administrativa aprueba la tarifa por hora según la tabla de la sede, el título y el MOCK. Con el pay scale firmado el candidato pasa a Dirección Administrativa para la aprobación de la contratación. "+AUDIT,None),
 # seguimiento, cierre e indexados
 "Marcar tarea cumplida":("La tarea de seguimiento del curso queda marcada con tu usuario y fecha; si tenía plazo (72 h, 48 h, 20%, 50%, 75%) deja de aparecer como pendiente.",None),
 "Solicitar indexado":("Se pide agregar un estudiante a este curso. Regular: con 48 h o más de anticipación; urgente: menos de 24 h, solo con autorización de Coordinación. El sistema envía el correo con asunto |REGULAR| o |URGENTE| INDEXO ESTUDIANTES y avisa al grupo de coordinación.",None),
 "Registrar contacto de reapertura":("Se registra el intento (WhatsApp, llamada o nota de voz), la respuesta del estudiante y el motivo si no continúa. Si confirma, queda 'Pendiente de pago' para que Secretaría lo matricule.",None),
 "Enviar reporte semanal de reaperturas":("Se genera el cuadro de reaperturas de la semana (cursos al 75%, estudiantes contactados, confirmados, perdidos y motivos) y se envía a Dirección Académica antes de la reunión del jueves.",None),
 # payment sheet
 "Registrar novedad":("Se registra un atraso (minutos), una cancelación con observación o un reemplazo (profesor que cubre, con 48 h de aviso). La novedad afecta el cálculo de la payment sheet del mes.",None),
 "Enviar correo de payment sheet":("Cada profesor recibe su resumen del mes: horas, valor hora, descuentos, subtotal, factura requerida y cuenta de pago. Tiene 3 días para observar antes de la consolidación. "+AUDIT,None),
 "Marcar Teacher of the Month":("Se marca al profesor del mes de la sede: recibe 5% adicional sobre su payment sheet y queda en su historial de desempeño. "+AUDIT,None),
 # activos fijos (propuesta)
 "Nueva solicitud de activo":("Se llena el formulario de solicitud (qué, para qué, sede, responsable, costo estimado). Pasa a aprobación de Gerencia; luego 2 o 3 cotizaciones, orden de compra, acta de entrega y registro en el inventario.",None),
 # reclutamiento administrativo (propuesta)
 "Nuevo postulante":("Se registra el postulante con su hoja de vida y la vacante; entra en 'Filtración y preselección' y Administración programa el pre-screen telefónico.",None),
 "Publicar vacante administrativa":("Se genera el texto del Anexo 1 (puesto, sede, funciones, requisitos, perfil, qué ofrecemos y aviso de protección de datos) y se registra el presupuesto de publicación para aprobación de Gerencia.",None),
 "Enviar aviso de no selección":("Se envía el correo de agradecimiento y aviso de no selección; el postulante queda como 'Descartado' y su expediente se conserva para futuras vacantes.",None),
 "Enviar oferta laboral":("Se envía la propuesta laboral (cargo, horario, remuneración menos aporte IESS, beneficios de ley, fecha de ingreso y documentación requerida). El postulante tiene un plazo para aceptar. "+AUDIT,None),
 "Solicitar exámenes":("Se envía al profesional externo la solicitud de evaluación psicológica y exámenes médicos preocupacionales con la hoja de vida y las funciones del cargo, bajo confidencialidad.",None),
 "Enviar correo de inicio de labores":("Tras la firma del contrato se envía el correo con misión y visión, reglamentos, funciones departamentales, organigrama, consentimiento de datos y manual de funciones.",None),
 "Comunicar ingreso al personal":("Se envía al personal el correo institucional con el nombre, cargo, funciones y datos de contacto del nuevo colaborador.",None),
 "Abrir en WooCommerce":"https://cambridgesol.edu.ec/tienda-virtual-cambridge-sol/",
 "Registrar traspaso":("Se registra el traspaso interno del activo entre sedes o responsables (acta C.T.I.): fecha de salida, fecha de ingreso, nueva ubicación y custodio. "+AUDIT,None),
}

def btn(label, href=None, primary=False, action=None, next=None):
    st=f"display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:0 18px;border:2px solid {INK};font-size:14px;font-weight:600;text-decoration:none;box-sizing:border-box;cursor:pointer;font-family:inherit;"
    st+= f"background:{INK};color:#fff;" if primary else f"background:#fff;color:{INK};"
    if href is None and action is None:
        a=ACTIONS.get(label)
        if isinstance(a,str): href=a
        elif a: action,next=a
    if href: return f'<a href="{href}" style="{st}">{label}</a>'
    if action is None: raise ValueError(f"Botón sin destino ni acción: {label}")
    nx=f' data-next="{next}"' if next else ""
    return f'<button type="button" data-action="{action}"{nx} style="{st}">{label}</button>'

# Pantallas ocultas: se generan (los enlaces siguen funcionando) pero no aparecen en el menú ni en el hub.
# Para volver a mostrar Facturación, vaciar este set.
HIDDEN=set()  # vacío: Facturación visible. Para ocultar un módulo: {"Facturas.html","DetalleFactura.html","RegistrarPago.html","NotaCredito.html"}

# Tipos de usuario (RBAC). Código → (nombre del rol, usuario de ejemplo)
ROLES=[("ADM","Administrador General","Estefanía"),("GER","Gerente General","Gerencia"),("DIR","Director Comercial","Dir. Comercial"),("SUC","Administrador de Sucursal","Admin. Valle"),("COO","Coordinador Académico","Coord. Académica"),("ASE","Asesor Comercial","Carla M."),("SEC","Secretaría","Secretaría"),("PRO","Profesor (consulta)","P. Gómez"),("CON","Contabilidad","Contabilidad")]
ALL="ADM,GER,DIR,SUC,COO,ASE,SEC,PRO,CON"
COMERCIAL="ADM,GER,DIR,SUC,ASE,SEC"
ACADEMICO="ADM,GER,SUC,COO,PRO"
APROBADORES="ADM,GER,DIR,SUC,COO"
def only(roles, html, inline=False):
    """Envuelve html para que solo lo vean esos roles (códigos separados por coma)."""
    return f'<{"span" if inline else "div"} data-roles="{roles}" style="display:contents">{html}</{"span" if inline else "div"}>'

# Menú lateral agrupado por áreas. Cada ítem: (nombre, archivo, roles que lo ven). Un área desaparece si el rol no ve ninguno de sus ítems.
NAV=[
 ("",[("Inicio","Home.html",ALL)]),
 ("Académico",[("Programas","Programas.html",ALL),("Cursos","Cursos.html",ALL),("Estudiantes","Estudiantes.html",ALL),("Sesiones","Sesiones.html",ACADEMICO+",SEC"),("Profesores","Profesores.html","ADM,GER,DIR,SUC,COO"),("Contratación","ContratacionProfesores.html","ADM,GER,DIR,SUC,COO"),("Exámenes","ExamenesInternacionales.html","ADM,GER,SUC,COO,SEC")]),
 ("Comercial",[("Leads","Leads.html",COMERCIAL),("Nueva matrícula","NuevaVenta.html",COMERCIAL),("Empresas","Empresas.html","ADM,GER,DIR,SUC,ASE"),("Tienda en línea","Pedidos.html",COMERCIAL+",SEC"),("Tablero comercial","TableroComercial.html","ADM,GER,DIR,SUC,ASE,CON"),("Facturación","Facturas.html",COMERCIAL+",CON"),("Comisiones","Comisiones.html","ADM,GER,DIR,SUC,ASE"),("Aprobaciones","Aprobaciones.html",APROBADORES)]),
 ("Inventario",[("Stock por sede","Inventario.html","ADM,GER,SUC,COO,SEC"),("Movimientos y pedidos","Movimientos.html","ADM,GER,SUC,SEC")]),
 ("Dirección",[("Insights de IA","Insights.html","ADM,GER,DIR,SUC,COO"),("Reportes","Reportes.html","ADM,GER,DIR,SUC,COO,CON"),("Dashboard ejecutivo","DashboardEjecutivo.html","ADM,GER,DIR")]),
 ("Administración",[("Usuarios y roles","Usuarios.html","ADM,GER"),("Configuración","Configuracion.html","ADM,GER"),("Audit log","AuditLog.html","ADM,GER,SUC"),("Integraciones","Integraciones.html","ADM"),("Reclutamiento","ReclutamientoAdministrativo.html","ADM,GER,SUC")]),
]
# alias: nombre antiguo de sección activa → ítem del menú
NAV_ALIAS={"Inventario":"Stock por sede","Facturación":"Facturación"}
def nav(active):
    active=NAV_ALIAS.get(active,active)
    out=""
    for area,items in NAV:
        items=[(n,h,r) for n,h,r in items if h not in HIDDEN]
        if not items: continue
        roles=",".join(sorted({c for _,_,r in items for c in r.split(",")}))
        links=""
        for n,h,r in items:
            st=f"display:block;padding:10px 16px;font-size:14px;text-decoration:none;color:{INK};"
            if n==active: st+=f"background:{FILL};font-weight:700;"
            links+=f'<a href="{h}" data-roles="{r}" style="{st}">{n}</a>'
        head=f'<div style="padding:14px 16px 4px;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:{MUTE}">{area}</div>' if area else ""
        out+=f'<div data-roles="{roles}" style="display:contents">{head}{links}</div>'
    return out

def shell(title, active, *parts, subtitle=""):
    body="".join(parts)
    return f'''<div style="min-height:{H}px;display:flex;flex-direction:column;font-family:'IBM Plex Sans',sans-serif;color:{INK};background:#fff">
<header style="display:flex;flex-wrap:wrap;align-items:center;gap:16px;padding:12px 24px;border-bottom:2px solid {INK}">
  <div style="font-weight:700;font-size:16px">Plataforma Cambridge</div>
  <div style="display:flex;align-items:center;gap:8px;margin-left:auto;font-size:13px">
    <label for="sede" style="color:{MUTE}">Sede</label>
    <select id="sede" style="height:30px;padding:0 6px;border:1px solid {LINE};border-radius:4px;background:#fff;font:inherit;font-size:13px;color:{INK};outline-offset:1px"><option>Todas</option><option>Quito</option><option>Valle</option><option>Ambato</option><option>Cuenca</option></select>
    <label for="rol" style="color:{MUTE};margin-left:8px">Ver como</label>
    <select id="rol" style="height:30px;padding:0 6px;border:1px solid {LINE};border-radius:4px;background:#fff;font:inherit;font-size:13px;color:{INK};outline-offset:1px">{"".join(f'<option value="{c}" data-user="{u}">{n}</option>' for c,n,u in ROLES)}</select>
  </div>
  <a href="Notificaciones.html" style="font-size:13px">Notificaciones (3)</a><a href="Chatbot.html" style="font-size:13px">Asistente</a><div id="rol-user" style="font-size:13px;color:{MUTE}">Estefanía · Administrador General</div>
</header>
<div style="display:flex;flex-wrap:wrap;flex:1">
  <nav style="width:200px;border-right:2px solid {INK};padding:8px 0">{nav(active)}</nav>
  <main style="flex:999 1 560px;min-width:0;padding:24px;display:flex;flex-direction:column;gap:20px">
    <div><h1 style="margin:0;font-size:24px">{title}</h1>{f'<p style="margin:4px 0 0;color:{MUTE};font-size:14px">{subtitle}</p>' if subtitle else ''}</div>
    {body}
  </main>
</div>
</div>'''

# Preguntas sugeridas y respuestas de ejemplo del asistente flotante, por pantalla (M9: solo lectura, respeta rol y sede)
AI_CTX={
 "Home.html":[("¿Qué debo atender hoy?","Hoy: 3 aprobaciones pendientes (la más antigua de ayer), 3 sesiones sin confirmar y 2 cursos terminados sin calificar. Lo más urgente es el descuento del 42% de Gabriela Núñez: la matrícula espera desde ayer."),("¿Cómo va la meta del mes?","Octubre lleva 76 niveles vendidos sobre una meta de 70 (109%). Quito aporta 40, Valle 22 y Ambato 14. Ambato lleva 2 semanas sin matrículas nuevas.")],
 "Cursos.html":[("¿Qué cursos están por abrir sin profesor?","Dos: Teens A2 (Ambato, Vi 15:00) y Tailored · Inglés corporativo (Ambato, Ma-Ju 07:00). Ambos inician en menos de 3 semanas. P. Gómez y M. Castro tienen horas libres compatibles."),("¿Cuáles tienen estudiantes con saldo?","9 cursos suman $2,840 pendientes. El mayor saldo está en B1 Virtual (0001-2026-0767): 2 estudiantes deben $445. Cuatro de esos cursos terminan en noviembre."),("¿Qué cursos terminaron sin calificar?","Adults A1 Sábados (0001-2026-0430) terminó hace 5 días con 14 estudiantes sin nota, y Teens A2 2025 (Valle). Hasta que se califiquen no se emiten certificados ni pueden matricularse en el siguiente nivel.")],
 "Estudiantes.html":[("¿Cuántos estudiantes activos hay por sede?","812 activos: Quito 420, Valle 230 y Ambato 162. Este mes entraron 52 nuevos y 14 están en transición entre niveles."),("¿Quiénes tienen asistencia menor a 75%?","14 estudiantes están en riesgo. Los 4 más críticos están en B1 Virtual (Quito) con menos de 60%. Puedo listarlos con su teléfono de contacto si quieres llamarlos."),("¿Hay duplicados entre sedes?","La migración detectó 23 posibles duplicados por cédula entre Quito y Valle. 18 ya están unificados; 5 esperan confirmación de Secretaría.")],
 "Profesores.html":[("¿Quién puede cubrir Teens B1 Virtual?","P. Gómez: dicta B1 Virtual en Quito con 88% de asistencia, tiene libres Lu-Ma-Mi-Ju 17:00–19:00 y le quedan 6 h antes del máximo de su contrato. S. Jiménez ya está al tope (20 h)."),("¿Qué profesores no tienen contrato vigente?","R. Salas (Ambato) tiene el contrato vencido y 8 h registradas este mes; D. Paredes (Valle) está pendiente de aprobación. Ninguno puede entrar en la payment sheet hasta resolverlo.")],
 "FichaProfesor.html":[("¿Cuántas horas lleva este mes?","P. Gómez lleva 48 h en octubre (24 sesiones). Su payment sheet suma $336 y coincide con su factura. Tiene 2 sesiones manuales fuera de horario pendientes de confirmar.")],
 "Ficha360.html":[("¿Qué nivel le toca y cuándo abre?","María está en el módulo 7 (B1). Al aprobarlo pasa al módulo 8 del mismo grupo (ya pagado, desde el 3 nov); después siguen los módulos 9 y 10 (B1+), presenciales los sábados desde enero de 2027. Compró los módulos 7 a 10 y aún no consume ninguno."),("¿Tiene saldo pendiente?","No. Su matrícula 001-202602794 está pagada ($980). Su descuento del 10% fue por referido y lo aplicó Carla M. dentro de su límite.")],
 "Inventario.html":[("¿Qué libros hay que pedir?","Tres productos con stock negativo: Empower B1+ (Valle −2), Super Minds 3 WB (Ambato −1) y Super Minds 3 SB (Ambato −2). El pedido sugerido a Books & Bits suma 16 libros."),("¿Cuántos códigos de activación quedan?","13 códigos comprados sin asignar: 9 en Valle y 4 en Quito. Uno de Empower A1 venció.")],
 "ContratacionProfesores.html":[("¿Qué candidatos están trabados?","Dos llevan más de 3 días en la misma etapa: Jorge Andrade espera el pay scale de Coord. Administrativa (3 días) y Paula Cevallos tiene 1 de 3 referencias (5 días). Esteban Ruiz no cumple el mínimo del MOCK (B1) y debería descartarse con retroalimentación."),("¿Quién está listo para crear el perfil?","María José Vinueza (Quito, Adults B2 Intensivo): contratación aprobada hoy y documentos completos. Al crear el perfil empieza su hoja de ruta de inducción con primer día el 3 nov.")],
 "DetalleCandidato.html":[("¿Qué le falta a Daniela para la aprobación?","El resultado del MOCK (mínimo B2), antecedentes penales y RUC. La demo es el 24 oct; con MOCK aprobado el pay scale sugerido es $6.50/h para Valle.")],
 "ReclutamientoAdministrativo.html":[("¿Qué postulante necesita respuesta hoy?","Mónica Terán (asesora comercial, Ambato) tiene la oferta laboral enviada y responde hasta el 28 oct; Valentina Rojas tiene entrevista con Gerencia el 27 oct y le faltan antecedentes penales y una carta de recomendación."),("¿Qué vacantes siguen sin cubrir?","Cuatro: Secretaría administrativa-académica (Quito), Asistente contable (Valle), Asesora comercial (Ambato) y Recepción (Quito). Coordinación académica ya se cubrió e inicia el 3 nov.")],
 "DetallePedido.html":[("¿Qué sigue con este pedido?","Validar: el pago está aprobado en Nuvei y los datos del cliente están completos. Después, contactar a Lorena Paz antes de mañana 09:12 para agendar el Mock Test con 15 días de anticipación.")],
 "PaymentSheet.html":[("¿Por qué no puedo aprobar la payment sheet?","Hay 3 alertas: L. Vega facturó $26 más que las horas registradas, R. Salas tiene contrato vencido con 8 h, y D. Paredes entregó factura sin sesiones. Resueltas esas tres, el total a pagar es $875.60 (P. Gómez $336, L. Vega $234, R. Salas $45.60 y M. Castro $260).")],
 "Comisiones.html":[("¿Qué descuentos dio cada asesor este mes?","Carla M. dio descuento en 12 ventas (promedio 9%), Sofía L. en 9 (8%) y Diego R. en 8 (6%). Total descontado: $1,860, el 5.6% de lo facturado. 3 ventas pasaron el límite del 10%: 1 aprobada, 1 pendiente (42% de Gabriela Núñez) y 1 rechazada."),("¿Cuánto gana cada asesor este mes?","Carla M. $420 (14 niveles, bono incluido), Sofía L. $330 (11) y Diego R. $180 (9, no llegó a la meta de 12). Solo se paga la comisión de ventas cobradas.")],
 "Aprobaciones.html":[("¿Qué pasa si apruebo el descuento del 42%?","La matrícula de Gabriela Núñez (A2) se cerraría en $261 en lugar de $450 y la comisión de Carla M. bajaría a $10. La regla permite hasta 10% sin aprobación; 42% queda en el audit log con tu justificación.")],
 "Configuracion.html":[("¿Qué aulas están libres el sábado en la mañana?","En Valle: C-2 (9 estudiantes) y C-7 (5). En Quito, Q-1 está ocupada al 60%. La capacidad se calcula con la norma SETEC.")],
 "Insights.html":[("¿Qué insight es el más urgente?","El descuento del 42% pendiente desde ayer bloquea una matrícula de $450. Después, los 14 estudiantes de A1 Sábados sin calificar: no pueden pasar a A2 y hay 3 cupos esperándolos.")],
}
NO_FAB={"Main.html","RecuperarContrasena.html","PortalEstudiante.html","VerificarCertificado.html"}
def analizar_pantalla(title, inner):
    """Análisis automático de la pantalla a partir de lo que se ve: KPIs, alertas (badges rojos/amarillos), tablas y acciones."""
    import re as _r, html as _h
    txt=lambda x: _h.unescape(_r.sub(r"<[^>]+>"," ",x)).strip()
    kp=[(txt(l),txt(v)) for l,v in _r.findall(r'<span class="kpi-label">(.*?)</span><span class="kpi-value">(.*?)</span>', inner, _r.S)][:4]
    bad=[txt(b) for b in _r.findall(r'<span class="badge badge-bad">(.*?)</span>', inner)]
    warn=[txt(b) for b in _r.findall(r'<span class="badge badge-warn">(.*?)</span>', inner)]
    ntab=len(_r.findall(r'class="wf-table tbl"', inner)); nrows=len(_r.findall(r'class="wf-row"', inner))
    acts=[txt(b) for b in _r.findall(r'class="btn btn-primary[^"]*"[^>]*>(.*?)</button>', inner, _r.S)][:3]
    out=[f"<b>Análisis de {title}</b>."]
    if kp: out.append("Indicadores: "+"; ".join(f"{l} <b>{v}</b>" for l,v in kp)+".")
    if nrows: out.append(f"Hay {ntab} listado{'s' if ntab!=1 else ''} con {nrows} registros en pantalla (según sede y filtros).")
    from collections import Counter
    if bad: c=Counter(bad); out.append("<b>Alertas críticas:</b> "+", ".join(f"{k} ×{n}" if n>1 else k for k,n in c.most_common(4))+".")
    if warn: c=Counter(warn); out.append("Por revisar: "+", ".join(f"{k} ×{n}" if n>1 else k for k,n in c.most_common(4))+".")
    if acts: out.append("Acción principal disponible: "+" · ".join(acts)+".")
    if not (kp or bad or warn or nrows): out.append("Es una pantalla de captura o detalle; puedo explicarte cada campo y qué pasa al guardar.")
    out.append("Recomendación: atiende primero lo marcado en rojo, luego lo amarillo; el resto está al día.")
    return " ".join(out)
AI_DEFAULT=[("¿Qué puedo hacer en esta pantalla?","Te explico lo que ves aquí y qué acciones tienes según tu rol. También puedo buscar un estudiante, curso o profesor por nombre o código."),("¿Hay algo pendiente que deba revisar?","Reviso aprobaciones, sesiones sin confirmar, saldos y alertas de inventario relacionados con esta pantalla y te digo qué es urgente.")]

def page(fname, title, inner, lang_title):
    fab='' if fname in NO_FAB else f'''<button type="button" class="ai-fab" id="ai-fab" aria-label="Abrir asistente">{ico("spark","nav-ico")}<span class="ai-fab-dot"></span></button>
<aside class="ai-panel" id="ai-panel" hidden aria-label="Asistente">
  <div class="ai-panel-head"><span class="ai-spark">{ico("spark","nav-ico")}</span><div><b>Asistente Cambridge</b><small>Estás en: <span id="ai-ctx">{lang_title}</span></small></div><button type="button" class="icon-btn" id="ai-close" aria-label="Cerrar">×</button></div>
  <div class="ai-log" id="ai-log"><div class="msg bot">Hola. Veo que estás en <b>{lang_title}</b>. Puedo responder sobre lo que tienes en pantalla o sobre cualquier dato de la plataforma, siempre según tu rol y sede.</div></div>
  <div class="ai-chips" id="ai-chips"><button type="button" class="chipq chipq-main" data-a="{analizar_pantalla(lang_title, inner).replace(chr(34),"&quot;")}">{ico("spark","nav-ico")} Analizar esta pantalla</button>{"".join(f'<button type="button" class="chipq" data-a="{a.replace(chr(34),"&quot;")}">{q}</button>' for q,a in AI_CTX.get(fname,[])+AI_DEFAULT)}</div>
  <form class="ai-in" id="ai-form"><label for="ai-input" class="sr">Pregunta</label><input id="ai-input" class="ctl" placeholder="Pregunta sobre {lang_title.lower()}…" autocomplete="off"><button type="submit" class="btn btn-primary">Enviar</button></form>
</aside>'''
    html=f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{lang_title} · Wireframes Plataforma Cambridge</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap">
<link rel="stylesheet" href="style.css">
</head>
<body>
{inner}
{fab}
<dialog id="wf-dialog">
  <h2 id="wf-dialog-title" style="margin:0 0 8px"></h2>
  <p id="wf-dialog-text" style="margin:0 0 20px;line-height:1.5"></p>
  <div style="display:flex;gap:8px;justify-content:flex-end;flex-wrap:wrap"><button type="button" id="wf-cancel" class="btn">Cancelar</button><button type="button" id="wf-ok" class="btn btn-primary">Confirmar</button></div>
</dialog>
<div id="wf-toast" role="status" aria-live="polite"></div>
<script src="assets/xlsx.js"></script>
<script>
(function(){{
  var dlg=document.getElementById('wf-dialog'),title=document.getElementById('wf-dialog-title'),text=document.getElementById('wf-dialog-text'),toast=document.getElementById('wf-toast'),cur=null;
  document.querySelectorAll('[data-action]').forEach(function(b){{
    b.addEventListener('click',function(){{cur=b;title.textContent=b.textContent.trim();text.textContent=b.dataset.action;dlg.showModal();}});
  }});
  document.getElementById('wf-cancel').addEventListener('click',function(){{dlg.close();}});
  function saveForm(list){{var rec={{}};document.querySelectorAll('.field').forEach(function(f){{var l=f.querySelector('label'),c=f.querySelector('input,select,textarea');if(!l||!c)return;var k=l.textContent.replace(/\*$/,'').trim();if(k in rec)return;var v=c.type==='file'?(c.files&&c.files[0]?c.files[0].name:''):(c.value||'');rec[k]=v.trim();}});rec._ts=Date.now();
    try{{var arr=JSON.parse(localStorage.getItem('wf-data-'+list)||'[]');arr.unshift(rec);localStorage.setItem('wf-data-'+list,JSON.stringify(arr));}}catch(e){{}}}}
  document.querySelectorAll('a[data-save]').forEach(function(a){{a.addEventListener('click',function(){{saveForm(a.dataset.save);}});}});
  document.getElementById('wf-ok').addEventListener('click',function(){{
    if(cur.dataset.save)saveForm(cur.dataset.save);
    dlg.close();toast.textContent='Hecho: '+cur.textContent.trim();toast.style.display='block';
    setTimeout(function(){{toast.style.display='none';if(cur.dataset.next)location.href=cur.dataset.next;}},1100);
  }});
}})();
(function(){{
  document.querySelectorAll('.picker-areas, .picker:not(.picker-areas .picker)').forEach(function(g){{g.querySelectorAll('.pick').forEach(function(b){{b.addEventListener('click',function(){{g.querySelectorAll('.pick').forEach(function(x){{x.classList.remove('on');x.setAttribute('aria-checked','false');}});b.classList.add('on');b.setAttribute('aria-checked','true');}});}});}});
  document.querySelectorAll('.pills').forEach(function(g){{var multi=g.hasAttribute('data-multi');g.querySelectorAll('.pill').forEach(function(b){{b.addEventListener('click',function(){{if(!multi)g.querySelectorAll('.pill').forEach(function(x){{x.classList.remove('on');x.setAttribute('aria-pressed','false');}});var on=multi?!b.classList.contains('on'):true;b.classList.toggle('on',on);b.setAttribute('aria-pressed',on);}});}});}});
}})();
(function(){{
  /* registros creados en esta demo (localStorage) → primeras filas de la lista */
  document.querySelectorAll('[data-list]').forEach(function(w){{var arr=[];try{{arr=JSON.parse(localStorage.getItem('wf-data-'+w.getAttribute('data-list'))||'[]');}}catch(e){{}}if(!arr.length)return;
    var tpl=JSON.parse(w.getAttribute('data-list-tpl')),tbl=w.querySelector('.wf-table'),first=tbl.querySelector('.wf-row');if(!first)return;
    function esc(x){{return String(x).replace(/[&<>"]/g,function(c){{return {{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c];}});}}
    function cell(t,rec){{t=t.replace(/[{{]([^}}]+)[}}]/g,function(_,k){{return esc(rec[k]||'—');}});
      if(t.indexOf('badge:')===0){{var p=t.split(':');return '<span class="badge badge-'+p[1]+'"><i></i>'+p.slice(2).join(':')+'</span>';}}
      if(t.indexOf('link:')===0){{var q=t.split(':');return '<a href="'+q[1]+'">'+q.slice(2).join(':')+'</a>';}}
      if(t.indexOf('mono:')===0)return '<span class="mono">'+t.slice(5)+'</span>';
      if(t.indexOf('|')>0){{var h=t.split('|');return '<span class="c2"><span>'+h[0]+'</span><small>'+h.slice(1).join('|')+'</small></span>';}}return t;}}
    arr.slice().reverse().forEach(function(rec){{var r=first.cloneNode(true);var tds=r.querySelectorAll('.td');tds.forEach(function(td,i){{td.innerHTML=cell(tpl[i]||'—',rec);}});
      var sede=(r.textContent.match(/Quito|Valle|Ambato|Cuenca/)||[])[0];if(sede)r.setAttribute('data-sede',sede);else r.removeAttribute('data-sede');r.removeAttribute('data-href');r.classList.add('is-new');tbl.insertBefore(r,first);}});}});
  document.querySelectorAll('.wf-row').forEach(function(r){{
    var a=r.querySelector('a[data-row]'); if(!a){{var last=r.lastElementChild; a=last&&last.querySelector('a[href]'); if(!a||last.querySelectorAll('a,button').length!==1) return;}}
    r.setAttribute('data-href',a.getAttribute('href'));
    [].forEach.call(r.children,function(c){{c.addEventListener('click',function(ev){{ if(ev.target.closest('a,button,select,input,label')) return; location.href=a.getAttribute('href'); }});}});
  }});
}})();
(function(){{
  var sel=document.getElementById('sede');
  function refresh(){{
    var v=sel?sel.value:'Todas';
    document.querySelectorAll('[data-sv]').forEach(function(e){{var d=JSON.parse(e.getAttribute('data-sv'));if(d[v]!=null)e.textContent=d[v];}});
    document.querySelectorAll('.wf-table').forEach(function(t){{
      var cols=JSON.parse(t.getAttribute('data-cols'));
      var host=t.closest('.tbl-wrap')||t; var f=host.previousElementSibling; while(f&&!f.classList.contains('wf-filters')&&!f.classList.contains('wf-table')&&!f.classList.contains('tbl-wrap')) f=f.previousElementSibling;
      var ctrls=(f&&f.classList.contains('wf-filters'))?[].slice.call(f.querySelectorAll('[data-fcol]')):[];
      var shown=0;
      t.querySelectorAll('.wf-row').forEach(function(r){{
        var rs=r.getAttribute('data-sede'); var ok=(!rs||v==='Todas'||rs==='Todas'||rs===v);
        var cells=[].map.call(r.children,function(c){{return c.textContent.trim().toLowerCase();}});
        ctrls.forEach(function(c){{ if(!ok) return; var q=c.value.trim().toLowerCase(); if(!q||/^tod[oa]s$/.test(q)) return;
          var col=c.getAttribute('data-fcol');
          if(col==='*'){{ ok=cells.some(function(x){{return x.indexOf(q)>=0;}}); }}
          else {{ var i=cols.indexOf(col); if(i>=0) ok=cells[i].indexOf(q)>=0; }} }});
        r.hidden=!ok; if(ok) shown++;
      }});
      var e=t.querySelector('.wf-empty'); if(e) e.style.display=shown?'none':'block';
      var pg=host.nextElementSibling; if(pg&&pg.classList.contains('wf-pager')){{var sp=pg.querySelector('.wf-shown'); if(sp) sp.textContent=' · '+shown+' en pantalla';}}
      if(f&&f.classList.contains('wf-filters')&&window.wfChips) window.wfChips(f,shown);
    }});
  }}
  if(sel){{
    var saved=null; try{{saved=localStorage.getItem('wf-sede');}}catch(e){{}}
    if(saved&&[].some.call(sel.options,function(o){{return o.value===saved;}})) sel.value=saved;
    sel.addEventListener('change',function(){{try{{localStorage.setItem('wf-sede',sel.value);}}catch(e){{}}refresh();}});
  }}
  document.querySelectorAll('[data-fcol]').forEach(function(c){{c.addEventListener('input',refresh);c.addEventListener('change',refresh);}});
  try{{var q=new URLSearchParams(location.search).get('q');var sb=document.querySelector('input[data-fcol="*"]');if(q&&sb){{sb.value=q;}}}}catch(e){{}}
  refresh();
}})();
(function(){{
  var rs=document.getElementById('rol'); if(!rs) return;
  function apply(){{
    var r=rs.value, opt=rs.options[rs.selectedIndex];
    var u=document.getElementById('rol-user'); if(u) u.innerHTML=opt.getAttribute('data-user')+'<small>'+opt.textContent+'</small>';
    var av=document.querySelector('.user .avatar'); if(av) av.textContent=opt.getAttribute('data-user').replace(/^(Dir\.|Admin\.|Coord\.)\s*/,'').charAt(0).toUpperCase();
    document.querySelectorAll('[data-roles]').forEach(function(e){{
      var ok=e.getAttribute('data-roles').split(',').indexOf(r)>=0;
      if(e.hasAttribute('data-panel')){{ if(!ok){{e.dataset.wfHidden='1';e.style.display='none';}} else {{delete e.dataset.wfHidden;}} return; }}
      if(e.dataset.wfD===undefined) e.dataset.wfD=e.style.display||'';
      e.style.display=ok?e.dataset.wfD:'none';
    }});
    (function(){{var nav=document.getElementById('sidenav'),sb=nav&&nav.parentElement;if(!nav)return;
      nav.querySelectorAll('details.nav-group').forEach(function(d){{var k='wf-nav-'+d.getAttribute('data-area');
        d.addEventListener('toggle',function(){{try{{localStorage.setItem(k,d.open?'1':'0');}}catch(e){{}}more();}});}});
      function more(){{var m=nav.scrollHeight-nav.clientHeight-nav.scrollTop>8;sb.classList.toggle('has-more',m);}}
      nav.addEventListener('scroll',more);window.addEventListener('resize',more);more();setTimeout(more,300);
      var a=nav.querySelector('.nav-link.active');if(a){{var r=a.getBoundingClientRect(),n=nav.getBoundingClientRect();if(r.bottom>n.bottom||r.top<n.top)nav.scrollTop=a.offsetTop-nav.clientHeight/2;}}
    }})();
    (function(){{var ub=document.getElementById('user-btn'),up=document.getElementById('user-pop');if(!ub)return;ub.addEventListener('click',function(e){{e.stopPropagation();var o=up.hidden;up.hidden=!o;ub.setAttribute('aria-expanded',o);}});up.addEventListener('click',function(e){{e.stopPropagation();}});document.addEventListener('click',function(e){{if(!up.hidden&&!up.contains(e.target))up.hidden=true;}});document.addEventListener('keydown',function(e){{if(e.key==='Escape')up.hidden=true;}});}})();
    (function(){{var box=document.getElementById('sched-custom');if(!box)return;var card=box.closest('.card');var sel=[].find.call(document.querySelectorAll('select.ctl'),function(x){{return [].some.call(x.options,function(o){{return /^Personalizado/.test(o.textContent);}});}});
      function upd(){{var on=sel&&/^Personalizado/.test(sel.value);card.style.display=on?'':'none';}} if(sel){{sel.addEventListener('change',function(){{upd();if(/^Personalizado/.test(sel.value))card.scrollIntoView({{behavior:'smooth',block:'start'}});}});}} upd();
    }})();
    (function(){{var nb=document.getElementById('notif-btn'),np=document.getElementById('notif-pop');if(!nb)return;nb.addEventListener('click',function(e){{e.stopPropagation();var o=np.hidden;np.hidden=!o;nb.setAttribute('aria-expanded',o);}});document.addEventListener('click',function(e){{if(!np.hidden&&!np.contains(e.target))np.hidden=true;}});document.addEventListener('keydown',function(e){{if(e.key==='Escape')np.hidden=true;}});}})();

document.querySelectorAll('.tabs').forEach(function(bar){{
      var btns=[].slice.call(bar.querySelectorAll('[data-tab]'));
      var act=btns.filter(function(b){{return b.getAttribute('aria-selected')==='true'&&b.style.display!=='none';}})[0];
      if(!act){{ var first=btns.filter(function(b){{return b.style.display!=='none';}})[0]; if(first) first.click(); }}
    }});
  }}
  var saved=null; try{{saved=localStorage.getItem('wf-rol');}}catch(e){{}}
  if(saved&&[].some.call(rs.options,function(o){{return o.value===saved;}})) rs.value=saved;
  rs.addEventListener('change',function(){{try{{localStorage.setItem('wf-rol',rs.value);}}catch(e){{}}apply();}});
  window.wfApplyRole=apply;
}})();
document.querySelectorAll('.tabs').forEach(function(bar){{
  var btns=bar.querySelectorAll('[data-tab]');
  btns.forEach(function(b){{
    b.addEventListener('click',function(){{
      btns.forEach(function(x){{var on=x===b;x.setAttribute('aria-selected',on);x.setAttribute('tabindex',on?'0':'-1');x.classList.toggle('on',on);}});
      var mb=bar.querySelector('.tab-more>.btn'); if(mb){{var inMore=!!b.closest('.menu-pop');mb.classList.toggle('on',inMore);mb.firstChild.textContent=inMore?b.textContent+' ':'Más ';var mp=bar.querySelector('.tab-more .menu-pop');if(mp&&getComputedStyle(mp).display!=='contents')mp.hidden=true;}}
      var el=bar.nextElementSibling;
      while(el&&el.hasAttribute('data-panel')){{el.style.display=(el.getAttribute('data-panel')===b.dataset.tab&&!el.dataset.wfHidden)?'flex':'none';el=el.nextElementSibling;}}
    }});
  }});
}});
(function(){{
  var fab=document.getElementById('ai-fab'),panel=document.getElementById('ai-panel'),log=document.getElementById('ai-log'),form=document.getElementById('ai-form'),inp=document.getElementById('ai-input');
  if(!fab) return;
  function open(){{panel.hidden=false;fab.classList.add('on');inp.focus();}}
  function close(){{panel.hidden=true;fab.classList.remove('on');}}
  fab.addEventListener('click',function(){{panel.hidden?open():close();}});
  document.getElementById('ai-close').addEventListener('click',close);
  function add(cls,html){{var d=document.createElement('div');d.className='msg '+cls;d.innerHTML=html;log.appendChild(d);log.scrollTop=log.scrollHeight;}}
  function answer(q,a){{add('me',q);var t=document.createElement('div');t.className='msg bot typing';t.textContent='…';log.appendChild(t);log.scrollTop=log.scrollHeight;
    setTimeout(function(){{t.remove();add('bot',a||('Sobre <b>'+document.getElementById('ai-ctx').textContent+'</b>: en el producto final respondo con datos reales de la base unificada, filtrados por tu rol y sede. En este mockup puedo responder las preguntas sugeridas.'));}},600);}}
  document.querySelectorAll('.chipq').forEach(function(c){{c.addEventListener('click',function(){{answer(c.textContent.trim(),c.getAttribute('data-a'));}});}});
  form.addEventListener('submit',function(e){{e.preventDefault();var q=inp.value.trim();if(!q)return;inp.value='';var m=[].find.call(document.querySelectorAll('.chipq'),function(c){{return q.toLowerCase().split(' ').filter(function(w){{return w.length>4}}).some(function(w){{return c.textContent.toLowerCase().indexOf(w)>=0;}});}});answer(q,m?m.getAttribute('data-a'):null);}});
  document.querySelectorAll('.btn-ask').forEach(function(b){{b.addEventListener('click',function(){{open();inp.value=b.getAttribute('data-ask')||'';}});}});
}})();

(function(){{
  /* menús emergentes: [data-menu] controla el elemento de aria-controls */
  function closeAll(except){{document.querySelectorAll('[data-menu][aria-expanded=true]').forEach(function(b){{if(b===except)return;b.setAttribute('aria-expanded','false');var m=document.getElementById(b.getAttribute('aria-controls'));if(m&&getComputedStyle(m).display!=='contents')m.hidden=true;}});}}
  document.querySelectorAll('[data-menu]').forEach(function(b){{
    b.addEventListener('click',function(e){{e.stopPropagation();var m=document.getElementById(b.getAttribute('aria-controls'));var open=b.getAttribute('aria-expanded')==='true';closeAll(b);b.setAttribute('aria-expanded',!open);m.hidden=open;if(!open){{var f=m.querySelector('a,button,select,input');if(f)f.focus();}}}});
  }});
  document.addEventListener('click',function(e){{if(!e.target.closest('.menu-pop,.filters-more'))closeAll();}});
  document.addEventListener('keydown',function(e){{if(e.key==='Escape'){{var o=document.querySelector('[data-menu][aria-expanded=true]');closeAll();if(o)o.focus();}}}});
  document.querySelectorAll('a[href^="#go-"]').forEach(function(a){{a.addEventListener('click',function(e){{e.preventDefault();var t=document.getElementById(a.getAttribute('href').slice(4));if(!t)return;var pn=t.closest('[data-panel]');if(pn){{var tb=document.querySelector('[data-tab="'+pn.getAttribute('data-panel')+'"]');if(tb)tb.click();}}t.click();t.scrollIntoView({{block:'center'}});}});}});
  /* navegación móvil */
  var mb=document.getElementById('menu-btn'),sb=document.querySelector('.sidebar'),scrim=document.querySelector('.scrim');
  function navOpen(o){{document.body.classList.toggle('nav-open',o);if(mb)mb.setAttribute('aria-expanded',o);if(o){{var a=sb.querySelector('.nav-link.active')||sb.querySelector('a');if(a)a.focus();}}else if(mb)mb.focus();}}
  if(mb&&sb){{mb.addEventListener('click',function(){{navOpen(!document.body.classList.contains('nav-open'));}});if(scrim)scrim.addEventListener('click',function(){{navOpen(false);}});
    document.addEventListener('keydown',function(e){{if(!document.body.classList.contains('nav-open'))return;if(e.key==='Escape')navOpen(false);if(e.key==='Tab'){{var f=[].slice.call(sb.querySelectorAll('a,button,select,summary')).filter(function(x){{return x.offsetParent!==null;}});if(!f.length)return;var first=f[0],last=f[f.length-1];if(e.shiftKey&&document.activeElement===first){{e.preventDefault();last.focus();}}else if(!e.shiftKey&&document.activeElement===last){{e.preventDefault();first.focus();}}}}}});}}
  /* sede dentro del menú en móvil */
  var sede=document.querySelector('.ctx-sede'),slot=document.querySelector('.sidebar-sede'),home=sede&&sede.parentElement,mq=window.matchMedia('(max-width:600px)');
  function placeSede(){{if(!sede||!slot)return;if(mq.matches){{if(sede.parentElement!==slot)slot.appendChild(sede);}}else if(sede.parentElement!==home)home.insertBefore(sede,home.firstChild);}}
  placeSede();if(mq.addEventListener)mq.addEventListener('change',placeSede);
  /* pestañas: flechas izquierda/derecha */
  document.querySelectorAll('.tabs').forEach(function(bar){{bar.addEventListener('keydown',function(e){{if(e.key!=='ArrowRight'&&e.key!=='ArrowLeft')return;var t=[].slice.call(bar.querySelectorAll('[role=tab]')).filter(function(x){{return x.offsetParent!==null||getComputedStyle(x).display!=='none';}});var i=t.indexOf(document.activeElement);if(i<0)return;e.preventDefault();var n=t[(i+(e.key==='ArrowRight'?1:-1)+t.length)%t.length];n.focus();n.click();}});}});
  /* chips de filtros activos */
  window.wfChips=function(f,shown){{var box=f.querySelector('.chips-active');if(!box)return;box.innerHTML='';var any=false;
    [].forEach.call(f.querySelectorAll('[data-fcol]'),function(c){{var v=(c.value||'').trim();if(!v||/^tod[oa]s$/i.test(v))return;any=true;var lab=c.tagName==='SELECT'?(c.closest('label').firstChild.textContent.trim()):'Buscar';var b=document.createElement('button');b.type='button';b.className='fchip';b.innerHTML='<b>'+lab+':</b> '+v.replace(/</g,'&lt;')+'<span aria-hidden="true">×</span>';b.setAttribute('aria-label','Quitar filtro '+lab+': '+v);b.addEventListener('click',function(){{if(c.tagName==='SELECT')c.selectedIndex=0;else c.value='';c.dispatchEvent(new Event('change'));}});box.appendChild(b);}});
    if(any){{var cl=document.createElement('button');cl.type='button';cl.className='fclear';cl.textContent='Limpiar todo';cl.addEventListener('click',function(){{[].forEach.call(f.querySelectorAll('[data-fcol]'),function(c){{if(c.tagName==='SELECT')c.selectedIndex=0;else c.value='';}});var x=f.querySelector('[data-fcol]');if(x)x.dispatchEvent(new Event('change'));}});box.appendChild(cl);}}
    var cnt=f.querySelector('.result-count');if(cnt)cnt.textContent=shown+(shown===1?' resultado':' resultados');
    var mbn=f.querySelector('.btn-more');if(mbn){{var n=[].filter.call(f.querySelectorAll('.filters-more [data-fcol]'),function(c){{var v=(c.value||'').trim();return v&&!/^tod[oa]s$/i.test(v);}}).length;var t=mbn.querySelector('.cnt');if(t)t.textContent=n?' · '+n+' activos':'';}}
  }};
  document.querySelectorAll('.wf-filters').forEach(function(f){{var x=f.querySelector('[data-fcol]');if(x)x.dispatchEvent(new Event('change'));}});
  /* elementos que aplican un filtro: franja de resumen y franja de etapas */
  document.querySelectorAll('[data-fset]').forEach(function(b){{b.addEventListener('click',function(){{var parts=b.getAttribute('data-fset').split('='),col=parts[0],val=parts[1];var grp=b.closest('[data-fgroup]');var on=b.getAttribute('aria-pressed')!=='true';if(grp)grp.querySelectorAll('[data-fset]').forEach(function(x){{x.setAttribute('aria-pressed','false');}});b.setAttribute('aria-pressed',on);
    var c=document.querySelector('[data-fcol="'+col+'"]');if(!c)return;if(c.tagName==='SELECT'){{var o=[].filter.call(c.options,function(o){{return o.text===val;}})[0];c.selectedIndex=on&&o?o.index:0;}}else c.value=on?val:'';c.dispatchEvent(new Event('change'));
    var host=c.closest('.wf-filters');if(host&&!on)return;}});}});
  /* controles segmentados */
  document.querySelectorAll('.seg').forEach(function(g){{var bs=g.querySelectorAll('[role=radio]');bs.forEach(function(b){{b.addEventListener('click',function(){{bs.forEach(function(x){{x.setAttribute('aria-checked',x===b);x.tabIndex=x===b?0:-1;var p=document.getElementById(x.getAttribute('aria-controls'));if(p)p.hidden=x!==b;}});}});
    b.addEventListener('keydown',function(e){{if(e.key!=='ArrowRight'&&e.key!=='ArrowLeft')return;e.preventDefault();var a=[].slice.call(bs),i=a.indexOf(b),n=a[(i+(e.key==='ArrowRight'?1:-1)+a.length)%a.length];n.focus();n.click();}});}});}});
  /* dirección por niveles: provincia → cantón → parroquia */
  document.querySelectorAll('select[data-dpa]').forEach(function(p){{var ids=p.getAttribute('data-dpa').split(','),c=document.getElementById(ids[0]),q=document.getElementById(ids[1]),d=JSON.parse(p.getAttribute('data-dpa-json'));
    function fill(sel,list){{sel.innerHTML=list.map(function(x){{return '<option>'+x+'</option>';}}).join('');}}
    p.addEventListener('change',function(){{fill(c,Object.keys(d[p.value]||{{}}));fill(q,((d[p.value]||{{}})[c.value]||[]).concat(['Otra parroquia…']));}});
    c.addEventListener('change',function(){{fill(q,((d[p.value]||{{}})[c.value]||[]).concat(['Otra parroquia…']));}});}});
  /* exportaciones reales: CSV de las tablas visibles, PDF por impresión, XML de ejemplo */
  document.querySelectorAll('[data-export]').forEach(function(b){{b.addEventListener('click',function(){{
    var kind=b.getAttribute('data-export'),name=((document.querySelector('h1')||{{}}).textContent||document.title||'reporte').replace(/[^\wáéíóúñ]+/gi,'-').toLowerCase()+'-'+new Date().toISOString().slice(0,10);
    function dl(txt,ext,mime){{var a=document.createElement('a');a.href=URL.createObjectURL(new Blob(['\ufeff'+txt],{{type:mime}}));a.download=name+'.'+ext;document.body.appendChild(a);a.click();setTimeout(function(){{URL.revokeObjectURL(a.href);a.remove();}},500);
      var t=document.getElementById('wf-toast');if(t){{t.textContent='Descargado: '+a.download;t.style.display='block';setTimeout(function(){{t.style.display='none';}},2200);}}}}
    if(kind==='pdf'){{window.print();return;}}
    var scope=b.closest('.panel,.card,.seg-panel')||document;var tables=[].slice.call(scope.querySelectorAll('.wf-table')).filter(function(t){{return t.offsetParent!==null;}});
    if(!tables.length)tables=[].slice.call(document.querySelectorAll('.wf-table')).filter(function(t){{return t.offsetParent!==null;}});
    function clean(s){{return '"'+s.replace(/\s+/g,' ').trim().replace(/"/g,'""')+'"';}}
    function tableRows(t){{var cols=JSON.parse(t.getAttribute('data-cols')),rows=[cols];t.querySelectorAll('.wf-row').forEach(function(r){{if(r.style.display==='none')return;var cells=[];r.querySelectorAll('.td').forEach(function(c){{var main=c.querySelector('.c2>span');cells.push((main?main.textContent:c.textContent).replace(/\s+/g,' ').trim());}});rows.push(cells);}});return rows;}}
    if(kind==='xlsx'&&window.wfXlsx){{var sheets=[],chart=null,title=((document.querySelector('h1')||{{}}).textContent||'Datos').trim();
      tables.forEach(function(t,k){{var rows3=tableRows(t);sheets.push({{name:'Datos'+(k?' '+(k+1):''),rows:rows3}});
        if(!chart&&rows3.length>1){{var numCols=[];for(var j=1;j<rows3[0].length;j++){{var ok=true;for(var i=1;i<rows3.length;i++){{var m=String(rows3[i][j]).replace(/[\s$,%h]/g,'');if(!/^-?\d+(\.\d+)?$/.test(m)){{ok=false;break;}}}}if(ok)numCols.push(j);}}
          if(numCols.length){{var rows4=[[rows3[0][0]].concat(numCols.map(function(j){{return rows3[0][j];}}))];for(var i=1;i<rows3.length;i++)rows4.push([rows3[i][0]].concat(numCols.map(function(j){{return rows3[i][j];}})));sheets.unshift({{name:'Gráfico',rows:rows4}});chart={{title:title,sheet:0,nCat:rows4.length-1,nSer:Math.min(numCols.length,4),kind:'col'}};}}}}}});
      /* gráfico visible en el mismo panel (barras horizontales o verticales): va como hoja y, si no hubo tabla numérica, como gráfico de Excel */
      var hb=scope.querySelector('.hbars'),vb=scope.querySelector('.vbars');
      if(hb){{var rows=[['Concepto','Valor']];hb.querySelectorAll('.hbar').forEach(function(r){{rows.push([r.querySelector('span').textContent.trim(),r.querySelector('b').textContent.replace(/[^\d.-]/g,'')]);}});if(!chart){{sheets.unshift({{name:'Gráfico',rows:rows}});chart={{title:title,sheet:0,nCat:rows.length-1,nSer:1,kind:'bar'}};}}else sheets.push({{name:'Gráfico de la pantalla',rows:rows}});}}
      else if(vb){{var ser=[].map.call((scope.querySelector('.legend')||{{querySelectorAll:function(){{return [];}}}}).querySelectorAll('.leg'),function(l){{return l.textContent.trim();}});if(!ser.length)ser=['Valor'];var rows2=[['Categoría'].concat(ser)];vb.querySelectorAll('.vgroup').forEach(function(g){{var vals=[].map.call(g.querySelectorAll('.vbar span'),function(x){{return x.textContent.replace(/[^\d.-]/g,'');}});rows2.push([g.querySelector('.vlabel').textContent.trim()].concat(vals));}});if(!chart){{sheets.unshift({{name:'Gráfico',rows:rows2}});chart={{title:title,sheet:0,nCat:rows2.length-1,nSer:ser.length,kind:'col'}};}}else sheets.push({{name:'Gráfico de la pantalla',rows:rows2}});}}
      if(!sheets.length){{var ks=[['Indicador','Valor','Detalle']];document.querySelectorAll('.sum-item').forEach(function(k){{ks.push([k.querySelector('.sum-label').textContent.trim(),(k.querySelector('.sum-value')||{{textContent:''}}).textContent.trim(),(k.querySelector('.sum-sub')||{{textContent:''}}).textContent.trim()]);}});sheets.push({{name:'Resumen',rows:ks}});chart={{title:title,sheet:0,nCat:ks.length-1,nSer:1,kind:'col'}};}}
      var fn=window.wfXlsx(name,sheets,chart);var t2=document.getElementById('wf-toast');if(t2){{t2.textContent='Descargado: '+fn+' (datos + gráfico)';t2.style.display='block';setTimeout(function(){{t2.style.display='none';}},2200);}}return;}}
    if(kind==='xml'){{var rows=[];tables.forEach(function(t){{var cols=JSON.parse(t.getAttribute('data-cols'));t.querySelectorAll('.wf-row').forEach(function(r){{if(r.style.display==='none')return;var o='  <registro>';r.querySelectorAll('.td').forEach(function(c,i){{o+='<'+(cols[i]||'campo').replace(/[^a-z0-9]/gi,'_')+'>'+c.textContent.replace(/\s+/g,' ').trim().replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</'+(cols[i]||'campo').replace(/[^a-z0-9]/gi,'_')+'>';}});rows.push(o+'</registro>');}});}});
      dl('<?xml version="1.0" encoding="UTF-8"?>\\n<exportacion origen="Plataforma Cambridge" fecha="'+new Date().toISOString()+'">\\n'+rows.join('\\n')+'\\n</exportacion>','xml','application/xml');return;}}
    var out=[];tables.forEach(function(t,k){{var cols=JSON.parse(t.getAttribute('data-cols'));if(k)out.push('');out.push(cols.map(clean).join(';'));t.querySelectorAll('.wf-row').forEach(function(r){{if(r.style.display==='none')return;var cells=[];r.querySelectorAll('.td').forEach(function(c){{cells.push(clean(c.textContent));}});out.push(cells.join(';'));}});}});
    if(!out.length){{out.push(clean(document.title));document.querySelectorAll('.sum-item').forEach(function(k){{out.push([k.querySelector('.sum-label'),k.querySelector('.sum-value'),k.querySelector('.sum-sub')].map(function(e){{return clean(e?e.textContent:'');}}).join(';'));}});}}
    dl(out.join('\\n'),'csv','text/csv;charset=utf-8');}});}});
  /* agregar otro módulo (sin diálogo) */
  document.querySelectorAll('[data-addmod]').forEach(function(b){{b.addEventListener('click',function(){{
    var scope=b.closest('.wiz-step')||b.closest('.card')||document;var groups=scope.querySelectorAll('.mod-group');var g=groups[groups.length-1];if(!g)return;
    var rows=g.querySelectorAll('.mod'),last=rows[rows.length-1],m=/Módulo (\d+)/.exec(last.textContent),n=m?+m[1]+1:rows.length+1;
    var c=last.cloneNode(true);c.querySelector('.m-n b').textContent='Módulo '+n;var cells=c.children;
    cells[1].innerHTML='Continúa en el mismo grupo<small>cupo reservado al matricular</small>';cells[3].innerHTML='por confirmar<small>inicia</small>';cells[4].innerHTML='<span class="badge badge-navy"><i></i>Reservado</span>';
    g.appendChild(c);c.classList.add('is-new');var t=document.getElementById('wf-toast');if(t){{t.textContent='Módulo '+n+' agregado a la venta';t.style.display='block';setTimeout(function(){{t.style.display='none';}},2200);}}
  }});}});
  /* descuento recalculable */
  document.querySelectorAll('select[data-disc]').forEach(function(sel){{var lg=document.querySelector('[data-ledger="'+sel.getAttribute('data-disc')+'"]');if(!lg)return;var lim=+sel.getAttribute('data-limit')||10;
    function money(x){{return '$'+Math.round(x).toLocaleString('en-US');}}
    function calc(){{var p=+sel.value,tot=0,dsc=0;lg.querySelectorAll('[data-sub]').forEach(function(c){{var v=+c.getAttribute('data-v'),dc=c.previousElementSibling,ok=dc.hasAttribute('data-dc'),d=ok?v*p/100:0;dc.textContent=(ok&&p)?p+'%':'—';c.textContent=money(v-d);tot+=v-d;dsc+=d;}});
      lg.querySelector('[data-ldisc]').textContent=dsc?'-'+money(dsc):'—';lg.querySelector('[data-ltotal]').textContent=money(tot);
      document.querySelectorAll('[data-total-for="'+sel.getAttribute('data-disc')+'"]').forEach(function(e){{e.textContent=money(tot);}});
      document.querySelectorAll('[data-disc-for="'+sel.getAttribute('data-disc')+'"]').forEach(function(e){{e.textContent=p?p+'% · -'+money(dsc):'sin descuento';}});
      var h=sel.parentElement.querySelector('[data-disc-hint]');if(h){{h.textContent=p>lim?'Más de '+lim+'%: la matrícula queda en espera hasta que Dirección Comercial apruebe el descuento':'Los valores de la tabla y el total se recalculan al cambiar';h.classList.toggle('is-warn',p>lim);}}}}
    sel.addEventListener('change',calc);}});
  /* asistente de pasos */
  document.querySelectorAll('[data-wizard]').forEach(function(w){{
    var steps=[].slice.call(w.querySelectorAll('.wiz-step')),n=steps.length,cur=0,max=0,ol=w.querySelector('.stepper'),bar=w.querySelector('.wiz-progress i'),mob=w.querySelector('.wiz-mobile b');
    var foot=w.parentElement.querySelector('.form-foot');w.classList.add('is-on');
    var finals=foot?[].slice.call(foot.querySelectorAll('.btn-primary')):[];
    var prev=document.createElement('button');prev.type='button';prev.className='btn';prev.textContent='Atrás';
    var next=document.createElement('button');next.type='button';next.className='btn btn-primary';
    if(foot){{foot.insertBefore(prev,foot.firstChild);foot.appendChild(next);}}
    var check='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6L9 17l-5-5"/></svg>';
    function render(focus){{
      steps.forEach(function(s,i){{s.classList.toggle('on',i===cur);}});
      [].forEach.call(ol.children,function(li,i){{li.classList.toggle('is-done',i<cur||(i<=max&&i!==cur&&i<max));if(i===cur)li.setAttribute('aria-current','step');else li.removeAttribute('aria-current');var b=li.querySelector('button');b.disabled=i>max;li.querySelector('.s-n').innerHTML=(i<cur||(i<max&&i!==cur))?check:(i+1);}});
      bar.style.width=Math.round(cur/(n-1)*100)+'%';
      if(mob)mob.textContent='Paso '+(cur+1)+' de '+n+' · '+steps[cur].getAttribute('data-title');
      prev.hidden=cur===0;next.hidden=cur===n-1;finals.forEach(function(f){{f.hidden=cur!==n-1;}});
      if(cur<n-1)next.textContent='Siguiente: '+steps[cur+1].getAttribute('data-title');
      if(focus){{var h=steps[cur].querySelector('h3');if(h){{h.setAttribute('tabindex','-1');h.focus();}}}}
      if(location.hash!=='#paso-'+(cur+1))history.pushState(null,'','#paso-'+(cur+1));
    }}
    function go(i,focus){{cur=Math.max(0,Math.min(n-1,i));max=Math.max(max,cur);render(focus);window.scrollTo({{top:0,behavior:'smooth'}});}}
    function validate(){{var bad=[].slice.call(steps[cur].querySelectorAll('[data-validate]')).filter(function(c){{var empty=!c.value.trim();c.setAttribute('aria-invalid',empty);var m=c.parentElement.querySelector('.field-error');if(empty&&!m){{m=document.createElement('span');m.className='field-error';m.id=c.id+'-err';m.textContent='Completa este dato para continuar.';c.parentElement.appendChild(m);c.setAttribute('aria-describedby',m.id);}}else if(!empty&&m)m.remove();return empty;}});ol.children[cur].classList.toggle('is-error',bad.length>0);if(bad.length)bad[0].focus();return !bad.length;}}
    next.addEventListener('click',function(){{if(validate())go(cur+1,true);}});
    prev.addEventListener('click',function(){{go(cur-1,true);}});
    [].forEach.call(ol.querySelectorAll('button'),function(b,i){{b.addEventListener('click',function(){{if(i<=max)go(i,true);}});}});
    w.querySelectorAll('[data-wgoto]').forEach(function(b){{b.addEventListener('click',function(){{go(+b.getAttribute('data-wgoto')-1,true);}});}});
    var tg=w.querySelector('.wiz-toggle');if(tg)tg.addEventListener('click',function(){{var o=ol.classList.toggle('is-open');tg.setAttribute('aria-expanded',o);tg.textContent=o?'Ocultar pasos':'Ver pasos';}});
    var sm=w.querySelector('.wiz-summary');function sumMode(){{if(sm)sm.open=!window.matchMedia('(max-width:1180px)').matches;}}sumMode();window.addEventListener('resize',sumMode);
    if(sm)sm.querySelector('summary').addEventListener('click',function(e){{if(!window.matchMedia('(max-width:1180px)').matches)e.preventDefault();}});
    function fromHash(){{var m=/^#paso-(\d)$/.exec(location.hash);if(m){{var i=+m[1]-1;if(i<=max||i===0){{cur=i;render(false);}}}}}}
    window.addEventListener('popstate',fromHash);var m0=/^#paso-(\d)$/.exec(location.hash);if(m0){{max=+m0[1]-1;cur=max;}}render(false);
  }});
}})();
if(window.wfApplyRole) window.wfApplyRole();
window.wfReady=true;
</script>
</body>
</html>'''
    open(os.path.join(ROOT,fname),"w").write(html)

def table(cols, rows, h=46, sede=None):
    """sede = índice de la columna cuyo valor (Quito/Valle/Ambato) filtra la fila con el selector global."""
    hd="".join(f'<div style="padding:10px 12px;font-weight:700;font-size:13px;border-bottom:2px solid {INK}">{c}</div>' for c in cols)
    body=""
    for r in rows:
        cells="".join(f'<div style="padding:12px;font-size:13px;border-bottom:1px solid {LINE};min-height:{h}px;box-sizing:border-box;display:flex;align-items:center;min-width:0;overflow-wrap:anywhere">{c}</div>' for c in r)
        sd=""
        if sede is not None:
            import re as _re
            m=_re.search(r"Quito|Valle|Ambato|Todas", str(r[sede]))
            if m: sd=f' data-sede="{m.group(0)}"'
        body+=f'<div class="wf-row" style="display:contents"{sd}>{cells}</div>'
    import json as _j
    empty=f'<div class="wf-empty" style="display:none;grid-column:1/-1;padding:24px;text-align:center;color:{MUTE};font-size:14px">Sin resultados con estos filtros</div>'
    return f'<div class="wf-table" data-cols=\'{_j.dumps(cols,ensure_ascii=False)}\' style="display:grid;grid-template-columns:repeat({len(cols)}, minmax(0, 1fr));border:2px solid {INK}">{hd}{body}{empty}</div>'

def tabs(items, active, panels=None, roles=None):
    """items: lista de etiquetas o (etiqueta, href). panels: dict etiqueta -> html del panel.
    Las pestañas con panel cambian de contenido en la misma página; las que tienen href navegan."""
    panels=panels or {}; roles=roles or {}
    bar=""; body=""
    for t in items:
        label,href = t if isinstance(t,tuple) else (t,None)
        on = label==active
        rl=f' data-roles="{roles[label]}"' if label in roles else ""
        st=f"padding:10px 16px;font-size:14px;font-family:inherit;color:{INK};background:none;border:0;border-bottom:3px solid {INK if on else 'transparent'};font-weight:{700 if on else 400};cursor:pointer;text-decoration:none"
        if href:
            bar+=f'<a href="{href}" role="tab"{rl} style="{st}">{label}</a>'
        else:
            bar+=f'<button type="button" role="tab" data-tab="{label}"{rl} aria-selected="{"true" if on else "false"}" style="{st}">{label}</button>'
    for label,content in panels.items():
        on = label==active
        rl=f' data-roles="{roles[label]}"' if label in roles else ""
        body+=f'<div role="tabpanel" data-panel="{label}"{rl} style="display:{"flex" if on else "none"};flex-direction:column;gap:20px">{content}</div>'
    return f'<div class="tabs" role="tablist" style="display:flex;flex-wrap:wrap;gap:4px;border-bottom:2px solid {LINE}">{bar}</div>{body}'

def form(fields, cols=2):
    out=""
    for i,f in enumerate(fields):
        out+=f'<div style="display:flex;flex-direction:column;gap:6px"><label for="f{i}" style="font-size:13px;font-weight:600">{f}</label><input id="f{i}" style="min-height:44px;padding:0 12px;border:2px solid {LINE};font-size:14px"></div>'
    return f'<div style="display:grid;grid-template-columns:repeat({cols}, minmax(0, 1fr));gap:16px">{out}</div>'

# ---------- Componentes de detalle (sin cajas grises) ----------
SEDES=["Todas","Quito","Valle","Ambato","Cuenca"]
def sv(todas,quito,valle,ambato,cuenca=None):
    """Valor que cambia con el selector de sede global."""
    import json as _j
    d=_j.dumps({"Todas":str(todas),"Quito":str(quito),"Valle":str(valle),"Ambato":str(ambato),"Cuenca":str(ambato if cuenca is None else cuenca)},ensure_ascii=False).replace("'","&#39;")
    return f"<span data-sv='{d}'>{todas}</span>"

def kpi(label, value, sub=""):
    return (f'<div style="border:2px solid {INK};padding:14px 16px;display:flex;flex-direction:column;gap:4px;min-width:0">'
            f'<span style="font-size:12px;color:{MUTE};text-transform:uppercase;letter-spacing:.04em">{label}</span>'
            f'<span style="font-size:26px;font-weight:700;line-height:1.1">{value}</span>'
            + (f'<span style="font-size:12px;color:{MUTE}">{sub}</span>' if sub else '') + '</div>')
def kpis(items):
    return f'<div style="display:grid;grid-template-columns:repeat({len(items)}, minmax(0, 1fr));gap:16px">'+"".join(kpi(*i) for i in items)+'</div>'

_fid=[0]
def _nid():
    _fid[0]+=1; return f"c{_fid[0]}"
CTL=f"min-height:40px;padding:0 10px;border:2px solid {LINE};font:inherit;font-size:14px;background:#fff;color:{INK};width:100%"
def sel(label, options, w="160px", col=None):
    """Dentro de filters(): filtra la tabla siguiente por la columna `col` (por defecto, la columna que se llama igual que la etiqueta). col=False no filtra."""
    i=_nid(); opts="".join(f'<option>{o}</option>' for o in options)
    fc="" if col is False else f' data-fcol="{col or label}"'
    return f'<label style="display:flex;flex-direction:column;gap:4px;width:{w};font-size:12px;color:{MUTE}">{label}<select id="{i}"{fc} style="{CTL}">{opts}</select></label>'
def search(label, placeholder, w="280px"):
    i=_nid()
    return f'<label style="display:flex;flex-direction:column;gap:4px;width:{w};font-size:12px;color:{MUTE}">{label}<input id="{i}" type="search" data-fcol="*" placeholder="{placeholder}" style="{CTL}"></label>'
def dates(label="Rango de fechas", a="2026-10-01", b="2026-10-31"):
    i=_nid()
    return (f'<div style="display:flex;flex-direction:column;gap:4px;font-size:12px;color:{MUTE}"><label for="{i}">{label}</label>'
            f'<div style="display:flex;gap:6px;align-items:center"><input id="{i}" type="date" value="{a}" style="{CTL};width:150px"><span>a</span><input type="date" value="{b}" aria-label="Hasta" style="{CTL};width:150px"></div></div>')
def filters(*ctrls, actions=""):
    return '<div class="wf-filters" style="display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end">'+"".join(ctrls)+(f'<div style="margin-left:auto;display:flex;flex-wrap:wrap;gap:12px;align-items:center">{actions}</div>' if actions else '')+'</div>'

def note(text, kind="info"):
    col={"info":ACC,"warn":"#b45309","ok":"#047857"}[kind]
    return f'<p style="margin:0;padding:10px 14px;border-left:4px solid {col};background:#f9fafb;font-size:13px;line-height:1.5;color:{INK}">{text}</p>'
def kv(*pairs):
    return '<div style="display:flex;flex-wrap:wrap;gap:6px 20px;font-size:14px;align-items:center">'+"".join(f'<span><span style="color:{MUTE}">{k}</span> <b>{v}</b></span>' for k,v in pairs)+'</div>'
def badge(text, kind="neutral"):
    bg={"neutral":FILL,"ok":"#d1fae5","warn":"#fef3c7","bad":"#fee2e2"}[kind]
    return f'<span style="display:inline-block;padding:2px 8px;border-radius:999px;background:{bg};font-size:12px;font-weight:600">{text}</span>'
def progress(pct, label=""):
    return (f'<div style="display:flex;flex-direction:column;gap:4px;font-size:13px"><div style="display:flex;justify-content:space-between"><span>{label}</span><b>{pct}%</b></div>'
            f'<div style="height:10px;background:{FILL};border:1px solid {LINE}"><div style="width:{pct}%;height:100%;background:{INK}"></div></div></div>')
def hbars(items, unit=""):
    mx=max(v for _,v in items) or 1; out=""
    for l,v in items:
        out+=(f'<div style="display:grid;grid-template-columns:150px 1fr 80px;gap:10px;align-items:center;font-size:13px"><span>{l}</span>'
              f'<div style="height:16px;background:{FILL}"><div style="width:{v/mx*100:.0f}%;height:100%;background:{INK}"></div></div><b style="text-align:right">{unit}{v:,}{"%" if unit=="" and mx<=100 else ""}</b></div>')
    return f'<div style="display:flex;flex-direction:column;gap:8px">{out}</div>'
def vbars(groups, series, h=150):
    cols=[INK,"#9ca3af","#d1d5db"]; mx=max(v for _,vs in groups for v in vs) or 1
    g="".join('<div style="display:flex;flex-direction:column;align-items:center;gap:6px;flex:1"><div style="display:flex;align-items:flex-end;gap:3px;height:%dpx">'%h+
              "".join(f'<div title="{series[i]}: {v}" style="width:22px;height:{v/mx*h:.0f}px;background:{cols[i]};position:relative"><span style="position:absolute;top:-16px;left:50%;transform:translateX(-50%);font-size:11px">{v}</span></div>' for i,v in enumerate(vs))+
              f'</div><span style="font-size:12px;text-align:center">{l}</span></div>' for l,vs in groups)
    leg="".join(f'<span style="display:inline-flex;align-items:center;gap:6px;font-size:12px"><i style="width:12px;height:12px;background:{cols[i]};display:inline-block"></i>{n}</span>' for i,n in enumerate(series))
    return f'<div style="display:flex;flex-direction:column;gap:10px;padding-top:16px"><div style="display:flex;gap:8px;border-bottom:1px solid {LINE};padding-bottom:6px">{g}</div><div style="display:flex;gap:16px">{leg}</div></div>'
def linechart(labels, series, h=160):
    W=600; cols=[INK,"#9ca3af","#60a5fa"]; mx=max(v for vs in series.values() for v in vs) or 1
    n=len(labels); xs=[40+i*(W-60)/(n-1) for i in range(n)]
    paths=""
    for k,(name,vs) in enumerate(series.items()):
        pts=" ".join(f"{xs[i]:.0f},{h-20-(v/mx)*(h-40):.0f}" for i,v in enumerate(vs))
        paths+=f'<polyline fill="none" stroke="{cols[k]}" stroke-width="2.5" points="{pts}"/>'
    axis="".join(f'<text x="{xs[i]:.0f}" y="{h-4}" font-size="12" text-anchor="middle" fill="{MUTE}">{l}</text>' for i,l in enumerate(labels))
    grid="".join(f'<line x1="40" x2="{W-20}" y1="{h-20-(h-40)*f:.0f}" y2="{h-20-(h-40)*f:.0f}" stroke="{FILL}"/><text x="36" y="{h-16-(h-40)*f:.0f}" font-size="12" text-anchor="end" fill="{MUTE}">{mx*f:.0f}</text>' for f in (0,.5,1))
    leg="".join(f'<span style="display:inline-flex;align-items:center;gap:6px;font-size:12px"><i style="width:16px;height:3px;background:{cols[k]};display:inline-block"></i>{n}</span>' for k,n in enumerate(series))
    return f'<div style="display:flex;flex-direction:column;gap:8px"><svg viewBox="0 0 {W} {h}" style="width:100%;height:auto" role="img" aria-label="Gráfico de líneas">{grid}{paths}{axis}</svg><div style="display:flex;gap:16px">{leg}</div></div>'
def funnel(stages):
    mx=stages[0][1]; out=""
    for i,(l,v) in enumerate(stages):
        conv=f' · {v/stages[i-1][1]*100:.0f}% del paso anterior' if i else ''
        out+=f'<div style="display:flex;align-items:center;gap:12px;font-size:13px"><div style="width:{v/mx*100:.0f}%;min-width:70px;background:{INK};color:#fff;padding:8px 10px;font-weight:600;box-sizing:border-box">{v:,}</div><span>{l}{conv}</span></div>'
    return f'<div style="display:flex;flex-direction:column;gap:6px">{out}</div>'
def stacked(parts):
    cols=[INK,"#6b7280","#9ca3af","#d1d5db"]
    bar="".join(f'<div title="{l} {p}%" style="width:{p}%;background:{cols[i%4]};height:100%"></div>' for i,(l,p) in enumerate(parts))
    leg="".join(f'<span style="display:inline-flex;align-items:center;gap:6px;font-size:12px"><i style="width:12px;height:12px;background:{cols[i%4]};display:inline-block"></i>{l} <b>{p}%</b></span>' for i,(l,p) in enumerate(parts))
    return f'<div style="display:flex;flex-direction:column;gap:8px"><div style="display:flex;height:24px;border:1px solid {LINE}">{bar}</div><div style="display:flex;flex-wrap:wrap;gap:12px">{leg}</div></div>'
def upload(label, hint):
    i=_nid()
    return (f'<div style="border:2px dashed {LINE};padding:20px;display:flex;flex-direction:column;align-items:center;gap:8px;text-align:center;font-size:13px;width:100%;box-sizing:border-box">'
            f'<label for="{i}" style="font-weight:600">{label}</label><input id="{i}" type="file" style="font:inherit;font-size:13px"><span style="color:{MUTE}">{hint}</span></div>')
def pager(total, per=20):
    pages="".join(f'<a href="#" aria-label="Página {n}" style="padding:4px 10px;border:1px solid {LINE};text-decoration:none;color:{"#fff" if n==1 else INK};background:{INK if n==1 else "#fff"}">{n}</a>' for n in (1,2,3))
    return (f'<div class="wf-pager" style="display:flex;align-items:center;gap:12px;font-size:13px;color:{MUTE}"><span>{total} registros · {per} por página<span class="wf-shown"></span></span>'
            f'<span style="margin-left:auto;display:flex;gap:4px">{pages}<a href="#" aria-label="Siguiente" style="padding:4px 10px;border:1px solid {LINE};text-decoration:none;color:{INK}">›</a></span></div>')
def logo():
    return f'<div style="display:flex;flex-direction:column;align-items:center;gap:2px;padding:8px 0"><span style="font-size:22px;font-weight:700;letter-spacing:.12em">CAMBRIDGE</span><span style="font-size:11px;color:{MUTE};letter-spacing:.2em;text-transform:uppercase">School of Languages</span></div>'
def ai(items, ask="¿Qué más quieres saber?", open_=False):
    """Desactivado a pedido del cliente: las observaciones viven en Insights.html y en el asistente flotante. Se conserva la firma para no tocar las páginas."""
    return ""
    """Acordeón 'Asistente': cerrado muestra el conteo; abierto, hasta 3 observaciones con enlace."""
    items=items[:3]
    lis="".join(f'<li><span class="ai-dot" aria-hidden="true"></span><span class="ai-text">{t}</span><a class="ai-link" href="{h}">{l}</a></li>' for t,l,h in items)
    return (f'<details class="ai"{" open" if open_ else ""}><summary><span class="ai-spark" aria-hidden="true">{ico("spark","nav-ico")}</span><span class="ai-title"><b>Asistente</b><small>{len(items)} observaciones para ti · según tu rol y sede</small></span><span class="ai-caret" aria-hidden="true"><span class="chev"></span></span></summary>'
            f'<ul>{lis}</ul><div class="ai-ask"><button type="button" class="btn btn-primary btn-ask" data-ask="{ask}">{ico("spark","nav-ico")}&nbsp;Preguntar al asistente</button><a href="Insights.html" class="btn">Ver todos los insights</a></div></details>')
def flow(steps):
    return '<ol style="margin:0;padding:0;list-style:none;display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:13px">'+"".join((f'<li style="padding:6px 10px;border:1px solid {INK}">{st}</li>'+('<li aria-hidden="true">→</li>' if i<len(steps)-1 else '')) for i,st in enumerate(steps))+'</ol>'


def row(*cells, gap=16):
    return f'<div style="display:flex;flex-wrap:wrap;gap:{gap}px;align-items:center">'+"".join(cells)+'</div>'

def two(a,b, ratio="1fr 1fr"):
    return f'<div style="display:grid;grid-template-columns:{ratio};gap:20px">{a}{b}</div>'

def card(title, inner):
    return f'<section style="border:2px solid {INK};padding:16px;display:flex;flex-direction:column;gap:12px"><h2 style="margin:0;font-size:16px">{title}</h2>{inner}</section>'

def li(items):
    return '<ul style="margin:0;padding-left:18px;font-size:14px;line-height:1.7">'+"".join(f"<li>{i}</li>" for i in items)+'</ul>'

# ================= TEMA MOCKUP · identidad Cambridge (sobrescribe los helpers lo-fi) =================
NAVY="#1D3F8F"; NAVY2="#152F6B"; RED="#D62839"; YELLOW="#F6C21C"; SKY="#4FA3DC"; OK="#1B9E77"; WARN="#C9900A"
CH=["#2F55B5","#D62839","#2E8BC9","#C9900A"]  # paleta de gráficos validada (dataviz)
SVG={
 "home":"<path d='M3 11l9-8 9 8v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z'/>",
 "users":"<circle cx='9' cy='8' r='3.5'/><path d='M2.5 20a6.5 6.5 0 0 1 13 0'/><path d='M16 4a3.5 3.5 0 0 1 0 7M21.5 20a6.5 6.5 0 0 0-5-6.3'/>",
 "book":"<path d='M4 4.5A2.5 2.5 0 0 1 6.5 2H20v16H6.5A2.5 2.5 0 0 0 4 20.5z'/><path d='M4 20.5V4.5M8 6h8'/>",
 "cal":"<rect x='3' y='5' width='18' height='16' rx='2'/><path d='M3 10h18M8 3v4M16 3v4'/>",
 "grad":"<path d='M2 9l10-5 10 5-10 5z'/><path d='M6 11.5V16c0 1.5 3 3 6 3s6-1.5 6-3v-4.5M22 9v6'/>",
 "plus":"<circle cx='12' cy='12' r='9'/><path d='M12 8v8M8 12h8'/>",
 "doc":"<path d='M6 2h8l5 5v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z'/><path d='M14 2v6h6M8 13h8M8 17h5'/>",
 "coin":"<circle cx='12' cy='12' r='9'/><path d='M15 9.5a3 3 0 0 0-3-1.5c-1.7 0-3 .9-3 2s1.3 2 3 2 3 .9 3 2-1.3 2-3 2a3 3 0 0 1-3-1.5M12 6v2M12 16v2'/>",
 "check":"<path d='M20 6L9 17l-5-5'/>",
 "box":"<path d='M21 8l-9-5-9 5v8l9 5 9-5z'/><path d='M3 8l9 5 9-5M12 13v8'/>",
 "swap":"<path d='M4 7h13l-3-3M20 17H7l3 3'/>",
 "chart":"<path d='M4 20V10M10 20V4M16 20v-7M22 20H2'/>",
 "trend":"<path d='M3 17l6-6 4 4 8-8'/><path d='M15 7h6v6'/>",
 "lock":"<rect x='4' y='10' width='16' height='11' rx='2'/><path d='M8 10V7a4 4 0 0 1 8 0v3'/>",
 "cog":"<circle cx='12' cy='12' r='3'/><path d='M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z'/>",
 "compass":"<circle cx='12' cy='12' r='9'/><path d='M15.5 8.5l-2 5-5 2 2-5z'/>",
 "plug":"<path d='M9 2v6M15 2v6M6 8h12v4a6 6 0 0 1-12 0zM12 18v4'/>",
 "search":"<circle cx='11' cy='11' r='7'/><path d='M20 20l-3.5-3.5'/>",
 "bell":"<path d='M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9'/><path d='M10 21h4'/>",
 "spark":"<path d='M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z'/>",
 "mail":"<rect x='3' y='5' width='18' height='14' rx='2'/><path d='M3 7l9 6 9-6'/>",
 "phone":"<path d='M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2z'/>",
 "pin":"<path d='M12 22s7-7 7-12a7 7 0 0 0-14 0c0 5 7 12 7 12z'/><circle cx='12' cy='10' r='2.5'/>",
 "id":"<rect x='3' y='5' width='18' height='14' rx='2'/><circle cx='9' cy='12' r='2.5'/><path d='M14 10h4M14 14h4'/>",
 "play":"<circle cx='12' cy='12' r='9'/><path d='M10 8.5v7l6-3.5z'/>",
 "clock":"<circle cx='12' cy='12' r='9'/><path d='M12 7v5l3 2'/>",
 "medal":"<circle cx='12' cy='9' r='5'/><path d='M8.5 13.5L7 22l5-3 5 3-1.5-8.5'/>",
 "edit":"<path d='M12 20h9M16.5 3.5a2.1 2.1 0 1 1 3 3L7 19l-4 1 1-4z'/>",
 "chat":"<path d='M21 12a8 8 0 0 1-11.6 7.1L4 21l1.9-4.6A8 8 0 1 1 21 12z'/>",
}
def ico(name, cls="nav-ico"):
    return f'<span class="{cls}" aria-hidden="true"><svg viewBox="0 0 24 24">{SVG.get(name,"")}</svg></span>'
ICON={"Contratación":"id","Reclutamiento":"users","Tienda en línea":"box","Tablero comercial":"chart","Exámenes":"medal","Programas":"grad","Leads":"trend","Empresas":"id","Insights de IA":"spark","Inicio":"home","Estudiantes":"users","Cursos":"book","Sesiones":"cal","Profesores":"grad","Nueva matrícula":"plus","Facturación":"doc","Comisiones":"coin","Aprobaciones":"check","Stock por sede":"box","Movimientos y pedidos":"swap","Reportes":"chart","Dashboard ejecutivo":"trend","Usuarios y roles":"lock","Configuración":"cog","Audit log":"compass","Integraciones":"plug"}

def btn(label, href=None, primary=False, action=None, next=None, kind=None, disabled_reason=None, save=None):
    """save='lista': al confirmar (o al navegar) guarda los campos del formulario en localStorage y la lista destino (ltable) muestra el registro nuevo."""
    if href is None and action is None:
        a=ACTIONS.get(label)
        if isinstance(a,str): href=a
        elif a: action,next=a
    k=kind or ("primary" if primary else ("danger" if label in ("Rechazar","Anular matrícula","Marcar no dictada","Reversar y anular","Anular factura","Eliminar matrícula","Retirar estudiante") else ""))
    cls="btn"+(f" btn-{k}" if k else "")
    if disabled_reason:
        i=_nid(); return f'<span class="btn-wrap"><button type="button" class="{cls}" aria-disabled="true" aria-describedby="{i}">{label}</button> <small class="why" id="{i}">{disabled_reason}</small></span>'
    sv_=f' data-save="{save}"' if save else ""
    if href: return f'<a href="{href}" class="{cls}"{sv_}>{label}</a>'
    if action is None: raise ValueError(f"Botón sin destino ni acción: {label}")
    if re.match(r"^(Exportar|Descargar)", label) and label not in ("Descargar expediente",):
        # Exportación real en la demo: CSV (abre en Excel) de las tablas visibles, PDF por impresión del navegador, XML de ejemplo.
        kind_="pdf" if "PDF" in label or label in ("Descargar certificado","Descargar factura","Descargar facturas pendientes") else ("xml" if "XML" in label else ("xlsx" if "Excel" in label or label=="Exportar" else "csv"))
        return f'<button type="button" class="{cls}" data-export="{kind_}" title="{action}">{label}</button>'
    nx=f' data-next="{next}"' if next else ""
    return f'<button type="button" class="{cls}" data-action="{action}"{nx}{sv_}>{label}</button>'

def _top_elems(html):
    """Divide HTML en sus elementos de primer nivel (para repartir acciones entre visibles y menú)."""
    out=[]; depth=0; start=None
    for m in re.finditer(r'<(/?)([a-zA-Z0-9]+)[^>]*?(/?)>', html):
        closing, tag, selfc = m.group(1), m.group(2).lower(), m.group(3)
        if tag in ("br","img","input","hr","path","circle","rect","line","polyline","polygon"):
            if depth==0 and not closing: out.append(m.group(0))
            continue
        if not closing and not selfc:
            if depth==0: start=m.start()
            depth+=1
        elif closing:
            depth-=1
            if depth==0 and start is not None: out.append(html[start:m.end()]); start=None
    return out
def more_menu(items_html, label="Más acciones"):
    i=_nid()
    return f'<div class="more"><button type="button" class="btn" data-menu aria-haspopup="menu" aria-expanded="false" aria-controls="{i}">{label} <span class="chev chev-d" aria-hidden="true"></span></button><div class="menu-pop" id="{i}" role="menu" hidden>{items_html}</div></div>'
def rowmenu(items_html, label="Acciones"):
    """Menú '⋯' de una fila (acciones múltiples)."""
    i=_nid()
    return f'<div class="more"><button type="button" class="btn kebab" data-menu aria-haspopup="menu" aria-expanded="false" aria-controls="{i}" aria-label="{label}">⋯</button><div class="menu-pop" id="{i}" role="menu" hidden>{items_html}</div></div>'
def split_actions(actions, keep=2):
    """Un primario + otra acción visibles; el resto va a 'Más acciones'."""
    els=_top_elems(actions)
    if len(els)<=keep: return actions
    prim=[e for e in els if 'btn-primary' in e][:1]
    rest=[e for e in els if e not in prim]
    vis=prim+rest[:keep-len(prim)]
    return "".join(vis)+more_menu("".join(e for e in els if e not in vis))

def nav(active):
    active=NAV_ALIAS.get(active,active); out=""
    for area,items in NAV:
        items=[(n,h,r) for n,h,r in items if h not in HIDDEN]
        if not items: continue
        roles=",".join(sorted({c for _,_,r in items for c in r.split(",")}))
        links="".join(f'<a href="{h}" data-roles="{r}" class="nav-link{" active" if n==active else ""}">{ico(ICON.get(n,"doc"))}{n}</a>' for n,h,r in items)
        if not area:
            out+=f'<div data-roles="{roles}" class="nav-group-root">{links}</div>'; continue
        has_active=any(n==active for n,_,_ in items)
        out+=(f'<details class="nav-group" data-roles="{roles}" data-area="{area}"{" open" if True else ""}{" data-active" if has_active else ""}>'
              f'<summary class="nav-area"><span>{area}</span><span class="nav-caret chev"></span></summary>{links}</details>')
    return out

def shell(title, active, *parts, subtitle="", actions=""):
    body="".join(parts)
    act=NAV_ALIAS.get(active,active)
    parent=next(((n,h) for _,items in NAV for n,h,_ in items if n==act),None)
    path=(f'<a href="{parent[1]}">{parent[0]}</a> / {title}' if parent and not title.startswith(parent[0]) else (subtitle or ""))
    back=parent[1] if parent and parent[0]!=title else "Home.html"
    crumb=(f'<a href="{parent[1]}" class="crumb-parent">{parent[0]}</a><span class="sep" aria-hidden="true">/</span><span class="here">{title}</span>' if parent and parent[0]!=title else f'<span class="here">{title}</span>')
    head_actions=f'<div class="page-head-actions">{actions}</div>' if actions else ""
    return f'''<div class="app">
<aside class="sidebar" id="sidebar" aria-label="Menú principal"><a class="brand" href="Home.html"><img src="assets/logo.webp" alt="Cambridge School of Languages"></a><div class="sidebar-sede"></div><nav id="sidenav">{nav(active)}</nav><script>(function(){{try{{document.querySelectorAll('#sidenav details.nav-group').forEach(function(d){{if(localStorage.getItem('wf-nav-'+d.getAttribute('data-area'))==='0'&&!d.hasAttribute('data-active'))d.removeAttribute('open');}});}}catch(e){{}}}})();</script><div class="sidebar-more" aria-hidden="true"></div></aside>
<div class="scrim" aria-hidden="true"></div>
<div class="shell-main">
<header class="topbar">
  <button type="button" class="icon-btn menu-btn" id="menu-btn" aria-label="Abrir menú" aria-controls="sidebar" aria-expanded="false"><span class="nav-ico" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg></span></button>
  <nav class="crumbs" aria-label="Ruta">{'' if active=="Inicio" else f'<a href="{back}" class="back" aria-label="Volver"><span class="chev chev-l"></span></a>'}{crumb}</nav>
  <div class="topbar-right">
  <label class="ctx-sede" title="Sede">{ico("pin","nav-ico")}<span class="sr">Sede</span><select id="sede"><option>Todas</option><option>Quito</option><option>Valle</option><option>Ambato</option><option>Cuenca</option></select></label>
  <form class="search" action="Estudiantes.html" role="search">{ico("search","nav-ico")}<label for="gsearch" class="sr">Buscar</label><input id="gsearch" name="q" placeholder="Buscar…"></form>
  <div class="notif"><button type="button" class="icon-btn" id="notif-btn" aria-label="Notificaciones" aria-expanded="false">{ico("bell","nav-ico")}{notif_dots()}</button>
    <div class="notif-pop" id="notif-pop" hidden><div class="notif-head"><b>Notificaciones</b><a href="Notificaciones.html">Ver todas</a></div>
{notif_pop()}
    </div></div>
  <a href="Chatbot.html" class="icon-btn" aria-label="Asistente">{ico("spark","nav-ico")}</a>
  <div class="user-menu"><button type="button" class="user" id="user-btn" aria-expanded="false" aria-label="Cuenta"><span class="avatar sm">E</span><span id="rol-user">Estefanía<small>Administrador General</small></span><span class="nav-caret chev"></span></button>
    <div class="user-pop" id="user-pop" hidden><div class="user-pop-title">Contexto de prueba</div><label>Ver como<select id="rol">{"".join(f'<option value="{c}" data-user="{u}">{n}</option>' for c,n,u in ROLES)}</select></label><a href="Usuarios.html">Mi cuenta</a><a href="Main.html">Cerrar sesión</a><div class="user-pop-foot">Plataforma Cambridge · mockup v2</div></div></div>
  </div>
</header>
<main class="main" id="main">
  <div class="page-head"><div><h1>{title}</h1>{f'<p>{subtitle}</p>' if subtitle else ''}</div>{head_actions}</div>
  {body}
</main>
</div>
</div>'''

# Notificaciones: (roles, tipo, tinte, símbolo, título, detalle, destino, cuándo, leída). Cada rol ve solo las suyas (campana y Notificaciones.html).
NOTIFS=[
 ("ADM,GER,DIR","Aprobación","yellow","!","Descuento 42% pendiente de tu aprobación","Gabriela Núñez · Carla M. · hace 1 día","Aprobaciones.html","Ayer",False),
 ("ADM,GER,SUC,SEC","Inventario","red","−","Stock negativo: Empower B1+ en Valle","Correo de las 07:00 enviado · hoy","Inventario.html","Hoy",False),
 ("ADM,GER,SUC,COO","Pagos","navy","$","Payment sheet de octubre lista para revisión","3 alertas · ayer 17:30","PaymentSheet.html","Ayer",False),
 ("ADM,SUC,COO","Alta","green","✓","Profesor M. Castro aprobado","Ya puede recibir cursos · ayer 11:05","Profesores.html","Ayer",True),
 ("GER,DIR","Ventas","navy","$","Octubre va 9% sobre la meta de niveles","76 de 70 niveles vendidos","DashboardEjecutivo.html","Hoy",True),
 ("DIR,SUC","Comisiones","navy","$","Comisiones de octubre en revisión","3 asesores · cierra el 31 oct","Comisiones.html","Hoy",False),
 ("ASE","Descuento","yellow","!","Tu solicitud de 42% para Gabriela Núñez espera a Dir. Comercial","Enviada ayer 16:00","SolicitudDescuento.html","Ayer",False),
 ("ASE","Leads","navy","+","Lead nuevo de Kommo: Lucía Paredes","Referida por María Andrade · sin contactar 2 días","Leads.html","Hoy",False),
 ("ASE,SEC","Cobranza","red","$","Cuota vencida: Gabriela Núñez · 2 de 2 · $225","Venció el 18 oct","Facturas.html","Hoy",False),
 ("ASE","Comisión","green","✓","Comisión de septiembre pagada","$300 · cierre del 5 oct","DetalleComision.html","05 oct",True),
 ("SEC","Rematrícula","yellow","!","Rematrícula por confirmar: Sofía Herrera","Transferencia reportada desde el portal · 12 oct","Facturas.html","Hoy",False),
 ("SEC","SRI","red","!","Factura 000021095 rechazada por el SRI","Cédula del cliente inválida","Facturas.html","Hoy",False),
 ("COO","Académico","red","!","Curso 0001-2026-0430 terminó sin calificar","14 estudiantes sin nota · hace 5 días","CalificarCurso.html","Hoy",False),
 ("COO","Curso","yellow","!","Teens A2 (Ambato) inicia el 27 oct sin profesor","0001-2026-0192 · 5 / 10 inscritos","Cursos.html","Hoy",False),
 ("PRO","Sesión","yellow","!","Sesión de hoy por confirmar: B1 Virtual 19:00","Lunes 19 oct · Zoom 2","Sesiones.html","Hoy",False),
 ("PRO","Asistencia","red","!","Sofía Herrera faltó 3 veces seguidas","B1 Virtual · 0001-2026-0767 · riesgo de perder el módulo","DetalleCurso.html","Hoy",False),
 ("PRO","Curso","navy","+","Te proponen Teens B1 Virtual (0001-2026-0772)","Lu-Ma-Mi-Ju 17:00–19:00 · inicia 20 oct","FichaProfesor.html","Ayer",True),
]
_NTONE={"yellow":"background:var(--tint-yellow);color:#B45309","red":"background:var(--tint-red);color:#B91C1C","navy":"background:var(--tint-navy);color:var(--navy)","green":"background:var(--tint-green);color:#15803D"}
def notif_pop():
    return "".join(f'<a href="{h}" data-roles="{r}" class="notif-item{" read" if rd else ""}"><span class="notif-ico nt-{t}" aria-hidden="true"></span><span><b>{ti}</b><small>{d}</small></span></a>' for r,_,t,sy,ti,d,h,_,rd in NOTIFS)
def notif_dots():
    by={}
    for c,_,_ in ROLES:
        n=sum(1 for r,*_,rd in NOTIFS if c in r.split(",") and not rd)
        by.setdefault(n,[]).append(c)
    return "".join(f'<span class="dot" data-roles="{",".join(cs)}">{n}</span>' for n,cs in by.items() if n)
def notif_table(code):
    return table(["Tipo","Mensaje","Fecha","Acción"],[[ty,c2(ti,d),w,f'<a href="{h}">Ver</a>'] for r,ty,_,_,ti,d,h,w,_ in NOTIFS if code in r.split(",")],wide=1)

def c2(main, sub):
    """Celda de dos líneas: dato principal + detalle secundario en gris."""
    return f'<span class="c2"><span>{main}</span><small>{sub}</small></span>'
_MONEY=re.compile(r'^-?\$[\d,]+(\.\d+)?$')
_CODE=re.compile(r'^(\d{4}-\d{4}-\d{4}|00\d{7}|001-\d{9}|NC-\d+|V-\d{4}-\d{4}|PG-\d+|\d{10,13})$')
_MARKS={"✓":'<span class="badge badge-ok">Sí</span>',"✗":'<span class="badge badge-bad">No</span>',"☑":'<input type="checkbox" class="chk" checked aria-label="Presente">',"☐":'<input type="checkbox" class="chk" aria-label="Presente">'}
def _cell(c):
    c=str(c); t=c.strip()
    if t in _MARKS: return _MARKS[t], ""
    if _MONEY.match(t): return f'<span class="mono">{t}</span>', " is-num"
    if _CODE.match(t): return f'<span class="mono">{t}</span>', ""
    m=re.fullmatch(r'<a href="([^"]+)">([^<]+)</a>', t)
    if m:
        h,txt=m.groups()
        if txt.lower().startswith("ver"): return f'<a href="{h}" class="row-go" aria-label="{txt}"><span class="chev" aria-hidden="true"></span></a>', ""
        return f'<a href="{h}" class="row-link">{txt}<span class="chev" aria-hidden="true"></span></a>', ""
    return c, ""
def table(cols, rows, h=46, sede=None, hide=(), wide=0):
    """sede: índice de la columna de sede (filtro global). hide: índices que no se muestran pero siguen filtrando. wide: columna principal."""
    import json as _j, re as _re
    n=len(cols); hide=set(hide)
    def cls(i): return ' td-hide' if i in hide else ''
    hd="".join(f'<div class="th{cls(i)}" role="columnheader">{c}</div>' for i,c in enumerate(cols)); body=""
    for r in rows:
        cells=""
        for i,c in enumerate(r):
            html,extra=_cell(c)
            cells+=f'<div class="td{cls(i)}{" td-wide" if i==wide else ""}{extra}" data-label="{cols[i] if i<n else ""}">{html}</div>'
        sd=""
        if sede is not None:
            m=_re.search(r"Quito|Valle|Ambato|Cuenca|Todas", str(r[sede]))
            if m: sd=f' data-sede="{m.group(0)}"'
        body+=f'<div class="wf-row"{sd}>{cells}</div>'
    empty='<div class="wf-empty" style="display:none;grid-column:1/-1">Sin resultados con estos filtros</div>'
    tpl=" ".join(("minmax(200px,2.2fr)" if i==wide else ("max-content" if cols[i] in ("Acción","Estado","") else "minmax(min-content,1fr)")) for i in range(n) if i not in hide)
    return f'<div class="tbl-wrap"><div class="wf-table tbl" data-cols=\'{_j.dumps(cols,ensure_ascii=False)}\' style="grid-template-columns:{tpl}">{hd}{body}{empty}</div></div>'

def ltable(lst, cols, rows, tpl=None, **kw):
    """Tabla que además muestra los registros creados en esta demo (localStorage 'wf-data-<lst>', guardados por btn(save=lst)).
    tpl: una plantilla por columna con {Etiqueta del campo}; 'a|b' = dos líneas, 'badge:kind:texto', 'link:Pagina.html:texto', 'mono:texto'."""
    import json as _j
    t=table(cols, rows, **kw)
    tpl=tpl or LIST_TPL[lst]
    return t.replace('<div class="tbl-wrap">',f'<div class="tbl-wrap" data-list="{lst}" data-list-tpl=\'{_j.dumps(tpl,ensure_ascii=False).replace("&#39;","")}\'>',1)
LIST_TPL={
 "empresas":["{Razón social}|RUC {RUC} · {Contacto de RR. HH.}","{Sede que la atiende}","{Descuento del convenio (%)}% · {¿Quién paga?} · {Crédito}","0","0","$0 / mes","badge:ok:Activo · creada en esta demo","link:DetalleEmpresa.html:Ver grupo"],
 "estudiantes":["{Nombres} {Apellidos}|{Cédula / ID} · {Sede} · {Programa de interés} · asesor {Asesor asignado}","mono:{Cédula / ID}","{Sede}","{Programa de interés}","—","{Asesor asignado}","badge:navy:Nuevo · sin matrícula","link:Ficha360.html:Ver ficha"],
 "cursos":["{Programa} {Nivel}|{Código} · {Sede} · {Aula o enlace virtual} · {Horario} · {Modalidad}","{Sede}","{Programa}","{Modalidad}","{Nivel}","(sin asignar)","0/{Cupo máximo}","0%","badge:warn:Por abrir · creado en esta demo","link:DetalleCurso.html:Ver"],
 "profesores":["{Nombres y apellidos}|{Sede} · {Tipo de contrato} · ${Tarifa por hora}/h","{Sede}","{Tipo de contrato}","0","0|sin clases hoy","0 h","—","badge:ok:Activo · creado en esta demo","link:FichaProfesor.html:Ver perfil"],
 "usuarios":["{Nombres y apellidos}|{Email}","{Rol}","{Sedes visibles}","badge:ok:Activo · creado en esta demo","link:Usuarios.html:Ver"],
}
def tabs(items, active, panels=None, roles=None, maxvis=5, counts=None):
    panels=panels or {}; roles=roles or {}; counts=counts or {}; btns=[]; body=""
    for t in items:
        label,href = t if isinstance(t,tuple) else (t,None); on=label==active
        rl=f' data-roles="{roles[label]}"' if label in roles else ""
        if href: btns.append((label,f'<a href="{href}" role="tab"{rl} class="tab{" on" if on else ""}"{" aria-selected=\"true\"" if on else ""}>{label}</a>'))
        else: btns.append((label,f'<button type="button" role="tab" id="tab-{_slug(label)}" data-tab="{label}"{rl} aria-selected="{"true" if on else "false"}" tabindex="{"0" if on else "-1"}" class="tab{" on" if on else ""}">{label}{(" "+count(counts[label])) if label in counts else ""}</button>'))
    bar="".join(b for _,b in btns[:maxvis])
    if len(btns)>maxvis:
        i=_nid(); act_in=[l for l,_ in btns[maxvis:] if l==active]
        bar+=f'<div class="tab-more"><button type="button" class="tab btn{" on" if act_in else ""}" data-menu aria-haspopup="menu" aria-expanded="false" aria-controls="{i}">{act_in[0]+" " if act_in else "Más "}<span class="chev chev-d" aria-hidden="true"></span></button><div class="menu-pop" id="{i}" hidden>{"".join(b for _,b in btns[maxvis:])}</div></div>'
    for label,content in panels.items():
        on=label==active; rl=f' data-roles="{roles[label]}"' if label in roles else ""
        body+=f'<div role="tabpanel" data-panel="{label}"{rl} class="panel" style="display:{"flex" if on else "none"}">{content}</div>'
    return f'<div class="tabs" role="tablist">{bar}</div>{body}'
def _slug(t):
    import unicodedata
    t=unicodedata.normalize("NFKD",re.sub(r"<[^>]+>","",str(t))).encode("ascii","ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+","-",t).strip("-")
def seg(options, panels, label="Vista", counts=None):
    """Control segmentado: opciones de vista dentro de un área. panels: lista de HTML en el mismo orden."""
    counts=counts or {}; ids=[_nid() for _ in options]
    bs="".join(f'<button type="button" role="radio" id="seg-{_slug(o)}" aria-checked="{"true" if k==0 else "false"}" tabindex="{0 if k==0 else -1}" aria-controls="{ids[k]}">{o}{(" "+count(counts[o])) if o in counts else ""}</button>' for k,o in enumerate(options))
    ps="".join(f'<div class="seg-panel panel" style="display:flex" id="{ids[k]}"{"" if k==0 else " hidden"}>{p}</div>' for k,p in enumerate(panels))
    return f'<div class="seg" role="radiogroup" aria-label="{label}">{bs}</div>{ps}'

_FID=[0]
def field(label, value="", kind="text", options=None, req=False, hint=""):
    """Un campo de formulario. kind: text|select|date|time|email|tel|number|file|textarea. value = valor de ejemplo o placeholder."""
    _FID[0]+=1; i=f"f{_FID[0]}"
    val=label.endswith("!"); label=label.rstrip("!")
    lab=f'<label for="{i}">{label}{"<em>*</em>" if req else ""}</label>'
    if kind=="select":
        opts="".join(f'<option{" selected" if o==value else ""}>{o}</option>' for o in (options or []))
        ctl=f'<select id="{i}" class="ctl">{opts}</select>'
    elif kind=="textarea":
        ctl=f'<textarea id="{i}" class="ctl" rows="3" placeholder="{value}"></textarea>'
    elif kind=="file":
        ctl=f'<label class="ctl ctl-file" for="{i}"><span>{value or "Seleccionar archivo…"}</span><b>Examinar</b><input id="{i}" type="file" hidden></label>'
    else:
        # Dato de ejemplo precargado (demo): en campos obligatorios o validados el valor va como value, no como placeholder,
        # para que los asistentes avancen sin que el usuario tenga que escribir. Las pistas ("Busca por…", "Ej.…") siguen como placeholder.
        hinty=(not value) or value.endswith("…") or value.lower().startswith(("busca","ej.","escribe","selecciona","se calcula")) or (kind=="date" and not re.match(r"^\d{4}-\d{2}-\d{2}$",value)) or (kind=="time" and not re.match(r"^\d{2}:\d{2}$",value))
        if (req or val) and not hinty: ctl=f'<input id="{i}" type="{kind}" class="ctl" value="{value}">'
        else: ctl=f'<input id="{i}" type="{kind}" class="ctl" placeholder="{value}">'
    if req: ctl=ctl.replace(f'id="{i}"',f'id="{i}" aria-required="true"',1)
    if val: ctl=ctl.replace(f'id="{i}"',f'id="{i}" data-validate',1)
    if hint and kind!="file": ctl=ctl.replace(f'id="{i}"',f'id="{i}" aria-describedby="{i}-h"',1)
    return f'<div class="field">{lab}{ctl}{f"<small class=field-hint id={i}-h>{hint}</small>" if hint else ""}</div>'

# División político-administrativa del Ecuador: provincia → cantón → parroquias (urbanas y rurales principales).
# Fuente: DPA del INEC (resumen para el mockup; en producción se carga la tabla completa del INEC o se consulta por API).
DPA={
 "Azuay":{"Cuenca":["El Sagrario","San Blas","San Sebastián","Sucre","Huayna Cápac","Yanuncay","Totoracocha","Monay","Machángara","Bellavista","El Batán","Hermano Miguel","El Vecino","Gil Ramírez Dávalos","San Joaquín (rural)","Baños (rural)","Ricaurte (rural)","Sayausí (rural)","Turi (rural)"],"Gualaceo":["Gualaceo","Daniel Córdova Toral","Jadán","San Juan"],"Paute":["Paute","Bulán","Chicán","El Cabo"],"Sígsig":["Sígsig","San Bartolomé","Ludo"]},
 "Bolívar":{"Guaranda":["Ángel Polibio Chaves","Gabriel Ignacio Veintimilla","Guanujo","Salinas","San Simón","Simiátug"],"San Miguel":["San Miguel","Balsapamba","Bilován"],"Chillanes":["Chillanes","San José del Tambo"]},
 "Cañar":{"Azogues":["Azogues","Aurelio Bayas Martínez","Borrero","San Francisco","Javier Loyola","Luis Cordero"],"La Troncal":["La Troncal","Manuel J. Calle","Pancho Negro"],"Cañar":["Cañar","Chontamarca","Honorato Vásquez","Ingapirca"],"Biblián":["Biblián","Nazón","Turupamba"]},
 "Carchi":{"Tulcán":["Tulcán","González Suárez","Julio Andrade","Urbina","Tufiño"],"Montúfar":["San Gabriel","González Suárez","Cristóbal Colón","La Paz"],"Espejo":["El Ángel","27 de Septiembre","La Libertad","San Isidro"]},
 "Chimborazo":{"Riobamba":["Lizarzaburu","Maldonado","Velasco","Veloz","Yaruquíes","Cacha (rural)","Calpi (rural)","Licán (rural)","San Luis (rural)"],"Alausí":["Alausí","Guasuntos","Huigra","Sibambe","Tixán"],"Guano":["Guano","El Rosario","San Andrés","Ilapo"],"Chambo":["Chambo"]},
 "Cotopaxi":{"Latacunga":["La Matriz","Eloy Alfaro","Ignacio Flores","Juan Montalvo","San Buenaventura","Aláquez (rural)","Belisario Quevedo (rural)","Guaytacama (rural)","Mulaló (rural)","Toacaso (rural)"],"Salcedo":["San Miguel","Cusubamba","Mulalillo","Panzaleo"],"La Maná":["La Maná","El Carmen","El Triunfo","Guasaganda"],"Pujilí":["Pujilí","Angamarca","Zumbahua","La Victoria"]},
 "El Oro":{"Machala":["Machala","El Cambio","Jambelí","Jubones","La Providencia","Nueve de Mayo","Puerto Bolívar","El Retiro"],"Pasaje":["Pasaje","Bolívar","Loma de Franco","Ochoa León","Tres Cerritos","Buenavista"],"Santa Rosa":["Santa Rosa","Jumón","Nuevo Santa Rosa","Puerto Jelí","Bellavista"],"Huaquillas":["Huaquillas","Ecuador","El Paraíso","Hualtaco","Milton Reyes","Unión Lojana"]},
 "Esmeraldas":{"Esmeraldas":["Esmeraldas","Bartolomé Ruiz","5 de Agosto","Luis Tello","Simón Plata Torres","Tachina (rural)","Vuelta Larga (rural)"],"Atacames":["Atacames","La Unión","Súa","Tonchigüe","Tonsupa"],"Quinindé":["Rosa Zárate","Cube","Chura","La Unión","Viche"]},
 "Galápagos":{"San Cristóbal":["Puerto Baquerizo Moreno","El Progreso"],"Santa Cruz":["Puerto Ayora","Bellavista","Santa Rosa"],"Isabela":["Puerto Villamil","Tomás de Berlanga"]},
 "Guayas":{"Guayaquil":["Tarqui","Ximena","Febres Cordero","Letamendi","García Moreno","Rocafuerte","Roca","Nueve de Octubre","Olmedo","Pedro Carbo","Sucre","Urdaneta","Bolívar","Ayacucho","Chongón (rural)","Pascuales (rural)","Posorja (rural)","Puná (rural)","Tenguel (rural)"],"Samborondón":["Samborondón","La Puntilla (Satélite)","Tarifa"],"Durán":["Eloy Alfaro","El Recreo","Divino Niño"],"Daule":["Daule","La Aurora (Satélite)","Juan Bautista Aguirre","Laurel","Limonal","Los Lojas"],"Milagro":["Milagro","Chobo","Mariscal Sucre","Roberto Astudillo"]},
 "Imbabura":{"Ibarra":["San Francisco","El Sagrario","Caranqui","Alpachaca","Priorato","Ambuquí (rural)","Angochagua (rural)","La Esperanza (rural)","San Antonio (rural)","Salinas (rural)"],"Otavalo":["Jordán","San Luis","Eugenio Espejo","González Suárez","Miguel Egas Cabezas (Peguche)","San Pablo","Quichinche"],"Cotacachi":["San Francisco","El Sagrario","Quiroga","Imantag","Apuela"],"Antonio Ante":["Atuntaqui","Andrade Marín","Chaltura","Natabuela","San Roque"]},
 "Loja":{"Loja":["El Sagrario","San Sebastián","Sucre","El Valle","Carigán","Punzara","Malacatos (rural)","Vilcabamba (rural)","Chuquiribamba (rural)","San Lucas (rural)"],"Catamayo":["Catamayo","San José","El Tambo","Guayquichuma","Zambi"],"Calvas":["Cariamanga","Chile","San Vicente","Colaisaca","Utuana"],"Paltas":["Catacocha","Lourdes","Cangonamá","Guachanamá"]},
 "Los Ríos":{"Babahoyo":["Clemente Baquerizo","Dr. Camilo Ponce","Barreiro","El Salto","Caracol","Febres Cordero","Pimocha","La Unión"],"Quevedo":["Quevedo","San Camilo","San Cristóbal","Venus del Río Quevedo","Viva Alfaro","Siete de Octubre","24 de Mayo","Nicolás Infante Díaz","La Esperanza","San Carlos"],"Ventanas":["Ventanas","10 de Noviembre","Zapotal","Chacarita"]},
 "Manabí":{"Portoviejo":["Portoviejo","12 de Marzo","Andrés de Vera","Colón","Picoazá","San Pablo","Simón Bolívar","18 de Octubre","Francisco Pacheco","Abdón Calderón (rural)","Crucita (rural)","Riochico (rural)"],"Manta":["Manta","Los Esteros","Tarqui","Eloy Alfaro","San Mateo","Santa Marianita"],"Chone":["Chone","Santa Rita","Canuto","Convento","Ricaurte","San Antonio"],"Sucre":["Bahía de Caráquez","Leonidas Plaza","Charapotó","San Isidro"]},
 "Morona Santiago":{"Morona":["Macas","Sevilla Don Bosco","General Proaño","Río Blanco","San Isidro"],"Sucúa":["Sucúa","Asunción","Huambi","Santa Marianita"],"Gualaquiza":["Gualaquiza","Mercedes Molina","Bomboiza","El Rosario"]},
 "Napo":{"Tena":["Tena","Ahuano","Chontapunta","Pano","Puerto Misahuallí","Puerto Napo","Tálag"],"Archidona":["Archidona","Cotundo","San Pablo de Ushpayacu"],"El Chaco":["El Chaco","Linares","Oyacachi","Santa Rosa"]},
 "Orellana":{"Francisco de Orellana":["Puerto Francisco de Orellana (El Coca)","Dayuma","El Dorado","Taracoa","San José de Guayusa"],"La Joya de los Sachas":["La Joya de los Sachas","Enokanqui","Pompeya","San Carlos","Unión Milagreña"]},
 "Pastaza":{"Pastaza":["Puyo","Canelos","Fátima","Tarqui","Teniente Hugo Ortiz","Veracruz","10 de Agosto"],"Mera":["Mera","Madre Tierra","Shell"]},
 "Pichincha":{"Quito":["Belisario Quevedo","Carcelén","Centro Histórico","Chilibulo","Chillogallo","Chimbacalle","Cochapamba","Comité del Pueblo","Concepción","Cotocollao","El Condado","El Inca","Guamaní","Iñaquito","Itchimbía","Jipijapa","Kennedy","La Argelia","La Ecuatoriana","La Ferroviaria","La Libertad","La Magdalena","La Mena","Mariscal Sucre","Ponceano","Puengasí","Quitumbe","Rumipamba","San Bartolo","San Isidro del Inca","San Juan","Solanda","Turubamba","Cumbayá (rural)","Tumbaco (rural)","Conocoto (rural)","Alangasí (rural)","Amaguaña (rural)","Calderón (rural)","Pomasqui (rural)","San Antonio de Pichincha (rural)","Nayón (rural)","Zámbiza (rural)","Pifo (rural)","Puembo (rural)","Yaruquí (rural)","Checa (rural)","Tababela (rural)","El Quinche (rural)","Guayllabamba (rural)","Lloa (rural)","Nono (rural)","Píntag (rural)","La Merced (rural)","Guangopolo (rural)"],"Rumiñahui":["Sangolquí","San Pedro de Taboada","San Rafael","Cotogchoa","Rumipamba"],"Mejía":["Machachi","Alóag","Aloasí","Cutuglagua","El Chaupi","Manuel Cornejo Astorga (Tandapi)","Tambillo","Uyumbicho"],"Cayambe":["Cayambe","Ayora","Juan Montalvo","Ascázubi","Cangahua","Olmedo","Otón","Santa Rosa de Cusubamba"],"Pedro Moncayo":["Tabacundo","La Esperanza","Malchinguí","Tocachi","Tupigachi"],"Pedro Vicente Maldonado":["Pedro Vicente Maldonado"],"Puerto Quito":["Puerto Quito"],"San Miguel de los Bancos":["San Miguel de los Bancos","Mindo"]},
 "Santa Elena":{"Santa Elena":["Santa Elena","Ballenita","Atahualpa","Colonche","Manglaralto","Simón Bolívar"],"La Libertad":["La Libertad"],"Salinas":["Salinas","Carlos Espinoza Larrea","General Alberto Enríquez Gallo","Vicente Rocafuerte","Anconcito","José Luis Tamayo (Muey)"]},
 "Santo Domingo de los Tsáchilas":{"Santo Domingo":["Santo Domingo de los Colorados","Abraham Calazacón","Bombolí","Chiguilpe","Río Toachi","Río Verde","Zaracay","Alluriquín (rural)","Luz de América (rural)","Valle Hermoso (rural)"],"La Concordia":["La Concordia","Monterrey","Plan Piloto","Las Villegas"]},
 "Sucumbíos":{"Lago Agrio":["Nueva Loja","Dureno","General Farfán","Jambelí","Pacayacu","Santa Cecilia","El Eno"],"Shushufindi":["Shushufindi","Limoncocha","Pañacocha","San Roque","Siete de Julio"],"Cascales":["El Dorado de Cascales","Santa Rosa de Sucumbíos","Sevilla"]},
 "Tungurahua":{"Ambato":["Atocha – Ficoa","Celiano Monge","Huachi Chico","Huachi Loreto","La Matriz","La Merced","La Península","Pishilata","San Francisco","Izamba (rural)","Picaihua (rural)","Atahualpa (rural)","Augusto N. Martínez (rural)","Quisapincha (rural)","Santa Rosa (rural)","Totoras (rural)","Huachi Grande (rural)","Martínez (rural)","Pilahuín (rural)","Juan Benigno Vela (rural)","Montalvo (rural)","Pasa (rural)","San Bartolomé de Pinllo (rural)","San Fernando (rural)","Cunchibamba (rural)","Unamuncho (rural)","Ambatillo (rural)","Constantino Fernández (rural)"],"Baños de Agua Santa":["Baños de Agua Santa","Lligua","Río Negro","Río Verde","Ulba"],"Pelileo":["Pelileo","Benítez","Bolívar","Chiquicha","Cotaló","El Rosario","García Moreno","Huambaló","Salasaca"],"Píllaro":["Píllaro","Baquerizo Moreno","Emilio María Terán","Marcos Espinel","Presidente Urbina","San Andrés","San José de Poaló","San Miguelito"],"Cevallos":["Cevallos"],"Mocha":["Mocha","Pinguilí"],"Patate":["Patate","El Triunfo","Los Andes","Sucre"],"Quero":["Quero","Rumipamba","Yanayacu"],"Tisaleo":["Tisaleo","Quinchicoto"]},
 "Zamora Chinchipe":{"Zamora":["Zamora","El Limón","Cumbaratza","Guadalupe","Imbana","Sabanilla","Timbara"],"Yantzaza":["Yantzaza","Chicaña","Los Encuentros"],"Centinela del Cóndor":["Zumbi","Triunfo-Dorado"]},
}

def direccion_fields(prov="Pichincha", canton="Quito", parroquia="Iñaquito", calle="Av. Amazonas N36-152 y Naciones Unidas", ref="Edificio Amazonas Plaza, frente al parque La Carolina", lat="-0.17631", lng="-78.48411", req=True):
    """Dirección sectorizada por niveles (Provincia → Cantón → Parroquia, DPA del INEC) + calle y referencia + ubicación exacta en Google Maps.
    Los selectores son dependientes (JS en page()): al cambiar la provincia se cargan sus cantones y al cambiar el cantón sus parroquias.
    'Buscar en Google Maps' usa Places Autocomplete para autocompletar provincia, cantón, parroquia y coordenadas; el pin se puede arrastrar."""
    import json as _j
    ids=[]
    for _ in range(3): _FID[0]+=1; ids.append(f"f{_FID[0]}")
    a,b,c=ids
    rq=' aria-required="true"' if req else ""; em="<em>*</em>" if req else ""
    po="".join(f'<option{" selected" if k==prov else ""}>{k}</option>' for k in DPA)
    co="".join(f'<option{" selected" if k==canton else ""}>{k}</option>' for k in DPA[prov])
    pa="".join(f'<option{" selected" if k==parroquia else ""}>{k}</option>' for k in DPA[prov][canton]+["Otra parroquia…"])
    data=_j.dumps(DPA,ensure_ascii=False).replace("'","&#39;")
    sel3=(f'<div class="field"><label for="{a}">Provincia{em}</label><select id="{a}" class="ctl"{rq} data-dpa="{b},{c}" data-dpa-json=\'{data}\'>{po}</select><small class="field-hint">Las 24 provincias del Ecuador</small></div>'
          f'<div class="field"><label for="{b}">Cantón{em}</label><select id="{b}" class="ctl"{rq}>{co}</select><small class="field-hint">Solo los cantones de la provincia elegida</small></div>'
          f'<div class="field"><label for="{c}">Parroquia{em}</label><select id="{c}" class="ctl"{rq}>{pa}</select><small class="field-hint">Urbanas y rurales del cantón; base de los reportes por zona</small></div>')
    rest=(field("Calle y número",calle,"text",None,req,"Se autocompleta desde Google Maps; se puede corregir")
          +field("Referencia",ref,"text",None,False,"Edificio, conjunto, punto conocido"))
    mapa=(f'<div class="field field-span"><label>Ubicación exacta (Google Maps)</label><div class="gmap" role="img" aria-label="Mapa con la ubicación del domicilio">'
          f'<div class="gmap-search"><span class="cico">{ico("search","")}</span><input class="ctl" value="Av. Amazonas N36-152, Quito" aria-label="Buscar dirección en Google Maps"><button type="button" class="btn">Buscar en Google Maps</button></div>'
          f'<div class="gmap-canvas"><i class="gmap-road r1"></i><i class="gmap-road r2"></i><i class="gmap-road r3"></i><i class="gmap-park"></i><span class="gmap-pin" title="Arrastra el pin para ajustar">{ico("pin","")}</span><span class="gmap-label">Parque La Carolina</span><span class="gmap-attrib">Google Maps · Places + Geocoding</span></div>'
          f'<div class="gmap-foot"><span class="mono">{lat}, {lng}</span><span class="field-hint">Al mover el pin se recalculan provincia, cantón y parroquia (geocodificación inversa) y queda la posición exacta para visitas y reportes por zona</span>{btn("Usar mi ubicación actual")}{btn("Abrir en Google Maps","https://www.google.com/maps")}</div></div></div>')
    return sel3+rest+mapa
def _auto_field(f):
    """Convierte 'Etiqueta (pista)' en un campo con tipo, placeholder u opciones deducidas de la pista."""
    if isinstance(f, tuple): return field(*f) if not isinstance(f[-1], dict) else field(*f[:-1], **f[-1])
    m=re.match(r"^(.*?)\s*\((.*)\)\s*$", f); label, hint = (m.group(1), m.group(2)) if m else (f, "")
    low=(label+" "+hint).lower(); hl=hint.lower()
    if hint and " / " in hint and not hl.startswith(("ej.","valida","automático","calculad","desde","se valida","lead")):
        opts=[o.strip() for o in hint.split(" / ")]
        if label.lower().startswith("cómo"): opts=opts
        return field(label, opts[0], "select", ["Seleccionar…"]+[o[0].upper()+o[1:] for o in opts] if len(opts)>2 else [o[0].upper()+o[1:] for o in opts])
    if hl.startswith("automático") or hl.startswith("calculad"):
        return field(label, hint.split(":")[-1].strip() if ":" in hint else "Se calcula al guardar", "text", hint="Automático")
    if label.lower()=="estado" and not hint: return field(label, "Activo", "select", ["Activo","Inactivo"])
    if label.lower()=="sede" or label.lower().startswith("sede"): return field(label, "Quito", "select", ["Quito","Valle de los Chillos","Ambato","Cuenca"] if "(s)" not in label else ["Quito","Valle de los Chillos","Ambato","Cuenca","Todas"])
    if "fecha" in low or "vigencia" in low: return field(label, "", "date", hint=hint)
    if label.lower().startswith("hora "): return field(label, "", "time")
    if "email" in low or "correo" in low: return field(label, "nombre@ejemplo.com", "email", hint=hint)
    if "teléfono" in low: return field(label, "099 000 0000", "tel")
    if "archivo" in low or "comprobante" in label.lower(): return field(label, "", "file", hint=hint if "archivo" not in hl else "")
    if any(k in low for k in ("monto","precio","cantidad","horas","cupo","tarifa","%","días de","umbral","aulas")) and "horario" not in low: return field(label, "0", "number", hint=hint)
    if label.lower().startswith(("observación","motivo","condición","columnas","descripción")): return field(label, hint or "Escribe aquí…", "textarea")
    return field(label, hint, "text")
def form(fields, cols=2, title="", extra=""):
    out="".join(direccion_fields() if f=="@@DIR@@" else _auto_field(f) for f in fields)
    grid=f'<div class="form-grid cols-{cols}">{out}</div>'
    if title or extra: return card(title, grid+extra)
    return grid

def kpi(label, value, sub="", tone=0, fset=None, href=None):
    """Un ítem de la franja de resumen. Si el detalle pide acción (vencida, rechazada…) se marca con punto rojo o ámbar.
    fset='Columna=Valor' lo vuelve un botón que aplica ese filtro a la tabla; href lo vuelve enlace."""
    low=str(sub).lower(); tone_cls=" is-bad" if any(w in low for w in ("vencid","rechaz","sin contactar","negativo","bloque","riesgo")) else (" is-warn" if any(w in low for w in ("por vencer","pendiente","sin enviar","por validar")) else "")
    inner=f'<span class="sum-label">{label}</span><span class="sum-value">{value}</span>{f"<span class=\'sum-sub{tone_cls}\'>{sub}</span>" if sub else ""}'
    if fset: return f'<button type="button" class="sum-item" data-fset="{fset}" aria-pressed="false">{inner}</button>'
    if href: return f'<a class="sum-item" href="{href}">{inner}</a>'
    return f'<div class="sum-item">{inner}</div>'
def kpis(items):
    """Franja de resumen: cifras en línea separadas por filetes (reemplaza la fila de tarjetas KPI)."""
    out=""
    for it in items:
        it=list(it); kw={}
        if len(it)>3 and isinstance(it[3],dict): kw=it.pop(3)
        out+=kpi(*it[:3],**kw)
    return f'<div class="summary" data-fgroup>{out}</div>'

def sel(label, options, w="160px", col=None):
    i=_nid(); fc="" if col is False else f' data-fcol="{col or label}"'
    return f'<label class="field" style="width:{w}">{label}<select id="{i}"{fc} class="ctl">{"".join(f"<option>{o}</option>" for o in options)}</select></label>'
def search(label, placeholder, w="280px"):
    i=_nid(); return f'<label class="field" style="width:{w}">{label}<input id="{i}" type="search" data-fcol="*" placeholder="{placeholder}" class="ctl"></label>'
def dates(label="Rango de fechas", a="2026-10-01", b="2026-10-31"):
    i=_nid(); return f'<div class="field"><label for="{i}">{label}</label><div style="display:flex;gap:6px;align-items:center"><input id="{i}" type="date" value="{a}" class="ctl" style="width:150px"><span>a</span><input type="date" value="{b}" aria-label="Hasta" class="ctl" style="width:150px"></div></div>'
def filters(*ctrls, actions="", show=3):
    """Buscador + hasta 2 selectores visibles; el resto en el popover 'Filtros'. Debajo, chips de filtros activos."""
    ctrls=[c for c in ctrls if c]
    main="".join(ctrls[:show]); more=ctrls[show:]
    i=_nid()
    extra=(f'<button type="button" class="btn btn-more" data-menu aria-expanded="false" aria-controls="{i}">Filtros ({len(more)})<span class="cnt"></span></button>' if more else "")
    hidden=(f'<div id="{i}" class="filters-more menu-pop" hidden>{"".join(more)}</div>' if more else "")
    acts=f'<div class="filters-actions">{split_actions(actions,2)}</div>' if actions else ''
    return f'<div class="wf-filters filters">{main}{extra}{hidden}{acts}<div class="chips-active" aria-live="polite"></div></div>'

def note(text, kind="info"):
    return ""  # las notas explicativas se quitaron del mockup a pedido del cliente; la explicación vive en docs/
def kv(*pairs):
    return '<div class="kv">'+"".join(f'<span><span class="k">{k}</span> <b>{v}</b></span>' for k,v in pairs)+'</div>'
def badge(text, kind="neutral"):
    """Estado = punto + texto en color semántico. Las etiquetas de alcance llevan fondo (tag)."""
    if str(text).startswith(("Propuesta","Requerimiento")): return f'<span class="tag tag-warn">{text}</span>'
    return f'<span class="badge badge-{kind}">{text}</span>'
def count(n):
    return f'<span class="count">{n}</span>'
def progress(pct, label="", color=None):
    return f'<div class="prog"><div class="prog-head"><span>{label}</span><b>{pct}%</b></div><div class="prog-track"><div class="prog-fill" style="width:{pct}%;background:{color or NAVY}"></div></div></div>'
def hbars(items, unit=""):
    mx=max(v for _,v in items) or 1
    return '<div class="hbars">'+"".join(f'<div class="hbar"><span>{l}</span><div class="hbar-track"><div class="hbar-fill" style="width:{v/mx*100:.0f}%"></div></div><b>{unit}{v:,}{"%" if unit=="" and mx<=100 else ""}</b></div>' for l,v in items)+'</div>'
def vbars(groups, series, h=150):
    mx=max(v for _,vs in groups for v in vs) or 1
    g="".join('<div class="vgroup"><div class="vbars-stack" style="height:%dpx">'%h+"".join(f'<div class="vbar" title="{series[i]}: {v}" style="height:{v/mx*h:.0f}px;background:{CH[i%4]}"><span>{v}</span></div>' for i,v in enumerate(vs))+f'</div><span class="vlabel">{l}</span></div>' for l,vs in groups)
    leg="".join(f'<span class="leg"><i style="background:{CH[i%4]}"></i>{n}</span>' for i,n in enumerate(series)) if len(series)>1 else ""
    return f'<div class="chart"><div class="vbars">{g}</div>{f"<div class=legend>{leg}</div>" if leg else ""}</div>'
def linechart(labels, series, h=160):
    W=600; mx=max(v for vs in series.values() for v in vs) or 1; n=len(labels); xs=[40+i*(W-60)/(n-1) for i in range(n)]
    paths="".join(f'<polyline fill="none" stroke="{CH[k%4]}" stroke-width="2.5" stroke-linejoin="round" points="{" ".join(f"{xs[i]:.0f},{h-20-(v/mx)*(h-40):.0f}" for i,v in enumerate(vs))}"/>' for k,(name,vs) in enumerate(series.items()))
    axis="".join(f'<text x="{xs[i]:.0f}" y="{h-4}" font-size="12" text-anchor="middle" fill="{MUTE}">{l}</text>' for i,l in enumerate(labels))
    grid="".join(f'<line x1="40" x2="{W-20}" y1="{h-20-(h-40)*f:.0f}" y2="{h-20-(h-40)*f:.0f}" stroke="{LINE}"/><text x="36" y="{h-16-(h-40)*f:.0f}" font-size="12" text-anchor="end" fill="{MUTE}">{mx*f:.0f}</text>' for f in (0,.5,1))
    leg="".join(f'<span class="leg"><i style="background:{CH[k%4]};height:3px"></i>{n}</span>' for k,n in enumerate(series))
    return f'<div class="chart"><svg viewBox="0 0 {W} {h}" style="width:100%;height:auto" role="img" aria-label="Gráfico de líneas">{grid}{paths}{axis}</svg><div class="legend">{leg}</div></div>'
def areachart(labels, values, h=150, color=None, unit="%"):
    """Una serie con relleno suave, como el gráfico de tendencia de la referencia."""
    W=600; c=color or CH[0]; mx=max(values) or 1; n=len(labels); xs=[36+i*(W-56)/(n-1) for i in range(n)]
    pts=[(xs[i], h-24-(v/mx)*(h-44)) for i,v in enumerate(values)]
    line=" ".join(f"{x:.0f},{y:.0f}" for x,y in pts); area=f"{pts[0][0]:.0f},{h-24} "+line+f" {pts[-1][0]:.0f},{h-24}"
    gid=_nid()
    axis="".join(f'<text x="{xs[i]:.0f}" y="{h-6}" font-size="12" text-anchor="middle" fill="{MUTE}">{l}</text>' for i,l in enumerate(labels))
    grid="".join(f'<line x1="36" x2="{W-20}" y1="{h-24-(h-44)*f:.0f}" y2="{h-24-(h-44)*f:.0f}" stroke="{LINE}"/><text x="32" y="{h-20-(h-44)*f:.0f}" font-size="12" text-anchor="end" fill="{MUTE}">{mx*f:.0f}{unit}</text>' for f in (0,.5,1))
    last=pts[-1]
    return f'<svg viewBox="0 0 {W} {h}" style="width:100%;height:auto" role="img" aria-label="Tendencia">{grid}<polygon points="{area}" fill="{c}" fill-opacity=".08"/><polyline fill="none" stroke="{c}" stroke-width="2.5" stroke-linejoin="round" points="{line}"/><circle cx="{last[0]:.0f}" cy="{last[1]:.0f}" r="5" fill="{c}" stroke="#fff" stroke-width="2"/>{axis}</svg>'
def stackbars(labels, series, h=170, unit="h"):
    """Barras apiladas por día (series: dict nombre -> lista), como 'Learning activity' de la referencia."""
    names=list(series); tot=[sum(series[n][i] for n in names) for i in range(len(labels))]; mx=max(tot) or 1
    cols=""
    for i,l in enumerate(labels):
        segs="".join(f'<div title="{n}: {series[n][i]}{unit}" style="height:{series[n][i]/mx*h:.0f}px;background:{CH[k%4]}"></div>' for k,n in enumerate(names) if series[n][i])
        cols+=f'<div class="vgroup"><div class="sbar" style="height:{h}px"><div class="sbar-track"></div><div class="sbar-fill">{segs}</div></div><span class="vlabel">{l}</span></div>'
    leg="".join(f'<span class="leg"><i style="background:{CH[k%4]}"></i>{n}</span>' for k,n in enumerate(names))
    ticks="".join(f'<span>{mx*f:g}{unit}</span>' for f in (1,.75,.5,.25,0))
    return f'<div class="chart"><div class="vbars axed"><div class="yaxis">{ticks}</div>{cols}</div><div class="legend">{leg}</div></div>'
def gauge(pct, label="", color=None, segments=False):
    """Medidor semicircular (0–100). segments=True pinta la escala en 4 colores como la referencia."""
    import math
    r=52; cx=70; cy=70; v=min(pct,100)
    def pt(p):
        a=math.pi*(1-p); return cx+r*math.cos(a), cy-r*math.sin(a)
    def arc(p0,p1,col,w=12):
        x0,y0=pt(p0); x1,y1=pt(p1)
        return f'<path d="M{x0:.1f},{y0:.1f} A52,52 0 0 1 {x1:.1f},{y1:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'
    if segments:
        cols=["#16A34A","#F6C21C","#F59E0B","#D62839"]; base="".join(arc(i*0.25+0.01,(i+1)*0.25-0.01,c) for i,c in enumerate(cols))
        x,y=pt(v/100); needle=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="#fff" stroke="{INK}" stroke-width="3"/>'
        return f'<div class="gauge"><svg viewBox="0 0 140 84" style="width:170px;height:auto" role="img" aria-label="{label} {pct}%">{base}{needle}<text x="70" y="64" text-anchor="middle" font-size="22" font-weight="600" fill="{INK}">{pct}%</text></svg><span class="kpi-sub">{label}</span></div>'
    c=color or CH[0]
    return f'<div class="gauge"><svg viewBox="0 0 140 84" style="width:160px;height:auto" role="img" aria-label="{label} {pct}%">{arc(0,1,LINE)}{arc(0,max(v,1)/100,c)}<text x="70" y="66" text-anchor="middle" font-size="22" font-weight="600" fill="{INK}">{pct}%</text></svg><span class="kpi-sub">{label}</span></div>'
def ring(pct, color=None, size=44):
    import math
    c=color or CH[0]; r=16; circ=2*math.pi*r
    return f'<svg viewBox="0 0 40 40" width="{size}" height="{size}" role="img" aria-label="{pct}%"><circle cx="20" cy="20" r="{r}" fill="none" stroke="{LINE}" stroke-width="5"/><circle cx="20" cy="20" r="{r}" fill="none" stroke="{c}" stroke-width="5" stroke-linecap="round" stroke-dasharray="{circ*pct/100:.1f} {circ:.1f}" transform="rotate(-90 20 20)"/><text x="20" y="24" text-anchor="middle" font-size="10" font-weight="700" fill="{INK}">{pct}%</text></svg>'
def avatar(initials, size="lg"):
    return f'<span class="avatar {size}">{initials}</span>'
def funnel(stages):
    mx=stages[0][1]; out=""
    for i,(l,v) in enumerate(stages):
        conv=f' · {v/stages[i-1][1]*100:.0f}% del paso anterior' if i else ''
        out+=f'<div class="funnel-row"><div class="funnel-bar" style="width:{v/mx*100:.0f}%;background:{CH[0]}">{v:,}</div><span>{l}{conv}</span></div>'
    return f'<div class="funnel">{out}</div>'
def stacked(parts):
    bar="".join(f'<div title="{l} {p}%" style="width:{p}%;background:{CH[i%4]}"></div>' for i,(l,p) in enumerate(parts))
    leg="".join(f'<span class="leg"><i style="background:{CH[i%4]}"></i>{l} <b>{p}%</b></span>' for i,(l,p) in enumerate(parts))
    return f'<div class="chart"><div class="stack">{bar}</div><div class="legend">{leg}</div></div>'
def upload(label, hint):
    i=_nid(); return f'<div class="upload"><label for="{i}">{label}</label><input id="{i}" type="file"><span class="kpi-sub">{hint}</span></div>'
def pager(total, per=20):
    pages="".join(f'<a href="#" aria-label="Página {n}" class="pg{" on" if n==1 else ""}">{n}</a>' for n in (1,2,3))
    return f'<div class="wf-pager pager"><span>{total} registros · {per} por página<span class="wf-shown"></span></span><span class="pages">{pages}<a href="#" aria-label="Siguiente" class="pg"><span class="chev"></span></a></span></div>'
def logo():
    return '<div class="brand brand-dark"><img src="assets/logo.webp" alt="Cambridge School of Languages" style="width:240px"></div>'
def flow(steps, horizontal=None):
    """Pasos de proceso numerados (línea vertical estilo GOV.UK). Cada paso: texto o (título, detalle, estado, 'done'|'now'|'')."""
    h=len(steps)<=3 if horizontal is None else horizontal
    lis=""
    for st in steps:
        t,d,e,k=(st+("","","",""))[:4] if isinstance(st,tuple) else (st,"","","")
        lis+=f'<li{f" class=is-{k}" if k else ""}><span class="p-t">{t}</span>{f"<span class=p-s>{e}</span>" if e else ""}{f"<span class=p-d>{d}</span>" if d else ""}</li>'
    return f'<ol class="proc{" proc-h" if h else ""}">{lis}</ol>'
def row(*cells, gap=16):
    return f'<div class="row" style="gap:{gap}px">'+"".join(cells)+'</div>'
def foot(*buttons):
    """Pie de formulario fijo abajo: acción principal primero, luego secundarias."""
    return '<div class="form-foot">'+"".join(buttons)+'</div>'
def two(a,b, ratio="1fr 1fr"):
    a=f'<div class="g-cell">{a}</div>'; b=f'<div class="g-cell">{b}</div>'
    if ratio=="1fr 1fr": return f'<div class="grid grid-2">{a}{b}</div>'
    return f'<div class="grid grid-r" style="--cols:{ratio}">{a}{b}</div>'
def card(title, inner, extra=""):
    head=f'<div class="card-head"><h2>{title}</h2>{extra}</div>' if (title or extra) else ""
    return f'<section class="card">{head}{inner}</section>'
def hero(pairs, actions="", extra="", tag=""):
    """Cabecera de página de detalle: tarjeta con datos clave en cuadrícula, acciones a la derecha y contenido extra (p. ej. progreso)."""
    facts="".join(f'<div class="fact"><dt>{k}</dt><dd>{v}</dd></div>' for k,v in pairs)
    top=f'<div class="hero-top"><div class="hero-tag">{tag}</div><div class="hero-actions">{split_actions(actions,2)}</div></div>' if (tag or actions) else ""
    return f'<section class="card hero">{top}<dl class="facts">{facts}</dl>{extra}</section>'
def li(items):
    return '<ul class="list">'+"".join(f"<li>{i}</li>" for i in items)+'</ul>'
def course_item(name, meta, pct, status, grade, cert, href="DetalleMatricula.html", tone=0, sessions="", hours=""):
    """Fila de curso matriculado: ícono tintado, nombre, meta, sesiones/horas, anillo, estado, nota, certificado."""
    tints=["var(--tint-navy)","var(--tint-red)","var(--tint-sky)","var(--tint-yellow)"]; inks=[NAVY,RED,"#1B6FA8","#B45309"]
    g=grade.split("/") if "/" in grade else [grade,""]
    return (f'<div class="course"><span class="course-ico" style="background:{tints[tone%4]};color:{inks[tone%4]}"><svg viewBox="0 0 24 24">{SVG["book"]}</svg></span>'
            f'<div class="course-name"><a href="{href}">{name}</a><small>{meta}</small></div>'
            f'<div class="course-meta"><span><svg viewBox="0 0 24 24">{SVG["play"]}</svg>{sessions}</span><span><svg viewBox="0 0 24 24">{SVG["clock"]}</svg>{hours}</span></div>'
            f'{ring(pct,inks[tone%4])}<span class="course-state">{status}<small>Certificado</small>{cert}</span><span class="course-grade">{g[0].strip()}{f"<small>/{g[1].strip()}</small>" if g[1] else ""}</span></div>')
def journey(levels):
    """Ruta del programa por niveles: (nivel, módulos, % avance, detalle). El ancho de cada tramo es proporcional a sus módulos."""
    segs="".join(f'<div class="journey-seg{" done" if p==100 else " now" if p>0 else ""}" style="flex:{m}"><div class="journey-bar"><i style="width:{p}%"></i></div><b>{n}</b><small>{d}</small></div>' for n,m,p,d in levels)
    return f'<div class="journey">{segs}</div>'
CHECK='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6L9 17l-5-5"/></svg>'
def route(levels):
    """Ruta de niveles del programa: (nivel, módulos, estado done|now|paid|todo, detalle, % del nivel actual)."""
    lab={"done":"Aprobado","now":"Estás aquí","paid":"Pagado","todo":"Por comprar"}
    lis=""
    for n,m,st,d,*pc in levels:
        pct=pc[0] if pc else (100 if st=="done" else 0)
        bar=f'<span class="r-bar" aria-hidden="true"><i style="width:{pct if st in ("now","done") else 0}%"></i></span>'
        name=f'<span class="r-name">{CHECK if st=="done" else ""}{n}</span>'
        here='<span class="r-here">Estás aquí</span>' if st=="now" else ('<span class="r-here r-paid">Pagado</span>' if st=="paid" else f'<span class="sr">{lab[st]}</span>')
        lis+=f'<li class="is-{st}" style="flex:{m}">{bar}{name}{here}<span class="r-det">{d}</span></li>'
    return f'<ol class="route" aria-label="Ruta de niveles del programa">{lis}</ol>'
def wizard(steps, summary="", saved="Borrador guardado 10:14"):
    """Asistente de pasos: steps=[(título, html, subtítulo)]. Un paso visible a la vez (JS en page()), stepper con barra de progreso y resumen lateral."""
    lis="".join(f'<li><button type="button"><span class="s-n">{i+1}</span><span class="s-t">{t}</span></button></li>' for i,(t,_,_) in enumerate(steps))
    secs="".join(f'<section class="wiz-step" data-title="{t}" aria-labelledby="wz{i}"><h3 id="wz{i}">Paso {i+1} · {t}{f"<small>{sub}</small>" if sub else ""}</h3>{h}</section>' for i,(t,h,sub) in enumerate(steps))
    return (f'<div class="wizard" data-wizard><div class="wiz-main"><div class="wiz-head"><ol class="stepper" aria-label="Pasos">{lis}</ol>'
            f'<div class="wiz-mobile"><b></b><button type="button" class="btn btn-ghost wiz-toggle" aria-expanded="false">Ver pasos</button></div>'
            f'<div class="wiz-progress" aria-hidden="true"><i></i></div>{f"<p class=wiz-saved>{saved}</p>" if saved else ""}</div>{secs}</div>{summary}</div>')
def wiz_summary(title_total, rows, extra=""):
    """Resumen lateral del asistente: rows=[(etiqueta, valor)] con '---' para separador y '*' al inicio para el total."""
    body=""
    for r in rows:
        if r=="---": body+="<hr>"; continue
        k,v=r; tot=k.startswith("*")
        body+=f'<dl{" class=tot" if tot else ""}><dt>{k.lstrip("*")}</dt><dd>{v}</dd></dl>'
    return f'<details class="wiz-summary" open><summary>Resumen<span>{title_total}</span></summary><div class="wiz-sum-body">{body}{extra}</div></details>'
def wizcard(steps_html, summary=""):
    """Convierte step()+step()… en un asistente de pasos (un paso a la vez)."""
    parts=steps_html.split('<div class="step"><span class="step-n">')[1:]
    out=[]
    for p_ in parts:
        body=p_.split('<div class="step-body"><h3>',1)[1]
        head,inner=body.split('</h3>',1)
        inner=inner[:-len('</div></div>')]
        m=re.match(r'(.*?)<small>(.*)</small>$',head,re.S)
        t,sub=(m.group(1),m.group(2)) if m else (head,"")
        out.append((t.strip(),inner,sub))
    return wizard(out, summary)
def facts(pairs):
    """Resumen en cuadrícula (etiqueta arriba, valor abajo), igual que la cabecera de detalle. Para confirmaciones y resúmenes."""
    return '<dl class="facts">'+"".join(f'<div class="fact"><dt>{k}</dt><dd>{v}</dd></div>' for k,v in pairs)+'</dl>'
_LID=[0]
def ledger_calc(items, disc=10, lid=None):
    """Tabla de valores con descuento recalculable (JS en page()). items=(concepto, detalle, valor, aplica_descuento).
    El selector de descuento se crea con disc_field(lid). Los elementos con data-total-for=lid / data-disc-for=lid se actualizan solos."""
    if lid is None: _LID[0]+=1; lid=f"lg{_LID[0]}"
    rows=""; tot=0; dsc=0
    for c,d,v,ok in items:
        dv=round(v*disc/100) if ok else 0; tot+=v-dv; dsc+=dv
        rows+=(f'<div>{c}<small>{d}</small></div><div class="n">${v:,}</div><div class="n ld"{" data-dc" if ok else ""}>{f"{disc}%" if ok and disc else "—"}</div><div class="n" data-sub data-v="{v}">${v-dv:,}</div>')
    return (f'<div class="ledger" data-ledger="{lid}"><div class="lh">Concepto</div><div class="lh n">Valor</div><div class="lh n ld">Dcto.</div><div class="lh n">Subtotal</div>{rows}'
            f'<div class="lt">Total</div><div class="lt n"></div><div class="lt n ld" data-ldisc>{f"-${dsc:,}" if dsc else "—"}</div><div class="lt n" data-ltotal>${tot:,}</div></div>')
def disc_field(lid, value=10, limit=10):
    """Selector de porcentaje de descuento ligado a un ledger_calc; por encima del límite del asesor avisa que pasa a aprobación."""
    _FID[0]+=1; i=f"f{_FID[0]}"
    opts=[(0,"0% · sin descuento"),(5,"5%"),(10,f"10% · tu límite sin aprobación"),(15,"15% · pasa a aprobación de Dirección Comercial"),(20,"20% · pasa a aprobación de Dirección Comercial")]
    o="".join(f'<option value="{p}"{" selected" if p==value else ""}>{t}</option>' for p,t in opts)
    return f'<div class="field"><label for="{i}">Descuento sobre el curso</label><select id="{i}" class="ctl" data-disc="{lid}" data-limit="{limit}">{o}</select><small class="field-hint" data-disc-hint>Los valores de la tabla y el total se recalculan al cambiar</small></div>'
def addmod_btn(label="Agregar otro módulo"):
    """Botón que agrega una fila de módulo al último grupo del paso (sin diálogo)."""
    return f'<button type="button" class="btn" data-addmod>{label}</button>'
def mod_row(n, nivel, prog, prog_sub, code, code_sub, fecha, estado):
    return f'<div class="mod"><div class="m-n"><b>Módulo {n}</b><small>Nivel {nivel}</small></div><div>{prog}<small>{prog_sub}</small></div><div><span class="mono">{code}</span><small>{code_sub}</small></div><div>{fecha}<small>inicia</small></div><div>{estado}</div></div>'
def tasks(items, title="Qué tengo pendiente hoy"):
    """Lista de tareas con estado (estilo Task list de GOV.UK): (título, detalle, estado, href)."""
    lis="".join(f'<li><span><a href="{h}">{t}</a><small>{d}</small></span>{e}<a href="{h}" class="row-go" aria-label="Abrir: {t}"><span class="chev" aria-hidden="true"></span></a></li>' for t,d,e,h in items)
    return f'<section aria-label="{title}"><h2 class="section-title" style="margin:0 0 12px">{title}</h2><ul class="tasks">{lis}</ul></section>'
def step(n, title, inner, sub=""):
    return f'<div class="step"><span class="step-n">{n}</span><div class="step-body"><h3>{title}{f"<small>{sub}</small>" if sub else ""}</h3>{inner}</div></div>'
# ================= FIN TEMA =================

# 1 Login
login=f'''<div class="auth">
<form>
  {logo()}
  <h1 style="margin:0;font-size:22px">Ingresar</h1>
  <label for="email">Correo</label>
  <input id="email" type="email" placeholder="nombre@cambridge.edu.ec" class="ctl">
  <label for="pass">Contraseña</label>
  <input id="pass" type="password" placeholder="••••••••" class="ctl">
  {btn("Ingresar","Home.html",True)}
  <a href="RecuperarContrasena.html" style="font-size:13px;text-align:center">Olvidé mi contraseña</a>
  <a href="VerificarCertificado.html" style="font-size:12px;text-align:center">Verificar un certificado</a>
  <p style="margin:0;font-size:12px;color:{MUTE};text-align:center">Un solo ingreso: según tu usuario entras al panel del equipo o al portal del estudiante · 2FA opcional</p>
  <a href="PortalEstudiante.html" style="font-size:12px;text-align:center;color:{MUTE}">Demo: ver qué ve un estudiante al ingresar</a>
</form>
</div>'''
page("Main.html","Login",login,"Login")
# 1b Portal del estudiante (propuesta fuera del alcance contractual)
portal_route=route([("A1",2,"done","módulos 1–2 · nota 80 · certificado"),("A2",4,"done","módulos 3–6 · nota 85 · certificado"),("B1",2,"now","módulos 7–8 · 60% del nivel",60),("B1+",2,"paid","módulos 9–10"),("B2",4,"todo","módulos 11–14"),("C1",2,"todo","módulos 15–16")])
portal=f'''<div class="portal">
<header class="portal-top"><a href="PortalEstudiante.html"><img src="assets/logo.webp" alt="Cambridge School of Languages"></a><div class="portal-title"><b>Portal del estudiante</b><small>{badge("Propuesta · fuera del alcance del contrato actual")}</small></div>
 <div class="portal-user">{avatar("MA","sm")}<span>Hola, María<small>EST-00412 · Quito</small></span><a href="Main.html" class="btn btn-ghost">Cerrar sesión</a></div></header>
<main class="portal-main">
 <section class="card" aria-labelledby="mi-progreso">
  <div class="prog-top">
   <div>
    <h2 id="mi-progreso" class="section-title">Mi progreso general</h2>
    <div class="prog-who"><span class="level-big">B1</span><span><b>English for Adults (ESL)</b><br><span class="p-prog">módulo 7 de 16 · 41% del programa</span></span></div>
    {portal_route}
    <div class="stat-line"><div><span>Horas cursadas</span><b>130 h</b></div><div><span>Asistencia general</span><b>92%</b></div><div><span>Promedio</span><b>83 / 100</b></div><div><span>Certificados</span><b>2</b></div></div>
   </div>
   <aside class="next-class" aria-label="Próxima clase"><span class="sum-label">Próxima clase</span><span class="nc-when">Hoy 19:00</span><span>Zoom 2 · P. Gómez · B1 módulo 7</span>{btn("Unirse a la clase",None,True)}</aside>
  </div>
 </section>
 <section class="card" aria-labelledby="mi-curso">
  <div class="card-head"><h2 id="mi-curso">Mi curso actual</h2>{btn("Escribir a mi asesor")}</div>
  <dl class="facts"><div class="fact"><dt>Curso</dt><dd>English for Adults B1 Virtual</dd></div><div class="fact"><dt>Horario</dt><dd>Lu-Ma-Mi-Ju 19:00–21:00</dd></div><div class="fact"><dt>Profesor</dt><dd>P. Gómez</dd></div><div class="fact"><dt>Módulo</dt><dd>7 de 16 · nivel B1</dd></div><div class="fact"><dt>Asesor</dt><dd>Carla M. · 099 000 0010</dd></div></dl>
  {progress(60,"Avance del nivel B1 · 22 de 36 h · termina el 20 nov")}
  {kpis([("Asistencia del curso","90%","mínimo 75% para el certificado"),("Puntaje","84 / 100","participación, quiz y examen")])}
 </section>
 {tabs(["Mis cursos","Asistencia","Notas y certificados","Pagos y facturas","Mis datos"],"Mis cursos",panels={
  "Mis cursos": card("Mi siguiente módulo",
     '<p style="margin:0"><b>Módulo 8</b> · inicia 3 nov · mismo grupo <span class="mono">0001-2026-0767</span> · P. Gómez</p>'
     +'<ul class="checklist"><li>'+CHECK+'Avance en el Muro: 100% del módulo 7</li><li>'+CHECK+'Nota 8.4 / 10 (mínimo 7)</li><li>'+CHECK+'Pago incluido en tu compra de los módulos 7 a 10</li></ul>'
     +row(btn("Confirmar mi cupo",None,True)))
   +card("Rematrícula · cuando termines lo que compraste",
     flow([("Aprobar el módulo 10","el último que compraste","Pendiente","now"),("Elegir horario","","Aún no disponible"),("Pagar en línea o subir el comprobante","","Aún no disponible"),("Secretaría confirma","","Aún no disponible"),("Entrar al grupo y a Teams","","Aún no disponible")],horizontal=False)
     +'<fieldset class="opts" disabled><legend class="sr">Horarios para B2 · módulo 11</legend>'
     +'<label class="opt"><input type="radio" name="hor" disabled><span><b>Virtual · Lu-Ma-Mi-Ju 19:00 a 21:00</b><small>Inicia mar 2027 · 6 cupos · $250 por módulo</small></span></label>'
     +'<label class="opt"><input type="radio" name="hor" disabled><span><b>Presencial Quito · Sábados 09:00 a 13:00</b><small>Inicia mar 2027 · 3 cupos · $250 por módulo</small></span></label></fieldset>'
     +row(btn("Rematricularme",disabled_reason="Se activa al aprobar el módulo 10")))
   +card("Próximos cursos", table(["Curso","Inicia","Profesor","Horario","Estado"],[[c2("English for Adults (ESL) · Virtual · Grupal · B1 módulo 8","0001-2026-0767"),"3 nov 2026","P. Gómez","Lu-Ma-Mi-Ju 19:00–21:00",badge("Confirma tu cupo","warn")],[c2("English for Adults (ESL) · Presencial · Grupal · B1+ módulos 9–10","sábados · Quito"),"9 ene 2027","L. Vega","Sa 09:00–13:00",badge("Pagado · cupo reservado","navy")],[c2("English for Adults (ESL) · Virtual · Grupal · B2 módulos 11–14","por abrir"),"mar 2027","por asignar","—",badge("Rematrícula al terminar B1+","neutral")]],wide=0))
   +card("Cursos", course_item("English for Adults (ESL) · Virtual · Grupal · B1","módulo 7 · P. Gómez",60,badge("En curso","warn"),"84 / 100",badge("Pendiente"),href="PortalEstudiante.html",tone=0,sessions="18",hours="36 h")
     +course_item("English for Adults A2","Adults · A2 · módulos 3–6 · L. Vega",100,badge("Completado","ok"),"85 / 100",badge("A2.pdf","navy"),href="PortalEstudiante.html",tone=2,sessions="36",hours="72 h")
     +course_item("English for Adults A1","Adults · A1 · módulos 1–2 · L. Vega",100,badge("Completado","ok"),"80 / 100",badge("A1.pdf","navy"),href="PortalEstudiante.html",tone=3,sessions="18",hours="36 h")
     +course_item("English for Adults B2 · por abrir","Adults · B2 · módulos 11–14 · inicia mar 2027",0,badge("Pendiente"),"—",badge("Ninguno"),href="PortalEstudiante.html",tone=1,sessions="0",hours="0 h")),
  "Asistencia": two(card("Esta semana", stackbars(["Lu","Ma","Mi","Ju","Vi","Sa","Do"],{"Clase":[2,2,2,2,0,0,0],"Moodle":[0.5,0,0.5,0,1,0,0]},h=160)),
     card("Últimas sesiones", row(btn("Justificar ausencia"),btn("Pedir reposición"))+table(["Sesión","Fecha","Asistí"],[["Sesión 11 · módulo 7","Mié 7 oct · 19:00",badge("Sí","ok")],["Sesión 10 · módulo 7","Mar 6 oct · 19:00",badge("Sí","ok")],["Sesión 9 · módulo 7","Lun 5 oct · 19:00",badge("No · aviso previo","warn")],["Sesión 8 · módulo 7","Jue 1 oct · 19:00",badge("Sí","ok")],["Sesión 7 · módulo 7","Mié 30 sep · 19:00",badge("Sí","ok")]])+kv(("Asistencia del curso","90%"),("Mínimo para certificado","75%")))),
  "Notas y certificados": two(card("Puntaje actual · B1", '<div class="perf">'+gauge(84,"Puntaje total",segments=True)+'<div class="perf-legend"><div><i style="background:#16A34A"></i>Participación<b>55%</b></div><div><i style="background:#F6C21C"></i>Quiz en clase<b>15%</b></div><div><i style="background:#F59E0B"></i>Examen<b>10%</b></div><div><i style="background:#D62839"></i>Ausencias<b>10%</b></div></div></div>'),
     card("Certificados por nivel y módulo", table(["Nivel","Módulos (programa · modalidad)","Nota","Acción"],[["A2",c2("Módulos 3–6","3 y 4 presencial · 5 y 6 virtual · ESL grupal"),"85 · Pass",btn("Descargar certificado")],["A1",c2("Módulos 1–2","presencial · ESL grupal"),"80 · Pass",btn("Descargar certificado")],["B1",c2("Módulos 7–8","7 virtual (en curso) · 8 virtual"),"en curso","—"]],wide=1))),
  "Pagos y facturas": two(card("Mi compra", kv(("Saldo pendiente","$0 · todo al día"),("Módulos comprados","7 a 10 · B1 y B1+"),("En curso","módulo 7 · quedan 3 por cursar"),("Plan de pago","2 cuotas · pagadas"))+progress(25,"Compra del 28 ago · 1 de 4 módulos en curso")
     +table(["Por pagar","Vence","Monto"],[["Rematrícula B2 · módulo 11 (al confirmarla)","al rematricularte","$250.00"]])+row(btn("Pagar en línea",None,True),btn("Subir comprobante"))),
     card("Facturas", table(["Factura","Total","Acción"],[[c2("000021090","28 ago 2026 · módulos 7 a 10 · pagada"),"$980.00",btn("Descargar factura")],[c2("000020411","15 jun 2026 · A2 · pagada"),"$450.00",btn("Descargar factura")],[c2("000019872","10 ene 2026 · A1 · pagada"),"$450.00",btn("Descargar factura")]]))),
  "Mis datos": card("Datos personales", kv(("Nombres","María Andrade"),("Cédula","1712345678"),("Email","maria.andrade@ejemplo.com"),("Teléfono","099 000 0001"),("Dirección","Quito · La Carolina"),("Sede","Quito"),("Representante","— (mayor de edad)"))+row(btn("Actualizar mis datos"),btn("Cambiar contraseña"))),
 })}
</main></div>'''
page("PortalEstudiante.html","Portal del estudiante",portal,"Portal del estudiante")

# ===== Programas (estructura académica) =====
PROGRAMAS=["Cambridge Eaglets (preescolar)","English for Kids","English for Teens","English for Adults","Business English","Exam Preparation","Listening & Speaking","Spanish","Summer for Kids","Summer for Preschoolers","Summer for Teens","Tailored"]
# Programas legados de TeamDesk que aquí son programa + modalidad: "English for Adults Virtual" y "Online" → English for Adults · Virtual
AULAS=["Zoom 1 (virtual)","Zoom 2 (virtual)","Teams 1 (virtual)"]+[f"Q-{i} · Quito · {c} pers." for i,c in zip(range(1,9),[15,12,12,10,10,8,8,6])]+[f"C-{i} · Valle · {c} pers." for i,c in zip(range(1,29),[12,10,10,10,8,8,8,8,6,6,6,6,6,6,10,10,8,8,8,8,6,6,6,6,6,6,6,6])]+[f"A-{i} · Ambato · {c} pers." for i,c in zip(range(1,7),[12,10,10,8,8,6])]
PLANTILLAS=["Regular noche · Lu-Ma-Mi-Ju 19:00–21:00 · 2 h","Regular tarde · Lu-Ma-Mi-Ju 17:00–19:00 · 2 h","Regular mañana · Lu-Mi 09:00–11:00 · 2 h","Sábados intensivo · Sa 09:00–13:00 · 4 h","Kids tarde · Ma-Ju 15:00–17:00 · 2 h","Eaglets · Ma-Ju 15:00–16:00 · 1 h","Personalizado · elegir días y horas…"]
def horario_builder(dias_on=(1,2), inicio="15:00", fin="16:00", total="20"):
    """Constructor de horario personalizado: días de la semana como chips múltiples, hora inicio/fin y vista previa de sesiones."""
    dias=pills(["Lu","Ma","Mi","Ju","Vi","Sa"],list(dias_on),multi=True)
    return (f'<div class="sched" id="sched-custom"><div class="pill-row"><span>Días</span>{dias}</div>'
            +form(fields=[("Hora inicio",inicio,'time',None,True),("Hora fin",fin,'time',None,True),("Horas por sesión","1",'number',None,False,"Se calcula de inicio y fin"),("Total de horas",total,'number',None,True,"One to one: 20 o 40 h")],cols=4)
            +kv(("Vista previa","Ma · Mi · 15:00–16:00 · 1 h por sesión · 20 sesiones · del 3 nov al 20 ene · salta 2 feriados (2-3 nov)"),("Choques","ninguno con el profesor ni con el aula"))
            +row(btn("Previsualizar calendario",None,False,"Se muestran todas las sesiones en el calendario con los feriados saltados."))+'</div>')

MODALIDADES=["Virtual","Presencial"]
TIPOS_CLASE=["Grupal","One to one","One to one reducido","One to one Business"]
# Tabla canónica nivel (CEFR) ↔ módulos (confirmada con el cliente, oct 2026). 1 nivel comercial = 2 módulos de 18 h; A2 y B2 son 2 niveles comerciales.
NIVELES=[("A1","1–2"),("A2","3–6"),("B1","7–8"),("B1+","9–10"),("B2","11–14"),("C1","15–16")]
NIVEL_LIBRO={"A1":"Empower A1 Starter","A2":"Empower A2 Elementary","B1":"Empower B1 Pre-intermediate","B1+":"Empower B1+ Intermediate","B2":"Empower B2 Upper-intermediate","C1":"Empower C1 Advanced"}
NIVEL_OPC=[f"{n} · módulos {m}" for n,m in NIVELES]
NIVEL_FILTRO=["Todos"]+[n for n,_ in NIVELES]
def _nmods(m):
    a,b=m.split("–"); return int(b)-int(a)+1
def tabla_niveles():
    return table(["Nivel","Módulos","Niveles comerciales","Libro"],[[n,m,str(_nmods(m)//2),NIVEL_LIBRO[n]] for n,m in NIVELES])
def tree(items):
    def node(label, children=None, meta=""):
        kids="".join(node(*c) if isinstance(c,tuple) else node(c) for c in (children or []))
        return f'<li><div class="tree-node"><b>{label}</b>{f"<small>{meta}</small>" if meta else ""}</div>{f"<ul>{kids}</ul>" if kids else ""}</li>'
    return '<ul class="tree">'+"".join(node(*i) if isinstance(i,tuple) else node(i) for i in items)+'</ul>'
jerarquia=tree([
 ("English for Adults (ESL)",[("Virtual",[("Grupal · Lu-Ma-Mi-Ju 19:00–21:00",None,'<a href="DetalleCurso.html">0001-2026-0767 · B1</a> · 12/15'),("One to one reducido · personalizado",None,"0001-2026-0790 · B2 · 20 h · lunes 15:00–16:00")]),("Presencial",[("Grupal · Sa 09:00–13:00",None,"0001-2026-0430 · A1 · Quito Q-1 · 14/15"),("One to one Business · personalizado",None,"0001-2026-0608 · B1 · Ma-Ju 07:00–08:30")])],"16 módulos · A1–C1 · 2 h por sesión, 4 h sábados"),
 ("English for Teens",[("Virtual",[("Grupal · Lu-Ma-Mi-Ju 17:00–19:00",None,"0001-2026-0772 · B1 · por abrir")]),("Presencial",[("Grupal · Vi 15:00–19:00",None,"0001-2026-0192 · A2 · Ambato · sin profesor")])],"12 módulos · 18 h"),
 ("English for Kids",[("Presencial",[("Grupal · Sa 09:00–13:00",None,"0001-2026-0328 · Kids 2 · Valle C-3")])],"8 módulos · 16 h"),
 ("Cambridge Eaglets (preescolar)",[("Presencial",[("Grupal · Ma-Ju 15:00–16:00",None,"0001-2026-0801 · Eaglets 1 · Quito · por abrir")])],"4 módulos · 12 h · 1 h por sesión"),
 ("Exam Preparation",[("Presencial",[("Grupal · Sa 09:00–13:00",None,"0001-2026-0815 · B2 First · Quito Q-2 · 8/10")])],"preparación a exámenes Cambridge · 36 h"),
 ("Spanish",[("Virtual",[("One to one · personalizado",None,"0001-2026-0820 · Aula Internacional 1 · 20 h")])],"español para extranjeros · 4 niveles"),
 ("Summer (Kids · Preschoolers · Teens)",[("Presencial",[("Grupal · Lu-Vi 09:00–12:00 · julio",None,"0001-2026-0700 · Summer Teens · Valle")])],"programas de vacaciones · 2 semanas"),
 ("Listening & Speaking · Tailored",[("Virtual",[("One to one · personalizado",None,"0001-2026-0790 · 20 h · lunes 15:00–16:00")])],"complementarios y a medida"),
 ("Business English",[("Virtual",[("One to one Business · paquete 40 h",None,"0001-2026-0810 · Grupo Nova · Teams")]),("Presencial",[("Grupal corporativo · Ma-Ju 07:00–08:30",None,"0001-2026-0608 · Grupo Nova · Ambato")])],"a medida · B1–C1"),
])
page("Programas.html","Programas",shell("Programas, modalidades y tipos de clase","Programas",
 kpis([("Programas","12","Eaglets, Kids, Teens, Adults, Business, Exam Prep, Listening & Speaking, Spanish, Summer ×3, Tailored"),("Modalidades","2","virtual y presencial"),("Tipos de clase","4","grupal y 3 variantes one to one"),("Cursos activos",sv(41,22,12,7),"en la jerarquía de abajo")]),
 tabs(["Jerarquía","Niveles y módulos","Tipos de clase y horas","Plantillas de horario","Feriados","Microsoft Teams"],"Jerarquía",panels={
  "Niveles y módulos": two(card("Nivel ↔ módulos · English for Adults (ESL)", tabla_niveles()),
     card("Regla", kv(("1 nivel comercial","2 módulos de 18 h"),("A2 y B2","4 módulos cada uno · se venden como 2 niveles"),("Programa completo","16 módulos · A1 a C1"),("Se vende y factura","por módulo (una matrícula por módulo, factura multi-módulo)"),("Certificado","al aprobar todos los módulos del nivel con nota ≥ 7"))+row(btn("Nuevo nivel","NuevoNivel.html")))),
  "Jerarquía": card("Programa → Modalidad → Tipo de clase → Curso", jerarquia+row(btn("Nuevo curso","NuevoCurso.html",True),btn("Nuevo nivel","NuevoNivel.html")),extra='<small class="card-hint">La misma jerarquía se refleja en la matrícula, las notas y los certificados</small>'),
  "Tipos de clase y horas": two(card("Tipos de clase", table(["Tipo","Horas por sesión","Duración","Precio"],[[c2("Grupal","Lunes a jueves · 6 a 15 estudiantes"),"2 h","18 h por módulo · 9 sesiones","Por nivel · catálogo"],[c2("Grupal sábados","Intensivo · 6 a 15 estudiantes"),"4 h","18 h por módulo · 4.5 sábados","Por nivel · catálogo"],[c2("One to one","1 estudiante · mismo contenido que el grupo"),"1 a 2 h","Paquete de 20 o 40 h","$18 / h"],[c2("One to one reducido","1 estudiante · menos horas que el grupo"),"1 h","Paquete de 20 h","$18 / h"],[c2("One to one Business","Ejecutivos y empresas · contenido a medida"),"1 a 2 h","Paquete de 20 o 40 h","$24 / h · factura a empresa"],[c2("Preescolar","4 a 5 años · 1 h por sesión"),"1 h","12 h por módulo","Por nivel · catálogo"]],wide=0)),
     card("Reglas", kv(("Horas por sesión","las define el tipo de clase; el curso solo elige la plantilla de horario"),("Fin del curso","se calcula: total de horas ÷ horas por sesión, saltando feriados"),("One to one","se vende como paquete de 20 o 40 h; el horario se arma a medida con el estudiante"),("Business","siempre factura a la empresa y aparece en la vista B2B"))+row(btn("Editar tipos de clase","Configuracion.html")))),
  "Plantillas de horario": two(card("Plantillas estándar", table(["Plantilla","Días","Hora","Horas por sesión","Usada en"],[["Regular tarde","Lu-Ma-Mi-Ju","17:00–19:00","2 h","9 cursos"],["Regular noche","Lu-Ma-Mi-Ju","19:00–21:00","2 h","14 cursos"],["Regular mañana","Lu-Mi","09:00–11:00","2 h","4 cursos"],["Sábados intensivo","Sa","09:00–13:00","4 h","8 cursos"],["Kids tarde","Ma-Ju","15:00–17:00","2 h","6 cursos"],["Preescolar","Ma-Ju","15:00–16:00","1 h","1 curso"]])+row(btn("Nueva plantilla",None,False,"Se crea una plantilla de horario reutilizable en nuevos cursos."))),
     card("Horario personalizado (one to one)", kv(("Ejemplo","Paquete de 20 h · solo lunes 15:00–16:00 · 20 semanas"),("Cómo se arma","se eligen días y horas con el estudiante; el sistema calcula las sesiones y la fecha de fin saltando feriados"),("Validación","no choca con otra clase del profesor ni con el aula"))+form(fields=[("Paquete","20 h",'select',["20 h","40 h"]),("Días","Lunes",'select',["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Varios…"]),("Hora","15:00",'time'),("Horas por sesión","1",'number'),"Fecha inicio","Fecha fin (calculada: 20 sesiones · salta feriados)"])+row(btn("Previsualizar calendario",None,False,"Se muestran las 20 sesiones en el calendario con los feriados saltados.")))),
  "Feriados": two(card("Calendario de feriados 2026 · Ecuador", table(["Fecha","Feriado","Origen","Aplica a"],[["1 ene","Año Nuevo","Ecuador · automático","Todas las sedes"],["16–17 feb","Carnaval","Ecuador · automático","Todas las sedes"],["3 abr","Viernes Santo","Ecuador · automático","Todas las sedes"],["1 may","Día del Trabajo","Ecuador · automático","Todas las sedes"],["24 may","Batalla de Pichincha","Ecuador · automático","Todas las sedes"],["10 ago","Primer Grito de Independencia","Ecuador · automático","Todas las sedes"],["9 oct","Independencia de Guayaquil","Ecuador · automático","Todas las sedes"],["2–3 nov","Difuntos e Independencia de Cuenca","Ecuador · automático","Todas las sedes"],["6 dic","Fundación de Quito","Local · configurado","Quito y Valle"],["25 dic","Navidad","Ecuador · automático","Todas las sedes"],["26 nov","Thanksgiving","EE. UU. · configurado","Cursos Business · Grupo Nova"]])),
     card("Cómo funciona", kv(("Automático","los feriados nacionales de Ecuador se cargan cada año desde el calendario oficial"),("Configurable","se agregan feriados locales o de otro país (p. ej. EE. UU. para clientes corporativos) por sede o por curso"),("Efecto","las sesiones que caen en feriado se saltan y la fecha de fin del curso se recalcula; el profesor y los estudiantes reciben el aviso"))+form(fields=[("Calendario","Ecuador",'select',["Ecuador","Estados Unidos","Personalizado"]),("Fecha","",'date'),("Nombre del feriado","Ej. Fiestas de Ambato"),("Aplica a","Todas las sedes",'select',["Todas las sedes","Quito","Valle","Ambato","Un curso específico"])])+row(btn("Agregar feriado",None,True,"El feriado queda en el calendario y los cursos afectados recalculan sus sesiones y fecha de fin.")))),
  "Microsoft Teams": card("Grupos de Teams vinculados a cursos", table(["Curso","Equipo de Teams","Profesor","Estudiantes","Estado"],[[c2("English for Adults B1 Virtual","0001-2026-0767 · Quito"),"CSL-2026-0767-B1","P. Gómez","12 / 12 sincronizados",badge("Vinculado","ok")],[c2("English for Teens B1 Virtual","0001-2026-0772 · Valle · por abrir"),"CSL-2026-0772-B1","—","6 / 6",badge("Sin profesor","bad")],[c2("Business · Grupo Nova","0001-2026-0810 · one to one Business"),"CSL-2026-0810-BUS","L. Vega","1 / 1",badge("Vinculado","ok")],[c2("English for Adults A2","0001-2026-0620 · Valle · presencial"),"—","P. Gómez","—",badge("No aplica · presencial","neutral")]],wide=0)+kv(("Al crear un curso virtual","se crea el equipo de Teams y se agregan profesor y estudiantes automáticamente"),("Al matricular","el estudiante entra al equipo; al retirarse, sale"),("Alerta","grupos de Teams sin profesor o estudiantes sin grupo aparecen en el dashboard"))+row(btn("Vincular equipo existente",None,False,"Se elige un equipo de Teams ya creado y se asocia al curso; se sincronizan profesor y estudiantes."),btn("Ver integración","Integraciones.html"))),
 }),
 subtitle="La estructura académica: programas, modalidades, tipos de clase, horarios, feriados y Teams"),"Programas y modalidades")

# ===== Leads (Kommo → matrícula) =====
VL='<a href="MatriculaLead.html">Matricular</a>'
def stages(head, items):
    """Franja de etapas de un embudo: (nombre, conteo, tasa, color, valor de filtro). Clic = filtra la tabla por Etapa."""
    st="".join(f'<button type="button" class="stage" data-fset="Etapa={fv}" aria-pressed="false" style="--sc:{c}"><span class="st-name"><i aria-hidden="true"></i>{n}</span><span class="st-count">{k}</span><span class="st-rate">{r}</span></button>' for n,k,r,c,fv in items)
    return f'<section class="stages" data-fgroup aria-label="Etapas del embudo"><div class="stages-head">{head}</div>{st}</section>'
page("Leads.html","Leads",shell("Leads y conversión","Leads",
 stages(f'<b>{sv(310,180,80,50,0)} leads del mes</b><span class="sync-ok">Sincronizado con Kommo hace 3 min</span><span style="margin-left:auto">'+btn("Sincronizar con Kommo",None,False,"Se traen los leads nuevos y cambios de etapa desde Kommo (API).",kind="ghost")+'</span>',[
   ("Nuevo",sv(23,12,7,4,0),"sin contactar · 2 con más de 24 h","var(--info)","Nuevo"),
   ("Contactado",sv(115,66,30,19,0),"74% de los leads","var(--info)","Contactado"),
   ("Cotizado",sv(120,70,30,20,0),"39% de los leads cotiza","var(--warn)","Cotizado"),
   ("Matriculado",sv(52,28,15,9,0),"17% matricula · meta 20%","var(--ok)","Ganado"),
   ("Perdido",sv(31,18,8,5,0),"precio y horario, las causas más comunes","var(--mute)","Perdido")]),
 filters(search("Buscar","Nombre, teléfono o correo",w="240px"),sel("Etapa",["Todas","Nuevo","Contactado","Cotizado","Ganado","Perdido"],w="150px"),sel("Asesor",["Todos","Carla M.","Diego R.","Sofía L."],w="150px"),sel("Origen",["Todos","Instagram","Web","Referido","Empresa","Walk-in"],w="140px"),actions='<span class="result-count" aria-live="polite"></span>'+btn("Exportar"))
 +table(["Lead","Sede","Origen","Interés","Asesor","Etapa","Último contacto","Acción"],[
  [c2("Andrea Villacís","099 000 0101 · a.villacis@ejemplo.com"),"Quito","Instagram","Adults · virtual · grupal","Carla M.",badge("Cotizado","info"),"Hoy 10:20",VL],
  [c2("Grupo Nova · RR. HH.","empresa · 8 ejecutivos"),"Ambato","Empresa","Business · one to one","Sofía L.",badge("Cotizado","info"),"Ayer",'<a href="DetalleEmpresa.html">Ver empresa</a>'],
  [c2("Martín Espinosa","099 000 0102"),"Valle","Web","Teens · presencial","Diego R.",badge("Contactado","navy"),"Ayer","—"],
  [c2("Lucía Paredes","099 000 0103"),"Quito","Referido · María Andrade","Adults · presencial sábados","Carla M.",badge("Nuevo","info"),badge("Sin contactar · 2 días","bad"),"—"],
  [c2("Familia Rojas (Kids)","099 000 0104"),"Ambato","Instagram","Kids · presencial","Sofía L.",badge("Nuevo","info"),badge("Sin contactar · 1 día","warn"),"—"],
  [c2("Sebastián Toro","099 000 0105"),"Quito","Web","Preescolar","Carla M.",badge("Ganado","ok"),"Matriculado 10 oct",'<a href="Ficha360.html">Ver ficha</a>'],
  [c2("Paula Cárdenas","099 000 0106"),"Valle","Referido","Adults · virtual","Diego R.",badge("Perdido","neutral"),"Precio · 05 oct","—"]],sede=1,hide=(1,),wide=0)+pager(sv(310,180,80,50)),
 subtitle="Cómo un lead de Kommo se convierte en matrícula, y dónde se queda en el camino",
 actions=btn("Registrar walk-in",None,True)),"Leads y conversión (Kommo)")

# ===== B2B / grupos empresariales =====
page("Empresas.html","Empresas",shell("Empresas y grupos B2B","Empresas",
 kpis([("Empresas activas",sv(6,3,1,2),"con convenio vigente"),("Estudiantes corporativos",sv(43,20,6,17),"en 9 cursos"),("Facturado B2B del mes",sv("$6,420","$2,900","$720","$2,800"),"15% del total"),("Por cobrar a empresas",sv("$2,400","$1,200","$0","$1,200"),"2 facturas a 30 días")]),
 filters(search("Buscar","Empresa o RUC",w="240px"),sel("Estado",["Todos","Activo","Por renovar","Inactivo"],w="130px"),actions=btn("Nueva empresa","NuevaEmpresa.html")+btn("Exportar PDF"))
 +ltable("empresas",["Empresa","Sede","Convenio","Estudiantes","Cursos","Facturación","Estado","Acción"],[
  [c2("Grupo Nova","RUC 1790012345001 · contacto RR. HH."),"Ambato","15% · factura a la empresa · 30 días","17","3 · Business one to one y grupal","$2,800 / mes",badge("Activo","ok"),'<a href="DetalleEmpresa.html">Ver grupo</a>'],
  [c2("Banco del Valle","RUC 1790098765001"),"Quito","10% · factura al empleado","12","2 · Adults virtual","$1,900 / mes",badge("Activo","ok"),'<a href="DetalleEmpresa.html">Ver grupo</a>'],
  [c2("Colegio Los Andes","convenio institucional"),"Valle","20% · Kids y Teens","6","1 · Teens presencial","$720 / mes",badge("Por renovar · dic","warn"),'<a href="DetalleEmpresa.html">Ver grupo</a>'],
  [c2("Clínica Santa Fe","RUC 1790055555001"),"Quito","10% · factura a la empresa","8","2 · Adults sábados","$1,000 / mes",badge("Activo","ok"),'<a href="DetalleEmpresa.html">Ver grupo</a>']],sede=1,hide=(1,),wide=0),
 seg(["Grupo Nova","Banco del Valle","Colegio Los Andes","Clínica Santa Fe"],[
   two(card("Grupo Nova · consolidado", kv(("Estudiantes","17 · 14 activos · 3 terminaron"),("Asistencia promedio","91%"),("Aprobación","12 de 12 módulos cerrados"),("Rematrícula","9 de 12 que terminaron (75%)"),("Saldo","$1,200 · factura 000021102 · vence 11 nov"))+hbars([("Business one to one · L. Vega",8),("Business grupal · Ma-Ju 07:00",6),("Adults B2 virtual",3)],unit="")+row(btn("Exportar PDF"),btn("Enviar estado de cuenta"),btn("Ver grupo","DetalleEmpresa.html"))),
       card("Convenio", kv(("Descuento","15% sobre el course fee"),("Factura","a la empresa · crédito 30 días"),("Contacto","RR. HH. · rrhh@gruponova.ejemplo.com"),("Vigencia","ene – dic 2026"),("Reporte mensual","asistencia, avance y aprobación por persona · se envía el 1 de cada mes")))),
   two(card("Banco del Valle · consolidado", kv(("Estudiantes","12 · 12 activos"),("Asistencia promedio","87%"),("Aprobación","8 de 9 módulos cerrados"),("Rematrícula","6 de 8 que terminaron (75%)"),("Saldo","$0 · factura al empleado"))+hbars([("Adults B1 virtual · Lu-Ju 19:00",7),("Adults A2 virtual · Ma-Ju 20:00",5)],unit="")+row(btn("Exportar PDF"),btn("Enviar estado de cuenta"),btn("Ver grupo","DetalleEmpresa.html"))),
       card("Convenio", kv(("Descuento","10% sobre el course fee"),("Factura","al empleado · la empresa no paga"),("Contacto","Talento Humano · th@bancodelvalle.ejemplo.com"),("Vigencia","mar 2026 – feb 2027"),("Reporte mensual","solo asistencia y avance; sin datos de pago")))),
   two(card("Colegio Los Andes · consolidado", kv(("Estudiantes","6 · 6 activos"),("Asistencia promedio","94%"),("Aprobación","3 de 3 módulos cerrados"),("Rematrícula","5 de 6 (83%)"),("Saldo","$720 · factura 000021110 · vence 30 oct"))+hbars([("Teens A2 presencial · Vi 15:00",6)],unit="")+row(btn("Exportar PDF"),btn("Enviar estado de cuenta"),btn("Ver grupo","DetalleEmpresa.html"))),
       card("Convenio", kv(("Descuento","20% · Kids y Teens"),("Factura","a la institución · crédito 15 días"),("Contacto","Vicerrectorado"),("Vigencia",badge("Por renovar · vence dic 2026","warn")),("Reporte mensual","asistencia y notas por estudiante al tutor")))),
   two(card("Clínica Santa Fe · consolidado", kv(("Estudiantes","8 · 7 activos · 1 congelado"),("Asistencia promedio","82%"),("Aprobación","4 de 5 módulos cerrados"),("Rematrícula","3 de 4 (75%)"),("Saldo","$1,000 · factura 000021108 · vence 20 nov"))+hbars([("Adults A1 sábados · Sa 09:00",5),("Adults B1 sábados · Sa 09:00",3)],unit="")+row(btn("Exportar PDF"),btn("Enviar estado de cuenta"),btn("Ver grupo","DetalleEmpresa.html"))),
       card("Convenio", kv(("Descuento","10% sobre el course fee"),("Factura","a la empresa · crédito 30 días"),("Contacto","Administración · admin@clinicasantafe.ejemplo.com"),("Vigencia","jul 2026 – jun 2027"),("Alerta",badge("1 estudiante congelado · regresa en enero","warn")))))],label="Empresa")
 +card("Qué resuelve", li(["Ver a todos los estudiantes de una empresa juntos, aunque estén en cursos y sedes distintas","Facturar a la empresa o al empleado según el convenio","Reporte mensual para RR. HH.: asistencia, avance y aprobación por persona","Alertas: convenio por vencer, saldo de la empresa, estudiantes sin grupo"])),
 subtitle="Vista consolidada por empresa: estudiantes, cursos, facturación y convenio"),"Empresas y grupos B2B")

# Detalle de empresa B2B (Ver grupo) y alta de empresa con convenio (Configuración → Empresas y convenios)
page("DetalleEmpresa.html","Detalle de empresa",shell("Grupo Nova","Empresas",
 hero([("RUC","1790012345001"),("Sede","Ambato"),("Convenio","15% · todos los programas"),("Factura a","la empresa · crédito 30 días"),("Contacto","RR. HH. · rrhh@gruponova.ejemplo"),("Vigencia","hasta dic 2027")],
   btn("Exportar PDF")+btn("Enviar estado de cuenta")+btn("Matricular empleado","NuevaVenta.html",True),
   tag='<span class="hero-code">B2B</span>'+badge("Activo","ok")+badge("Ambato","navy")),
 kpis([("Estudiantes","17","14 activos · 3 terminaron"),("Asistencia promedio","91%","meta 85%"),("Aprobación","12 de 12","módulos cerrados"),("Saldo de la empresa","$1,200","factura 000021102 · vence 11 nov")]),
 card("Estudiantes del grupo", filters(search("Buscar","Nombre o curso",w="220px"),sel("Estado",["Todos","En curso","Terminó"],w="140px"))
  +table(["Estudiante","Curso","Profesor","Asistencia","Estado","Acción"],[
   [c2('<a href="Ficha360.html">Ricardo Almeida</a>',"Gerente comercial"),c2("Business · one to one","0001-2026-0810 · Teams · 40 h"),"L. Vega","96%",badge("En curso","ok"),'<a href="Ficha360.html">Ver ficha</a>'],
   [c2('<a href="Ficha360.html">Carolina Benítez</a>',"Jefa de finanzas"),c2("Business grupal","0001-2026-0608 · Ma-Ju 07:00–08:30"),"M. Castro","90%",badge("En curso","ok"),'<a href="Ficha360.html">Ver ficha</a>'],
   [c2('<a href="Ficha360.html">Jorge Paredes</a>',"Analista"),c2("Business grupal","0001-2026-0608 · Ma-Ju 07:00–08:30"),"M. Castro","88%",badge("En curso","ok"),'<a href="Ficha360.html">Ver ficha</a>'],
   [c2('<a href="Ficha360.html">Natalia Cruz</a>',"Coordinadora de logística"),c2("Adults B2 Virtual · módulo 11","0001-2026-0790 · one to one reducido · lunes 15:00"),"L. Vega","92%",badge("En curso","ok"),'<a href="Ficha360.html">Ver ficha</a>'],
   [c2('<a href="Ficha360.html">Esteban Vaca</a>',"Supervisor de planta"),c2("Business grupal","0001-2026-0608 · Ma-Ju 07:00–08:30"),"M. Castro","72%",badge("Riesgo asistencia","bad"),'<a href="Ficha360.html">Ver ficha</a>'],
   [c2('<a href="Ficha360.html">Paola Ruiz</a>',"Asistente de gerencia"),c2("Adults B1+ · módulo 10","terminó en sep · nota 8.6"),"P. Gómez","94%",badge("Terminó","neutral"),'<a href="Ficha360.html">Ver ficha</a>']],wide=0)),
 two(card("Facturación a la empresa", table(["Factura","Concepto","Total","Estado","Acción"],[[c2("000021102","12 oct · crédito 30 días"),"Octubre · 14 estudiantes","$1,200.00",badge("Por vencer · 11 nov","warn"),'<a href="DetalleFactura.html">Ver</a>'],[c2("000021088","sin estudiantes asignados"),"Business one to one · paquete 40 h","$1,200.00",badge("Sin vincular","bad"),'<a href="Facturas.html">Vincular</a>'],[c2("000021041","12 sep"),"Septiembre · 15 estudiantes","$1,600.00",badge("Pagada","ok"),'<a href="DetalleFactura.html">Ver</a>']],wide=0)),
     card("Reporte mensual para RR. HH.", kv(("Incluye","asistencia, avance y aprobación por persona"),("Se envía","el día 1 de cada mes a rrhh@gruponova.ejemplo"),("Alertas","1 estudiante con asistencia < 75%"),("Convenio","se renueva en dic 2027 · aviso 60 días antes"))+row(btn("Exportar PDF"),btn("Editar convenio","NuevaEmpresa.html")))),
 two(card("Condiciones comerciales e historial", table(["Desde","Programa contratado","Condición"],[["ene 2026","Business grupal · Ambato","15% · factura a la empresa · 30 días"],["mar 2026","One to one Business · 40 h","precio especial $22/h"],["sep 2026","Adults virtual para empleados","10% · factura al empleado"]])),
     card("Ventas, facturación y pagos por período", filters(sel("Período",["Este año","Este mes","2025"],w="130px",col=False))+kv(("Vendido","$14,400 · servicios educativos"),("Facturado","$15,100"),("Cobrado","$13,900"),("Pendiente","$1,200"))+row(btn("Ver detalle")))),
 subtitle="Todos los estudiantes de la empresa juntos, aunque estén en cursos y sedes distintas"),"Detalle de empresa B2B")

page("NuevaEmpresa.html","Nueva empresa",shell("Nueva empresa y convenio","Empresas",
 form(title="Datos de la empresa", fields=[("Razón social","Ej. Clínica Santa Fe S.A.",'text',None,True),("RUC","",'text',None,True,"13 dígitos · se valida en el SRI"),("Dirección fiscal","",'text',None,True,"Para la factura electrónica"),("Sede que la atiende","Quito",'select',["Quito","Valle","Ambato"],True),("Contacto de RR. HH.","",'text',None,True),("Email de RR. HH.","",'email',None,True,"Recibe el reporte mensual"),("Teléfono","",'tel')]),
 form(title="Convenio", fields=[("Descuento del convenio (%)","10",'number',None,True,"Se aplica como motivo 'Convenio empresa' en la matrícula"),("¿Quién paga?","La empresa",'select',["La empresa","El empleado"],True,"Define a quién se emite la factura"),("Crédito","30 días",'select',["Contado","15 días","30 días"],True),("Programas incluidos","Todos",'select',["Todos","Adults (ESL)","Business English","Kids y Teens"],True),("Vigencia desde","",'date',None,True),("Vigencia hasta","",'date',None,True,"Aviso automático 60 días antes"),("Convenio firmado","",'file',None,True,"PDF firmado por ambas partes")]),
 foot(btn("Guardar empresa",None,True,"La empresa y su convenio quedan activos: aparecen en '¿Paga la empresa?' y 'Facturar a' de Nueva matrícula, y en la vista B2B. "+AUDIT,"DetalleEmpresa.html",save="empresas"),btn("Cancelar","Empresas.html")),
 subtitle="El convenio se ofrece en la matrícula y alimenta la vista B2B"),"Nueva empresa y convenio")

# ===== Tienda en línea (WooCommerce) · pedidos, SLA, incidencias =====
WOO="https://cambridgesol.edu.ec/tienda-virtual-cambridge-sol/"
VPED='<a href="DetallePedido.html">Ver</a>'
pedidos_tbl=table(["Pedido","Sede","Cliente","Producto","Pago (Nuvei)","Recibido","Etapa","SLA","Acción"],[
 [c2("#WC-10482","hoy 09:12 · tienda en línea"),"Quito",c2("Lorena Paz","099 000 0201 · l.paz@ejemplo.com"),"Mock Test Internacional · B2","$45.00 · aprobado","hace 2 h","Por validar",badge("Validar antes de 13:12","warn"),VPED],
 [c2("#WC-10481","hoy 08:40"),"Valle",c2("Grupo Nova · RR. HH.","empresa · 3 traducciones"),"Traducción · 12 páginas","$180.00 · aprobado","hace 3 h","Validado · registrar factura",badge("Contactar antes de mañana 08:40","warn"),VPED],
 [c2("#WC-10479","ayer 17:05"),"Quito",c2("Esteban Ruiz","099 000 0203"),"TOEFL ITP","$60.00 · aprobado","hace 20 h","Contactado · agendado",badge("Al día","ok"),VPED],
 [c2("#WC-10477","ayer 11:30"),"Ambato",c2("Daniela Cruz","099 000 0204"),"SIELE Global","$155.00 · aprobado","hace 26 h","Facturado · servicio en gestión",badge("Al día","ok"),VPED],
 [c2("#WC-10475","20 oct"),"Quito",c2("Marco Vinueza","099 000 0205"),"Mock Test Internacional · C1","$45.00 · rechazado en Nuvei","3 días","Cancelado · llamar para recuperar",badge("Recuperación pendiente","bad"),VPED],
 [c2("#WC-10474","20 oct"),"Valle",c2("Sin datos de contacto","pedido abandonado en checkout"),"Traducción · 3 páginas","sin pago","3 días","Abandonado",badge("Sin datos · no recuperable","neutral"),"—"],
 [c2("#WC-10470","19 oct"),"Quito",c2("Ana Lucía Torres","099 000 0207"),"Mock Test Internacional · B1","$45.00 · aprobado","4 días","Incidencia · pedido duplicado",badge("Resolver antes de 48 h","bad"),VPED],
 [c2("#WC-10466","17 oct"),"Ambato",c2("Jorge Salazar","099 000 0208"),"Traducción · 4 páginas","$60.00 · aprobado","6 días","Entregado",badge("Cerrado · 2 días laborables","ok"),VPED]],sede=1,hide=(1,),wide=0)
plantillas_correo=table(["Producto","Asunto del correo","Qué explica","Acción"],[
 [c2("Mock Test Internacional","Cambridge · presencial"),"Confirmación de proceso para tu Mock Test Internacional","Pago → contacto en 24 h → fecha con 15 días de anticipación → respaldo de inscripción → horarios 3 días antes (disponibilidad todo el día)",btn("Enviar correo informativo")],
 [c2("Traducciones","PDF por correo"),"Confirmación de proceso de entrega de traducción","Hasta 4 páginas: 3 días laborables; más de 5 páginas: proporcional; urgentes con recargo; adjuntar documento a infoquito@…",btn("Enviar correo informativo")],
 [c2("SIELE y TOEFL ITP","presenciales en el instituto"),"Confirmación de proceso para tu examen internacional","Inscripción con 15 días de anticipación · horarios flexibles · TOEFL: certificado físico en 1 semana · SIELE: certificado digital, validez 5 años",btn("Enviar correo informativo")]],wide=0)
incidencias_tbl=table(["Incidencia","Pedido","Tipo","Reportada","Plazo (48 h)","Estado","Acción"],[
 [c2("INC-031","Ana Lucía Torres pagó dos veces el mismo Mock Test"),"#WC-10470","Duplicación de pedido","19 oct 10:20",badge("Vencido · 2 días","bad"),"Notificada a Dir. Administrativa",btn("Resolver incidencia")],
 [c2("INC-030","Pago aprobado en Nuvei pero el pedido quedó 'Pendiente' en WooCommerce"),"#WC-10468","Pago no se registra","18 oct 15:00",badge("Resuelta en 6 h","ok"),"Cerrada",'<a href="Pedidos.html">Ver</a>'],
 [c2("INC-029","Cliente no responde a WhatsApp, correo ni llamada"),"#WC-10461","Cliente no responde","16 oct",badge("Resuelta · 3 intentos","ok"),"Cerrada · reembolso",'<a href="Pedidos.html">Ver</a>'],
 [c2("INC-028","Precio del TOEFL en la tienda distinto al catálogo"),"#WC-10455","Error en precio","14 oct",badge("Resuelta en 20 h","ok"),"Cerrada · precio corregido",'<a href="Pedidos.html">Ver</a>']],wide=0)
page("DetallePedido.html","Detalle pedido",shell("Pedido #WC-10482 · Mock Test Internacional B2","Tienda en línea",
 hero([("Cliente","Lorena Paz · 099 000 0201 · l.paz@ejemplo.com"),("Producto","Mock Test Internacional · B2"),("Pago","$45.00 · aprobado en Nuvei · 09:12"),("Recibido","hoy 09:12 · tienda en línea"),("Sede","Quito"),("Asignado a","Secretaría Académica Quito")],
  btn("Validar pedido",None,True)+btn("Marcar contactado")+more_menu(btn("Enviar correo informativo")+btn("Registrar incidencia")+btn("Llamar para recuperar venta")+btn("Abrir en WooCommerce",WOO)),
  tag='<span class="hero-code">#WC-10482</span>'+badge("Por validar · vence 13:12","warn")+badge("Quito","navy")),
 two(card("Seguimiento del pedido", flow([("Recepción automática","WooCommerce crea el pedido y avisa por correo a Secretaría Académica","máx. 4 h laborales para revisar","done"),("Validación","Pago aprobado en Nuvei (sin rechazo), datos del cliente, producto, correo y teléfono; estado Pagado/Completado","máx. 12 h","done"),("Registro interno","La factura se registra en la plataforma (hoy TeamDesk) según el proceso de ingreso de facturas","","now"),("Contacto con el cliente","WhatsApp, correo o llamada: explicar pasos y agendar el servicio","máx. 24 h",""),("Gestión del servicio","Según el producto: Mock Test, traducción, SIELE/TOEFL o derivación a Books and Bits","",""),("Cierre y seguimiento","Entrega del servicio; reporte semanal a Dirección Administrativa","","")])+kv(("Etapa actual","Validación · lleva 2 h de las 12 h"),("Siguiente","contacto con el cliente antes de mañana 09:12"))),
     card("Historial", table(["Cuándo","Quién","Qué pasó"],[["hoy 09:12","WooCommerce","Pedido creado · pago aprobado en Nuvei (lote 44812)"],["hoy 09:13","Sistema","Correo de aviso a Secretaría Académica Quito"],["hoy 09:20","Secretaría","Pedido abierto · revisión iniciada"],["—","—","Pendiente: validar datos y registrar factura"]],wide=2)
       +kv(("Correo automático al cliente","Confirmación de proceso para tu Mock Test Internacional · enviado 09:12"),("Factura","por registrar al validar")))),
 subtitle="Cada pedido tiene su propio seguimiento con los plazos del procedimiento (4 h, 12 h, 24 h)"),"Detalle de pedido de la tienda en línea")
page("Pedidos.html","Tienda en línea",shell("Tienda en línea · pedidos WooCommerce","Tienda en línea",
 kpis([("Pedidos de la semana",sv(23,12,6,5),"tienda cambridgesol.edu.ec"),("Tiempo promedio de contacto",sv("9 h","7 h","11 h","12 h"),"meta < 24 h"),("Sin gestionar",sv(2,1,1,0),"1 por validar · 1 por contactar"),("Cancelados / abandonados",sv("2 · 8.7%","1","1","0"),"meta < 5% · 1 para recuperar"),("Atendidos correctamente",sv("96%","100%","92%","100%"),"meta 99%")]),
 tabs(["Pedidos","Incidencias","Correos al cliente","Certificaciones internacionales","Control semanal"],"Pedidos",counts={"Pedidos":8,"Incidencias":4},panels={
  "Pedidos": filters(search("Buscar","Nº de pedido, cliente o producto",w="260px"),sel("Etapa",["Todas","Por validar","Validado · registrar factura","Contactado · agendado","Facturado · servicio en gestión","Entregado","Cancelado · llamar para recuperar","Abandonado","Incidencia · pedido duplicado"],w="220px"),sel("Producto",["Todos","Mock Test Internacional","Traducción","TOEFL ITP","SIELE Global"],w="180px",col="Producto"),dates(),actions='<span class="result-count" aria-live="polite"></span>'+btn("Sincronizar pedidos",None,False,"Se traen los pedidos nuevos y cambios de estado de WooCommerce y el resultado del pago en Nuvei."))
   +pedidos_tbl+pager(sv(23,12,6,5))
   +two(card("Pedido #WC-10482 · qué sigue", kv(("Cliente","Lorena Paz · 099 000 0201 · l.paz@ejemplo.com"),("Producto","Mock Test Internacional · B2 · $45.00"),("Pago","Aprobado en Nuvei · 09:12 · sin rechazo"),("Recibido","hoy 09:12 · revisar antes de 13:12"),("Asignado a","Secretaría Académica Quito"))+flow([("Validar pedido","pago, datos, producto","","now"),("Registrar factura","","",""),("Contactar y agendar","antes de mañana 09:12","",""),("Enviar correo informativo","plantilla Mock Test","","")])+row(btn("Validar pedido",None,True),btn("Registrar factura","Facturas.html"),btn("Marcar contactado"),btn("Enviar correo informativo"),btn("Registrar incidencia"))),
        card("Pedidos cancelados · recuperar la venta", kv(("Regla","si hay datos del cliente, llamar para conocer el inconveniente e intentar recuperar la venta"),("Hoy","1 cancelado con datos (Marco Vinueza · pago rechazado en Nuvei)"),("Guion","confirmar el rechazo, ofrecer transferencia o pago en sede, registrar el resultado"))+row(btn("Llamar para recuperar venta",None,True),btn("Marcar como perdido",None,False,"El pedido queda como perdido con el motivo registrado; cuenta en el indicador de abandonados.")))),
  "Incidencias": filters(sel("Tipo",["Todos","Pago no se registra","Cliente no responde","Error en producto","Error en precio","Duplicación de pedido"],w="200px"),sel("Estado",["Todos","Abierta","Vencida","Cerrada"],w="130px",col=False),actions=btn("Registrar incidencia",None,True))+incidencias_tbl+kv(("Regla","toda incidencia se registra, se notifica a Dirección Administrativa y se resuelve en máximo 48 h")),
  "Correos al cliente": plantillas_correo+kv(("Firma","Secretaría Académica · infoquito@cambridgesol.edu.ec · Secretarías Quito, Valle de los Chillos y Ambato"),("Cuándo","al validar el pedido; el correo queda registrado en el historial del cliente")),
  "Certificaciones internacionales": card("Cambridge, Oxford y Anglia · se compran en Books and Bits", kv(("Dónde","exams.booksandbits.ec/csol (URL exclusiva para Cambridge)"),("Quién gestiona","Books and Bits: transacción, información, citas y todo lo del servicio"),("Qué recibimos","correo de confirmación por cada registro y un cierre diario de registros"),("En la plataforma","los registros del cierre diario se cargan como candidatos en Exámenes internacionales"))+row(btn("Abrir Books and Bits","https://exams.booksandbits.ec/csol",True),btn("Ver candidatos","ExamenesInternacionales.html"),btn("Cargar cierre diario",None,False,"Se carga el correo de cierre diario de Books and Bits y se crean o actualizan los candidatos en Exámenes internacionales."))),
  "Control semanal": two(card("Semana 20–24 oct", kv(("Pedidos","23"),("Tiempo promedio de respuesta","9 h (meta < 24 h)"),("Sin gestionar","2"),("Cancelados","2 · 1 recuperable"),("Incidencias abiertas","1 vencida"))+row(btn("Enviar reporte a Dirección Administrativa",None,True),btn("Exportar PDF"))),
     card("Indicadores", hbars([("Contacto en menos de 24 h",96),("Atendidos correctamente (meta 99%)",96),("Abandonados (meta < 5%)",9),("Conversión tienda (visitas → pedido)",3)],unit=""))),
 }),
 actions=btn("Abrir la tienda (WooCommerce)",WOO,True)+btn("Ver en Books and Bits","https://exams.booksandbits.ec/csol"),
 subtitle="Procedimiento de pedidos de la tienda virtual: validación, registro, contacto en 24 h, servicio, incidencias y reporte semanal"),"Tienda en línea · pedidos WooCommerce")

# 2 Home
home=shell("Inicio","Inicio",
 only("ADM,GER,DIR,SUC", tasks([("Aprobar descuento de 42% · Gabriela Núñez","pedido por Carla M. ayer · supera el límite de 10%",badge("Espera tu decisión","warn"),"Aprobaciones.html"),("Revisar la payment sheet de octubre","3 alertas: diferencia de $26 y una factura sin sesiones",badge("Pendiente","warn"),"PaymentSheet.html"),("Cobrar $12,450 en matrículas con saldo","el 60% en 4 cursos que terminan en noviembre",badge("Por vencer","warn"),"Facturas.html"),("Ambato sin matrículas nuevas hace 2 semanas","2 cursos por abrir con menos de 5 inscritos",badge("Requiere acción","bad"),"Cursos.html")]))+
 only("SEC", tasks([("Confirmar 2 rematrículas","Sofía Herrera reportó una transferencia desde el portal",badge("Pendiente","warn"),"Facturas.html"),("Corregir la factura 000021095","rechazada por el SRI: cédula del cliente inválida",badge("Rechazada SRI","bad"),"Facturas.html"),("Llamar por 2 cuotas vencidas","$725 en cartera · Pedro Mora y Gabriela Núñez",badge("Vencida","bad"),"Facturas.html"),("Pedir 3 libros con stock negativo","el correo de las 07:00 ya salió",badge("Stock negativo","bad"),"Inventario.html")]))+
 only("ASE", tasks([("Contactar 5 leads de Kommo","2 llevan más de 3 días sin respuesta",badge("Sin contactar","bad"),"Leads.html"),("Seguir tu solicitud de descuento de 42%","Gabriela Núñez · espera a Dirección Comercial",badge("En revisión","info"),"SolicitudDescuento.html"),("Llamar a 4 estudiantes con saldo vencido","$1,420 en total",badge("Vencida","bad"),"Facturas.html")]))+
 only("COO,PRO", tasks([("Confirmar 3 sesiones de esta semana","2 de P. Gómez · Teens A2 lleva 2 días",badge("Pendiente","warn"),"Sesiones.html"),("Calificar Adults A1 Sábados","terminó hace 5 días · 14 estudiantes esperan su certificado",badge("Requiere acción","bad"),"CalificarCurso.html"),("Asignar profesor a Teens B1 Virtual","abre en 2 semanas · P. Gómez tiene horario libre",badge("Sin profesor","warn"),"Cursos.html")]))+
 only("SEC", kpis([("Estudiantes activos",sv(812,420,230,162),"en tu sede"),("Rematrículas por confirmar",sv(2,1,1,0),"pago reportado desde el portal"),("Cobrado hoy",sv("$3,160","$1,420","$980","$760"),"15 pagos · caja abierta"),("Facturas sin autorizar",sv(2,2,0,0),"1 rechazada por el SRI")]))+
 only("ADM,GER,DIR,SUC", kpis([("Estudiantes activos",sv(812,420,230,162),"+3% vs mes anterior"),("Ventas del mes (niveles)",sv(76,40,22,14),"meta 70"),("Matrículas con saldo",sv("$12,450","$6,200","$4,100","$2,150"),sv("31 matrículas","15 matrículas","10 matrículas","6 matrículas")),("Aprobaciones pendientes",sv(3,2,1,0),"la más antigua: ayer")]))+
 only("COO,PRO", kpis([("Cursos en curso",sv(41,22,12,7),"esta semana"),("Sesiones por confirmar",sv(3,1,1,1),"de esta semana"),("Terminados sin calificar",sv(2,1,1,0),"bloquean certificados"),("Estudiantes en riesgo",sv(14,6,5,3),"asistencia < 75%")]))+
 only("ASE", kpis([("Mis matrículas del mes",sv(14,14,0,0),"meta 12 · 117%"),("Mis leads Kommo",sv(23,23,0,0),"5 sin contactar"),("Mis matrículas con saldo",sv("$1,420","$1,420","$0","$0"),"4 estudiantes"),("Comisión estimada",sv("$443","$443","$0","$0"),"meta cumplida · ver cálculo")])),
 only("ADM,GER,DIR,SUC", two(card("Matrículas por mes (niveles vendidos)", areachart(["May","Jun","Jul","Ago","Sep","Oct"],[58,61,55,64,70,76],h=150,unit="")), card("Mix del mes", stacked([("Adults",58),("Teens",24),("Kids",18)])+stacked([("Presencial",63),("Virtual",37)])+'<div class="gauges">'+gauge(71,"Cobrado del mes")+gauge(82,"Ocupación de cursos",CH[2])+gauge(109,"Meta de niveles",CH[3])+'</div>'))) ,
 two(only("ADM,GER,DIR,SUC", card("Pendientes de aprobación", li(["Descuento 42% · Gabriela Núñez · Carla M.","Tarifa de profesor fuera de tabla · coordinación","Asignación profesor sin contrato activo"])+row(btn("Ir a aprobaciones","Aprobaciones.html"))))
     +only("COO", card("Pendientes de aprobación", li(["Tarifa de profesor fuera de tabla · coordinación","Asignación profesor sin contrato activo"])+row(btn("Ir a aprobaciones","Aprobaciones.html"))))
     +only("SEC", card("Pendientes de secretaría", li(['<a href="Facturas.html">2 rematrículas por confirmar · Sofía Herrera reportó transferencia</a>','<a href="Facturas.html">Factura 000021095 rechazada por el SRI · cédula inválida</a>','<a href="Facturas.html">Cartera vencida: 2 cuotas · $725</a>','<a href="Inventario.html">3 libros con stock negativo · correo de las 07:00 enviado</a>'])+row(btn("Ir a facturación","Facturas.html"))))
     +only("ASE", card("Mis pendientes", li(['<a href="SolicitudDescuento.html">Solicitud de descuento 42% · Gabriela Núñez · esperando a Dir. Comercial</a>',"4 matrículas con saldo vencido · llamar esta semana","Lead Kommo sin contactar: 5"])+row(btn("Ver estudiantes","Estudiantes.html"))))
     +only("PRO", card("Mis clases de hoy", li(["Adults A2 · 14:00–16:00 · Valle C-5 · 9 estudiantes","B1 Virtual · 19:00–21:00 · Zoom 2 · 12 estudiantes"])+row(btn("Registrar sesión",None,True),btn("Ver mis cursos","Cursos.html")))),
     card("Accesos rápidos", row(only(COMERCIAL,btn("Nueva matrícula",None,True),True),only("ADM,GER,DIR,SUC,ASE,SEC",btn("Nuevo estudiante","NuevoEstudiante.html"),True),only("ADM,GER,SUC,COO",btn("Nuevo curso","NuevoCurso.html"),True),only("ADM,GER,SUC,COO,PRO",btn("Registrar sesión",None,False),True),only("ADM,GER,SUC,COO",btn("Payment sheet","PaymentSheet.html"),True),only("ADM,GER,DIR,ASE",btn("Comisiones","Comisiones.html"),True),only("ADM,GER,SUC,COO,SEC",btn("Inventario","Inventario.html"),True),only("ADM,GER,DIR,SUC,COO",btn("Reportes","Reportes.html"),True)))),
 only("ADM,GER,DIR,SUC", ai([("Octubre va 9% sobre la meta de niveles, pero Ambato lleva 2 semanas sin matrículas nuevas y tiene 2 cursos por abrir con menos de 5 inscritos.","Ver cursos de Ambato","Cursos.html"),("Hay $12,450 en matrículas con saldo; el 60% está en 4 cursos que terminan en noviembre. Conviene cobrar antes del cierre.","Ver matrículas con saldo","Cursos.html"),("La payment sheet de octubre tiene 3 alertas: una diferencia de $26 y una factura de profesor sin sesiones registradas.","Revisar payment sheet","PaymentSheet.html"),("Stock negativo en 3 libros de cursos que ya están en curso: 4 estudiantes sin material.","Ver inventario","Inventario.html")],"Pregunta: ¿qué cursos terminan este mes con saldo pendiente?"))+
 only("COO,PRO", ai([("Hoy hay 3 sesiones sin confirmar; dos son de P. Gómez y la tercera (Teens A2, Ambato) lleva 2 días pendiente.","Confirmar sesiones","Sesiones.html"),("Adults A1 Sábados terminó hace 5 días y sigue sin calificar: 14 estudiantes esperan su certificado y no pueden matricularse en A2.","Calificar curso","DetalleCurso.html"),("Teens B1 Virtual abre en 2 semanas sin profesor. P. Gómez tiene libre Lu-Ma-Mi-Ju 17:00–19:00 y ya dicta B1.","Ver perfil de P. Gómez","FichaProfesor.html"),("4 estudiantes con asistencia menor a 60% en B1 Virtual: riesgo de perder el módulo.","Ver estudiantes del curso","DetalleCurso.html")],"Pregunta: ¿qué profesores tienen horas libres el sábado?"))+
 only("ASE", ai([("Tienes 5 leads de Kommo sin contactar desde hace más de 3 días; dos preguntaron por B1 Virtual, que abre el 3 de noviembre con 3 cupos.","Ver leads","Estudiantes.html"),("4 estudiantes tuyos tienen saldo vencido ($1,420). Dos de ellos terminan curso en noviembre.","Ver matrículas con saldo","Cursos.html"),("Tu solicitud de descuento del 42% para Gabriela Núñez sigue pendiente desde ayer; con 10% la matrícula se puede cerrar hoy.","Ver solicitud","SolicitudDescuento.html")],"Pregunta: ¿cuántos niveles me faltan para el bono del mes?")),
 subtitle="Resumen del día según tu rol")
page("Home.html","Inicio",home,"Inicio por rol")

# 3 Estudiantes
est=shell("Estudiantes","Estudiantes",
 filters(search("Buscar","Nombre, cédula o email",w="300px"),sel("Estado",["Todos","Activo","En transición","Inactivo"],w="150px"),sel("Programa",["Todos","Preescolar","Adults","Teens","Kids","Business"],w="130px"),sel("Nivel",NIVEL_FILTRO+["Kids 1","Kids 2"],w="120px"),sel("Asesor",["Todos","Carla M.","Diego R.","Sofía L."],w="130px"),sel("Vista",["Alumnos activos","Alumnos inactivos","Duplicados entre sedes","Matrículas con saldo","Nuevos este mes"],w="190px",col=False),actions=only(COMERCIAL,btn("Nuevo estudiante",None,True),True)+only("ADM,GER,SUC,SEC",btn("Importar / Exportar"),True)+only("ADM,GER,DIR,SUC,SEC,COO",btn("Correo masivo"),True)),
 note("Las vistas guardadas reemplazan las de TeamDesk (Alumnos indexados activos / inactivos / x cruzar). Un nivel = 2 módulos; se muestra el nivel comercial y el módulo académico en curso."),
 ltable("estudiantes",["Nombre","Cédula","Sede","Programa","Nivel","Asesor","Estado","Acción"],[
  [c2("María Andrade","1712345678 · Quito · English for Adults · asesor Carla M."),"1712345678","Quito","Adults","B1 · módulo 7","Carla M.",badge("Activo","ok"),'<a href="Ficha360.html">Ver ficha</a>'],
  [c2("Juan Pérez","1723456789 · Valle · English for Adults · asesor Diego R."),"1723456789","Valle","Adults","A2 · módulo 4","Diego R.",badge("En transición","warn"),'<a href="Ficha360.html">Ver ficha</a>'],
  [c2("Luis Torres","1834567890 · Ambato · English for Adults · asesor Sofía L."),"1834567890","Ambato","Adults","A1 · módulo 1","Sofía L.",badge("Inactivo","neutral"),'<a href="Ficha360.html">Ver ficha</a>'],
  [c2("Ana Ruiz (menor)","1745678901 · Quito · English for Kids · asesor Carla M."),"1745678901","Quito","Kids","Kids 2","Carla M.",badge("Activo","ok"),'<a href="Ficha360.html">Ver ficha</a>'],
  [c2("Pedro Mora","1756789012 · Valle · English for Adults · asesor Diego R."),"1756789012","Valle","Adults","B1 · módulo 7","Diego R.",badge("Activo","ok"),'<a href="Ficha360.html">Ver ficha</a>'],
  [c2("Camila Sánchez","1867890123 · Ambato · English for Teens · asesor Sofía L."),"1867890123","Ambato","Teens","A2 · módulo 5","Sofía L.",badge("Activo","ok"),'<a href="Ficha360.html">Ver ficha</a>'],
  [c2("Diego Vargas (menor)","1778901234 · Valle · English for Kids · asesor Diego R."),"1778901234","Valle","Kids","Kids 1","Diego R.",badge("Activo","ok"),'<a href="Ficha360.html">Ver ficha</a>'],
  [c2("Valeria Cedeño","1789012345 · Quito · English for Adults · asesor Carla M."),"1789012345","Quito","Adults","B2 · módulo 11","Carla M.",badge("Activo","ok"),'<a href="Ficha360.html">Ver ficha</a>'],
  [c2("Mateo Salazar (menor)","1890123456 · Ambato · English for Teens · asesor Sofía L."),"1890123456","Ambato","Teens","A1 · módulo 2","Sofía L.",badge("En transición","warn"),'<a href="Ficha360.html">Ver ficha</a>'],
  [c2("Gabriela Núñez","1701234567 · Quito · English for Adults · asesor Carla M."),"1701234567","Quito","Adults","A2 · módulo 4","Carla M.",badge("En transición","warn"),'<a href="Ficha360.html">Ver ficha</a>']],sede=2,hide=(1,2,3),wide=0),
 pager(sv(812,420,230,162)),
 subtitle="Una sola base para Quito, Valle y Ambato · exportar queda registrado en el audit log")
page("Estudiantes.html","Estudiantes",est,"Listado de estudiantes")

# 4 Ficha 360
ficha=shell("María Andrade","Estudiantes",
 f'''<div class="grid" style="grid-template-columns:320px 1fr">
  <aside class="profile"><div class="profile-cover"></div><div class="profile-body">{avatar("MA")}<div class="chips" style="justify-content:center;gap:8px"><span class="badge badge-navy">EST-00412</span>{badge("Activa","bad").replace("badge-bad","badge-bad")}</div><h2>María Andrade</h2><span class="kpi-sub">Matriculada el 10 jul 2025 · Quito</span>
    <div class="actions"><button type="button" class="btn" style="flex:0 0 46px" aria-label="Llamar" data-action="Se abre el marcador con el teléfono del estudiante y se registra el contacto en su historial.">{ico("phone")}</button><button type="button" class="btn" style="flex:0 0 46px" aria-label="Email" data-action="Se abre un correo con la plantilla de contacto y queda registrado en el historial.">{ico("mail")}</button><button type="button" class="btn" style="background:var(--tint-navy);border-color:var(--tint-navy)" data-action="Se abre WhatsApp con la plantilla elegida (enlace de clase, recordatorio de saldo, certificado listo).">{ico("chat")}&nbsp;WhatsApp</button></div>
    <div class="section"><h3>Contacto</h3><div class="clist"><div><span class="cico">{ico("mail","")}</span><span><b>Email</b>maria.andrade@example.com</span></div><div><span class="cico">{ico("phone","")}</span><span><b>Teléfono</b>099 000 0001</span></div><div><span class="cico">{ico("pin","")}</span><span><b>Sector</b>Quito Norte · La Carolina (ubicada en el mapa)</span></div><div><span class="cico">{ico("id","")}</span><span><b>Cédula · ID legado</b>1712345678 · TeamDesk Quito 001-2026xxxxx</span></div><div><span class="cico">{ico("grad","")}</span><span><b>Programa · asesor</b>English for Adults · B1 (módulo 7 de 16) · Carla M.</span></div></div></div>
    <div class="section"><h3>Logros y certificados</h3><div class="awards"><div><i></i>Certificado A1 · dic 2025</div><div><i></i>Certificado A2 · jun 2026 · nota 85</div><div><i></i>Asistencia perfecta · módulo 5</div><div><i></i>Mejor progreso del grupo · módulo 6</div><div><i></i>Referido: trajo a 1 estudiante</div></div></div>
    <div class="actions">{btn("Nueva matrícula",None,True)}<a href="PortalEstudiante.html" class="btn" title="Ver como estudiante" aria-label="Ver como estudiante" style="flex:0 0 46px">{ico("user")}</a><a href="NuevoEstudiante.html" class="btn">{ico("edit")}&nbsp;Editar</a></div></div></aside>
  <div style="display:flex;flex-direction:column;gap:20px;min-width:0">
    <div class="grid" style="grid-template-columns:1.25fr 1fr">
      {card("Actividad de aprendizaje", '<div class="hours"><b>6</b><span>horas</span><b>30</b><span>minutos esta semana</span></div>'+stackbars(["Lu","Ma","Mi","Ju","Vi","Sa","Do"],{"B1 Virtual":[2,2,2,2,0,0,0],"Club de conversación":[0,1,0,0,0,0,0],"Moodle":[0.5,0,0.5,0,1,0,0]},h=160)+'<div class="chips"><span class="chip" style="background:var(--tint-navy)"><b>8 h</b>B1 Virtual · P. Gómez</span><span class="chip" style="background:var(--tint-red)"><b>1 h</b>Club de conversación</span><span class="chip" style="background:var(--tint-sky)"><b>2 h</b>Tareas en Moodle</span></div>', sel("Período",["Esta semana","Últimas 4 semanas","Módulo actual"],w="160px",col=False))}
      {card("Rendimiento", '<div class="perf">'+gauge(84,"Puntaje total",segments=True)+'<div class="perf-legend"><div><i style="background:#16A34A"></i>Participación<b>55%</b></div><div><i style="background:#F6C21C"></i>Quiz en clase<b>15%</b></div><div><i style="background:#F59E0B"></i>Examen<b>10%</b></div><div><i style="background:#D62839"></i>Ausencias<b>10%</b></div></div></div><div class="trend"><div class="big"><b>84% <span class="up">+3.4%</span></b>últimos 6 meses</div>'+areachart(["May","Jun","Jul","Ago","Sep","Oct"],[72,78,75,81,83,84],h=140)+'</div><div class="quote">Va al día con el módulo 7 y mejoró 12 puntos desde mayo. Si mantiene la asistencia, cierra B1 en noviembre con certificado.</div>', sel("Período",["Últimos 6 meses","Módulo actual","Todo"],w="160px",col=False))}
    </div>
    {card("Rematrícula (conectada con el Muro)", '<div class="grid" style="grid-template-columns:1fr 1fr 1fr">'+kpi("Avance en el Muro","100%","módulo 7 · B1 Virtual")+kpi("Nota de aprobación","8.4 / 10","mínimo 7 · aprobado")+kpi("Siguiente","Módulo 8","ya pagado · mismo grupo · inicia 3 nov")+'</div>'+kv(("Estado",badge("Continúa sin pago","ok")),("Por qué","los módulos 7 a 10 están en la venta del 28 ago (factura 000021090)"),("Rematrícula con pago","se activa al aprobar el módulo 10, el último comprado"))+only(COMERCIAL,row(btn("Nueva matrícula",None,True),btn("Enviar recordatorio"))),extra=badge("Condiciones cumplidas","ok"))}
    {card("Cursos matriculados", course_item("English for Adults B1 Virtual","Adults · B1 · módulo 7 · P. Gómez",60,badge("En curso","warn"),"84 / 100",badge("Pendiente"),tone=0,sessions="18",hours="36 h")+course_item("English for Adults A2","Adults · A2 · módulos 3–6 · L. Vega",100,badge("Completado","bad"),"85 / 100",badge("A2.pdf","navy"),tone=2,sessions="36",hours="72 h")+course_item("English for Adults A1","Adults · A1 · módulos 1–2 · L. Vega",100,badge("Completado","bad"),"80 / 100",badge("A1.pdf","navy"),tone=3,sessions="18",hours="36 h")+course_item("Club de conversación B1","Extracurricular · sábados · S. Jiménez",35,badge("En curso","warn"),"—",badge("Ninguno"),tone=1,sessions="4",hours="4 h")+course_item("English for Adults B2 · por abrir","Adults · B2 · módulos 11–14 · inicia mar 2027",0,badge("Pendiente"),"—",badge("Ninguno"),tone=0,sessions="0",hours="0 h"), filters(search("Buscar","Curso, categoría…",w="240px"),sel("Estado",["Todos","En curso","Completado","Pendiente"],w="130px",col=False),actions='<a href="Cursos.html" class="btn btn-primary">Ver todos</a>'))}
  </div>
</div>''',
 tabs(["Datos","Matrículas y notas","Niveles / crédito","Facturas y pagos","Archivos y certificados","Historial"],"Matrículas y notas",roles={"Niveles / crédito":COMERCIAL,"Facturas y pagos":COMERCIAL,"Historial":"ADM,GER,DIR,SUC,COO,SEC"},panels={
  "Datos": two(card("Datos personales", form([("Nombres","María"),("Apellidos","Andrade"),("Cédula / ID","1712345678"),"Fecha de nacimiento",("Email","maria.andrade@ejemplo.com",'email'),("Teléfono","099 000 0001",'tel'),"@@DIR@@","Sede"])),
               card("Comercial y origen", form(["Asesor asignado","Lead Kommo (origen)","Ocupación / empresa","Cómo nos conoció"])+note("Mayor de edad: no requiere representante. Si fuera menor, aquí van nombre, cédula y teléfono del representante y la autorización firmada.")))+row(btn("Guardar cambios",None,True)),
  "Matrículas y notas": table(["Matrícula","Curso","Horario","Módulo","Total","Pagado","Saldo","Asistencia","Nota","Estado","Acción"],hide=(0,2,4,5),wide=1,rows=[
     ["001-202602794",c2('<a href="DetalleMatricula.html">English for Adults (ESL) · Virtual · Grupal · B1</a>',"001-202602794 · 0001-2026-0767 · módulo 7 · Lu-Ma-Mi-Ju 19:00–21:00"),"Lu-Ma-Mi-Ju 19:00–21:00","7","$305","$305","$0","90%","—",badge("En curso","ok"),'<a href="DetalleMatricula.html">Ver</a>'],
     ["001-202601245",c2('<a href="DetalleMatricula.html">English for Adults (ESL) · Presencial · Grupal · A2</a>',"001-202601245 · 0001-2026-0620 · módulo 4 · Lu-Mi 14:00–16:00"),"Lu-Mi 14:00–16:00","4","$240","$240","$0","95%","85 · Pass",badge("Aprobado","ok"),'<a href="DetalleMatricula.html">Ver</a>'],
     ["001-202601102",c2('<a href="DetalleMatricula.html">English for Adults A2</a>',"001-202601102 · 0001-2026-0512 · Lu-Mi 18:00–20:00"),"Lu-Mi 18:00–20:00","3","$240","$240","$0","92%","88 · Pass",badge("Aprobado","ok"),'<a href="DetalleMatricula.html">Ver</a>'],
     ["001-202500811",c2('<a href="DetalleMatricula.html">English for Adults A1</a>',"001-202500811 · 0001-2025-0430 · Sa 09:00–13:00"),"Sa 09:00–13:00","2","$495","$455","$0","88%","80 · Pass",badge("Aprobado","ok"),'<a href="DetalleMatricula.html">Ver</a>']])
     +kv(("Matrículas","4"),("Módulos aprobados","6"),("Asistencia promedio","91%"),("Saldo total","$0"))
     +note("Cada matrícula conserva su número y código de curso de TeamDesk (migración). Notas y asistencia se sincronizan desde Moodle cada noche; nota mínima para Pass: 70."),
  "Niveles / crédito": two(card("Niveles comprados vs consumidos", kv(("Comprados","módulos 1 a 10 (A1, A2, B1, B1+)"),("Aprobados","6 (A1 y A2)"),("En curso","módulo 7 (B1)"),("Pagados por cursar","módulos 8, 9 y 10"))+progress(38,"Avance del programa · 6 de 16 módulos aprobados")+table(["Nivel","Estado","Curso","Cierre"],[["A1",badge("Pass","ok"),"Adults A1 · L. Vega","dic 2025"],["A2",badge("Pass","ok"),"Adults A2 · L. Vega","jun 2026"],["B1",badge("En curso"),"Adults B1 Virtual · P. Gómez","—"],["B1+",badge("Pagado","warn"),"Sábados · por abrir","—"]])),
     card("Resumen financiero", kv(("Factura","000021090 (módulos 7–10)"),("Total","$980"),("Pagado","$980"),("Saldo","$0"),("Descuento","10% referido · dentro del límite del asesor"))+hbars([("Facturado",1880),("Cobrado",1880),("Notas de crédito",45)],"$")+row('<a href="DetalleFactura.html" style="font-size:13px">Ver factura 000021090</a>')))+
     card("Cursos tomados", table(["Curso","Nivel","Profesor","Estado","Nota"],[["Adults B1 Virtual","B1","P. Gómez","En curso","—"],["Adults A2","A2","L. Vega","Pass","85"]])),
  "Facturas y pagos": row(btn("Enviar estado de cuenta"),btn("Descargar facturas pendientes"))+table(["Factura","Concepto","Total","Pagado","Saldo","Estado","Acción"],[["000021090","Venta multi-módulo · módulos 7 a 10","$980","$980","$0","Pagada",btn("Ver","DetalleFactura.html")],["000020411","A2 · módulos 3 a 6","$450","$450","$0","Pagada",btn("Ver","DetalleFactura.html")],["000019872","A1 · módulos 1 y 2","$450","$450","$0","Pagada",btn("Ver","DetalleFactura.html")],["NC-000000298","Nota de crédito · libro devuelto","-$45","—","—","Aplicada",btn("Ver","DetalleFactura.html")]])+row(btn("Nueva venta","NuevaVenta.html",True),btn("Registrar pago")),
  "Archivos y certificados": two(card("Archivos", table(["Archivo","Tipo","Subido por","Fecha"],[["cedula_maria_andrade.pdf","Identificación","Carla M.","12 ene"],["matricula-001-202602794.pdf","Matrícula firmada","Carla M.","28 ago"],["comprobante_transferencia_884512.pdf","Comprobante de pago","Secretaría","28 ago"]])+row(upload("Adjuntar archivo","PDF, JPG o PNG · máx. 10 MB"),btn("Subir archivo",None,True))),
     card("Certificados emitidos", table(["Nivel","Nota","Emitido","Acción"],[["A1","80 · Pass","dic 2025",btn("Descargar PDF")],["A2","85 · Pass","jun 2026",btn("Descargar PDF")]])+row(btn("Emitir certificado"))+note("Los exámenes internacionales (tabla International Exams de TeamDesk) no están en los 11 módulos del contrato: se migran como archivo histórico y se confirma con el cliente si se gestionan aquí."))),
  "Historial": table(["Fecha/hora","Usuario","Acción","Detalle"],[["27 sep 17:20","Secretaría","Registró pago","Cuota 2 de 2 · $490 · tarjeta"],["28 ago 10:11","Carla M.","Creó venta","Módulos 7 a 10 · 4 matrículas · factura 000021090 · 10% referido"],["30 jun 16:00","Sistema","Cerró nivel","A2 · Pass · nota 85"],["10 jul 2025","Secretaría","Creó estudiante","Alta desde lead Kommo"]])+note("Vista filtrada del audit log para este estudiante. El registro completo está en Configuración → Audit log."),
 }),
 only("ADM,GER,DIR,SUC,COO,ASE,SEC", ai([("Lleva 6 módulos aprobados (A1 y A2) con 91% de asistencia; con lo comprado llega al módulo 10 (B1+) en febrero de 2027. Buen candidato para ofrecerle B2 (módulos 11 a 14) antes de que termine B1+.","Nueva matrícula","NuevaVenta.html"),("Faltó 2 veces seguidas la semana pasada en B1 Virtual (antes nunca). Vale la pena un mensaje antes de que afecte el módulo.","Ver asistencia","DetalleMatricula.html"),("Su descuento del 10% fue por referido: trajo a Pedro Mora, que ya está matriculado.","Ver detalle de comisión","DetalleComision.html")],"Pregunta: ¿qué nivel le toca y cuándo abre el próximo curso?")),
 subtitle="Ficha 360°: todo lo del estudiante en una sola vista")
page("Ficha360.html","Ficha estudiante",ficha,"Ficha 360 del estudiante")

# 5 Nueva venta
# 5 Nueva matrícula: sigue el flujo del Enrollment de TeamDesk (una matrícula por módulo; la venta de varios módulos sale en una sola factura "multi-módulo")
ACTIONS.update({
 "Buscar estudiante":("Se busca por cédula, pasaporte o nombre en las tres sedes. Si existe se cargan sus datos y su historial (estudiante antiguo); si no, se crea desde Nuevo estudiante.",None),
 "Agregar otro módulo":("Se agrega el siguiente módulo del mismo programa a la venta. Cada módulo genera su propia matrícula 001-AAAANNNNN; todas salen en una sola factura multi-módulo.",None),
 "Agregar pago":("Se agrega otra línea de pago (p. ej. parte en efectivo y parte con tarjeta) con su comprobante.",None),
 "Guardar borrador":("La venta queda como borrador del asesor; no reserva cupo ni compromete libros hasta confirmarla.",None),
 "Imprimir etiquetas de libros":("Se imprimen las etiquetas de los libros que están en stock en la sede para entregarlos de inmediato al estudiante.",None),
 "Confirmar matrícula y emitir factura":("Se crea la venta V-2026-0412 con su valor completo y 4 matrículas (001-202602794 a 001-202602797, una por módulo), una factura multi-módulo firmada y enviada al SRI, las cuotas del plan de pago en la cartera, la comisión del asesor en estado Pendiente y se reservan los libros. El estudiante entra al grupo de Teams y recibe el enlace de clase. "+AUDIT,"DetalleMatricula.html"),
})
venta_sum=wiz_summary('<span data-total-for="lgv">$980</span>',[("Estudiante","María Andrade"),("Cédula","1712345678"),("Clasificación","Continuidad"),("Asesor","Carla M."),"---",("Módulos 7 y 8","0001-2026-0767"),("Módulos 9 y 10","por abrir · sábados"),"---",("Subtotal","$1,080"),("Descuento","-$100"),("*Total",'<span data-total-for="lgv">$980</span>'),"---",("Pagado hoy","$490"),("Saldo en cartera","$490")])
mods=('<div class="mod-group"><header>B1 · Virtual · Lu-Ma-Mi-Ju 19:00 a 21:00 · P. Gómez</header>'
  +'<div class="mod"><div class="m-n"><b>Módulo 7</b><small>Nivel B1</small></div><div>English for Adults (ESL) · Virtual · Grupal<small>Plantilla regular noche · 2 h por sesión</small></div><div><span class="mono">0001-2026-0767</span><small>Zoom 2</small></div><div>1 sep 2026<small>inicia</small></div><div>'+badge("12 de 15 cupos","ok")+'</div></div>'
  +'<div class="mod"><div class="m-n"><b>Módulo 8</b><small>Nivel B1</small></div><div>Continúa en el mismo grupo<small>cupo reservado al matricular</small></div><div><span class="mono">0001-2026-0767</span><small>Lu-Ma-Mi-Ju 19:00–21:00 · Zoom 2 · P. Gómez</small></div><div>3 nov 2026<small>inicia</small></div><div>'+badge("Reservado","info")+'</div></div></div>'
  +'<div class="mod-group"><header>B1+ · Presencial Quito · Sábados 09:00 a 13:00</header>'
  +'<div class="mod"><div class="m-n"><b>Módulo 9</b><small>Nivel B1+</small></div><div>English for Adults (ESL) · Presencial · Grupal<small>Plantilla sábados · 4 h por sesión</small></div><div><span>Por abrir</span><small>Quito</small></div><div>ene 2027<small>inicia</small></div><div>'+badge("Por abrir","neutral")+'</div></div>'
  +'<div class="mod"><div class="m-n"><b>Módulo 10</b><small>Nivel B1+</small></div><div>Continúa en el mismo grupo<small>sábados</small></div><div><span>Por abrir</span><small>Quito</small></div><div>feb 2027<small>inicia</small></div><div>'+badge("Por abrir","neutral")+'</div></div></div>')
ledger=ledger_calc([("Derecho de matrícula","tuition fee · estudiante antiguo, exonerado",0,False),("Valor del curso","course fee · 4 módulos × $250",1000,True),("Libros y materiales","Empower B1 Combo A + B1+ Combo B",80,False)],10,"lgv")
review=('<dl class="review">'
  +'<div><dt>Estudiante y origen</dt><dd>María Andrade · CED 1712345678 · continuidad · Carla M. · Kommo KM-48213 (contacto: madre)</dd><button type="button" class="btn btn-ghost" data-wgoto="1">Editar</button></div>'
  +'<div><dt>Programa y cursos</dt><dd>Módulos 7 y 8 en 0001-2026-0767 (virtual) · módulos 9 y 10 por abrir (sábados)</dd><button type="button" class="btn btn-ghost" data-wgoto="2">Editar</button></div>'
  +'<div><dt>Valores y descuentos</dt><dd>Subtotal $1,080 · descuento 10% referido (-$100) · total $980</dd><button type="button" class="btn btn-ghost" data-wgoto="3">Editar</button></div>'
  +'<div><dt>Factura y pago</dt><dd>A nombre de María Andrade · 2 cuotas cada 30 días · hoy $490 por transferencia</dd><button type="button" class="btn btn-ghost" data-wgoto="4">Editar</button></div></dl>')
venta=shell("Nueva matrícula","Nueva matrícula",
 wizard([
  ("Estudiante y origen",
   form([("Estudiante","María Andrade · CED 1712345678","text",None,True,"Busca por cédula, pasaporte o nombre"),("Clasificación","Continuidad","select",["Nueva","Reingreso (exestudiante)","Continuidad"],True,"Se sugiere sola; puede corregirse"),("Oportunidad Kommo","KM-48213 · contacto: madre","text",None,False,"El contacto puede no ser el estudiante"),
         ("Asesor (vendor)","Carla M.","select",["Carla M.","Diego R.","Andrea S.","Luis P."],True),("Origen del contacto","Estrategia pagada","select",["Estrategia pagada","Referido","Walk-in","Exalumno","Convenio o alianza","Feria","Lead anterior"],True),("Tipo de venta","Nivel completo (2 módulos)","select",["Nivel completo (2 módulos)","Módulo suelto","Varios niveles"],True,"Una venta por nivel se relaciona con sus dos módulos"),
         ("¿Indexado?","No","select",["No","Sí · entra al curso de indexados con 100% de descuento (regular ≥ 48 h · urgente < 24 h con autorización)"],False,"Como el campo Indexed? de TeamDesk"),("¿Paga la empresa?","No","select",["No","Sí · Grupo Nova (convenio 15% · factura a la empresa · 30 días)","Sí · Clínica Santa Fe (convenio 10% · factura a la empresa)"],False,"Marca Sí si la factura la paga la empresa del estudiante"),("Sede","Quito","text",None,False,"Automático")],cols=3)
   +row(btn("Buscar estudiante"),btn("Nuevo estudiante","NuevoEstudiante.html",kind="ghost")),"Viene del lead de Kommo o de la búsqueda; si ya existe se reutiliza su ficha"),
  ("Programa y cursos", form([("Programa","English for Adults","select",PROGRAMAS,True),("Nivel","B1 · módulos 7 y 8","select",["A1 · módulos 1 y 2","A2 · módulos 3 y 4","B1 · módulos 7 y 8","B1+ · módulos 9 y 10","B2 · módulos 11 y 12"],True),
     ("Curso para el módulo 7","En curso · 0001-2026-0767 · Virtual · Lu-Ma-Mi-Ju 19:00–21:00 · inició 1/09/2026 · P. Gómez · 12/15","select",["En curso · 0001-2026-0767 · Virtual · Lu-Ma-Mi-Ju 19:00–21:00 · inició 1/09/2026 · P. Gómez · 12/15","Por abrir · 0001-2026-0983 · Virtual · QUITO INDEXADO · Lu-Ma-Mi-Ju 07:00–09:00 · inicia 26/10/2026","Por abrir · 0001-2026-0985 · Virtual · Lu-Ma-Mi-Ju 19:00–21:00 · inicia 9/11/2026 · L. Vega","Por abrir · 0001-2026-1005 · Presencial Quito · Sa 09:00–13:00 · inicia 9/11/2026 · S. Jiménez","Por abrir · 0001-2026-0772 · Virtual Valle · Lu-Ma-Mi-Ju 17:00–19:00 · inicia 2/11/2026"],True,"Estado · código · modalidad · horario · inicio · profesor · cupo. Solo cursos del programa y nivel elegidos, con cupo y sin choque de horario")],cols=3)
   +mods+row(addmod_btn(),more_menu(btn("Agregar a lista de espera"),"Más")),
   "Una matrícula por módulo. Solo aparecen cursos del programa y módulo elegidos, con cupo y sin choque de horario"),
  ("Valores y descuentos",
   two(ledger+kv(("Tu límite sin aprobación","10%"),("Aplicado",'<span data-disc-for="lgv">10% · -$100</span>'),("Más de 10%",'<a href="SolicitudDescuento.html">pasa a aprobación de Dirección Comercial</a>')),
       disc_field("lgv",10)+form([("Motivo del descuento","Referido","select",["Referido","Promoción vigente","Convenio empresa","Hermano matriculado","Beneficio cancela 2 módulos","Indexado","Otro"],True,"Obligatorio si hay descuento"),
             ("Observaciones","","textarea",None,False,"Ej.: matrícula condicionada, ingresa a medio nivel"),("Firma de la matrícula","Enviar para firma digital al correo del estudiante","select",["Enviar para firma digital al correo del estudiante","Adjuntar matrícula firmada en papel (PDF)"],True,"Reemplaza el envío de contrato por Jotform")],cols=1),ratio="7fr 5fr"),
   "Cada concepto tiene su propio descuento, como en TeamDesk"),
  ("Factura y pago",
   form([("Facturar a","María Andrade · CED 1712345678","select",["María Andrade · CED 1712345678","Consumidor final","Grupo Nova · RUC 1790012345001","Clínica Santa Fe · RUC 1790055555001","Otro cliente…"],True),("Identificación","Cédula","select",["Cédula","RUC","Pasaporte"],True),
         ("RUC especial","No","select",["No","Sí · verificado en el SRI"],False,"Solo si verificaste el RUC en el SRI"),("Plan de pago","2 cuotas · cada 30 días","select",["Contado","2 cuotas · cada 15 días","2 cuotas · cada 30 días","3 cuotas · cada 30 días"],True),
         ("Crédito","Sí · 30 días","text",None,False,"Automático"),("Actualizar datos de facturación en la ficha","No","select",["No","Sí · reemplazar en la ficha del estudiante"],False)],cols=3)
   +table(["Pago","Método","Comprobante","Monto"],[["Cuota 1 · hoy, 28 ago","Transferencia","Banco Pichincha · ref. 884512","$490.00"],["Cuota 2 · 27 sep 2026",badge("Programada","neutral"),"queda en la cartera del estudiante","$490.00"]])
   +row(btn("Agregar pago",kind="ghost"),btn("Imprimir etiquetas de libros",kind="ghost")),"Efectivo, cheque, tarjeta, depósito, transferencia, retención, nota de crédito, cruce de cuentas, gift card o pago en línea"),
  ("Confirmación", review+'<h4 class="section-title">Qué pasa al confirmar</h4>'
   +flow([("Se crean 4 matrículas","001-202602794 a 001-202602797, una por módulo"),("Se emite 1 factura multi-módulo","firmada y enviada al SRI"),("Las cuotas pasan a la cartera","cuota 2 de $490 vence el 27 sep"),("Se reservan libros y códigos","Empower B1 Combo A y B1+ Combo B"),("Entra al grupo de Teams","y recibe el enlace de clase"),("La comisión del asesor queda pendiente","se paga al cobrar todo")]),
   "Revisa antes de emitir: la factura no se puede deshacer sin nota de crédito")], venta_sum),
 foot(btn("Confirmar matrícula y emitir factura",None,True),btn("Guardar borrador",kind="ghost"),btn("Salir sin guardar")),
 subtitle="Sigue el flujo de matrícula de TeamDesk: una matrícula por módulo y una factura por la venta")
page("NuevaVenta.html","Nueva matrícula",venta,"Nueva matrícula (una por módulo, factura multi-módulo)")

# Matrícula desde un lead de Kommo: el estudiante se crea con los datos del lead (precargados) y sigue el mismo flujo de 5 pasos
venta_lead=shell("Nueva matrícula · desde lead","Nueva matrícula",
 wizcard(step(1,"Estudiante creado desde el lead",
   flow([("Entra a Kommo","Instagram · 17 oct 09:40 · formulario de la campaña","Kommo","done"),("Kommo lo pasa a la plataforma","sincronización automática cada 5 min · lead KM-48310 · etapa Cotizado · 10:20","Plataforma","done"),("Matrícula desde el lead","los datos del lead ya están aquí; al confirmar, Kommo recibe 'Ganado' y el enlace a la ficha","Asesor","now")])
   +kv(("Lead","Andrea Villacís · KM-48310 · Instagram · cotizado hoy 10:20"),("Interés","Adults · virtual · grupal"),("Asesor","Carla M. · Quito"))
   +form([("Nombres","Andrea","text",None,True,"Del lead"),("Apellidos","Villacís","text",None,True,"Del lead"),("Teléfono","099 000 0101","tel",None,True,"Del lead"),
          ("Email","a.villacis@ejemplo.com","email",None,True,"Del lead"),("Tipo de identificación","Cédula","select",["Cédula","RUC","Pasaporte"],True),("Cédula / ID!","1726543210","text",None,True,"Falta en el lead · se valida al pasar al siguiente paso"),
          "@@DIR@@",("Tipo de estudiante","Nuevo · creado desde el lead","text",None,False,"Automático"),
          ("Asesor (vendor)","Carla M.","select",["Carla M.","Diego R.","Andrea S.","Luis P."],True),("Canal de contacto","Kommo · Facebook / Instagram","select",["Kommo · WhatsApp","Kommo · Facebook / Instagram","Walk-in (visita a la sede)","Referido","Empresa (convenio)"],True,"Del lead"),("Sede","Quito","text",None,False,"Del lead")],cols=3)
   ,sub="El lead entra a Kommo y de Kommo a la plataforma: sus datos se precargan; solo faltan la cédula y la dirección")
  +step(2,"Programa, nivel y curso por módulo",
   kv(("Prueba de ubicación","A1 · sin conocimientos previos · 15 oct"))
   +'<div class="mod-group"><header>A1 · Virtual · Lu-Ma-Mi-Ju 17:00 a 19:00 · L. Vega · Zoom 3</header>'
   +mod_row(1,"A1","English for Adults (ESL) · Virtual · Grupal","Plantilla regular tarde · 2 h por sesión","0001-2026-0781","Lu-Ma-Mi-Ju 17:00–19:00 · Zoom 3 · L. Vega","3 nov 2026",badge("8 de 15 cupos","ok"))
   +mod_row(2,"A1","Continúa en el mismo grupo","cupo reservado al matricular","0001-2026-0781","Lu-Ma-Mi-Ju 17:00–19:00 · Zoom 3 · L. Vega","1 dic 2026",badge("Reservado","navy"))+'</div>'
   +row(addmod_btn()),sub="A1 = módulos 1 y 2 (1 nivel). Solo se listan cursos del programa y módulo elegidos, con cupo y sin choque de horario")
  +step(3,"Valores y descuentos",
   ledger_calc([("Derecho de matrícula","tuition fee · estudiante nuevo",25,False),("Valor del curso","course fee · 2 módulos × $225 · virtual",450,True),("Libros y materiales","Empower A1 Starter SB with digital pack",70,False)],0,"lgl")
   +kv(("Tu límite sin aprobación","10%"),("Aplicado",'<span data-disc-for="lgl">sin descuento</span>'))
   +'<div class="form-grid cols-3">'+disc_field("lgl",0)+field("Motivo del descuento","Sin descuento","select",["Sin descuento","Referido","Promoción vigente","Convenio empresa","Hermano matriculado","Otro"],False,"Obligatorio si hay descuento")+field("Matrícula firmada","","file",None,True,"Adjunta la matrícula original firmada (PDF)")+'</div>',
   sub="Mismos conceptos que una venta normal; el asesor puede aplicar hasta 10% con motivo")
  +step(4,"Factura y forma de pago",
   form([("Facturar a","Andrea Villacís · cédula por completar","select",["Andrea Villacís · cédula por completar","Consumidor final","Otro cliente…"],True),("Plan de pago","Contado","select",["Contado","2 cuotas · cada 15 días","2 cuotas · cada 30 días","3 cuotas · cada 30 días"],True),("Crédito","No","text",None,False,"Automático")],cols=3)
   +table(["Pago","Método","Comprobante","Monto"],[["Pago único · hoy, 19 oct","Tarjeta de crédito","Datafast · lote 0193","$545.00"]])
   +row(btn("Agregar pago")))
  +step(5,"Confirmación",
   '<div class="review-facts">'+facts([("Estudiante","Andrea Villacís · nueva"),("Origen","Lead KM-48310 · Kommo · Instagram"),("Matrículas",'<span class="mono">001-202603224</span> y <span class="mono">001-202603225</span>'),("Curso",'<span class="mono">0001-2026-0781</span> · A1 virtual · Lu-Ma-Mi-Ju 17:00–19:00'),("Factura","1 multi-módulo · módulos 1 y 2"),("Total",'<span data-total-for="lgl">$545</span>'),("Pagado hoy","$545 · tarjeta"),("Comisión del asesor","Carla M. · pendiente hasta el cierre del mes")])+'</div>'
   +flow(["Estudiante creado con los datos del lead","Matrículas por módulo","Factura firmada y enviada al SRI","Libros y códigos reservados","Lead Ganado en Kommo"])),summary=wiz_summary('<span data-total-for="lgl">$545</span>',[("Estudiante","Andrea Villacís"),("Cédula","1726543210"),("Clasificación","Nueva · desde Kommo"),("Asesor","Carla M."),"---",("Módulos 1 y 2","0001-2026-0781 · Lu-Ju 17:00"),"---",("*Total",'<span data-total-for="lgl">$545</span>'),("Pagado hoy",'<span data-total-for="lgl">$545</span>')])),
 foot(btn("Confirmar matrícula y emitir factura",None,True,"Se crea la estudiante Andrea Villacís con los datos del lead, 2 matrículas (001-202603224 y 001-202603225), una factura multi-módulo enviada al SRI y la comisión de Carla M. en Pendiente. El lead se marca como Ganado en Kommo y queda enlazado a la ficha. "+AUDIT,"Ficha360.html"),btn("Guardar borrador"),btn("Volver a leads","Leads.html",kind="ghost")),
 subtitle="El lead se convierte en estudiante sin volver a escribir sus datos")
page("MatriculaLead.html","Matrícula desde lead",venta_lead,"Matrícula desde un lead de Kommo")

# 5b Detalle de matrícula (equivalente al Enrollment de TeamDesk: una matrícula por módulo)
ACTIONS.update({
 "Imprimir matrícula":("Se genera la matrícula en PDF con los datos del estudiante, curso, valores y plan de pago para firmar.",None),
 "Agregar comentario":("Se agrega un comentario con tu usuario y fecha al historial de la matrícula.",None),
 "Reversar y anular":("Requiere aprobación. Se revierte la matrícula: nota de crédito por lo pagado, cuotas pendientes canceladas, libro de vuelta al stock y comisión del asesor en NA. "+AUDIT,None),
})
page("DetalleMatricula.html","Detalle matrícula",shell("Matrícula 001-202602794","Estudiantes",
 hero([("Estudiante",'<a href="Ficha360.html">María Andrade</a>'),("Curso",'<a href="DetalleCurso.html">0001-2026-0767</a>'),("Programa","English for Adults (ESL) · Virtual · Grupal"),("Nivel","Módulo 7 · B1"),("Horario","Lu-Ma-Mi-Ju 19:00–21:00"),("Inicio","1 sep 2026"),("Asesor (vendor)","Carla M."),("Plan de pago","2 cuotas · cada 30 días"),("Indexado","No"),("Tipo de estudiante","Antiguo · 3.ª matrícula"),("Documento de matrícula",'<a href="#">matricula-001-202602794.pdf</a>'),("Comisión del asesor","Pendiente · se paga al cobrar")],
  only(COMERCIAL+",COO",btn("Cambio de curso"),True)+only(ACADEMICO+",SEC",btn("Enviar enlace de clase"),True)+only(ACADEMICO+",SEC",btn("Hoja de asistencia"),True)+btn("Ver venta completa","DetalleVenta.html")+btn("Imprimir matrícula")+btn("Agregar comentario")+only("ASE,DIR,ADM",btn("Eliminar matrícula"),True)+only("ADM,GER,DIR,SUC",btn("Reversar y anular"),True),
  tag='<span class="hero-code">001-202602794</span>'+badge("En curso","ok")+badge("Quito","navy")+badge("Antiguo","neutral")),
 only(COMERCIAL,
 two(card("Resumen", kv(("Subtotal","$330.00"),("Descuento","-$25.00 · referido"),("Total","$305.00"),("Pagado","$305.00"),("Saldo","$0 · venta pagada en 2 cuotas"))+progress(100,"Pagado de esta matrícula")
       +kv(("Venta","multi-módulo · 4 matrículas en la factura 000021090"),("Canal de contacto","Kommo · WhatsApp"),("Paga la empresa","No"),("Matrícula firmada",'<a href="#">matricula-001-202602794.pdf</a>'))),
     card("Valores y descuentos", table(["Concepto","Valor","Dcto.","Subtotal"],[[c2("Derecho de matrícula (tuition fee)","estudiante antiguo · exonerado"),"$0","—","$0"],[c2("Valor del curso (course fee)","módulo 7 · B1"),"$250","10%","$225"],[c2("Libros y materiales","Empower B1 Combo A + B1+ Combo B"),"$80","—","$80"]])
       +kv(("Motivo del descuento","Referido · dentro del límite del asesor"),("Observaciones","Continúa en el mismo grupo para el módulo 8"))))),
 only("COO,PRO", card("Resumen académico", kv(("Módulo","7 · B1"),("Asistencia","10/11 · 90%"),("Nota parcial","8.4"),("Estado",badge("En curso","ok")))+progress(60,"Avance del módulo 7"))),
 tabs(["Matrículas de la venta","Estado de la matrícula","Facturas y pagos","Cartera","Códigos de libros","Asistencia","Portafolio","Certificados","Comisión","Historial"],"Matrículas de la venta",roles={"Estado de la matrícula":COMERCIAL+",COO","Facturas y pagos":COMERCIAL,"Cartera":COMERCIAL,"Comisión":"ADM,GER,DIR,ASE"},panels={
  "Estado de la matrícula": flow(["Reservada","En curso","Congelada (máx. 3 meses)","Reactivada","Terminada · aprobada o reprobada","Retirada"])
     +table(["Cambio","Qué pasa","Quién aprueba","Acción"],[
       [c2("Congelar","viaje, salud o trabajo"),"Libera el cupo; guarda módulos pagados y saldo; recordatorio de regreso","Coordinación si supera 1 mes",btn("Congelar matrícula")],
       [c2("Reactivar","al volver"),"Elige un curso con cupo del mismo módulo","—",btn("Reactivar matrícula")],
       [c2("Cambio de curso","otro horario o modalidad"),"Mueve la matrícula y ajusta la diferencia de precio","—",btn("Cambio de curso")],
       [c2("Retiro","deja el instituto"),"Nota de crédito, devolución o saldo a favor según la política","Administración de sucursal",btn("Retirar estudiante")],
       [c2("Transferir saldo","a otro estudiante"),"Nota de crédito aquí y saldo a favor en el otro","Administración de sucursal",btn("Transferir saldo")]],wide=0),
  "Matrículas de la venta": table(["Matrícula","Módulo","Curso","Total","Estado","Acción"],[["001-202602794","7 · B1",c2("0001-2026-0767","Virtual · Lu-Ma-Mi-Ju 19:00–21:00"),"$305",badge("En curso","ok"),'<a href="DetalleMatricula.html">Ver</a>'],["001-202602795","8 · B1",c2("Mismo grupo","se asigna al cerrar el módulo 7"),"$225",badge("Reservada","navy"),'<a href="DetalleMatricula.html">Ver</a>'],["001-202602796","9 · B1+",c2("Por abrir · Quito","Presencial · sábados"),"$225",badge("Por iniciar","neutral"),'<a href="DetalleMatricula.html">Ver</a>'],["001-202602797","10 · B1+",c2("Por abrir · Quito","Presencial · sábados"),"$225",badge("Por iniciar","neutral"),'<a href="DetalleMatricula.html">Ver</a>']],wide=2),
  "Facturas y pagos": table(["Factura","Fecha","Monto","Pagado","Saldo","Estado","Acción"],[["000021090","28 ago 2026","$980","$980","$0",badge("Pagada","ok"),'<a href="DetalleFactura.html">Ver</a>']])+row(btn("Registrar pago"),btn("Emitir nota de crédito")),
  "Cartera": table(["Cuota","Vence","Monto","Pagado","Días vencidos","Estado"],[["1 de 2","28 ago 2026","$490","$490","—",badge("Pagada","ok")],["2 de 2","27 sep 2026","$490","$490","—",badge("Pagada","ok")]])+row(btn("Enviar estado de cuenta"),btn("Registrar pago")),
  "Códigos de libros": table(["Material","ISBN","Código de activación","Entregado","Acción"],[["Empower B1 Combo A (digital pack)","9781108961516","EMP-B1-7K2Q-••••","28 ago 2026",badge("Activado","ok")],["Empower B1+ Combo B (digital pack)","9781108961523","EMP-B1P-3M9X-•••• · reservado","se entrega en el módulo 9",btn("Asignar código",None,False)]]),
  "Asistencia": table(["Sesión","Fecha","Presente","Observación"],[["8","13 oct · 19:00","✓","—"],["9","14 oct · 19:00","✓","—"],["10","15 oct · 19:00","✗","Aviso previo"],["11","19 oct · 19:00","✓","—"]])+kv(("Asistencia","10 de 11 sesiones · 90%"),("Mínimo para aprobar","75%")),
  "Portafolio": table(["Módulo","Documento","Generado","Acción"],[["7",c2("Student Report · módulo 7","notas, asistencia y comentarios del profesor"),"al cerrar el módulo",badge("Se genera al calificar","neutral")],["6",c2("Student Report · módulo 6","A2 · nota 8.1 · asistencia 92%"),"28 ago 2026",btn("Ver PDF")],["5",c2("Student Report · módulo 5","A2 · nota 7.9 · asistencia 88%"),"3 jul 2026",btn("Ver PDF")]],wide=1)+kv(("Portafolio","un Student Report en PDF por módulo cerrado, como la pestaña Portfolio de TeamDesk; se adjunta al expediente y lo ve el estudiante en el portal")),
  "Certificados": table(["Módulo","Programa · modalidad · curso","Nota","Certificado","Acción"],[["7",c2("English for Adults (ESL) · Virtual · Grupal","0001-2026-0767 · P. Gómez · Quito"),"8.4 · en curso",badge("Al cerrar el módulo","neutral"),"—"],["8",c2("English for Adults (ESL) · Virtual · Grupal","0001-2026-0767 · P. Gómez · Quito"),"—",badge("Pendiente","neutral"),"—"]],wide=1)+kv(("Certificado de nivel B1","se emite al aprobar los módulos 7 y 8 con nota ≥ 7, con código único de verificación"))+row(btn("Emitir certificado")),
  "Comisión": kv(("Asesor","Carla M."),("Regla","Rango 11+ · 4% virtual"),("Monto","$39.20 por la venta de 4 módulos"),("Estado",badge("Pagada en el cierre de septiembre","ok")))+row('<a href="DetalleComision.html">Ver detalle de comisiones del asesor</a>'),
  "Historial": table(["Fecha","Usuario","Acción"],[["28 ago 10:11","Carla M.","Creó la venta multi-módulo (4 matrículas) y la factura 000021090"],["28 ago 10:12","Sistema","Factura autorizada por el SRI y enviada al cliente"],["28 ago 10:15","Carla M.","Adjuntó la matrícula firmada"],["31 ago 09:00","Sistema","Envió el enlace de clase y agregó a la estudiante al equipo de Teams"],["27 sep 17:20","Secretaría","Registró el pago de la cuota 2"]]),
 }),
 subtitle="Una matrícula por módulo, como el Enrollment de TeamDesk; la venta agrupa sus módulos en una factura"),"Detalle de matrícula")


# 8b Calificar curso (cierra el módulo: notas, pass/fail y certificados)
page("CalificarCurso.html","Calificar curso",shell("Calificar módulo 7 · 0001-2026-0767","Cursos",
 hero([("Curso","English for Adults (ESL) · Virtual · Grupal · B1"),("Módulo","7 · primero del nivel B1"),("Profesor","P. Gómez"),("Horas dictadas","18 de 18 del módulo"),("Escala","0 a 10 · aprueba con 7"),("Asistencia mínima","75%")],
  btn("Importar notas del Muro"), tag='<span class="hero-code">0001-2026-0767</span>'+badge("Módulo por cerrar","warn")),
 card("Notas por estudiante", table(["Estudiante","Asistencia","Participación 40%","Quiz 30%","Examen 30%","Nota final","Resultado"],[
   [c2('<a href="Ficha360.html">María Andrade</a>',"001-202602794"),"90%","8.8","8.2","8.0","8.4",badge("Aprobado","ok")],
   [c2('<a href="Ficha360.html">Pedro Mora</a>',"001-202602846"),"85%","8.0","7.5","7.2","7.6",badge("Aprobado","ok")],
   [c2('<a href="Ficha360.html">Sofía Herrera</a>',"001-202602871"),"70%","7.5","6.8","6.4","7.0",badge("Bloqueado · asistencia","bad")],
   [c2('<a href="Ficha360.html">Andrés Pazmiño</a>',"001-202602875"),"45%","5.0","4.5","—","—",badge("Reprobado","bad")]],wide=0)
   +kv(("Aprobados","10 de 12"),("Bloqueados por asistencia","1 · decide Coordinación"),("Reprobados","1 · repite el módulo"))),
 two(card("Al cerrar el módulo", flow(["Speaking mock y notas en GradeKeeper (48 h)","Aprobados avanzan al módulo 8 de su compra","Nivel cerrado → certificado con código de verificación y End of level report","Reprobados: rematrícula del mismo módulo"])),
     card("Reglas del proceso de cierre", table(["Nota final","Qué pasa"],[['<span class="mono">≥ 7.00</span>',"Aprueba · Student Report en PDF a su expediente"],['<span class="mono">6.50 – 6.99</span>',"Tutorías y examen de recuperación antes de decidir"],['<span class="mono">≤ 6.49</span>',"Pierde el módulo · repite con descuento para repetir"],["Cualquiera · con deuda","No se envía la nota ni el certificado hasta regularizar el saldo"],["Menor a 7.00","Coordinación llama al estudiante o representante antes de publicar"]],wide=0)
       +kv(("Plazo","72 h después de la última clase"),("Encuesta","se envía al cerrar; el informe trimestral consolida resultados por sede")))),
 foot(btn("Cerrar módulo y emitir certificados",None,True),btn("Guardar borrador de notas"),btn("Cancelar","DetalleCurso.html")),
 subtitle="Reemplaza la vista 'Finished courses with ungraded students' de TeamDesk: el curso no se cierra sin notas"),"Calificar curso")

# 8c Exámenes internacionales (propuesta: no está en los 11 módulos del contrato)
page("ExamenesInternacionales.html","Exámenes internacionales",shell("Exámenes internacionales","Exámenes",
 hero([("Qué es","Inscripción a exámenes Cambridge, Oxford, TOEFL, SIELE y Anglia"),("Cambridge · Oxford · Anglia","se compran en Books and Bits (exams.booksandbits.ec/csol); llega confirmación por registro y cierre diario"),("TOEFL ITP · SIELE · Mock Test","se compran en la tienda en línea (WooCommerce) y Secretaría gestiona el pedido"),("Hoy en TeamDesk","tabla International Exams")],btn("Cargar calendario anual")+btn("Ver pedidos de la tienda","Pedidos.html")+btn("Abrir Books and Bits","https://exams.booksandbits.ec/csol"),tag=badge("Requerimiento de Dirección Comercial · confirmar alcance","warn")),
 kpis([("Candidatos 2026",sv(64,38,16,10),"inscritos este año"),("Esperando resultados",sv(9,5,3,1),"enviados al centro"),("Listos para retirar",sv(4,2,1,1),"certificado en la sede"),("Facturado",sv("$7,680","$4,560","$1,920","$1,200"),"exámenes 2026")]),
 filters(search("Buscar","Candidato o cédula",w="220px"),sel("Examen",["Todos","Cambridge","Oxford","TOEFL","Anglia"],w="140px"),sel("Estado",["Todos","Inscrito","Esperando resultados","Listo para retirar","Entregado"],w="190px"),actions=btn("Nuevo candidato","NuevaInscripcionExamen.html",True)),
 table(["Candidato","Sede","Examen","Factura","Puntaje y nivel","Estado","Acción"],[
  [c2("Lucía Benítez","CED 1716543210 · 17 años"),"Quito",c2("Cambridge · B2 First (FCE)","14 nov 2026"),"000021101 · pagada","—",badge("Inscrito","navy"),btn("Registrar resultado")],
  [c2("Tomás Villacrés","CED 1719876543"),"Quito",c2("Cambridge · C1 Advanced","10 oct 2026"),"000021043 · pagada","—",badge("Esperando resultados","warn"),btn("Registrar resultado")],
  [c2("Paula Ortiz","PAS AB123456"),"Valle",c2("TOEFL iBT","26 sep 2026"),"000021020 · pagada","96 · B2",badge("Listo para retirar","ok"),btn("Registrar resultado")],
  [c2("Daniel Paz","CED 1803456789"),"Ambato",c2("Oxford Test of English","19 sep 2026"),"000020998 · pagada","128 · B2",badge("Entregado","neutral"),btn("Registrar resultado")],
  [c2("Emilia Torres","CED 1724567890 · 12 años"),"Valle",c2("Cambridge · A2 Key for Schools","5 dic 2026"),"000021105 · crédito","—",badge("Inscrito","navy"),btn("Registrar resultado")],
  [c2("Gabriel Mora","CED 1712349876"),"Quito",c2("Anglia · Intermediate","28 nov 2026"),"000021110 · pagada","—",badge("Inscrito","navy"),btn("Registrar resultado")]],sede=1,wide=0),
 card("Reporte por examen", table(["Examen","Internos","Externos","Importe","Asesor con más ventas"],[["B2 First (FCE)","12","5","$3,995","Carla M."],["C1 Advanced","4","3","$1,925","Diego R."],["TOEFL iBT","2","6","$1,600","Ana P."]])),
 card("Flujo", flow(["Inscripción y factura","Envío al centro autorizado","Esperando resultados","Puntaje y nivel","Listo para retirar","Entregado con firma"])),
 subtitle="Propuesta para validar con Cambridge: hoy se gestiona en la tabla International Exams de TeamDesk"),"Exámenes internacionales")


# ===== Procesos comerciales (documento de Dirección Comercial, oct 2026) =====
CONCEPTOS=[("Servicios educativos","formación vendida · base de metas",CH[0]),("Inscripción","derecho de matrícula",CH[1]),("Materiales","libros y digital packs",CH[2]),("Exámenes internacionales","Cambridge, Oxford, TOEFL, Anglia",CH[3]),("Traducciones","las registra Secretaría",CH[4] if len(CH)>4 else CH[0]),("Mercadería","tomatodos, camisetas, otros",CH[5] if len(CH)>5 else CH[1])]

# Detalle de venta: la compra completa con módulos, facturas, pago único y aplicaciones de saldo
page("DetalleVenta.html","Detalle de venta",shell("Venta V-2026-0412","Tablero comercial",
 hero([("Estudiante",'<a href="Ficha360.html">María Andrade</a>'),("Asesor original","Carla M."),("Sede","Quito"),("Fecha de venta","28 ago 2026"),("Clasificación","Continuidad"),("Origen","Referido · Kommo KM-48213"),("Programa · modalidad","Adults (ESL) · Virtual"),("Compra","3 módulos · B1 y B1+")],
  btn("Corregir clasificación")+btn("Exportar"),
  progress(33,"Aplicado a matrículas · $200 de $600 pagados"),
  tag='<span class="hero-code">V-2026-0412</span>'+badge("Pagada","ok")+badge("Saldo a favor $400","navy")),
 kpis([("Valor total vendido","$600","servicios educativos de 3 módulos"),("Facturado a la fecha","$200","1 factura · módulo 7"),("Cobrado","$600","pago único · 28 ago"),("Saldo a favor","$400","para los módulos 8 y 9")]),
 two(card("Conceptos de la venta", table(["Concepto","Valor","Cuenta para metas"],[["Servicios educativos (3 módulos × $200)","$600",badge("Sí","ok")],["Inscripción","$0 · exonerada",badge("No","neutral")],["Materiales","se venden aparte",badge("No","neutral")]])),
     card("Fechas de la venta", table(["Evento","Fecha","Monto"],[["Venta","28 ago 2026","$600"],["Factura módulo 7","28 ago 2026","$200"],["Pago único","28 ago 2026","$600"],["Aplicación de saldo · módulo 8","3 nov 2026 (programada)","$200"],["Aplicación de saldo · módulo 9","ene 2027 (programada)","$200"]]))),
 card("Módulos, matrículas, facturas y aplicaciones del saldo", table(["Módulo","Matrícula","Factura","Pagado con","Estado","Acción"],[
   [c2("Módulo 7 · B1","0001-2026-0767 · Virtual"),"001-202602794","000021090","pago PG-0942 · $200",badge("En curso","ok"),'<a href="DetalleMatricula.html">Ver</a>'],
   [c2("Módulo 8 · B1","mismo grupo · inicia 3 nov"),"por crear (Secretaría)","por emitir","saldo a favor · $200",badge("Pendiente de continuidad","warn"),'<a href="MatriculaContinuidad.html">Matricular</a>'],
   [c2("Módulo 9 · B1+","por abrir · sábados"),"por crear (Secretaría)","por emitir","saldo a favor · $200",badge("Pagado · sin curso aún","neutral"),'<a href="MatriculaContinuidad.html">Matricular</a>']],wide=0)
   +kv(("Pago único","PG-0942 · transferencia · $600 · validado por Contabilidad y confirmado por Secretaría"),("Regla","cada aplicación consume el saldo sin generar otra venta ni otro cobro"))),
 card("Historial", table(["Fecha","Usuario","Acción"],[["28 ago 10:11","Carla M.","Creó la venta (3 módulos · nivel completo B1 + módulo 9)"],["28 ago 10:20","Carla M.","Registró el pago de $600 y subió el comprobante"],["28 ago 16:05","Contabilidad","Validó la transferencia"],["28 ago 16:30","Secretaría","Confirmó el pago en el sistema"]])),
 subtitle="La compra completa: valor vendido, módulos, facturas, pago único y saldo a favor, sin duplicar ventas ni cobros"),"Detalle de venta")

# Matrícula de continuidad (Secretaría): aplica el saldo a favor
page("MatriculaContinuidad.html","Matrícula de continuidad",shell("Matrícula de continuidad","Facturación",
 wizcard(step(1,"Estudiante y venta original", kv(("Estudiante","María Andrade"),("Venta","V-2026-0412 · asesor original Carla M."),("Saldo a favor","$400.00"),("Módulos pagados por cursar","8 y 9")))
  +step(2,"Siguiente módulo y curso", form([("Módulo","Módulo 8 · B1","select",["Módulo 8 · B1","Módulo 9 · B1+"],True),("Curso","0001-2026-0767 · Virtual · Lu-Ma-Mi-Ju 19:00–21:00 · 12/15","select",["0001-2026-0767 · Virtual · Lu-Ma-Mi-Ju 19:00–21:00 · 12/15","0001-2026-0781 · Presencial Quito · Sa 09:00–13:00 · 9/15"],True)],cols=2))
  +step(3,"Aplicar el saldo y facturar el módulo", table(["Concepto","Monto"],[["Valor del módulo 8 (precio de la venta original)","$200.00"],["Aplicado desde el saldo a favor","-$200.00"],["A cobrar ahora","$0.00"],["Saldo a favor que queda","$200.00"]])
     +kv(("Factura","se emite la del módulo 8, relacionada con la misma venta y el mismo pago"),("Para metas y comisiones","no cuenta como venta nueva ni como cobro del mes")))),
 foot(btn("Aplicar saldo a favor",None,True),btn("Emitir factura del módulo"),btn("Cancelar","Facturas.html")),
 subtitle="Secretaría matricula en el siguiente módulo usando el saldo ya pagado"),"Matrícula de continuidad")

# Inscripción a examen internacional (venta, factura, pago e inscripción)
page("NuevaInscripcionExamen.html","Inscripción a examen",shell("Nueva inscripción a examen internacional","Exámenes",
 wizcard(step(1,"Cliente y destinatario de la factura", form([("Tipo de cliente","Estudiante de Cambridge","select",["Estudiante de Cambridge","Cliente externo"],True),("Estudiante","Lucía Benítez · CED 1716543210","text",None,False,"Si es estudiante se reutiliza su ficha"),("Facturar a","Su madre · Carmen Ortiz · CED 1705432198","select",["La misma candidata","Su madre · Carmen Ortiz · CED 1705432198","Empresa","Otra persona"],True,"El destinatario puede ser distinto del candidato")],cols=3))
  +step(2,"Examen, tarifa y pago", form([("Categoría","Cambridge","select",["Cambridge","Oxford","TOEFL","Anglia"],True),("Examen","B2 First (FCE)","select",["A2 Key","B1 Preliminary","B2 First (FCE)","C1 Advanced"],True),("Tarifa vigente","$235.00","text",None,False,"Automático"),("Forma de pago","Tarjeta de crédito","select",["Efectivo","Tarjeta de crédito","Tarjeta de débito","Transferencia","Depósito"],True)],cols=4)
     +kv(("Factura","000021101 · se emite al registrar el pago"),("Validación del pago","posterior, por Contabilidad")))
  +step(3,"Datos de quien rendirá el examen", form([("Apellidos","Benítez Ortiz","text",None,True),("Nombres","Lucía","text",None,True),("Género","Femenino","select",["Femenino","Masculino","Otro"],True),("Identificación","1716543210","text",None,True),("Fecha de nacimiento","2001-05-14","date",None,True),("Celular","099 000 0031","tel",None,True),("Correo","lucia.b@ejemplo.com","email",None,True,"Para las comunicaciones del examen")],cols=4)
     +upload("Identificación del candidato (parte frontal)","Foto o PDF · se contrasta con nombres y fecha de nacimiento"))
  +step(4,"Fecha del calendario anual", table(["Fecha","Sede","Cierre de inscripción","Disponible"],[["14 nov 2026","Quito","25 oct",badge("Sí · faltan 26 días","ok")],["5 dic 2026","Quito","15 nov",badge("Sí","ok")],["7 nov 2026","Valle","18 oct",badge("No · menos de 20 días","bad")]])
     +kv(("Regla","la inscripción debe hacerse con al menos 20 días de anticipación")))
  +step(5,"Verificar con el cliente y enviar", kv(("Revisar","datos, examen y fecha con el cliente (puede enviarse una captura)"))+row(btn("Imprimir y enviar")))),
 foot(btn("Inscribir candidato",None,True),btn("Cancelar","ExamenesInternacionales.html")),
 subtitle="Venta, factura, pago e inscripción vinculados; candidato separado del pagador"),"Inscripción a examen")

# Venta de mercadería
page("VentaMercaderia.html","Venta de mercadería",shell("Venta de mercadería","Facturación",
 wizcard(step(1,"Cliente y factura", form([("Cliente","María Andrade · CED 1712345678","text",None,True,"Estudiante registrado o cliente externo"),("Facturar a","La misma estudiante","select",["La misma estudiante","Consumidor final","Otra persona"],True)],cols=2))
  +step(2,"Producto", table(["Producto","Precio","Stock en tu sede","Cantidad"],[["Tomatodo Cambridge","$12.00 · IVA incluido",badge("18","ok"),"1"],["Camiseta Summer Camp · talla M","$15.00",badge("4","warn"),"0"],["Cuaderno Cambridge","$4.50",badge("0","bad"),"0"]]))
  +step(3,"Pago y entrega", form([("Forma de pago","Efectivo","select",["Efectivo","Tarjeta de débito","Tarjeta de crédito","Transferencia"],True),("Monto","$12.00","text",None,False,"Automático")],cols=2)
     +kv(("Al guardar","factura de mercadería, pago registrado y stock descontado; luego se entrega el artículo")))),
 foot(btn("Registrar venta y entregar",None,True),btn("Cancelar","Facturas.html")),
 subtitle="La mercadería se registra aparte de los servicios educativos, la inscripción y los materiales"),"Venta de mercadería")

# Informe mensual de comisiones del asesor (anexo 1)
page("InformeComisiones.html","Informe de comisiones",shell("Mi informe de comisiones · Octubre 2026","Comisiones",
 flow(["Asesor revisa y envía","Dirección Comercial revisa","Administración revisa y asigna el pago"]),
 kpis([("Ventas del mes","9","6 nuevas · 2 reingresos · 1 continuidad"),("Servicios educativos vendidos","$4,860","base de la meta"),("Total facturado","$5,320","incluye inscripción y materiales"),("Cobros del mes de ventas anteriores","$980","2 ventas de septiembre")]),
 card("Ventas del mes", filters(sel("Sede",["Todas","Quito","Valle"],w="130px",col=False),actions=btn("Exportar Excel"))+table(["Fecha","Estudiante · venta","Módulos vendidos","Total facturado","Servicios educativos","Programa · modalidad","Sede"],[
   ["03 oct",c2('<a href="DetalleVenta.html">Sofía Herrera</a>',"V-2026-0398 · 001-202603218"),"2 · nivel B1","$530","$450","Adults · Virtual","Quito"],
   ["08 oct",c2('<a href="DetalleVenta.html">Andrés Pazmiño</a>',"V-2026-0403 · 001-202603230"),"1","$275","$230","Adults · Presencial","Quito"],
   ["12 oct",c2('<a href="DetalleVenta.html">Paula Ortiz</a>',"V-2026-0407 · venta en otra sede"),"4 · B1 y B1+","$1,060","$920","Adults · Virtual","Valle"],
   ["15 oct",c2('<a href="DetalleVenta.html">Gabriel Mora</a>',"V-2026-0411 · 001-202603241"),"2 · nivel A1","$500","$420","Teens · Presencial","Quito"]],wide=1)),
 card("Cobros del mes de ventas anteriores", table(["Venta original","Fecha de venta","Asesor original","Cobrado en octubre","Cuenta como"],[[c2('<a href="DetalleVenta.html">V-2026-0371</a>',"Gabriela Núñez · cuota 2"),"18 sep","Carla M.","$225",badge("Cobro, no venta nueva","navy")],[c2('<a href="DetalleVenta.html">V-2026-0365</a>',"Mateo Salazar · saldo"),"5 sep","Carla M.","$755",badge("Cobro, no venta nueva","navy")]])),
 foot(only("ASE",btn("Enviar a Dirección Comercial",None,True),True)+only("DIR",btn("Aprobar y enviar a Administración",None,True),True)+only("ADM,GER",btn("Asignar pago de comisión",None,True),True)+only("DIR,ADM,GER",btn("Devolver con observaciones"),True)+btn("Volver","Comisiones.html")),
 subtitle="Reemplaza el registro manual del asesor: ventas, servicios educativos y cobros de ventas anteriores con su asesor original"),"Informe de comisiones del asesor")

# Tablero comercial (diario y mensual) y consolidado de Dirección Comercial (anexo 2)
conc_tbl=table(["Concepto","Hoy","Mes","Meta","Cumplimiento"],[[c2("Servicios educativos","base de metas"),"$1,240",sv("$18,460","$9,820","$4,310","$2,630","$1,700"),"$20,000",badge("92%","warn")],["Inscripción","$80","$1,520","—","—"],["Materiales","$160","$2,880","—","—"],["Exámenes internacionales","$235","$3,290","—","—"],["Traducciones","$0","$420","—","—"],["Mercadería","$27","$310","—","—"]],wide=0,hide=(3,))
page("TableroComercial.html","Tablero comercial",shell("Tablero comercial","Tablero comercial",
 filters(sel("Período",["Hoy","Este mes","Mes anterior","Este año"],w="140px",col=False),sel("Asesor",["Todos","Carla M.","Diego R.","Sofía L.","Ana P."],w="140px",col=False),sel("Programa",["Todos","Preescolar","Kids","Teens","Adults","Business"],w="140px",col=False),sel("Modalidad",["Todas","Virtual","Presencial"],w="130px",col=False),sel("Origen",["Todos","Estrategia pagada","Referido","Walk-in","Exalumno","Convenio o alianza","Feria","Lead anterior"],w="170px",col=False),sel("Datos",["Solo plataforma nueva","Incluir histórico TeamDesk (referencia)"],w="250px",col=False),actions=btn("Exportar Excel"),show=3),
 kpis([("Nuevas matrículas válidas",sv(46,24,11,7,4),"meta 52 · 88%"),("Servicios educativos",sv("$18,460","$9,820","$4,310","$2,630","$1,700"),"meta $20,000 · 92%"),("Total facturado",sv("$26,880","$14,100","$6,420","$3,960","$2,400"),"todos los conceptos"),("Cobros del período",sv("$24,310","$12,900","$5,880","$3,530","$2,000"),"incluye $3,120 de ventas anteriores")]),
 tabs(["Hoy y acumulado","Ventas","Cobros del período","Clasificación","Consolidado por sede","Origen y oferta"],"Hoy y acumulado",roles={"Consolidado por sede":"ADM,GER,DIR,SUC"},panels={
  "Hoy y acumulado": two(card("Por concepto (no se mezclan)", conc_tbl),
     card("Indicadores", kv(("Ventas","38 · 52 módulos · 21 niveles"),("Ticket de servicios por matrícula válida","$401"),("Ticket total por venta","$707"),("Saldos pendientes","$4,120 · 17 estudiantes"),("Saldos a favor","$6,800 · 23 ventas")))
       +linechart(["1","5","10","15","19"],{"Servicios 2026":[1.2,5.4,9.8,14.6,18.5],"Mismo día 2025":[1.0,4.8,9.1,13.0,16.2]})),
  "Ventas": table(["Fecha de venta","Venta · estudiante","Clasificación","Módulos · niveles","Servicios educativos","Asesor · sede","Acción"],[
    ["19 oct",c2("V-2026-0412","María Andrade"),badge("Continuidad","neutral"),"3 · 1 nivel","$600","Carla M. · Quito",'<a href="DetalleVenta.html">Ver venta</a>'],
    ["18 oct",c2("V-2026-0411","Gabriel Mora"),badge("Nueva","ok"),"2 · 1 nivel","$420","Carla M. · Quito",'<a href="DetalleVenta.html">Ver venta</a>'],
    ["17 oct",c2("V-2026-0409","Pedro Mora"),badge("Reingreso","navy"),"1","$230","Diego R. · Valle",'<a href="DetalleVenta.html">Ver venta</a>'],
    ["17 oct",c2("V-2026-0405","Martín Ortega"),badge("Nueva","ok"),"4 · 2 niveles","$880","Ana P. · Cuenca",'<a href="DetalleVenta.html">Ver venta</a>'],
    ["16 oct",c2("V-2026-0401","Camila Sánchez"),badge("Nueva","ok"),"2 · 1 nivel","$460","Sofía L. · Ambato",'<a href="DetalleVenta.html">Ver venta</a>']],sede=5,wide=1)+pager(38),
  "Cobros del período": table(["Fecha de cobro","Venta original","Fecha de venta","Asesor original","Monto","Tipo"],[["19 oct",c2('<a href="DetalleVenta.html">V-2026-0371</a>',"Gabriela Núñez · cuota 2"),"18 sep","Carla M.","$225",badge("Venta anterior","navy")],["18 oct",c2('<a href="DetalleVenta.html">V-2026-0411</a>',"Gabriel Mora"),"18 oct","Carla M.","$500",badge("Venta del mes","ok")],["15 oct",c2('<a href="DetalleVenta.html">V-2026-0352</a>',"Tomás Villacrés · saldo"),"30 ago","Diego R.","$410",badge("Venta anterior","navy")]],wide=1)
     +kv(("Aplicaciones de saldo a favor","no aparecen aquí: no son cobros nuevos")),
  "Clasificación": table(["Matrícula","Estudiante","Clasificada como","Debería ser","Acción"],[["001-202603241","Gabriel Mora",badge("Nueva","ok"),"Nueva",btn("Corregir clasificación")],["001-202603236","Valeria Cedeño",badge("Nueva","ok"),"Reingreso · estudió en 2024",btn("Corregir clasificación")],["001-202603230","Andrés Pazmiño",badge("Continuidad","neutral"),"Nueva",btn("Corregir clasificación")]],wide=1)
     +kv(("Regla","solo las nuevas válidas cuentan para la meta de matrículas; cada corrección queda trazada")),
  "Consolidado por sede": table(["Sede","Matrículas oct 2026","Oct 2025","Variación","Servicios educativos","Meta","Cumplimiento"],[["Quito","24","21","+14%","$9,820","$10,000",badge("98%","ok")],["Valle","11","13","-15%","$4,310","$5,000",badge("86%","warn")],["Ambato","7","6","+17%","$2,630","$3,000",badge("88%","warn")],["Cuenca","4","—","sin base","$1,700","$2,000",badge("85%","warn")]],sede=0,wide=0)
     +kv(("Comparación","mismo número de días transcurridos y mismos conceptos (sin inscripción ni materiales)"),("Sin base de comparación","se muestra 'sin base' en lugar de dividir por cero"))+row(btn("Editar metas")),
  "Origen y oferta": two(card("Ventas por origen del lead", hbars([("Estrategia pagada",14),("Referido",9),("Walk-in",6),("Exalumno",4),("Convenio o alianza",3),("Feria",1),("Lead anterior",1)],unit="")),
     card("Ventas por oferta", hbars([("Niveles",21),("One to one",6),("Certificaciones (exámenes)",14),("Traducciones",3),("Cursos de español",2)],unit=""))),
 }),
 subtitle="Ventas, facturación, servicios educativos y cobros con cifras reales; cada total abre su detalle"),"Tablero comercial")
# 6 Aprobaciones
apr=shell("Bandeja de aprobaciones","Aprobaciones",
 tabs(["Todas (3)","Descuentos","Tarifas de profesores","Asignaciones"],"Todas (3)",{
  "Todas (3)": table(["Tipo","Detalle","Solicitado por","Fecha","Acción"],[["Descuento","42% · Gabriela Núñez · A2 · motivo: referido","Carla M. (asesor)","Hoy",row(btn("Aprobar",None,True),btn("Rechazar"),gap=8)],["Tarifa de profesor","D. Paredes · $9.00/h · fuera de la tabla ($6.50–$7.50)","Coordinación académica","Ayer",row(btn("Aprobar",None,True),btn("Rechazar"),gap=8)],["Asignación","Profesor sin contrato activo en curso B1","Coordinación académica","Ayer",row(btn("Aprobar",None,True),btn("Rechazar"),gap=8)]],h=64),
  "Descuentos": table(["Tipo","Detalle","Solicitado por","Fecha","Acción"],[["Descuento","42% · Gabriela Núñez · A2 · motivo: referido","Carla M. (asesor)","Hoy",row(btn("Aprobar",None,True),btn("Rechazar"),gap=8)]],h=64)+note("Regla vigente: hasta 10% lo aplica el asesor. Más de 10% requiere Director Comercial."),
  "Tarifas de profesores": table(["Tipo","Detalle","Solicitado por","Fecha","Acción"],[["Tarifa de profesor","D. Paredes · $9.00/h · fuera de la tabla ($6.50–$7.50)","Coordinación académica","Ayer",row(btn("Aprobar",None,True),btn("Rechazar"),gap=8)]],h=64)+note(""),
  "Asignaciones": table(["Tipo","Detalle","Solicitado por","Fecha","Acción"],[["Asignación","Profesor sin contrato activo en curso B1","Coordinación académica","Ayer",row(btn("Aprobar",None,True),btn("Rechazar"),gap=8)]],h=64)+note("Se bloquea la asignación de un profesor sin contrato vigente hasta que Coordinación apruebe la excepción.","warn"),
 }),
 card("Decisiones recientes", table(["Fecha","Tipo","Detalle","Decisión","Por","Justificación"],[["Ayer 16:20","Descuento","15% · Ana Ruiz","Aprobado","Dir. Comercial","Convenio empresa"],["Ayer 11:05","Tarifa de profesor","M. Castro · $8.00/h","Aprobado","Dirección","Perfil CELTA · justificado"],["02 oct","Descuento","30% · Luis Torres","Rechazado","Dir. Comercial","Sin motivo válido"]])+note("Cada decisión queda en el audit log con quién, cuándo y justificación. El solicitante recibe notificación en la plataforma y por email.")),
 subtitle="Control preventivo: nada sensible pasa sin un segundo par de ojos")
page("Aprobaciones.html","Aprobaciones",apr,"Bandeja de aprobaciones")

# 7 Cursos
V='<a href="DetalleCurso.html">Ver</a>'
cursos=shell("Cursos","Cursos",
 filters(search("Buscar","Código, nombre o profesor",w="240px"),sel("Vista",["Todos los cursos","Cursos abiertos por horario","Disponibilidad (cupos libres)","Cursos con saldos de estudiantes","Terminados sin calificar","Próximos a iniciar","Cerrados"],w="230px",col=False),sel("Programa",["Todos","Adults","Teens","Kids","Tailored"],w="130px"),sel("Nivel",NIVEL_FILTRO+["Kids 1","Kids 2"],w="110px"),sel("Modalidad",["Todas","Virtual","Presencial"],w="130px"),sel("Profesor",["Todos","P. Gómez","L. Vega","M. Castro","(sin asignar)"],w="150px"),sel("Estado",["Todos","En curso","Por abrir","Sin calificar","Cerrado"],w="160px"),actions=only("ADM,GER,SUC,COO",btn("Nuevo curso",None,True),True)),
 only(COMERCIAL, kpis([("Cursos en curso",sv(41,22,12,7),"esta semana"),("Por abrir",sv(6,2,3,1),"inician en 30 días"),("Con saldos de estudiantes",sv(9,4,3,2),sv("$2,840 pendientes","$1,320","$980","$540")),("Terminados sin calificar",sv(2,1,1,0),"bloquean certificados")])),
 only("COO,PRO", kpis([("Cursos en curso",sv(41,22,12,7),"esta semana"),("Por abrir",sv(6,2,3,1),"inician en 30 días"),("Sesiones por confirmar",sv(3,2,1,0),"de esta semana"),("Terminados sin calificar",sv(2,1,1,0),"bloquean certificados")])),
 ltable("cursos",["Curso","Sede","Programa","Modalidad","Nivel","Profesor","Cupo","Avance","Estado","Acción"],[
  [c2("English for Adults B1 Virtual","0001-2026-0767 · Quito · Zoom 2 · Lu-Ma-Mi-Ju 19:00–21:00 · Virtual"),"Quito","Adults","Virtual","B1","P. Gómez","12/15",progress(60),badge("En curso","ok"),V],
  [c2("English for Kids 2 Tarde","0001-2026-0328 · Valle · C-3 · Sa 09:00–13:00 · Presencial"),"Valle","Kids","Presencial","Kids 2","L. Vega","8/10",progress(55),badge("En curso","ok"),V],
  [c2("English for Teens A2","0001-2026-0192 · Ambato · A-1 · Vi 15:00–19:00 · Presencial"),"Ambato","Teens","Presencial","A2","(sin asignar)","5/10",progress(0),badge("Por abrir","warn"),V],
  [c2("English for Adults A2","0001-2026-0620 · Valle · C-5 · Lu-Mi 14:00–16:00 · Presencial"),"Valle","Adults","Presencial","A2","P. Gómez","9/12",progress(59),badge("En curso","ok"),V],
  [c2("English for Kids 1 Mañana","0001-2026-0518 · Ambato · A-2 · Lu-Mi 16:00–18:00 · Presencial"),"Ambato","Kids","Presencial","Kids 1","M. Castro","7/10",progress(28),badge("En curso","ok"),V],
  [c2("English for Adults B2 Intensivo","0001-2026-0538 · Quito · Q-4 · Sa 09:00–13:00 · Presencial"),"Quito","Adults","Presencial","B2","L. Vega","11/12",progress(46),badge("En curso","ok"),V],
  [c2("English for Adults A1 Sábados","0001-2026-0430 · Quito · Q-1 · Sa 09:00–13:00 · Presencial"),"Quito","Adults","Presencial","A1","L. Vega","14/15",progress(100),badge("Sin calificar","bad"),V],
  [c2("English for Teens B1 Virtual","0001-2026-0772 · Valle · Teams 1 · Lu-Ma-Mi-Ju 17:00–19:00 · Virtual"),"Valle","Teens","Virtual","B1","P. Gómez (propuesto)","6/12",progress(0),badge("Por abrir","warn"),V],
  [c2("English for Kids 2 Mañana","0001-2026-0599 · Quito · Q-2 · Sa 09:00–13:00 · Presencial"),"Quito","Kids","Presencial","Kids 2","M. Castro","10/10",progress(53),badge("En curso","ok"),V],
  [c2("Tailored · Inglés corporativo","0001-2026-0608 · Ambato · Zoom 1 · Ma-Ju 07:00–08:30 · Virtual"),"Ambato","Tailored","Virtual","B1","(sin asignar)","3/12",progress(0),badge("Por abrir","warn"),V],
  [c2("English for Teens A2","0001-2025-0330 · Valle · C-2 · Vi 15:00–19:00 · Presencial"),"Valle","Teens","Presencial","A2","L. Vega","9/10",progress(100),badge("Cerrado"),V]],sede=1,hide=(1,2,3),wide=0),
 pager(sv(58,29,18,11)),
 only("ADM,GER,DIR,SUC,COO,ASE,SEC", card("Reaperturas · cursos al 75% que terminan en las próximas semanas", filters(sel("Semana",["Esta semana","Próxima semana"],w="150px",col=False),actions=btn("Registrar contacto de reapertura",None,True)+btn("Enviar reporte semanal de reaperturas"))
   +table(["Curso que termina","Sede","Siguiente curso","Estudiantes","Contactados","Confirmados","Perdidos · motivo","Acción"],[
    [c2("English for Adults B1 Virtual · módulo 8","0001-2026-0767 · termina 20 nov"),"Quito",c2("B1+ Virtual · módulos 9–10","0001-2026-0801 · upcoming · Lu-Ju 19:00"),"12","10","7",c2("2","precio 1 · horario 1"),btn("Registrar contacto de reapertura")],
    [c2("English for Kids 2 Tarde","0001-2026-0328 · termina 28 nov"),"Valle",c2("Kids 3 Tarde","0001-2026-0812 · upcoming · Sa 09:00"),"8","8","6",c2("1","se muda"),btn("Registrar contacto de reapertura")],
    [c2("English for Adults A2","0001-2026-0620 · termina 4 dic"),"Valle",c2("B1 Presencial","por crear · Lu-Mi 14:00"),"9","3","1",c2("0","—"),btn("Registrar contacto de reapertura")],
    [c2("English for Kids 1 Mañana","0001-2026-0518 · termina 12 dic"),"Ambato",c2("Kids 2 Mañana","por crear"),"7","0","0",c2("0","aún no inicia el contacto"),btn("Registrar contacto de reapertura")]],sede=1,hide=(1,),wide=0)
   +kv(("Protocolo","al 75% del curso: mensaje de WhatsApp → llamada → nota de voz; 10% de descuento al pagar 2 módulos"),("Cuándo","se crean los cursos de continuidad como 'upcoming' y se revisa el cuadro cada jueves"),("Control","Dirección Académica audita entre el 10% y el 20% de los contactos registrados")))),
 note("El código de curso conserva el formato de TeamDesk (0001-AAAA-NNNN) para la migración y la reconciliación. Avance = % de horas dictadas sobre el total."),
 only("ADM,GER,SUC,COO", ai([("Adults A1 Sábados terminó hace 5 días sin calificar: 14 estudiantes no pueden matricularse en A2 y hay 3 cupos esperándolos en 0001-2026-0620.","Calificar","DetalleCurso.html"),("Dos cursos 'por abrir' en Ambato tienen menos de 5 inscritos a 2 semanas del inicio. Históricamente no abren con menos de 6.","Ver cursos de Ambato","Cursos.html"),("El aula Q-1 está al 60% de ocupación y C-2 (Valle) al 0%: el nuevo Kids 2 podría ir a C-2 el sábado.","Ver aulas","Configuracion.html")],"Pregunta: ¿qué cursos abren en noviembre y cuántos libros necesitan?")),
 subtitle="Programa, nivel, modalidad, horario y aula por sede")
page("Cursos.html","Cursos",cursos,"Listado de cursos")

# 8 Detalle curso
det=shell("English for Adults B1 Virtual","Cursos",
 hero([("Programa","English for Adults"),("Nivel","B1 · módulos 7–8"),("Modalidad","Virtual · Zoom 2"),("Horario","Lu-Ma-Mi-Ju 19:00–21:00"),("Inicio","1 sep 2026"),("Fin","20 nov 2026"),("Cupo","12 / 15"),("Libro","Empower B1+ Combo B")],
  btn("Registrar sesión",None,True)+btn("Enviar enlace de clase")+btn("Hoja de asistencia")+only("ADM,GER,SUC,COO",btn("Calificar profesor")+btn("Editar curso"),True),
  progress(60,"Avance del curso · 22 de 36 horas dictadas · termina en 7 semanas"),
  tag='<span class="hero-code">0001-2026-0767</span>'+badge("En curso","ok")+badge("Quito","navy")),
 two(card("Profesor asignado", kv(("Profesor",'<a href="FichaProfesor.html">P. Gómez</a>'),("Contrato",badge("Activo hasta dic 2026","ok")),("Horas en este curso","22 h dictadas"))+only("ADM,GER,SUC",kv(("Tarifa","$7.00/h · $154 en este curso")))+only("ADM,GER,SUC,COO",filters(sel("Cambiar profesor",["P. Gómez","L. Vega","M. Castro","R. Salas (contrato vencido)"],w="260px"),actions=btn("Cambiar",None,False,"Si el nuevo profesor no tiene contrato activo, el cambio queda pendiente de aprobación de Coordinación.")))),
     card("Sesiones", table(["Fecha","Horas","Registro"],[["Lu 12 oct","2","Automático"],["Ma 13 oct","2","Automático"],["Mi 14 oct","2","Manual"],["Ju 15 oct","2","Automático"],["Lu 19 oct","2","Pendiente"]]))),
 card("Estudiantes matriculados", only(COMERCIAL, filters(sel("Mostrar",["Todos","Con saldo pendiente","En riesgo (asistencia < 75%)"],w="220px",col=False),actions=only("ADM,GER,DIR,SUC",btn("Exportar"),True))+table(["Matrícula","Estudiante","Asistencia","Total","Pagado","Saldo","Estado","Acción"],[
  ["001-202602794",c2('<a href="Ficha360.html">María Andrade</a>',"001-202602794 · 099 000 0001"),"90%","$305","$305","$0",badge("En curso","ok"),'<a href="DetalleMatricula.html">Ver</a>'],
  ["001-202602846",c2('<a href="Ficha360.html">Pedro Mora</a>',"001-202602846 · 099 000 0002"),"85%","$250","$0","$250",badge("Factura vencida","bad"),'<a href="DetalleMatricula.html">Ver</a>'],
  ["001-202602871",c2('<a href="Ficha360.html">Sofía Herrera</a>',"001-202602871 · 099 000 0005"),"70%","$230","$230","$0",badge("Riesgo asistencia","bad"),'<a href="DetalleMatricula.html">Ver</a>'],
  ["001-202602875",c2('<a href="Ficha360.html">Andrés Pazmiño</a>',"001-202602875 · 099 000 0006"),"45%","$195","$0","$195",badge("Sin pago · riesgo","bad"),'<a href="DetalleMatricula.html">Ver</a>']],hide=(0,),wide=1)+kv(("Matriculados","12/15"),("Saldo pendiente del curso","$445"),("Asistencia promedio","84%")))
  +only("COO,PRO", filters(sel("Mostrar",["Todos","En riesgo (asistencia < 75%)"],w="220px",col=False),actions=btn("Calificar curso",None,True)+only("COO",btn("Exportar"),True))+table(["Estudiante","Asistencia","Nota parcial","Muro","Estado","Acción"],[
  [c2('<a href="Ficha360.html">María Andrade</a>',"001-202602794"),"90%","8.4","100% módulo 7",badge("En curso","ok"),'<a href="CalificarCurso.html">Calificar</a>'],
  [c2('<a href="Ficha360.html">Pedro Mora</a>',"001-202602846"),"85%","7.6","90%",badge("En curso","ok"),'<a href="CalificarCurso.html">Calificar</a>'],
  [c2('<a href="Ficha360.html">Sofía Herrera</a>',"001-202602871"),"70%","6.9","75%",badge("Riesgo asistencia","bad"),'<a href="CalificarCurso.html">Calificar</a>'],
  [c2('<a href="Ficha360.html">Andrés Pazmiño</a>',"001-202602875"),"45%","—","30%",badge("Riesgo asistencia","bad"),'<a href="CalificarCurso.html">Calificar</a>']],wide=0)+kv(("Matriculados","12/15"),("Asistencia promedio","84%"),("Mínimo para aprobar","75% de asistencia y nota ≥ 7")))
  +only("ADM,GER,SUC",row(btn("Calificar curso",None,True)))),
 only("ADM,GER,DIR,SUC,COO,PRO,SEC", card("Seguimiento del curso · apertura, acompañamiento y cierre", flow([
   ("Crear el curso en Cambridge One y GradeKeeper","72 h antes del inicio · Coord. Académica","Hecho · 28 ago","done"),
   ("Correo informativo a los estudiantes (YAMM)","48 h antes · horario, aula o enlace, libro y profesor","Hecho · 30 ago","done"),
   ("Grupo de WhatsApp y contrato firmado","Grupo solo informativo; ningún estudiante inicia sin contrato firmado","Hecho · 12 de 12","done"),
   ("Recepción y bienvenida","Primera clase: presentación, reglas, acceso a plataformas","Hecho · 1 sep","done"),
   ("Checklist de bienvenida","Segunda clase: libros entregados, códigos activados, Teams","Hecho · 2 sep","done"),
   ("Observación de clase","Al 20% del curso · rúbrica de observación y retroalimentación al profesor","Hecho · 15 sep · 4.2/5","done"),
   ("Follow up con estudiantes","Al 50% · asistencia, notas parciales, saldos; llamada a los que están en riesgo","Hecho · 6 oct · 2 en riesgo","done"),
   ("Mensaje de próximo módulo y Mock Test","Al 75% · oferta del siguiente curso (reapertura) y agendar Mock Test","Vence 30 oct","now"),
   ("Encuesta de satisfacción","Última semana · se envía a todos los estudiantes",""," "),
   ("Cierre del curso","72 h después de la última clase: speaking mock, notas en GradeKeeper en 48 h, End of level report",""," ")])
   +kv(("Responsables","Coord. Académica · profesor · Secretaría"),("Regla","un curso no se cierra sin notas ni se envía nota a un estudiante con deuda"))+row(btn("Marcar tarea cumplida",None,True)))),
 only("ADM,GER,DIR,SUC,COO,SEC", card("Indexados · agregar estudiantes al curso", kv(("Regular","con 48 h o más de anticipación · correo con asunto |REGULAR| INDEXO ESTUDIANTES"),("Urgente","menos de 24 h · solo con autorización de Coord. Académica · asunto |URGENTE|"),("Aviso","grupo de WhatsApp |IMPORTANTE| INDEXADOS CAMBRIDGE SOL"),("Nivelación","si entra en la primera semana rinde la prueba de ubicación antes de la clase"),("Último indexado","Sofía Herrera · regular · 8 sep · 3 días antes"))+row(btn("Solicitar indexado",None,True)))),
 only(COMERCIAL+",COO",card("Lista de espera", table(["Estudiante","Desde","Asesor","Estado","Acción"],[["Lucía Benítez","10 oct","Carla M.",badge("Primera en la lista","navy"),btn("Ofrecer cupo")],["Tomás Villacrés","14 oct","Diego R.",badge("Esperando","neutral"),btn("Ofrecer cupo")]])+kv(("Regla","al liberarse un cupo se avisa al primero; tiene 48 h para confirmar")))),
 subtitle="Las sesiones registradas aquí alimentan la payment sheet del profesor y el progreso del estudiante")
page("DetalleCurso.html","Detalle curso",det,"Detalle de curso y sesiones")

# 9 Profesores
prof=shell("Profesores","Profesores",
 filters(search("Buscar","Nombre o cédula",w="260px"),sel("Estado",["Todos","Activo","Standby","Inactivo","Anterior"],w="150px"),sel("Contrato",["Todos","Por horas","Nómina","Vencido"],w="140px"),sel("Vista",["Todos","Dictando ahora","Con horas libres","Sin contrato vigente"],w="170px",col=False),actions=btn("Alta de profesor","AltaProfesor.html",True)+btn("Contratación","ContratacionProfesores.html")+btn("Payment sheet","PaymentSheet.html")+btn("Correo masivo")),
 kpis([("Profesores activos",sv(36,18,11,7),"de 100 registrados"),("Dictando ahora",sv(5,3,1,1),"sesiones en curso"),("Horas esta semana",sv(412,210,124,78),"programadas"),("Sin contrato vigente con clases",sv(1,0,0,1),"bloquea pago")]),
 ltable("profesores",["Profesor","Sede","Contrato","Cursos activos","Clases hoy","Horas / semana","Asistencia","Estado","Acción"],[
  [c2("P. Gómez","Quito · Por horas · vigente · $7.00/h"),"Quito","Por horas · vigente","3",c2("2","B1 Virtual 19:00, A2 18:00"),"14 h",progress(88),badge("Activo","ok"),'<a href="FichaProfesor.html">Ver perfil</a>'],
  [c2("L. Vega","Valle · Por horas · vigente · $6.50/h"),"Valle","Por horas · vigente","2",c2("1","Kids 2 Tarde 15:00"),"10 h",progress(91),badge("Activo","ok"),'<a href="FichaProfesor.html">Ver perfil</a>'],
  [c2("R. Salas","Ambato · Vencido · $5.70/h"),"Ambato","Vencido","0",c2("0","sin clases hoy"),"0 h","—",badge("Inactivo","bad"),'<a href="FichaProfesor.html">Ver perfil</a>'],
  [c2("M. Castro","Ambato · Por horas · vigente · $6.50/h"),"Ambato","Por horas · vigente","2",c2("1","Kids 1 Mañana 16:00"),"8 h",progress(84),badge("Activo","ok"),'<a href="FichaProfesor.html">Ver perfil</a>'],
  [c2("S. Jiménez","Quito · Nómina · —/h"),"Quito","Nómina","4",c2("2","A1 Sábados, B2 Intensivo"),"20 h",progress(93),badge("Activo","ok"),'<a href="FichaProfesor.html">Ver perfil</a>'],
  [c2("D. Paredes","Valle · Por horas · $9.00/h (tarifa en aprobación)"),"Valle","Por horas","0",c2("0","sin clases hoy"),"0 h","—",badge("Nuevo · tarifa en aprobación","warn"),'<a href="FichaProfesor.html">Ver perfil</a>'],
  [c2("A. Ruiz","Quito · Por horas · vigente · $6.50/h"),"Quito","Por horas · vigente","0",c2("0","disponible para reemplazos"),"0 h","—",badge("Standby","warn"),'<a href="FichaProfesor.html">Ver perfil</a>'],
  [c2("J. Mena","Valle · salió en jun 2026"),"Valle","—","0",c2("0","—"),"0 h","—",badge("Anterior","neutral"),'<a href="FichaProfesor.html">Ver perfil</a>']],sede=1,hide=(1,2),wide=0),
 ai([("Teens B1 Virtual (Valle) abre en 2 semanas sin profesor. P. Gómez dicta B1 Virtual en Quito con 88% de asistencia y tiene libres Lu-Ma-Mi-Ju 17:00–19:00.","Ver perfil","FichaProfesor.html"),("S. Jiménez está en 20 h/semana, el máximo de su contrato de nómina. No asignarle el curso nuevo de sábado.","Ver carga","FichaProfesor.html"),("R. Salas tiene contrato vencido y 8 h registradas este mes: la payment sheet no se puede aprobar hasta renovar o anular esas sesiones.","Renovar contrato","PaymentSheet.html")],"Pregunta: ¿quién puede cubrir Kids 2 Tarde el miércoles?"),
 card("De candidato a profesor", flow(["Selección y evaluación (CV, referencias, entrevista, demo, MOCK)","Pay scale aprobado por Coord. Administrativa","Contratación aprobada por Dirección Administrativa","Coordinación crea el profesor","Inducción y primer curso"])+kv(("Alta del profesor","la crea Coordinación Académica sin pedir otra autorización: las aprobaciones ya ocurrieron en el proceso de contratación"),("Payment sheet","solo entra con pay scale aprobado, RUC y contrato firmado"),("Ver el proceso",'<a href="ContratacionProfesores.html">Contratación de profesores</a>'))),
 subtitle="Nadie crea un profesor que pueda cobrar sin aprobación (el caso del profesor falso)")
page("Profesores.html","Profesores",prof,"Listado de profesores")

# 10 Payment sheet
ps=shell("Payment sheet · Octubre 2026","Profesores",
 filters(sel("Mes",["Octubre 2026","Septiembre 2026","Agosto 2026"],w="170px"),sel("Contrato",["Todos","Por horas","Nómina"],w="150px"),sel("Alerta",["Todas","Diferencia","Contrato vencido","Factura sin sesiones"],w="190px"),actions=kv(("Estado",badge("Borrador","warn")),("Total a pagar","$875.60"),("Alertas","3"))+btn("Exportar")+btn("Aprobar pagos",None,True)),
 table(["Profesor","Sede","Contrato","Sesiones","Horas","Tarifa","A pagar","Factura prof.","Alerta"],[
  ["P. Gómez","Quito","Por horas","24","48","$7.00","$336","$336","—"],
  ["L. Vega","Valle","Por horas","18","36","$6.50","$234","$260",badge("Diferencia +$26","warn")],
  ["R. Salas","Ambato","Por horas","4","8","$5.70","$45.60","—",badge("Contrato vencido","bad")],
  ["M. Castro","Ambato","Por horas","20","40","$6.50","$260","$260","—"],
  ["S. Jiménez","Quito","Nómina","30","60","—","Salario","—","—"],
  ["D. Paredes","Valle","Por horas","0","0","$6.00","$0","$120",badge("Factura sin sesiones","bad")]],sede=1),
 two(card("Cómo se calcula", flow(["Sesiones confirmadas","× tarifa/hora","Monto a pagar","vs factura del profesor","Alertas"])+kv(("Sesiones","se generan al crear el curso, descontando feriados; one to one se liquida desde 10 h"),("Actividades sin código de curso","payment sheet manual (talleres, mock, reemplazos)"),("Teacher of the Month","+5% sobre la payment sheet de la sede"),("Cierre","revisión mensual → correo al profesor → 3 días para observar → consolidación → factura del profesor"))),
     card("Alertas del mes", table(["Profesor","Alerta","Acción"],[["L. Vega","Factura $260 vs calculado $234 (+$26)",'<a href="FichaProfesor.html">Revisar sesiones</a>'],["R. Salas","Contrato vencido · 8 h registradas",btn("Renovar contrato",None,False,"Se renueva el contrato de R. Salas con la tarifa vigente de la tabla y vigencia hasta dic 2027. Al quedar vigente, sus 8 h registradas entran al pago de este mes. "+AUDIT,"FichaProfesor.html")],["D. Paredes","Factura $120 sin sesiones registradas",'<a href="Sesiones.html">Revisar sesiones</a>']]))),
 two(card("Novedades del mes · atrasos, cancelaciones y reemplazos", filters(sel("Tipo",["Todos","Atraso","Cancelación","Reemplazo"],w="150px"),actions=btn("Registrar novedad",None,True)+only("ADM,GER,SUC,COO",btn("Marcar Teacher of the Month"),True))
   +table(["Fecha","Profesor","Tipo","Novedad"],[
    ["14 oct",c2("L. Vega","Kids 2 Tarde"),"Atraso",c2("12 min · -$1.30","CAMB-CLOCK · Minutes Late")],
    ["09 oct",c2("P. Gómez","Adults A2"),"Reemplazo",c2("Cubrió A. Ruiz · 2 h pasan a A. Ruiz","aviso con 72 h · aprobado")],
    ["07 oct",c2("M. Castro","Kids 1 Mañana"),"Cancelación",c2("Feriado local · sin pago","Remarks: se repone el 21 oct")],
    ["03 oct",c2("D. Paredes","—"),"Cancelación",c2("Sin estudiantes · sin pago","Remarks: curso aún no abre")],
    ["01 oct",c2("S. Jiménez","B2 Intensivo"),"Atraso",c2("5 min · sin descuento","dentro de la tolerancia")]],hide=(2,),wide=3)
   +kv(("Reemplazos","con 48 h de aviso; las horas se pagan al profesor que cubre"),("Atrasos","minutos del reloj de asistencia; se descuentan según la política"),("Teacher of the Month · octubre",'<a href="FichaProfesor.html">P. Gómez · Quito</a> · +5%'))),
     card("Correo de payment sheet al profesor", kv(("Asunto","Payment sheet · Octubre 2026 · Cambridge Quito"),("Plantilla","Estimado/a «NOMBRES»: en octubre dictaste «hrs» horas a «V.H» por hora; descuentos «DCTOS»; subtotal «SUBT». Emite tu factura por «FACT» (RIMPE o régimen general) y confirma la cuenta «No. cuenta»."),("Plazo para observar","3 días desde el envío"),("Último envío",badge("Pendiente · se envía al aprobar","warn")))+row(btn("Enviar correo de payment sheet",None,True)))),
 subtitle="Reemplaza el Excel + Drive de 2 días al mes")
page("PaymentSheet.html","Payment sheet",ps,"Payment sheet de profesores")

# 11 Comisiones
V3='<a href="DetalleMatricula.html">Ver</a>'
descuentos=table(["Fecha","Estudiante","Asesor","Venta","Precio lista","% dcto.","Descuento","Motivo","Aprobación","Acción"],[
  ["28 ago",c2('<a href="Ficha360.html">María Andrade</a>',"Quito · módulos 7–10"),"Carla M.","B1–B1+","$1,000","10%","-$100","Referido",badge("Dentro del límite","ok"),V3],
  ["11 oct",c2('<a href="Ficha360.html">Valeria Cedeño</a>',"Quito · B2"),"Carla M.","B2","$550","10%","-$55","Promoción octubre",badge("Dentro del límite","ok"),V3],
  ["11 oct",c2('<a href="Ficha360.html">Camila Sánchez</a>',"Ambato · A2–B1"),"Sofía L.","A2–B1","$1,000","15%","-$150","Convenio empresa",badge("Aprobado · Dir. Comercial","navy"),V3],
  ["10 oct",c2('<a href="Ficha360.html">Ana Ruiz (menor)</a>',"Quito · Kids 2"),"Carla M.","Kids 2","$387.50","0%","$0","—",badge("Sin descuento","neutral"),V3],
  ["09 oct",c2('<a href="Ficha360.html">Juan Pérez</a>',"Valle · A2"),"Diego R.","A2","$500","5%","-$25","Referido",badge("Dentro del límite","ok"),V3],
  ["24 sep",c2('<a href="Ficha360.html">Pedro Mora</a>',"Valle · B1 módulos 7–8"),"Diego R.","B1","$500","20%","-$100","Otro",badge("Rechazado · sin motivo válido","bad"),V3],
  ["06 oct",c2('<a href="Ficha360.html">Mateo Salazar (menor)</a>',"Ambato · A1"),"Sofía L.","A1","$420","10%","-$42","Hermano matriculado",badge("Dentro del límite","ok"),V3],
  ["03 oct",c2('<a href="Ficha360.html">Gabriela Núñez</a>',"Quito · A2"),"Carla M.","A2","$450","42%","-$189","Referido",badge("Pendiente de aprobación","warn"),V3]],hide=(3,),wide=1)
com=shell("Comisiones y descuentos · Octubre 2026","Comisiones",
 tabs(["Comisiones","Descuentos otorgados"],"Comisiones",roles={"Descuentos otorgados":"ADM,GER,DIR,SUC"},panels={
  "Comisiones": only("ASE", card("Tu comisión de octubre, en corto", kpis([("Vendiste","14 niveles","meta 12 · 117%"),("Rango","11+","4% virtual · 5% presencial"),("Comisión estimada","$443.30","incluye bono $50"),("Retenido","$22.50","1 venta sin cobrar")])+progress(100,"Meta: 14 de 12 niveles",CH[0])+row(btn("Preparar mi informe del mes","InformeComisiones.html",True),btn("Ver el cálculo paso a paso","DetalleComision.html"))))
   +only("ADM,GER,DIR,SUC", filters(sel("Período",["Octubre 2026","Septiembre 2026","Agosto 2026"],w="170px"),actions=kv(("Estado",badge("En revisión","warn")),("Total comisiones","$930"),("Niveles vendidos","34"))+btn("Reglas de comisión")+btn("Informes de asesores","InformeComisiones.html")+btn("Exportar")+btn("Aprobar período",None,True)))
   +only("ADM,GER,DIR,SUC", flow(["Borrador (cálculo automático)","En revisión (Dir. Comercial)","Aprobado (se paga)"])
   +table(["Asesor","Niveles vendidos","Virtual / Presencial","Meta","Real","Comisión","Acción"],[
    ["Carla M.","14","6 / 8","12","14","$443",'<a href="DetalleComision.html">Ver cálculo</a>'],
    ["Diego R.","9","4 / 5","12","9","$180",'<a href="DetalleComision.html">Ver cálculo</a>'],
    ["Sofía L.","11","7 / 4","10","11","$330",'<a href="DetalleComision.html">Ver cálculo</a>']])
   +two(card("Meta vs real por asesor", vbars([("Carla M.",[12,14]),("Diego R.",[12,9]),("Sofía L.",[10,11])],["Meta","Real"])),
        card("Reglas activas", li(["Rango 1–5 niveles: 2% virtual · 3% presencial","Rango 6–10 niveles: 3% virtual · 4% presencial","Rango 11+ niveles: 4% virtual · 5% presencial","Bono $50 por cumplir meta mensual"])+row('<a href="ReglasComision.html" style="font-size:13px">Editar reglas</a>')))),
  "Descuentos otorgados": kpis([("Ventas con descuento",sv("23 de 34","12 de 18","6 de 9","5 de 7"),"68% de las ventas del mes"),("Total descontado",sv("$1,860","$940","$425","$495"),"5.6% de lo facturado"),("Descuento promedio",sv("8.4%","9.1%","6.2%","9.8%"),"límite del asesor: 10%"),("Fuera del límite",sv("3","1","1","1"),"1 aprobado · 1 pendiente · 1 rechazado")])
   +filters(search("Buscar","Estudiante o venta",w="220px"),sel("Asesor",["Todos","Carla M.","Diego R.","Sofía L."],w="140px"),sel("Aprobación",["Todos","Dentro del límite","Aprobado","Pendiente","Rechazado","Sin descuento"],w="170px"),sel("Período",["Octubre 2026","Septiembre 2026","Agosto 2026"],w="160px",col=False),actions=btn("Exportar"))
   +descuentos+pager(sv(34,18,9,7))
   +two(card("Descuento promedio por asesor", hbars([("Carla M. · 12 ventas",9),("Sofía L. · 9 ventas",8),("Diego R. · 8 ventas",6)],unit="")+kv(("Límite sin aprobación","10% (Configuración → Reglas de aprobación)"),("Más de 10%","requiere aprobación del Director Comercial"))),
        card("Motivos del mes", hbars([("Referido",11),("Promoción octubre",6),("Convenio empresa",3),("Hermano matriculado",2),("Otro",1)],unit="")+row(btn("Editar motivos permitidos","Configuracion.html")))),
 }),
 subtitle="Comisiones calculadas al cierre de mes; descuentos de cada asesor visibles para Dirección")
page("Comisiones.html","Comisiones",com,"Motor de comisiones")

# 11b Insights de IA (M9 + M8): todas las observaciones del asistente, por área, con prioridad y acción
INS_COMERCIAL={"Comercial","Cobranza","Dirección"}  # áreas que un académico (COO) no ve
def insight(area, sev, title, text, link, href, when="hoy"):
    k={"alta":"bad","media":"warn","baja":"neutral"}[sev]
    rl=f' data-roles="ADM,GER,DIR,SUC"' if area in INS_COMERCIAL else ""
    return (f'<div class="insight"{rl}><div class="insight-side"><span class="badge badge-{k}">{sev}</span><small>{when}</small></div><div class="insight-body"><small class="insight-area">{area}</small><b>{title}</b><p>{text}</p>'
            f'<div class="insight-actions"><a href="{href}" class="btn btn-primary">{link}</a>{btn("Marcar como atendido")}{btn("Descartar")}</div></div></div>')
INSIGHTS=[
 ("Académico","media","Teens B1 Virtual (Valle) abre en 2 semanas y su candidata aún no rinde el MOCK","Daniela Paredes tiene la clase demostrativa el 24 oct; si el MOCK y el pay scale toman más de una semana, el curso abre sin profesor. P. Gómez podría cubrir las primeras clases.","Ver candidata","DetalleCandidato.html","hoy"),
 ("Académico","alta","4 estudiantes pagaron y no tienen grupo asignado","Matriculados entre el 8 y 12 oct en Adults virtual; no aparecen en ningún curso ni equipo de Teams. Dos ya preguntaron por el enlace de clase.","Asignar grupo","Estudiantes.html","hoy"),
 ("Comercial","media","De los 20 que terminaron en septiembre, 6 no se han rematriculado","3 dijeron precio, 2 horario, 1 no responde. Los de horario podrían entrar al grupo de sábados que abre el 9 ene.","Ver retención","Reportes.html","hoy"),
 ("Inventario","alta","3 libros con stock negativo hoy: el correo de las 07:00 ya salió a 5 personas","Empower B1+ Combo B (Valle -2), Super Minds L3 (Ambato -2) y Aula Internacional 1 (todas). Hay 1 pedido en camino que cubre solo el primero.","Ver stock negativo","Inventario.html","hoy 07:00"),
 ("Comercial","media","Carla M. aplicó descuento en 10 de sus 12 ventas (promedio 9%)","Está dentro del límite del 10%, pero el 83% de sus ventas con descuento es el doble que el resto del equipo. Vale revisar si el motivo 'Referido' se está usando bien.","Ver descuentos otorgados","Comisiones.html","hoy"),
 ("Comercial","alta","Descuento del 42% bloquea una matrícula de $450","La solicitud de Carla M. para Gabriela Núñez espera desde ayer. Con 10% la matrícula cierra hoy; con 42% la comisión baja a $23 y requiere justificación.","Resolver en Aprobaciones","Aprobaciones.html","hace 1 día"),
 ("Académico","alta","14 estudiantes de A1 Sábados sin calificar","El curso 0001-2026-0430 terminó hace 5 días. Sin notas no se emiten certificados y los estudiantes no pueden matricularse en A2, donde hay 3 cupos esperándolos.","Calificar curso","DetalleCurso.html","hace 5 días"),
 ("Pagos a profesores","alta","Payment sheet de octubre con 3 alertas","L. Vega facturó $26 más que sus horas; R. Salas tiene contrato vencido con 8 h; D. Paredes entregó factura sin sesiones. Bloquean la aprobación.","Revisar payment sheet","PaymentSheet.html","hoy"),
 ("Académico","media","Teens B1 Virtual abre en 2 semanas sin profesor","P. Gómez tiene libres Lu-Ma-Mi-Ju 17:00–19:00, dicta B1 con 88% de asistencia y le quedan 8 h de contrato. Es el mejor candidato.","Ver perfil y asignar","FichaProfesor.html","hoy"),
 ("Cobranza","media","$12,450 en matrículas con saldo; el 60% vence con cursos que terminan en noviembre","4 cursos concentran $7,470. Conviene contactar antes del cierre: después del fin de curso la recuperación cae a la mitad.","Ver matrículas con saldo","Cursos.html","hoy"),
 ("Inventario","media","Stock negativo en 3 libros de cursos en marcha","Empower B1+ (Valle −2), Super Minds 3 WB y SB (Ambato). 4 estudiantes están sin material. Pedido sugerido a Books & Bits: 16 libros.","Crear pedido","NuevoPedido.html","hoy"),
 ("Comercial","media","Ambato lleva 2 semanas sin matrículas nuevas","Tiene 2 cursos por abrir con menos de 5 inscritos. Históricamente no abren con menos de 6. Hay 5 leads de Kommo sin contactar en esa sede.","Ver cursos de Ambato","Cursos.html","hace 3 días"),
 ("Académico","media","4 estudiantes de B1 Virtual con asistencia menor a 60%","Riesgo de perder el módulo 7. Dos de ellos nunca habían faltado antes de la semana pasada.","Ver estudiantes del curso","DetalleCurso.html","hoy"),
 ("Operación","baja","Aula Q-1 al 60% y C-2 (Valle) al 0% el sábado","El nuevo Kids 2 de sábado podría ir a C-2 sin chocar con otro curso.","Ver aulas","Configuracion.html","hoy"),
 ("Dirección","baja","Octubre va 9% sobre la meta de niveles","76 niveles vendidos sobre 70. Quito empuja (+15%); Ambato es la única sede bajo meta.","Ver dashboard ejecutivo","DashboardEjecutivo.html","hoy"),
]
_ins_rows="".join(insight(*i) for i in INSIGHTS)
page("Insights.html","Insights de IA",shell("Insights de IA","Insights de IA",
 only("ADM,GER,DIR,SUC", kpis([("Insights abiertos","14","5 de prioridad alta"),("Atendidos esta semana","7","tiempo medio de atención: 1.4 días"),("Impacto estimado","$21,300","matrículas y cobros en juego"),("Cobertura","7 áreas","académico · comercial · pagos · cobranza · inventario · operación · dirección")])),
 only("COO", kpis([("Insights abiertos","8","4 de prioridad alta"),("Atendidos esta semana","5","tiempo medio de atención: 1.2 días"),("Estudiantes en juego","26","sin grupo, sin nota o en riesgo"),("Cobertura","4 áreas","académico · pagos a profesores · inventario · operación")])),
 two(card("Insights por área", only("ADM,GER,DIR,SUC", hbars([("Académico",4),("Comercial",4),("Inventario",2),("Pagos a profesores",1),("Cobranza",1),("Operación",1),("Dirección",1)],""))+only("COO", hbars([("Académico",4),("Inventario",2),("Pagos a profesores",1),("Operación",1)],""))), card("Evolución (últimas 8 semanas)", linechart(["S1","S2","S3","S4","S5","S6","S7","S8"],{"Nuevos":[6,8,7,9,8,11,9,10],"Atendidos":[4,7,6,8,9,9,8,7]},h=150)+'<span class="kpi-sub">El asistente analiza cada noche la base unificada y propone acciones. Solo lectura: nada cambia sin que alguien lo confirme.</span>')),
 filters(sel("Área",["Todas","Académico","Comercial","Pagos a profesores","Cobranza","Inventario","Operación","Dirección"],w="180px",col=False),sel("Prioridad",["Todas","alta","media","baja"],w="130px",col=False),sel("Estado",["Abiertos","Atendidos","Descartados"],w="140px",col=False),actions=btn("Preguntar al asistente",None,False,action="",next=None) if False else '<button type="button" class="btn btn-ask" data-ask="¿Qué insight es el más urgente?">✦&nbsp;Preguntar al asistente</button>'),
 f'<div class="insights">{_ins_rows}</div>',
 subtitle="Todo lo que el asistente detectó en la base unificada, por área y prioridad"),"Insights de IA")

# 12 Reportes · las tres vistas comparten la misma barra de pestañas (cada una es una pantalla)
# 29 Constructor de reportes (guiado, para usuarios no técnicos)
PREG=[("¿Cuántos estudiantes nuevos tuvimos?","Por mes y por sede, con quién los trajo","users"),
      ("¿Quiénes nos deben dinero?","Matrículas con saldo, cuánto y desde cuándo","coin"),
      ("¿Cómo van las ventas de cada asesor?","Niveles vendidos, meta y comisión","chart"),
      ("¿Qué facturamos y cobramos este mes?","Facturas, pagos, notas de crédito y XML del SRI","doc")]
PREG_COO=[("¿Qué cursos terminaron sin calificar?","Bloquean certificados y rematrícula","cal"),
      ("¿Cuántos aprobaron y cuántos perdieron el nivel?","Por programa, nivel y profesor","medal"),
      ("¿Cuántas horas dictó cada profesor?","Sesiones confirmadas del mes","grad"),
      ("¿Quiénes están en riesgo por asistencia?","Menos de 75% en el módulo actual","users")]
PREG_AREAS=[("Estudiantes y matrículas",[
      ("¿Cuántos estudiantes nuevos tuvimos?","Por mes y por sede, con quién los trajo","users"),
      ("¿Quiénes están activos, inactivos o en transición?","El consolidado de las 3 sedes, sin cruzar listas","users"),
      ("¿Quiénes están por terminar su nivel?","Para ofrecerles el siguiente a tiempo","spark"),
      ("¿Cuántos aprobaron y cuántos perdieron el nivel?","Por programa, nivel y profesor","medal"),
      ("¿Cuántos se rematricularon?","Retención por cohorte: terminaron, aprobaron, volvieron","trend"),
      ("¿De qué sectores vienen los estudiantes?","Por zona de la ciudad y sede","pin")]),
   ("Cursos y profesores",[
      ("¿Qué cursos están por abrir o sin profesor?","Con cupo, fecha de inicio y aula","book"),
      ("¿Qué cursos terminaron sin calificar?","Bloquean certificados y rematrícula","cal"),
      ("¿Cuántas horas dictó cada profesor?","Sesiones confirmadas y payment sheet del mes","grad"),
      ("¿Qué aulas y horarios están disponibles?","Ocupación por sede y franja","home"),
      ("¿Qué cursos abren próximamente y cuáles no tienen profesor?","Con cupo, fecha y equipo de Teams","cal")]),
   ("Ventas y facturación",[
      ("¿Qué facturamos y cobramos este mes?","Facturas, pagos y notas de crédito por sede","doc"),
      ("¿Quiénes nos deben dinero?","Facturas con saldo, días de atraso y asesor","coin"),
      ("¿Qué facturas faltan por autorizar o enviar?","Estado SRI y comprobantes sin enviar","check"),
      ("¿Cómo van las ventas de cada asesor?","Niveles vendidos, meta y comisión","chart"),
      ("¿Qué descuentos dio cada asesor?","Porcentaje, monto, motivo y si fue aprobado","coin"),
      ("¿Este mes vs el anterior?","Ventas, matrículas y cobros comparados","trend"),
      ("Facturas y XML del SRI de un período","Para contabilidad: lista y archivos descargables","swap"),
      ("¿Cómo va cada empresa (B2B)?","Estudiantes, asistencia, aprobación y facturación por empresa","id")]),
   ("Inventario",[
      ("¿Qué libros faltan en stock?","Por sede, con pedidos en camino","box"),
      ("¿Qué compramos a cada proveedor?","Ingresos, egresos y notas de crédito por proveedor","swap"),
      ("¿Qué códigos de activación están sin asignar?","Comprados vs entregados","lock")]),
   ("Otra pregunta",[("Escríbela con tus palabras","El asistente arma el reporte y lo puedes guardar","chat")])]
AREAS_COMERCIALES={"Ventas y facturación"}  # un académico (COO) no ve estas preguntas
def picker_areas(areas, on=(0,0)):
    out=""
    for gi,(area,items) in enumerate(areas):
        rl=' data-roles="ADM,GER,DIR,SUC,ASE,SEC"' if area in AREAS_COMERCIALES else ""
        cards="".join(f'<button type="button" class="pick{" on" if (gi,i)==on else ""}" role="radio" aria-checked="{"true" if (gi,i)==on else "false"}">{ico(ic,"pick-ico")}<b>{t}</b><small>{d}</small></button>' for i,(t,d,ic) in enumerate(items))
        out+=f'<div class="pick-area"{rl}><h4>{area}</h4><div class="picker">{cards}</div></div>'
    return f'<div class="picker-areas" role="radiogroup">{out}</div>'
def picker(items, on=0):
    out="".join(f'<button type="button" class="pick{" on" if i==on else ""}" role="radio" aria-checked="{"true" if i==on else "false"}">{ico(ic,"pick-ico")}<b>{t}</b><small>{d}</small></button>' for i,(t,d,ic) in enumerate(items))
    return f'<div class="picker" role="radiogroup">{out}</div>'
def pills(items, on=0, multi=False):
    out="".join(f'<button type="button" class="pill{" on" if (i in on if isinstance(on,(list,tuple,set)) else i==on) else ""}" aria-pressed="{"true" if (i in on if isinstance(on,(list,tuple,set)) else i==on) else "false"}">{t}</button>' for i,t in enumerate(items))
    return f'<div class="pills"{" data-multi" if multi else ""}>{out}</div>'
def rep_tabs(active):
    return tabs([("Dashboard por rol","Reportes.html"),("Reportes self-service","ConstructorReportes.html"),("Dashboard ejecutivo","DashboardEjecutivo.html")],active,roles={"Dashboard ejecutivo":"ADM,GER,DIR"})
rep=shell("Reportes y dashboards","Reportes",
 rep_tabs("Dashboard por rol"),
 only("ADM,GER,DIR,SUC", kpis([("Ventas del mes (niveles)",sv(76,40,22,14),"meta 70 · 109%"),("Matrículas del mes",sv(52,28,15,9),"+8% vs sep"),("Cobrado / pendiente",sv("$31,200 / $12,450","$16,900 / $6,200","$9,100 / $4,100","$5,200 / $2,150"),"71% cobrado"),("Ocupación de cursos",sv("82%","86%","78%","75%"),sv("41 cursos activos","22 cursos","12 cursos","7 cursos"))])
 +two(card("Ventas por sede y modalidad (niveles, octubre)", vbars([("Quito",[24,16]),("Valle",[14,8]),("Ambato",[9,5])],["Presencial","Virtual"])),
     card("Pipeline comercial (Kommo → venta → matrícula)", funnel([("Leads Kommo",310),("Contactados",205),("Cotizaciones",120),("Ventas",76),("Matriculados",52)])))),
 only("COO", kpis([("Ocupación de cursos",sv("82%","86%","78%","75%"),sv("41 cursos activos","22 cursos","12 cursos","7 cursos")),("Asistencia promedio",sv("86%","88%","84%","83%"),"meta 85%"),("Aprobación (nota ≥ 7)",sv("91%","93%","89%","88%"),"módulos cerrados en sep"),("Terminados sin calificar",sv(2,1,1,0),"bloquean certificados")])
 +two(card("Aprobación por nivel (módulos cerrados, %)", hbars([(f"{n} · módulos {m}",v) for (n,m),v in zip(NIVELES,[94,91,90,88,86,92])],unit="")),
     card("Asistencia por sede y modalidad (%)", vbars([("Quito",[88,86]),("Valle",[85,82]),("Ambato",[84,81])],["Presencial","Virtual"])))),
 kpis([("Programas","12","Eaglets · Kids · Teens · Adults · Business · Exam Prep · Spanish · Summer · Tailored"),("Cursos activos",sv(41,22,12,7),sv("6 por abrir","3 por abrir","2 por abrir","1 por abrir")),("Estudiantes activos",sv(812,420,230,162),"43 corporativos"),("Libros en stock",sv("1,240","640","380","220"),"3 con stock negativo")]),
 two(card("Retención · cohorte que terminó en septiembre", funnel([("Terminaron su nivel",20),("Aprobaron (nota ≥ 7)",18),("Se rematricularon",14),("Rematrícula pagada",12)])+kv(("Retención","70% (14 de 20)"),("Se fueron","6 · 3 por precio, 2 por horario, 1 sin respuesta"),)+only("ADM,GER,DIR,SUC",kv(("Pendientes de pago","2 · recordatorio enviado")))+row(btn("Ver quiénes no se rematricularon","Estudiantes.html"))),
     card("Alertas de información escondida", table(["Alerta","Cuántos","Acción"],[[c2("Estudiantes sin grupo asignado","matriculados y pagados, sin curso"),"4",'<a href="Estudiantes.html">Ver</a>'],[c2("Grupos de Teams sin profesor","curso virtual creado sin docente"),"1",'<a href="Programas.html">Ver</a>'],[c2("Cursos por abrir sin profesor","inician en menos de 3 semanas"),"2",'<a href="Cursos.html">Ver</a>'],[c2("Terminados sin calificar","bloquean certificado y rematrícula"),"2",'<a href="Cursos.html">Ver</a>'],],wide=0)+only("ADM,GER,DIR,SUC",table(["Alerta comercial","Cuántos","Acción"],[[c2("Rematrículas pendientes de pago","más de 5 días"),"2",'<a href="Facturas.html">Ver</a>']],wide=0)))),
 card("Cursos que abren próximamente", table(["Curso","Programa · modalidad · tipo","Inicia","Profesor","Cupo","Estado","Acción"],[[c2("Teens B1 Virtual","0001-2026-0772 · Valle"),"Teens · Virtual · Grupal","20 oct","P. Gómez","6 / 12",badge("Confirmado","ok"),'<a href="DetalleCurso.html">Ver</a>'],[c2("Teens A2","0001-2026-0192 · Ambato"),"Teens · Presencial · Grupal","27 oct","sin asignar","5 / 10",badge("Sin profesor","bad"),'<a href="DetalleCurso.html">Ver</a>'],[c2("Preescolar Pre 1","0001-2026-0801 · Quito"),"Preescolar · Presencial · Grupal","3 nov","M. Castro","4 / 8",badge("Cupo bajo","warn"),'<a href="DetalleCurso.html">Ver</a>'],[c2("ESL B1 módulo 8","0001-2026-0767 · Quito · continúa"),"Adults · Virtual · Grupal","3 nov","P. Gómez","12 / 15",badge("Confirmado","ok"),'<a href="DetalleCurso.html">Ver</a>'],[c2("Business · Grupo Nova","0001-2026-0810 · Ambato"),"Business · Virtual · One to one","10 nov","L. Vega","1 / 1",badge("Confirmado","ok"),'<a href="DetalleCurso.html">Ver</a>']],wide=0)+row(btn("Exportar PDF"))),
 card("¿Qué quieres saber hoy?", only("ADM,GER,DIR,SUC",picker(PREG[:4],None))+only("COO",picker(PREG_COO,None))+row(btn("Armar mi reporte","ConstructorReportes.html",True),btn("Ver reportes guardados","ConstructorReportes.html")),extra='<small class="card-hint">Elige una pregunta y te la respondemos en palabras, gráfico y tabla</small>'),
 subtitle="Estefanía arma sus propios reportes sin pedirle nada a un desarrollador")
page("Reportes.html","Reportes",rep,"Reportes y dashboards")


# 13 Usuarios y roles
page("Usuarios.html","Usuarios",shell("Usuarios y roles","Usuarios y roles",
 filters(search("Buscar","Nombre o email",w="260px"),sel("Rol",["Todos","Administrador General","Gerente General","Director Comercial","Administrador de Sucursal","Coordinador Académico","Asesor Comercial","Secretaría","Profesor (consulta)"],w="220px"),sel("Estado",["Todos","Activo","Inactivo"],w="130px"),actions=btn("Nuevo usuario",None,True)),
 ltable("usuarios",["Usuario","Rol","Sedes visibles","Estado","Acción"],[["Estefanía","Administrador General","Todas","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Carla M.","Asesor Comercial","Quito","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Coord. Académica","Coordinador Académico","Valle","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["P. Gómez","Profesor (consulta)","Quito","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Diego R.","Asesor Comercial","Valle","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Sofía L.","Asesor Comercial","Ambato","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Dir. Comercial","Director Comercial","Todas","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Secretaría Ambato","Secretaría","Ambato","Inactivo",'<a href="NuevoUsuario.html">Editar</a>'],["Admin. Sucursal Valle","Administrador de Sucursal","Valle","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Gerencia","Gerente General","Todas","Activo",'<a href="NuevoUsuario.html">Editar</a>']],sede=2),
 note("Los empleados de TeamDesk (tabla Employees: p. ej. 'Administrador de Sucursal') se migran como usuarios con rol; los datos personales del empleado (cédula, teléfono, cumpleaños) quedan en su ficha de usuario, no en una tabla aparte."),
 card("Matriz de permisos por rol", table(["Acción","Admin General","Gerente","Dir. Comercial","Admin. Sucursal","Coord. Académica","Asesor","Secretaría"],[["Crear estudiante / matrícula","✓","—","✓","✓","—","✓","✓"],["Aplicar descuento >10%","✓","—","✓","—","—","—","—"],["Aprobar profesor","✓","✓","✓","—","—","—","—"],["Calificar curso (pass/fail)","✓","—","—","—","✓","—","—"],["Aprobar payment sheet","✓","✓","—","✓","—","—","—"],["Exportar base completa","✓","—","—","—","—","—","—"],["Ver otras sedes","✓","✓","✓","—","—","—","—"],["Dashboard ejecutivo","✓","✓","✓","—","—","—","—"]])),
 subtitle="RBAC: roles, permisos por acción y visibilidad multi-sede"),"Usuarios y roles")

# 14 Audit log
page("AuditLog.html","Audit log",shell("Audit log","Audit log",
 filters(sel("Usuario",["Todos","Estefanía","Carla M.","Dir. Comercial","Secretaría","Coord. Académica"],w="160px"),sel("Acción",["Todas","Creó","Modificó","Aprobó","Rechazó","Exportó","Eliminó"],w="130px"),sel("Entidad",["Todas","Estudiante","Factura","Descuento","Profesor","Tarifa","Curso","Inventario"],w="140px"),dates(),actions=btn("Exportar log")),
 table(["Fecha/hora","Usuario","Acción","Entidad","Detalle","IP / sede"],[["04 oct 10:12","Carla M.","Creó","Estudiante","Gabriela Núñez","Quito"],["04 oct 09:40","Carla M.","Solicitó","Descuento","42% · Gabriela Núñez · pendiente","Quito"],["03 oct 17:05","Secretaría","Exportó","Estudiantes","120 registros (filtro Valle)","Valle"],["03 oct 15:30","Estefanía","Modificó","Tarifa","P. Gómez $6.50 → $7.00","Quito"],["03 oct 11:20","Coord. Académica","Creó","Curso","Teens B1 Virtual · Valle","Valle"],["02 oct 16:45","Carla M.","Rechazó","Descuento","Solicitud 30% · Luis Torres (retirada)","Quito"],["02 oct 10:05","Secretaría","Modificó","Inventario","Traslado 3 × Adults B1 Quito → Valle","Valle"],["01 oct 09:30","Dir. Comercial","Aprobó","Profesor","M. Castro · $6.50/h","Ambato"],["30 sep 18:00","Estefanía","Eliminó","Curso","Kids 1 Tarde (sin inscritos)","Ambato"]],sede=5),
 pager(sv("4,120","2,210","1,180","730"),50),
 card("Alertas marcadas para revisión", table(["Fecha","Alerta","Usuario","Estado"],[["03 oct 17:05","Exportación masiva: 120 estudiantes (incluye menores)","Secretaría",badge("Revisada","ok")],["03 oct 15:30","Cambio de tarifa de profesor","Estefanía",badge("Pendiente","warn")],["02 oct 11:00","Descuento fuera de regla (42%)","Carla M.",badge("Rechazado","bad")]])+note("Exportaciones masivas, cambios de tarifa y descuentos fuera de regla se marcan automáticamente (LOPDP, datos de menores). Nada se borra.")),
 card("Papelera", table(["Eliminado","Registro","Por","Acción"],[["30 sep 18:00","Curso Kids 1 Tarde (sin inscritos) · Ambato","Estefanía",btn("Restaurar")],["28 sep 11:10","Estudiante duplicado · Juan Pérez (Valle)","Secretaría",btn("Restaurar")],["20 sep 09:45","Factura borrador sin número · Consumidor final","Diego R.",btn("Restaurar")]])+kv(("Se conserva","90 días; después se archiva, y el audit log nunca se borra"))),
 subtitle="Quién hizo qué, cuándo y desde dónde. Nada se borra."),"Audit log")

VP='<a href="DetalleProducto.html">Ver</a>'
def prod(cod,nombre,sub,tipo,cat,prog,precio,iva,stock,estado="Activo"):
    k={"Activo":"ok","Inactivo":"neutral","Sin stock":"bad"}[estado]
    return [cod,c2(f'<a href="DetalleProducto.html">{nombre}</a>',sub),tipo,cat,prog,precio,iva,stock,badge(estado,k),VP]
catalogo=table(["Código","Producto o servicio","Tipo","Categoría","Programa","Precio","IVA","Stock (Q / V / A)","Estado","Acción"],[
  prod("00139","Servicios educativos · nivel (2 módulos)","Precio por nivel según programa y modalidad · se factura como servicio","Servicio","Servicio educativo","Adults · Teens · Kids","$450–$550","0%","—"),
  prod("00140","Matrícula (tuition fee)","Una vez por estudiante nuevo · $0 en promociones","Servicio","Servicio educativo","Todos","$30.00","0%","—"),
  prod("00151","Clases individuales / Tailored","Precio por hora · corporativo o particular","Servicio","Servicio educativo","Tailored","$18.00 / h","0%","—"),
  prod("00160","Club de conversación","Sábados · 4 sesiones al mes","Servicio","Servicio educativo","Adults","$25.00 / mes","0%","—"),
  prod("00170","Examen internacional B2 First (FCE)","Inscripción al examen Cambridge · se paga al centro autorizado","Servicio","Examen internacional","Adults · Teens","$215.00","0%","—"),
  prod("00171","Examen internacional A2 Key (KET) for Schools","Inscripción al examen Cambridge","Servicio","Examen internacional","Teens · Kids","$120.00","0%","—"),
  prod("00180","Summer Camp Teens · 2 semanas","Julio · incluye camiseta y materiales","Servicio","Programa especial","Teens","$180.00","0%","—"),
  prod("00190","Certificado de nivel (reimpresión)","Duplicado físico del certificado","Servicio","Otro servicio","Todos","$5.00","12%","—"),
  prod("1132","Empower A1 Starter SB with digital pack 2nd Ed","ISBN 9781108961691 · Cambridge · nivel A1 · módulos 1–2","Producto","Libro","Adults","$70.00","0%","2 / 1 / 0"),
  prod("1141","Empower B1+ Intermediate Combo B with digital pack","ISBN 9781108961523 · nivel B1+ · módulos 9–10","Producto","Libro","Adults","$40.00","0%","4 / -2 / 1","Sin stock"),
  prod("1115","Prepare 3 SB with eBook 2E","ISBN 9781009029780 · nivel A2 · módulos 3–4","Producto","Libro","Teens","$40.00","0%","8 / 2 / 5"),
  prod("1116","Prepare 3 WB with Digital Pack 2E","ISBN 9781009030502 · workbook · nivel A2","Producto","Libro","Teens","$24.00","0%","1 / 1 / 1"),
  prod("1292","Super Minds 2Ed Level 3 SB with eBook","ISBN 9781108812276 · Kids 2","Producto","Libro","Kids","$36.00","0%","3 / 0 / -2","Sin stock"),
  prod("1309","Compact First Student's Digital Pack 3rd Edition","ISBN 9781009013482 · código de activación · sin stock físico","Producto","Libro digital","Adults","$54.50","0%","13 códigos"),
  prod("1230","Aula Internacional Nueva Edición 1 · Libro del alumno","ISBN 9788419236043 · programa de español · módulos 1–2","Producto","Libro","Spanish","$58.00","0%","0 / 0 / 0","Sin stock"),
  prod("1341","Botella térmica corporativa azul","Merchandising · obsequio de matrícula","Producto","Merchandising","Todos","$10.43","12%","12 / 6 / 4"),
  prod("1261","Camiseta Summer Camp teens","Tallas S–XL · incluida en Summer Camp","Producto","Merchandising","Teens","$11.00","12%","20 / 0 / 0"),
  prod("1453","Canguro celeste","Merchandising","Producto","Merchandising","Todos","$11.31","12%","5 / 0 / 0"),
  prod("1999","Libreta Superpower","Útiles · obsequio Kids","Producto","Merchandising","Kids","$10.00","12%","25 / 10 / 8"),
  prod("1228","Complete Advanced SB with digital pack 3rd Ed","ISBN 9781009162333 · nivel C1 · descontinuado","Producto","Libro","Adults","$83.00","0%","0 / 0 / 0","Inactivo")],hide=(0,2,4),wide=1)
productos_tab=(kpis([("Productos",sv("96","96","96","96"),"libros, digitales y merchandising"),("Servicios",sv("14","14","14","14"),"niveles, exámenes, programas"),("Sin stock en alguna sede",sv("9","4","3","2"),"3 con stock negativo"),("Códigos digitales sin asignar",sv("13","6","4","3"),"comprados, sin entregar")])
  +filters(search("Buscar","Código, ISBN, nombre o descripción",w="280px"),sel("Tipo",["Todos","Producto","Servicio"],w="130px"),sel("Categoría",["Todas","Libro","Libro digital","Merchandising","Servicio educativo","Examen internacional","Programa especial","Otro servicio"],w="180px"),sel("Programa",["Todos","Adults","Teens","Kids","Spanish","Tailored"],w="130px"),sel("Estado",["Todos","Activo","Sin stock","Inactivo"],w="130px"),actions=btn("Nuevo producto o servicio",None,True,"Se crea el producto o servicio con código, tipo, categoría, precio, IVA y, si aplica, ISBN, stock por sede y parámetros de matrícula (programa, modalidad, módulos).","DetalleProducto.html")+btn("Importar catálogo","ImportExport.html")+btn("Exportar"))
  +catalogo+pager(sv(110,110,110,110)))
page("DetalleProducto.html","Detalle producto",shell("Empower B1+ Intermediate Combo B","Configuración",
 hero([("Tipo","Producto físico · no digital"),("Categoría","Libro · Student Book + Workbook"),("ISBN","9781108961523"),("Precio de venta","$40.00 · IVA 0% · $40.00 con IVA"),("Costo último ingreso","$35.98 · Books & Bits · 1 oct"),("Stock","Quito 4 · Valle -2 · Ambato 1"),("Códigos digitales","2 comprados · 1 sin asignar"),("Descripción","Combo B · nivel B1+ · English for Adults")],
   btn("Editar",None,False,"Se editan nombre, precio, IVA, categoría y parámetros de matrícula; el historial de precios guarda el cambio. "+AUDIT)+btn("Pedir a proveedor","NuevoPedido.html")+btn("Ver movimientos","Movimientos.html")+btn("Desactivar",None,False,"El producto deja de ofrecerse en nuevas ventas; las matrículas existentes no cambian. "+AUDIT),
   tag='<span class="hero-code">1141</span>'+badge("Producto","navy")+badge("Activo","ok")+badge("Stock negativo en Valle","bad")),
 two(card("Parámetros de matrícula", kv(("Programa","English for Adults"),("Nivel","B1+"),("Módulos","9 y 10"),("Modalidades","Virtual y presencial"),("Se descuenta del stock","al matricular, de la sede del curso"),("Reemplaza a","Empower B1+ 1st Ed (inactivo)"))+row(btn("Editar parámetros",None,False,"Se editan programa, nivel, módulos y modalidades en los que este producto se entrega al matricular."))),
     card("Stock por sede", table(["Sede","Stock","Estado"],[[c2("Quito","comprometido 5 · mínimo 6"),"4",badge("Bajo mínimo","warn")],[c2("Valle","comprometido 3 · mínimo 6"),"-2",badge("Negativo","bad")],[c2("Ambato","comprometido 0 · mínimo 4"),"1",badge("Bajo mínimo","warn")]],wide=0)+kv(("Pedido en camino","#P-041 · 12 unidades · llega 8 oct")))),
 two(card("Códigos de activación comprados", table(["Código","Estado"],[[c2("EMP-B1P-7K2Q-…","Ingreso IM202610-01 · 1 oct · sin entregar"),badge("Sin asignar","warn")],[c2("EMP-B1P-3M9X-…","Ingreso IM202609-12 · reservado para María Andrade (módulo 9) · 12 oct"),badge("Entregado","ok")]],wide=0)),
     card("Historial de precios", table(["Vigente desde","Precio","IVA","Cambió"],[["1 ene 2026","$40.00","0%","Administración"],["1 ene 2025","$38.00","0%","Administración"],["1 mar 2024","$36.00","0%","Administración"]]))),
 card("Movimientos recientes", table(["Fecha","Tipo","Sede","Cantidad","Vinculado a","Usuario"],[["28 ago","Reserva · venta","Quito","-1","Factura 000021090 · María Andrade","Carla M."],["01 oct","Ingreso · proveedor","Valle","+1","IM202610-01 · Books & Bits","Secretaría Valle"],["30 sep","Devolución","Quito","+1","NC-000000312 · Luis Torres","Secretaría Quito"],["25 sep","Traslado","Quito → Ambato","1","Movimiento MV-0912","Secretaría Quito"]])),
 subtitle="Equivale al registro Product/Service de TeamDesk: ítem, precio e IVA, stock, parámetros de matrícula y códigos comprados"),"Detalle de producto o servicio")

# 15 Configuración
page("Configuracion.html","Configuración",shell("Configuración","Configuración",
 tabs(["Sedes","Aulas","Programas y niveles","Productos y servicios","Empresas y convenios","Tarifas de profesores","Reglas de aprobación","Metas comerciales","Plantillas de correo","Parámetros"],"Programas y niveles",{
  "Metas comerciales": filters(sel("Período",["Octubre 2026","Noviembre 2026","2026"],w="150px",col=False),sel("Sede",["Todas","Quito","Valle","Ambato","Cuenca"],w="130px",col=False))+table(["Indicador","Quito","Valle","Ambato","Cuenca"],[["Nuevas matrículas válidas","26","13","8","5"],["Servicios educativos","$10,000","$5,000","$3,000","$2,000"],["Niveles vendidos","12","6","4","2"],["Exámenes internacionales","8","4","2","2"]])+kv(("Servicios educativos","excluye inscripción y materiales"))+row(btn("Editar metas")),
  "Plantillas de correo": table(["Plantilla","Categoría","Se usa en","Canal","Acción"],[
     [c2("Bienvenida al curso","enlace de clase, horario y profesor"),"Académico","al confirmar la matrícula","Correo y WhatsApp",btn("Editar")],
     [c2("Enlace de clase","Zoom / Teams del curso"),"Académico","Enviar enlace de clase","Correo y WhatsApp",btn("Editar")],
     [c2("Recordatorio de pago","cuota por vencer o vencida, con saldo"),"Cobranza","Cartera y estado de cuenta","Correo y WhatsApp",btn("Editar")],
     [c2("Rematrícula","te faltan X días"),"Comercial","recordatorios automáticos","Correo y WhatsApp",btn("Editar")],
     [c2("Certificado emitido","PDF con código de verificación"),"Académico","al cerrar el nivel","Correo",btn("Editar")],
     [c2("Comunicado general","texto libre"),"Masivo","Correo masivo de Estudiantes y Profesores","Correo",btn("Editar")]],wide=0)+row(btn("Nueva plantilla",None,True)),
  "Sedes": table(["Sede","Ciudad","Dirección","Aulas","Base TeamDesk de origen","Estado"],[["Quito centro","Quito","Av. Amazonas N24-03","6","Cambridge Quito","Activa"],["Valle de los Chillos","Quito","Av. Ilaló 120","7","Cambridge Los Chillos","Activa"],["Ambato","Ambato","Av. Cevallos 08-33","3","Cambridge Ambato","Activa"],["Quito Norte","Quito","—","—","—","Próxima"]])+note("Hoy cada sede es una base TeamDesk independiente. La migración las consolida en una sola base con el campo Sede.")+row(btn("Nueva sede",None,True)),
  "Aulas": filters(sel("Sede",["Todas","Quito","Valle","Ambato"],w="140px",col=False),sel("Tipo",["Todas","Física","Virtual"],w="130px"),actions=btn("Nueva aula",None,True,"Se crea el aula con sus dimensiones; la capacidad se calcula con la norma SETEC (2 m² instructor + 1.5 m² por estudiante).","Configuracion.html"))+table(["Aula","Sede","Tipo","Dimensiones","Área","Capacidad SETEC","Ocupación semanal","Cursos activos","Estado"],[
     ["C-1","Valle","Física","3.40 × 4.30 m","14.62 m²","9 estudiantes","12 h / 60 h","1",badge("Disponible","ok")],
     ["C-2","Valle","Física","3.40 × 3.80 m","12.92 m²","9 estudiantes","0 h / 60 h","0",badge("Libre")],
     ["C-3","Valle","Física","4.65 × 3.85 m","17.90 m²","12 estudiantes","20 h / 60 h","2",badge("Disponible","ok")],
     ["C-5","Valle","Física","4.65 × 3.85 m","17.90 m²","12 estudiantes","8 h / 60 h","1",badge("Disponible","ok")],
     ["C-7","Valle","Física","2.90 × 3.10 m","8.99 m²","5 estudiantes","4 h / 60 h","1",badge("Disponible","ok")],
     ["Q-1","Quito","Física","5.00 × 4.00 m","20.00 m²","12 estudiantes","36 h / 60 h","3",badge("Alta ocupación","warn")],
     ["A-1","Ambato","Física","4.00 × 3.50 m","14.00 m²","8 estudiantes","8 h / 60 h","1",badge("Disponible","ok")],
     ["Zoom 2","Quito","Virtual","—","—","15 estudiantes","8 h / 60 h","1",badge("Disponible","ok")]],sede=1)+note("Capacidad SETEC: 2 m² para el instructor y 1.5 m² por estudiante. Al crear un curso, el cupo no puede superar la capacidad del aula y el horario no puede chocar con otro curso en la misma aula."),
  "Programas y niveles": two(card("Programas", table(["Programa","Módulos","Estado"],[[c2("Cambridge Eaglets (preescolar)","4–5 años · 12 h por módulo · 1 h por sesión"),"4",badge("Activo","ok")],[c2("English for Kids","6–11 años · 16 h por módulo"),"8",badge("Activo","ok")],[c2("English for Teens","12–17 años · 18 h por módulo"),"12",badge("Activo","ok")],[c2("English for Adults (ESL)","18+ años · 18 h por módulo"),"16 (A1–C1)",badge("Activo","ok")],[c2("Business English","Ejecutivos y empresas · one to one o grupal · a medida"),"a medida",badge("Activo","ok")],[c2("Exam Preparation","B2 First, C1 Advanced, A2 Key for Schools · 36 h"),"1 por examen",badge("Activo","ok")],[c2("Listening & Speaking","Complementario · club y refuerzo"),"libre",badge("Activo","ok")],[c2("Spanish","Español para extranjeros · Aula Internacional"),"8 (4 niveles)",badge("Activo","ok")],[c2("Summer for Kids · Preschoolers · Teens","Vacacionales de julio · 2 semanas"),"1",badge("Activo","ok")],[c2("Tailored","Corporativo o individual · a medida"),"a medida",badge("Activo","ok")],[c2("English for Adults Virtual · Online","Legado TeamDesk: ahora English for Adults + modalidad Virtual"),"—",badge("Migrado","neutral")]])+row('<a href="Programas.html" class="btn">Ver jerarquía completa</a>')),
     card("Regla nivel ↔ módulo", note("1 nivel comercial = 2 módulos académicos. Se vende y factura por nivel; se dicta y califica por módulo. Un módulo aprobado consume medio nivel del paquete del estudiante.")+tabla_niveles()))+
     table(["Programa","Nivel","Módulos","Precio virtual","Precio presencial","Vigencia","Estado"],[["Adults",n,m,pv,pp,"2026","Activo"] for (n,m),(pv,pp) in zip(NIVELES,[("$450","$500"),("$450","$500"),("$500","$550"),("$500","$550"),("$550","$600"),("$580","$630")])]+[["Teens","A2","3–6","$420","$470","2026","Activo"],["Kids","Kids 2","3–4","$380","$420","2026","Activo"]])+row(btn("Nuevo nivel",None,True),btn("Editar precios")),
  "Productos y servicios": productos_tab,
  "Empresas y convenios": table(["Empresa","RUC","Convenio","Paga","Vigencia","Acción"],[[c2("Grupo Nova","Ambato · RR. HH."),"1790012345001","15%","Empresa · 30 días","hasta dic 2027",'<a href="DetalleEmpresa.html">Ver</a>'],[c2("Banco del Valle","Quito"),"1790098765001","10%","Empleado","hasta jun 2027",'<a href="DetalleEmpresa.html">Ver</a>'],[c2("Clínica Santa Fe","Quito"),"1790055555001","10%","Empresa · 30 días","hasta mar 2027",'<a href="DetalleEmpresa.html">Ver</a>'],[c2("Colegio Los Andes","Valle · institucional"),"1790077777001","20% · Kids y Teens","Empleado","por renovar · dic 2026",'<a href="DetalleEmpresa.html">Ver</a>']],wide=0)+row(btn("Nueva empresa","NuevaEmpresa.html",True)),
  "Tarifas de profesores": table(["Tipo de contrato","Tarifa base / hora","Modalidad","Vigencia","Estado"],[["Por horas","$7.00","Presencial","2026","Activa"],["Por horas","$6.50","Virtual","2026","Activa"],["Nómina","Salario mensual","Ambas","2026","Activa"]])+note("La tarifa individual se fija en la ficha del profesor y requiere aprobación de Dirección."),
  "Reglas de aprobación": table(["Regla","Condición","Aprueba","Estado"],[["Descuento del asesor sin aprobación","Hasta 10% · con motivo obligatorio","Nadie (se registra y Dirección lo ve)","Activa"],["Descuento fuera de regla","> 10%","Director Comercial","Activa"],["Alta de profesor","Nunca · Coordinación Académica lo crea directamente","— (queda en audit log)","Activa"],["Tarifa de profesor fuera de tabla","Tarifa por hora distinta a la tabla vigente","Dirección","Activa"],["Asignación sin contrato","Profesor sin contrato vigente","Coordinación Académica","Activa"],["Exportar base completa","Siempre","Administrador General","Activa"]])+row(btn("Nueva regla",None,True)),
  "Parámetros": form(title="Generales", fields=[("Moneda","USD",'select',["USD"]),("Zona horaria","America/Guayaquil",'select',["America/Guayaquil"]),("Días de vencimiento de factura a crédito","15",'number'),("Umbral de alerta de stock (mínimo por sede)","6",'number'),("Email de notificaciones del sistema","notificaciones@cambridgesol.edu.ec",'email'),("Proveedor de libros por defecto","Books & Bits",'select',["Books & Bits","Otro"])])
   +form(title="Correo diario de stock negativo", fields=[("Activo","Sí",'select',["Sí","No"]),("Hora de envío","07:00",'time'),("Destinatarios","secretaria.quito@…, secretaria.valle@…, secretaria.ambato@…, admin.sucursal@…, gerencia@…",'textarea'),("Incluir bajo mínimo además de negativo","Sí",'select',["Sí","No"]),("Enviar también cuando no haya novedades","No",'select',["No","Sí"]),("Copiar al asistente de insights","Sí",'select',["Sí","No"])])
   +row(btn("Guardar cambios",None,True)),
 }),
 subtitle="Todo lo que hoy está hardcodeado en TeamDesk, configurable sin desarrollador"),"Configuración")

# 16 Nuevo estudiante
page("NuevoEstudiante.html","Nuevo estudiante",shell("Nuevo estudiante","Estudiantes",
 form(title="Datos de la persona que estudiará", fields=[("Nombres","María",'text',None,True),("Apellidos","Andrade",'text',None,True),("Cédula / ID","1712345678",'text',None,True,"Al guardar se detectan duplicados en las 4 sedes"),("Género","Femenino",'select',["Femenino","Masculino","Otro / prefiere no decir"],True),("Fecha de nacimiento","",'date',None,True,"Si es menor de 18 se pide representante"),("Discapacidad","No",'select',["No","Sí · se marca como dato sensible"],True),("Ocupación","Trabaja",'select',["Estudia","Trabaja","Estudia y trabaja","Otra"],True),("Lugar de estudio o trabajo","Ej. Banco del Pacífico",'text',None,True,"Según la ocupación elegida"),("Email","",'email',None,True),("Teléfono","",'tel',None,True),"@@DIR@@","Sede",("Ocupación / empresa","Ej. Analista · Banco Pichincha"),("Cómo nos conoció","Instagram",'select',["Instagram","Facebook","Referido","Google","Empresa / convenio","Lead Kommo"])]),
 two(form(title="Datos de facturación (destinatario de la factura)", fields=[("Tipo de identificación","Cédula",'select',["Cédula","Pasaporte","RUC"],True),("¿Facturar a nombre del estudiante?","Sí · se completa con su ficha",'select',["Sí · se completa con su ficha","No · otra persona o empresa"],True,"Si es Sí, puedes revisar y editar antes de guardar"),("Dirección de facturación","Av. Amazonas y NN. UU.",'text',None,True),("Teléfono de facturación","099 000 0001",'tel',None,True),("Nombre o razón social para la factura","María Andrade"),("CED / RUC de facturación","1712345678"),("Correo para comprobantes SRI","maria.andrade@ejemplo.com",'email')],cols=1),
     form(title="Ubicación y origen", fields=[("Programa de interés","English for Adults (ESL)",'select',["Preescolar","English for Kids","English for Teens","English for Adults (ESL)","Business English"],True),("Examen de ubicación","Agendar",'select',["Agendar","Ya rendido · resultado A2 módulo 3","No aplica · empieza en el módulo 1"],True,"Define el módulo de inicio"),("Asesor asignado","Carla M.",'select',["Carla M.","Diego R.","Sofía L."],True),("Lead de Kommo (origen)","Automático si viene de Leads",'text',None,False,"Automático"),("Consentimiento de datos (LOPDP)","Firmado",'select',["Firmado","Pendiente · se envía al correo"],True)],cols=1))
 +row(btn("Agendar examen de ubicación")),
 card("Representante · solo si es menor de 18 años", form(["Nombre del representante","Relación (madre / padre / tutor legal)","Cédula del representante","Teléfono del representante","Correo del representante","Autorización firmada (archivo)"])+note("Marcador automático de dato sensible: menor de edad · discapacidad. Estos registros exigen autorización firmada y se marcan en toda exportación (LOPDP).","warn")),
 card("Adjuntos", upload("Contrato de servicios de la primera matrícula","PDF firmado · obligatorio en la primera matrícula")+upload("Condiciones especiales (opcional)","Documentos formales de acuerdos especiales")),
 foot(btn("Guardar y matricular","NuevaVenta.html",True,"Antes de guardar se buscan cédulas iguales en las 4 sedes: si ya existe, se ofrece reutilizar la ficha y actualizar sus datos (reingreso).","NuevaVenta.html",save="estudiantes"),btn("Guardar estudiante","Ficha360.html"),btn("Cancelar","Estudiantes.html")),
 subtitle="Estudiante, representante y destinatario de la factura se guardan por separado"),"Nuevo estudiante")

# 17 Importar / exportar
page("ImportExport.html","Importar / exportar",shell("Importar / exportar estudiantes","Estudiantes",
 two(card("Importar", upload("Arrastrar archivo CSV o Excel","Columnas: nombres, apellidos, cédula, fecha de nacimiento, email, teléfono, sede")+kv(("Archivo","estudiantes_valle.xlsx"),("Filas","120"),("Válidas",badge("115","ok")),("Duplicados",badge("3","warn")),("Cédula inválida",badge("2","bad")))+table(["Fila","Nombre","Cédula","Problema"],[["17","Juan Pérez","1712345678","Ya existe (Valle)"],["42","Ana Ruiz","1798765432","Ya existe (Quito)"],["88","Pedro Mora","17-ABC","Cédula inválida"]])+row(btn("Descargar plantilla"),btn("Importar",None,True))),
     card("Exportar", filters(sel("Estado",["Todos","Activo","En transición","Inactivo"],w="150px"),sel("Programa",["Todos","Adults","Teens","Kids"],w="130px"),sel("Columnas",["Básicas (nombre, cédula, sede, nivel)","Completas","Contacto"],w="260px"))+kv(("Registros a exportar",sv(812,420,230,162)),("Incluye menores","sí (marcado sensible)"))+note("La exportación queda registrada en el audit log con tu usuario, filtros y cantidad de registros.","warn")+row(btn("Exportar CSV",None,True)))),
 subtitle="Carga masiva con validación y exportación auditada"),"Importar / exportar")

# 18 Nuevo curso
page("NuevoCurso.html","Nuevo curso",shell("Nuevo curso","Cursos",
 form(title="Datos del curso", fields=["Código (automático: 0001-2026-0773)",("Programa","English for Adults",'select',PROGRAMAS,True,"1º programa"),("Modalidad","Virtual",'select',MODALIDADES,True,"2º modalidad"),("Tipo de clase","Grupal",'select',TIPOS_CLASE,True,"3º tipo · define horas por sesión y precio"),("Nivel","B1 · módulos 7–8",'select',NIVEL_OPC,True),"Sede",("Multisucursal","No",'select',["No","Sí · admite estudiantes de varias sedes"]),("Tarifa especial del profesor","No · tabla vigente",'select',["No · tabla vigente","Sí · tarifa especial para este curso (va a aprobación)"]),("Aula o enlace virtual","Q-1 · Quito · 15 pers.",'select',AULAS,True,"Solo aulas de la sede elegida · capacidad SETEC"),("Horario","Regular noche · Lu-Ma-Mi-Ju 19:00–21:00 · 2 h",'select',PLANTILLAS,True,"Plantilla, o 'Personalizado' para elegir días y horas"),"Fecha inicio","Fecha fin (calculada: horas ÷ horas por sesión · salta feriados de Ecuador)",("Total de horas","36",'number',None,True,"One to one: paquete de 20 o 40 h"),("Equipo de Microsoft Teams","Se crea automáticamente · CSL-2026-0773",'text',None,False,"Solo cursos virtuales"),("Cupo máximo","15",'number',None,True,"≤ capacidad del aula"),("Libro / material del nivel","Empower B1+ Combo B",'text',None,False,"Se descuenta del stock al matricular"),("Precio del nivel","$500 virtual · $550 presencial",'text',None,False,"Desde catálogo")]),
 card("Horario personalizado", horario_builder(), extra='<small class="card-hint">Se muestra al elegir "Personalizado" en Horario</small>'),
 card("Profesor", filters(search("Buscar profesor","Nombre, especialidad o sede",w="300px"),sel("Contrato",["Todos","Activo","Vencido"],w="130px"),sel("Disponible en el horario",["Todos","Sí","No"],w="170px"),actions=kv(("Seleccionado",'<b>P. Gómez</b> · contrato activo · 14 de 20 h')))
   +table(["Profesor","Contrato","Carga","Disponible en el horario","Especialidad","Acción"],[
    [c2("P. Gómez","Quito y Valle · CELTA"),"Activo","14 / 20 h","Sí","Adults · B1–C1",badge("Seleccionado","navy")],
    [c2("L. Vega","Quito · TKT"),"Activo","18 / 20 h","Sí","Adults · Teens",btn("Seleccionar")],
    [c2("M. Castro","Ambato · Kids specialist"),"Activo","8 / 20 h","No · dicta Kids 1 a esa hora","Kids · Eaglets",btn("Seleccionar")],
    [c2("D. Paredes","Valle · nueva · tarifa en aprobación"),"Activo","0 / 20 h","Sí","Teens · Adults",btn("Seleccionar")],
    [c2("S. Jiménez","Quito · Business"),"Activo","12 / 20 h","Sí","Business · Exam Preparation",btn("Seleccionar")],
    [c2("R. Salas","Quito"),"Vencido","—","—","Adults",btn("Seleccionar",None,False,"El contrato de este profesor está vencido: la asignación quedará pendiente de aprobación de Coordinación y el curso se creará sin profesor hasta entonces.")]],wide=0)),
 foot(btn("Crear curso","DetalleCurso.html",True,save="cursos"),btn("Cancelar","Cursos.html")),
 subtitle="Al crear el curso se descuenta el stock de libros por cupo (inventario)"),"Nuevo curso")

# 19 Sesiones
cal="".join(f'<div><b>{d}</b><br>{c}</div>' for d,c in [("Lun 5","B1 Virtual 18:00<br>Kids 2 15:00"),("Mar 6","Teens A2 16:00"),("Mié 7","B1 Virtual 18:00<br>Kids 2 15:00"),("Jue 8","Teens A2 16:00"),("Vie 9","B1 Virtual 18:00"),("Sáb 10","Intensivo A1 09:00"),("Dom 11","")])
page("Sesiones.html","Sesiones",shell("Registro de sesiones","Sesiones",
 filters(sel("Semana",["5–11 oct 2026","28 sep–4 oct 2026","12–18 oct 2026"],w="190px",col=False),sel("Profesor",["Todos","P. Gómez","L. Vega","M. Castro"],w="160px"),sel("Origen",["Todos","Automática (Moodle)","Manual"],w="170px"),sel("Estado",["Todas","Confirmada","Pendiente","No dictada"],w="140px"),actions=kv(("Confirmadas","4"),("Pendientes","3"),("No dictadas","1"))+btn("Registrar sesión manual",None,True)),
 table(["Fecha","Curso","Sede","Profesor","Horas","Origen","Estado"],[["Lun 5 · 18:00","B1 Virtual","Quito","P. Gómez","2","Automática (Moodle)",badge("Pendiente","warn")],["Lun 5 · 15:00","Kids 2 Tarde","Valle","L. Vega","2","Manual",badge("Confirmada","ok")],["Mar 6 · 16:00","Teens A2","Ambato","M. Castro","2","Manual",badge("Confirmada","ok")],["Mié 7 · 18:00","B1 Virtual","Quito","P. Gómez","2","Automática (Moodle)",badge("Confirmada","ok")],["Mié 7 · 15:00","Kids 2 Tarde","Valle","L. Vega","2","Manual",badge("No dictada","bad")],["Jue 8 · 16:00","Teens A2","Ambato","M. Castro","2","Manual",badge("Pendiente","warn")],["Vie 9 · 18:00","B1 Virtual","Quito","P. Gómez","2","Automática (Moodle)",badge("Pendiente","warn")],["Sáb 10 · 09:00","Intensivo A1","Quito","L. Vega","4","Manual",badge("Confirmada","ok")]],sede=2),
 card("Calendario de la semana", f'<div class="cal">{cal}</div>'),
 two(card("Sesión seleccionada", kv(("Curso","B1 Virtual · Quito"),("Fecha","Lun 5 oct · 18:00–20:00"),("Profesor","P. Gómez"),("Horas","2"),("Origen","Automática (Moodle)"),("Asistencia","12/15"),("Estado",badge("Pendiente","warn")))+row(btn("Confirmar sesión",None,True),btn("Marcar no dictada"))),
     card("Alertas", li(["Sesión fuera del horario programado","Profesor con contrato vencido","Curso sin sesiones registradas esta semana"]))),
 subtitle="Las sesiones confirmadas alimentan progreso y payment sheet"),"Registro de sesiones")

# 20 Ficha profesor
prof_aside=f'''<aside class="profile"><div class="profile-cover"></div><div class="profile-body">{avatar("PG")}<div class="chips" style="justify-content:center;gap:8px"><span class="badge badge-navy">PRO-0042</span>{badge("Activo","ok")}</div><h2>Pablo Gómez</h2><span class="kpi-sub">Profesor por horas · desde feb 2024 · Quito y Valle</span>
    <div class="actions"><button type="button" class="btn" style="flex:0 0 46px" aria-label="Llamar" data-action="Se abre el marcador con el teléfono del profesor.">{ico("phone")}</button><button type="button" class="btn" style="flex:0 0 46px" aria-label="Email" data-action="Se abre un correo al profesor.">{ico("mail")}</button><button type="button" class="btn" style="background:var(--tint-navy);border-color:var(--tint-navy)" data-action="Se abre WhatsApp con el profesor (enlace de clase, recordatorio de sesión por confirmar).">{ico("chat")}&nbsp;WhatsApp</button></div>
    <div class="section"><h3>Contacto</h3><div class="clist"><div><span class="cico">{ico("mail","")}</span><span><b>Email</b>p.gomez@ejemplo.com</span></div><div><span class="cico">{ico("phone","")}</span><span><b>Teléfono</b>099 000 0020</span></div><div><span class="cico">{ico("id","")}</span><span><b>Cédula</b>1709876543</span></div><div><span class="cico">{ico("pin","")}</span><span><b>Dirección</b>Quito · Cumbayá</span></div></div></div>
    <div class="section"><h3>Educación y certificaciones</h3><div class="awards"><div><i></i>Lic. en Lingüística Aplicada · PUCE · 2019</div><div><i></i>CELTA · Cambridge · 2021</div><div><i></i>C2 Proficiency · 2020</div><div><i></i>Teaching Young Learners · 2023</div></div></div>
    {only("ADM,GER,SUC,COO", '<div class="section"><h3>Tarifa y pago</h3><div class="clist"><div><span class="cico">'+ico("coin","")+'</span><span><b>Tarifa por hora</b>$7.00 · dentro de la tabla ($6.50–$7.50)</span></div><div><span class="cico">'+ico("doc","")+'</span><span><b>Contrato</b>Por horas · vigente hasta 31 dic 2026 · máx. 20 h/sem</span></div><div><span class="cico">'+ico("lock","")+'</span><span><b>Pago</b>Transferencia · Banco Pichincha · ahorros ····4821 · quincenal</span></div><div><span class="cico">'+ico("cal","")+'</span><span><b>Factura del profesor</b>Emite factura · RUC 1709876543001</span></div></div></div>')}
    <div class="actions">{only("ADM,GER,SUC,COO",btn("Asignar a curso",None,True,"Se elige un curso sin profesor compatible con su disponibilidad; si el contrato no está vigente la asignación va a aprobación."),True)}{only("ADM,GER,SUC,COO",'<a href="AltaProfesor.html" class="btn">'+ico("edit")+'&nbsp;Editar</a>',True)}</div></div></aside>'''
perf_panel=two(card("Desempeño · últimos 6 meses", '<div class="gauges">'+gauge(88,"Asistencia de sus cursos",CH[2])+gauge(94,"Pass rate",CH[3])+gauge(97,"Sesiones registradas a tiempo",CH[0])+'</div>'+linechart(["May","Jun","Jul","Ago","Sep","Oct"],{"Asistencia":[84,86,85,88,89,88],"Pass rate":[90,92,93,95,94,94]},h=150)),
   card("Comparado con la sede", hbars([("Asistencia · P. Gómez",88),("Asistencia · promedio Quito",84),("Pass rate · P. Gómez",94),("Pass rate · promedio Quito",89),("Retención al siguiente nivel · P. Gómez",78),("Retención · promedio Quito",71)],unit="")+kv(("Cursos dictados","23 desde feb 2024"),("Estudiantes formados","286"),("Horas acumuladas","1,340 h"))))+card("Reconocimientos y observaciones", table(["Fecha","Tipo","Detalle","Registró"],[["sep 2026",badge("Reconocimiento","ok"),"Mejor asistencia de la sede en el trimestre","Coord. Académica"],["jul 2026",badge("Observación","warn"),"2 sesiones registradas fuera de horario; confirmadas luego","Coord. Académica"],["mar 2026",badge("Reconocimiento","ok"),"100% de pass en Adults A2 (0001-2026-0512)","Coord. Académica"]])+only("ADM,GER,SUC,COO",row(btn("Agregar observación",None,False,"Se agrega una observación o reconocimiento al historial del profesor; queda en el audit log."))))
page("FichaProfesor.html","Ficha profesor",shell("P. Gómez","Profesores",
 f'<div class="grid" style="grid-template-columns:320px 1fr">{prof_aside}<div style="display:flex;flex-direction:column;gap:20px;min-width:0">'
 +'<div class="grid" style="grid-template-columns:1.2fr 1fr 1fr 1fr">'+kpi("Dictando ahora","B1 Virtual · Zoom 2","19:00–21:00 · 12 estudiantes conectados")+'<div class="card" style="align-items:center">'+gauge(60,"Carga · 12 de 20 h")+'</div><div class="card" style="align-items:center">'+gauge(88,"Asistencia de sus cursos",CH[2])+'</div><div class="card" style="align-items:center">'+gauge(94,"Pass últimos 3 módulos",CH[3])+'</div></div>'
 +tabs(["Agenda y carga","Desempeño","Datos y educación","Contrato, tarifa y pago","Cursos","Sesiones","Historial de pagos"],"Agenda y carga",roles={"Contrato, tarifa y pago":"ADM,GER,DIR,SUC,COO","Historial de pagos":"ADM,GER,SUC,COO"},panels={
  "Agenda y carga": two(card("Clases de hoy · lunes 19 oct", table(["Hora","Curso","Estado"],[[c2("14:00","16:00"),c2("Adults A2","0001-2026-0620 · Valle · C-5 · 9/12 estudiantes"),badge("Confirmada","ok")],[c2("19:00","21:00"),c2("Adults B1 Virtual","0001-2026-0767 · Quito · Zoom 2 · 12/15 estudiantes"),badge("En curso ahora","warn")]],wide=1)),
     card("Carga semanal (horas)", vbars([("Lu",[4]),("Ma",[2]),("Mi",[4]),("Ju",[2]),("Vi",[0]),("Sa",[0])],["Horas dictadas"],h=120)+kv(("Total","12 h"),("Máximo contrato","20 h"),("Disponible","Lu-Ma-Mi-Ju 17:00–19:00 · Vi · Sa"))))
     +card("Cursos que dicta ahora", table(["Código","Curso","Sede","Horario","Estudiantes","Asistencia","Avance","Termina","Acción"],[["0001-2026-0767",c2('<a href="DetalleCurso.html">English for Adults B1 Virtual</a>',"0001-2026-0767 · Quito · Zoom 2"),"Quito",c2("Lu-Ma-Mi-Ju","19:00–21:00"),"12/15","90%",progress(60),"20 nov",V],["0001-2026-0620",c2('<a href="DetalleCurso.html">English for Adults A2</a>',"0001-2026-0620 · Valle · C-5"),"Valle",c2("Lu-Mi","14:00–16:00"),"9/12","85%",progress(59),"5 dic",V],["0001-2026-0772",c2('<a href="DetalleCurso.html">English for Teens B1 Virtual</a>',"0001-2026-0772 · propuesto · Valle · Teams 1"),"Valle",c2("Lu-Ma-Mi-Ju","17:00–19:00"),"6/12","—",progress(0),"inicia 20 oct",V]],sede=2,hide=(0,2),wide=1)),
  "Desempeño": perf_panel,
  "Datos y educación": two(form(title="Datos personales", fields=[("Nombres y apellidos","Pablo Gómez"),("Cédula / ID","1709876543"),"Fecha de nacimiento",("Email","p.gomez@ejemplo.com",'email'),("Teléfono","099 000 0020",'tel'),"Sede(s)",("Dirección","Quito · Cumbayá"),"Foto (archivo)"]),
     card("Educación y certificaciones", table(["Título / certificación","Institución","Año","Documento"],[["Lic. en Lingüística Aplicada","PUCE","2019",btn("Ver PDF")],["CELTA","Cambridge Assessment","2021",btn("Ver PDF")],["C2 Proficiency","Cambridge Assessment","2020",btn("Ver PDF")],["Teaching Young Learners","Cambridge Assessment","2023",btn("Ver PDF")]])+only("ADM,GER,SUC,COO",row(btn("Agregar título o certificación",None,False,"Se agrega el título o certificación con su documento adjunto."))))),
  "Contrato, tarifa y pago": two(card("Contrato y tarifa", kv(("Tipo","Por horas · máx. 20 h/semana"),("Tarifa","$7.00/h · dentro de la tabla"),("Vigencia","1 ene – 31 dic 2026"),("Modalidades","Virtual y presencial"),("Creado por","Coord. Académica · 8 ene 2026"))+table(["Documento","Subido por","Fecha"],[["contrato_pgomez_2026.pdf","Coord. Académica","8 ene 2026"],["cedula_pgomez.pdf","Coord. Académica","8 ene 2026"]])+table(["Vigencia","Tipo","Tarifa","Observación"],[["2026","Por horas","$7.00/h","Dentro de tabla"],["2025","Por horas","$6.50/h","Dentro de tabla"],["2024","Por horas","$6.00/h","Dentro de tabla"]])),
     card("Datos de pago", kv(("Forma de pago","Transferencia"),("Banco","Banco Pichincha"),("Cuenta","Ahorros ····4821"),("Titular","Pablo Gómez"),("Frecuencia","Quincenal, contra payment sheet aprobada"),("Emite factura","Sí · RUC 1709876543001"))+row(btn("Editar datos de pago",None,False,"Se editan los datos bancarios del profesor; el cambio queda en el audit log y se notifica a Administración.")))),
  "Cursos": table(["Código","Curso","Sede","Nivel","Modalidad","Horario","Estudiantes","Asistencia","Pass","Estado"],[["0001-2026-0767",c2("English for Adults B1 Virtual","0001-2026-0767 · Quito · Lu-Ma-Mi-Ju 19:00–21:00"),"Quito","B1","Virtual","Lu-Ma-Mi-Ju 19:00–21:00","12","90%","—",badge("En curso","ok")],["0001-2026-0620",c2("English for Adults A2","0001-2026-0620 · Valle · Lu-Mi 14:00–16:00"),"Valle","A2","Presencial","Lu-Mi 14:00–16:00","9","85%","—",badge("En curso","ok")],["0001-2026-0512",c2("English for Adults A2","0001-2026-0512 · Quito · Lu-Mi 18:00–20:00"),"Quito","A2","Presencial","Lu-Mi 18:00–20:00","11","92%","100%",badge("Cerrado")],["0001-2025-0430",c2("English for Adults A1","0001-2025-0430 · Quito · Sa 09:00–13:00"),"Quito","A1","Presencial","Sa 09:00–13:00","14","88%","93%",badge("Cerrado")],["0001-2025-0210",c2("English for Adults B1","0001-2025-0210 · Quito · Lu-Mi 18:00–20:00"),"Quito","B1","Presencial","Lu-Mi 18:00–20:00","13","86%","92%",badge("Cerrado")]],sede=2,hide=(0,2,5),wide=1),
  "Sesiones": table(["Fecha","Curso","Duración","Origen","Estado"],[["05 oct","Adults B1 Virtual","2 h","Automática (Moodle)",badge("Confirmada","ok")],["05 oct","Adults A2","2 h","Manual",badge("Confirmada","ok")],["01 oct","Adults B1 Virtual","2 h","Automática (Moodle)",badge("Pendiente","warn")]])+row(btn("Registrar sesión","Sesiones.html",True)),
  "Historial de pagos": table(["Mes","Horas","Tarifa","Monto","Estado","Acción"],[["Oct 2026","48","$7.00","$336",badge("Borrador"),btn("Ver","PaymentSheet.html")],["Sep 2026","44","$7.00","$308",badge("Pagado","ok"),btn("Ver","PaymentSheet.html")],["Ago 2026","40","$7.00","$280",badge("Pagado","ok"),btn("Ver","PaymentSheet.html")]]),
 })+'</div></div>',
 subtitle="Perfil completo: contacto, educación, tarifa y pago, desempeño, cursos y pagos"),"Ficha del profesor")

# 21 Alta profesor
page("AltaProfesor.html","Alta de profesor",shell("Alta de profesor","Profesores",
 form(title="Datos personales", fields=[("Nombres y apellidos","Daniela Paredes",'text',None,True),("Cédula / ID","1712345679",'text',None,True),"Fecha de nacimiento",("Email","d.paredes@ejemplo.com",'email'),("Teléfono","099 000 0030",'tel'),"Sede(s)","Dirección","Foto (archivo)"]),
 form(title="Educación y certificaciones", fields=[("Título principal","Lic. en Educación · Universidad Central · 2022"),("Certificaciones","TKT · 2023; B2 First"),"Título / certificado (archivo)","Hoja de vida (archivo)"]),
 form(title="Contrato, tarifa y pago", fields=["Tipo de contrato (por horas / nómina)",("Tarifa por hora","9.00",'number',None,True,"Pay scale aprobado: $6.50–$7.50 según sede, título y MOCK; una tarifa distinta pasa a aprobación de Dirección"),("Pay scale aprobado (archivo)","",'file'),("RUC","1712345679001",'text',None,True,"Sin RUC no se emite factura de servicios profesionales"),("Antecedentes penales (archivo)","",'file'),("Resultado del MOCK","C1",'select',["B2","C1","C2"],True),"Vigencia del contrato","Horas máximas por semana","Modalidades (virtual / presencial / ambas)","Contrato firmado (archivo)",("Forma de pago","Transferencia",'select',["Transferencia","Efectivo"]),("Banco y cuenta","Banco Pichincha · ahorros ····"),("Emite factura (sí / no)","Sí",'select',["Sí","No"]),"RUC (si emite factura)"]),
 card("Qué pasa al guardar", flow(["Coordinación Académica guarda","Profesor activo de inmediato","Puede recibir cursos","Aparece en payment sheet","Empieza la hoja de ruta de inducción"])+kv(("Quién puede crear profesores","Coordinación Académica, Administración de sucursal y Administrador General, sin pedir otra autorización"),("Por qué no hace falta","el candidato ya pasó por el proceso de contratación: pay scale aprobado por Coord. Administrativa y contratación aprobada por Dirección Administrativa"),("Lo único que vuelve a aprobación","una tarifa por hora distinta al pay scale aprobado → Dirección"),("Desde un candidato",'<a href="DetalleCandidato.html">María José Vinueza · aprobada · lista para crear perfil</a>: los datos, documentos y pay scale se precargan'),("Siempre queda","en el audit log con quién lo creó, el contrato y los documentos habilitantes adjuntos"))),
 foot(btn("Guardar profesor",None,True,save="profesores"),btn("Cancelar","Profesores.html")),
 subtitle="Coordinación lo crea directamente; cada alta queda registrada con contrato adjunto"),"Alta de profesor")


# ===== Contratación de profesores (manual de contratación de servicios profesionales, BPMN, checklists) =====
VC='<a href="DetalleCandidato.html">Ver</a>'
ETAPAS_CONTRATACION=[
 ("Vacante aprobada","Coordinación Académica detecta la necesidad y Dirección General Académica aprueba abrir el proceso","Coord. Académica · DGA","done"),
 ("Anuncio y recepción de CV","Publicación en LinkedIn y web; los CV llegan a la carpeta compartida de la sede","Asistente de Gerencia","done"),
 ("Revisión de CV y entrevista telefónica","Filtro de perfil (título, experiencia, nivel de inglés) y primera llamada","Coord. Académica","done"),
 ("Referencias","Formato de referencias de empleo: 2 laborales + 1 personal, con cargo, período y motivo de salida","Coord. Académica","done"),
 ("Entrevista de contratación","Informe FT-SGC-002: trayectoria, intereses, conocimiento docente, manejo de clase, enseñanza virtual, desarrollo profesional y expectativas","Coord. Académica","done"),
 ("Clase demostrativa","Rúbrica D-SGC-002: planificación, ambiente, recursos, lenguaje, manejo de clase y evaluación (1 a 5 por aspecto)","Coord. Académica","now"),
 ("MOCK C1","Resultado mínimo B2 para dictar; C1 para niveles altos","Coord. Académica",""),
 ("Entrevista formal","Entrevista con Dirección General Académica y decisión de continuar","DGA",""),
 ("Pay scale","Escala salarial según sede, título y resultado del MOCK; aprobada por Coordinación Administrativa","Coord. Administrativa",""),
 ("Aprobación de contratación","Validación de documentos habilitantes y visto bueno final","Dirección Administrativa",""),
 ("Alta del profesor","Se crea el perfil con contrato, tarifa aprobada y documentos; correo de bienvenida e inducción","Coord. Académica · Asistencia Académica",""),
 ("Hoja de ruta e inducción","Checklist de inducción (plataformas, Moodle New Edge, políticas) y seguimiento del primer curso","Coord. Académica · Coord. Administrativa",""),
]
DOCS_HABILITANTES=[("Hoja de vida",True),("Cédula o pasaporte",True),("Título universitario o certificación docente",True),("Certificado de antecedentes penales",True),("Resultado del MOCK (≥ B2)",True),("Rúbrica de clase demostrativa",True),("Pay scale firmado",True),("RUC activo (servicios profesionales)",True),("Certificaciones internacionales (TKT, CELTA, etc.)",False),("Contrato civil de servicios firmado",True)]
candidatos_tbl=table(["Candidato","Sede","Vacante","Etapa","Último paso","Responsable","Hace","Acción"],[
 [c2('<a href="DetalleCandidato.html" data-row>Daniela Paredes</a>',"Lic. en Educación · TKT · C1"),"Valle","Teens B1 Virtual · Lu-Ju 17:00","Clase demostrativa",badge("Demo agendada · 24 oct 16:00","navy"),"Coord. Académica Valle","2 días",VC],
 [c2("Jorge Andrade","Lic. en Lingüística · CELTA"),"Quito","Adults A1 Sábados","Pay scale",badge("Esperando aprobación de Coord. Administrativa","warn"),"Coord. Administrativa","3 días",VC],
 [c2("Paula Cevallos","Ing. Comercial · B2 First"),"Ambato","Business English · Ma-Ju 07:00","Referencias",badge("1 de 3 referencias recibidas","warn"),"Coord. Académica Ambato","5 días",VC],
 [c2("Esteban Ruiz","Lic. en Idiomas · TKT"),"Quito","Kids 2 Mañana","MOCK C1",badge("Resultado B1 · no cumple el mínimo","bad"),"Coord. Académica Quito","1 día",VC],
 [c2("Carolina Mera","MSc. en Enseñanza de Inglés · CELTA"),"Valle","Exam Preparation · Sa 09:00","Aprobación de contratación",badge("Documentos completos · falta visto bueno","warn"),"Dirección Administrativa","hoy",VC],
 [c2("Andrés Calle","Lic. en Educación"),"Ambato","Kids 1 Tarde","Revisión de CV",badge("Entrevista telefónica pendiente","neutral"),"Coord. Académica Ambato","6 días",VC],
 [c2("María José Vinueza","Lic. en Lingüística · CELTA · C1"),"Quito","Adults B2 Intensivo","Alta del profesor",badge("Aprobada · lista para crear perfil","ok"),"Coord. Académica Quito","hoy",VC],
 [c2("Luis Guamán","Tecnólogo · B2"),"Valle","Teens A2","Descartado",badge("No continúa · referencias","neutral"),"—","12 días",VC]],sede=1,hide=(1,),wide=0)
hoja_ruta=table(["Tarea","Responsable","Cuándo","Estado"],[
 ["Correo de bienvenida con horario, sede y contacto de coordinación","Coord. Académica","Al aprobar la contratación",badge("Hecho","ok")],
 ["Crear cuenta de correo institucional y acceso a Drive de la sede","Asistencia Académica","Antes del primer día",badge("Hecho","ok")],
 ["Alta en Moodle New Edge, Cambridge One y GradeKeeper","Asistencia Académica","Antes del primer día",badge("Pendiente","warn")],
 ["Registro en el reloj de asistencia (tablet CAMB-CLOCK)","Coord. Administrativa","Primer día",badge("Pendiente","warn")],
 ["Entrega de credencial, locker y material del nivel","Coord. Administrativa","Primer día",badge("Pendiente","warn")],
 ["Inducción: políticas, payment sheet, reemplazos, atrasos y cancelaciones","Coord. Académica","Primera semana",badge("Pendiente","warn")],
 ["Agregar al grupo de WhatsApp de docentes de la sede","Coord. Académica","Primera semana",badge("Pendiente","warn")],
 ["Observación de la primera clase y retroalimentación","Coord. Académica","Al 20% del primer curso",badge("Programada","neutral")]],wide=0)
fin_contrato=table(["Tarea","Responsable","Estado"],[
 ["Desvincular de cursos activos y reasignar profesor","Coord. Académica",badge("Hecho","ok")],
 ["Dar de baja en Moodle, Cambridge One, GradeKeeper y Teams","Asistencia Académica",badge("Hecho","ok")],
 ["Retirar correo institucional, Drive y grupos de WhatsApp","Asistencia Académica",badge("Pendiente","warn")],
 ["Entrega de reportes finales (notas, portafolio, End of level report)","Profesor",badge("Pendiente","warn")],
 ["Encuesta de salida","Coord. Académica",badge("Pendiente","warn")],
 ["Confirmar saldo por facturar y última payment sheet","Coord. Administrativa",badge("Pendiente","warn")],
 ["Devolución de locker, credencial y material","Coord. Administrativa",badge("Pendiente","warn")],
 ["Pago final y cierre del expediente","Dirección Administrativa",badge("Bloqueado hasta completar lo anterior","neutral")]],wide=0)
page("ContratacionProfesores.html","Contratación de profesores",shell("Contratación de profesores","Profesores",
 stages('<b>'+sv(8,4,3,1,0)+' candidatos en proceso</b><span class="sync-ok">Manual de contratación de servicios profesionales · 2026</span>',[
   ("Selección",sv(3,1,1,1,0),"CV, llamada, referencias","var(--info)","Selección"),
   ("Evaluación",sv(2,1,1,0,0),"entrevista, demo, MOCK","var(--warn)","Evaluación"),
   ("Aprobaciones",sv(2,1,1,0,0),"pay scale y contratación","var(--warn)","Aprobaciones"),
   ("Alta e inducción",sv(1,1,0,0,0),"perfil creado y hoja de ruta","var(--ok)","Alta")]),
 tabs(["Candidatos","Etapas del proceso","Documentos habilitantes","Hoja de ruta de inducción","Finalización de contrato"],"Candidatos",roles={"Finalización de contrato":"ADM,GER,DIR,SUC"},counts={"Candidatos":8},panels={
  "Candidatos": filters(search("Buscar","Nombre, título o vacante",w="240px"),sel("Etapa",["Todas","Revisión de CV","Referencias","Clase demostrativa","MOCK C1","Pay scale","Aprobación de contratación","Alta del profesor","Descartado"],w="210px"),sel("Vacante",["Todas","Teens B1 Virtual · Lu-Ju 17:00","Adults A1 Sábados","Business English · Ma-Ju 07:00","Kids 2 Mañana","Exam Preparation · Sa 09:00","Kids 1 Tarde","Adults B2 Intensivo","Teens A2"],w="220px"),actions='<span class="result-count" aria-live="polite"></span>'+btn("Nuevo candidato",None,True)+btn("Publicar vacante"))+candidatos_tbl+pager(8),
  "Etapas del proceso": card("Del anuncio a la primera clase", flow(ETAPAS_CONTRATACION)+kv(("Regla","ningún profesor recibe cursos ni entra a la payment sheet sin pay scale aprobado y documentos habilitantes completos"),("Quién crea el perfil","Coordinación Académica, al llegar a la etapa de alta; la autorización ya ocurrió en las etapas anteriores"),("Formatos","D-SGC-001 banco de preguntas · FT-SGC-002 informe de entrevista · D-SGC-002 rúbrica de clase demostrativa · formato de referencias"))),
  "Documentos habilitantes": card("Expediente del profesor", table(["Documento","Obligatorio","Quién lo revisa"],[[d,badge("Sí","navy") if r else badge("Opcional","neutral"),"Coord. Administrativa" if d in ("RUC activo (servicios profesionales)","Pay scale firmado","Contrato civil de servicios firmado") else "Coord. Académica"] for d,r in DOCS_HABILITANTES],wide=0)+kv(("Sin RUC","no se puede emitir la factura de servicios profesionales: la payment sheet queda retenida"),("Antecedentes penales","vigencia máxima 6 meses al momento de la contratación"))),
  "Hoja de ruta de inducción": card("Hoja de ruta · María José Vinueza · Adults B2 Intensivo · Quito", hoja_ruta+kv(("Avance","2 de 8 tareas"),("Primer día","3 nov 2026"),("Responsables","Coord. Académica · Asistencia Académica · Coord. Administrativa"))),
  "Finalización de contrato": card("Checklist de finalización · R. Salas · Ambato", fin_contrato+kv(("Motivo","contrato vencido · no renueva"),("Última sesión","30 sep 2026"),("Regla","el pago final se libera cuando todas las tareas están completas"))),
 }),
 subtitle="Pipeline de selección, evaluación, aprobaciones, alta e inducción; cada etapa con su responsable y formato"),"Contratación de profesores")

rubrica=table(["Aspecto","Puntaje (1–5)","Observación"],[
 ["a) Planificación",'<span class="mono">4</span>',"Objetivos claros alineados al currículo; faltó diferenciar por nivel"],
 ["b) Ambiente de aprendizaje",'<span class="mono">5</span>',"Participación de todos los estudiantes"],
 ["c) Recursos",'<span class="mono">4</span>',"Buen uso de Cambridge One; material impreso justo"],
 ["d) Lenguaje y destrezas",'<span class="mono">4</span>',"Lenguaje claro; retroalimentación oportuna"],
 ["e) Manejo de clase",'<span class="mono">3</span>',"Transiciones lentas entre actividades"],
 ["f) Evaluación y retroalimentación",'<span class="mono">4</span>',"Comprobó comprensión al final de cada actividad"]],wide=0)
page("DetalleCandidato.html","Detalle candidato",shell("Daniela Paredes · candidata","Profesores",
 hero([("Vacante","Teens B1 Virtual · Valle · Lu-Ju 17:00–19:00"),("Perfil","Lic. en Educación · TKT 2023 · B2 First"),("Nivel de inglés","C1 (autoevaluación) · MOCK pendiente"),("Experiencia","3 años · colegio y academia"),("Origen","LinkedIn · 8 oct 2026"),("Responsable","Coord. Académica Valle")],
  btn("Registrar resultado de clase demostrativa",None,True)+btn("Agendar MOCK")+more_menu(btn("Descartar candidato",None,False,kind="danger")+btn("Reprogramar demo")+btn("Descargar expediente")),
  tag=badge("Clase demostrativa · 24 oct 16:00","navy")+badge("Valle","navy")),
 two(card("Etapas", flow(ETAPAS_CONTRATACION[:8])),
     card("Entrevista de contratación · FT-SGC-002", kv(("Fecha","15 oct 2026 · 45 min"),("Entrevistó","Coord. Académica Valle"),("Trayectoria","3 años en colegio bilingüe y academia; Kids y Teens"),("Conocimiento docente","Enfoque comunicativo, TKT; sin experiencia en exámenes internacionales"),("Manejo de clase","Rutinas claras con niños; poca experiencia con adolescentes"),("Enseñanza virtual","Zoom y Teams; usa Kahoot y Wordwall"),("Desarrollo profesional","Quiere CELTA en 2027"),("Expectativas","15–20 h/semana en la tarde; disponible sábados"),("¿Continúa el proceso?",badge("Sí","ok")))
       +table(["Referencia","Relación","Resultado"],[["Colegio Los Andes · Coordinadora","Laboral · 2023–2025",badge("Favorable","ok")],["Academia Speak Up · Directora","Laboral · 2021–2023",badge("Favorable","ok")],["Referencia personal","Personal",badge("Favorable","ok")]],wide=0))),
 card("Clase demostrativa · rúbrica D-SGC-002", rubrica+kv(("Total","24 / 30 · promedio 4.0"),("Mínimo para continuar","3.5 de promedio y ningún aspecto en 1"),("Retroalimentación","entregar por escrito al candidato con fortalezas y áreas de mejora"))+'<p class="plain">La rúbrica se llena durante la clase de 30 minutos frente a un grupo real o simulado. El puntaje promedio y las observaciones quedan en el expediente y los ve Dirección General Académica en la entrevista formal.</p>'),
 two(card("Pay scale propuesto", kv(("Sede","Valle"),("Título","Tercer nivel · educación"),("MOCK","pendiente"),("Tarifa sugerida por la tabla","$6.50/h"),("Estado",badge("Se calcula al tener el MOCK","neutral")))+only("ADM,GER,DIR,SUC",row(btn("Aprobar pay scale",None,False,disabled_reason="Falta el resultado del MOCK")))),
     card("Documentos habilitantes", table(["Documento","Estado"],[["Hoja de vida",badge("Recibido","ok")],["Cédula",badge("Recibido","ok")],["Título universitario",badge("Recibido","ok")],["Antecedentes penales",badge("Pendiente","warn")],["RUC",badge("Pendiente","warn")],["Resultado del MOCK",badge("Pendiente","warn")],["Pay scale firmado",badge("Después de la aprobación","neutral")]],wide=0))),
 subtitle="Expediente del candidato: entrevista, referencias, clase demostrativa, MOCK, pay scale y documentos"),"Detalle de candidato")


# ===== Reclutamiento de personal administrativo (proceso ISO 9001) · propuesta fuera del alcance =====
VR='<a href="ReclutamientoAdministrativo.html">Ver</a>'
ETAPAS_RECLUTAMIENTO=[
 ("Vacante aprobada","Necesidad nueva o existente, aprobada por Gerencia General","Gerencia General · Administración","done"),
 ("Perfil del cargo","Funciones, competencias, experiencia y modalidad según el manual de funciones","Administración · Área solicitante","done"),
 ("Publicación de la vacante","LinkedIn, Indeed y sitio web, con presupuesto de publicación aprobado (Anexo 1)","Administración","done"),
 ("Filtración y preselección","Revisión de hojas de vida y pre-screen telefónico de 10 minutos (Anexo 2)","Administración · Talento Humano","done"),
 ("Entrevistas","Presenciales o virtuales: conocimientos, competencias, disponibilidad y encaje","Administración · Gerencia","now"),
 ("Documentación","CV, cédula, papeleta de votación, certificados, cartas de recomendación, antecedentes penales (Anexo 3)","Administración",""),
 ("Verificación de referencias","Referencias personales y laborales: cargo, período, conducta (Anexo 4)","Administración",""),
 ("Evaluaciones y exámenes","Pruebas de habilidades, evaluación psicológica y exámenes médicos preocupacionales (Anexo 5)","Administración · Profesional externo",""),
 ("Oferta laboral y aceptación","Correo de propuesta: cargo, horario, remuneración, beneficios de ley y fecha de ingreso (Anexo 6)","Administración",""),
 ("Inducción","Misión y visión, reglamentos, organigrama, manual de funciones; entrega de equipos con acta","Administración · Área solicitante",""),
 ("Firma del contrato","Contrato bajo relación de dependencia conforme a la legislación vigente","Gerencia General · Administración",""),
 ("Comunicación institucional","Correo al personal con funciones y datos de contacto del nuevo colaborador","Administración",""),
]
postulantes_tbl=table(["Postulante","Sede","Vacante","Etapa","Último paso","Responsable","Hace","Acción"],[
 [c2("Valentina Rojas","Lic. en Administración · 4 años"),"Quito","Secretaría administrativa-académica","Entrevistas",badge("Entrevista con Gerencia · 27 oct 10:00","navy"),"Administración","hoy",VR],
 [c2("Kevin Suárez","Tecnólogo en contabilidad"),"Valle","Asistente contable","Evaluaciones y exámenes",badge("Evaluación psicológica solicitada","warn"),"Profesional externo","2 días",VR],
 [c2("Mónica Terán","Lic. en Marketing · 2 años"),"Ambato","Asesora comercial","Oferta laboral y aceptación",badge("Oferta enviada · responde hasta 28 oct","warn"),"Administración","1 día",VR],
 [c2("Pablo Cárdenas","Bachiller · atención al cliente"),"Quito","Recepción","Filtración y preselección",badge("Pre-screen pendiente","neutral"),"Talento Humano","4 días",VR],
 [c2("Gabriela Ponce","MSc. en Educación · 6 años"),"Valle","Coordinación académica","Inducción",badge("Contrato firmado · inicia 3 nov","ok"),"Administración · Área solicitante","hoy",VR],
 [c2("Diego Rivas","Lic. en Administración"),"Quito","Secretaría administrativa-académica","Verificación de referencias",badge("1 de 4 referencias verificadas","warn"),"Administración","3 días",VR],
 [c2("Carla Moreno","Ing. en Sistemas"),"Ambato","Asistente de administración","Descartado",badge("No seleccionada · correo enviado","neutral"),"—","8 días",VR]],sede=1,hide=(1,),wide=0)
docs_admin=table(["Documento","Obligatorio","Estado · Valentina Rojas"],[
 ["Hoja de vida actualizada",badge("Sí","navy"),badge("Recibido","ok")],["Copia a color de la cédula",badge("Sí","navy"),badge("Recibido","ok")],["Papeleta de votación",badge("Sí","navy"),badge("Recibido","ok")],
 ["Títulos y certificados habilitantes",badge("Sí","navy"),badge("Recibido","ok")],["Cartas de recomendación (2 personales + 2 laborales)",badge("Sí","navy"),badge("3 de 4","warn")],["Certificado de antecedentes penales",badge("Sí","navy"),badge("Pendiente","warn")],
 ["Planilla de servicios básicos",badge("Sí","navy"),badge("Pendiente","warn")],["Exámenes médicos preocupacionales",badge("Según el cargo","neutral"),badge("Después de la oferta","neutral")],["Evaluación psicológica",badge("Según el cargo","neutral"),badge("Después de la oferta","neutral")]],wide=0)
correos_recl=table(["Momento","Correo","Qué incluye","Acción"],[
 [c2("Al descartar","Anexo · aviso no seleccionado"),"Aviso de no selección","Agradecimiento, decisión de avanzar con otro perfil y disposición a futuras oportunidades",btn("Enviar aviso de no selección")],
 [c2("Al seleccionar","Anexo 6"),"Propuesta laboral y bienvenida","Cargo, horario, almuerzo, jornadas adicionales, remuneración menos aporte IESS, décimos, fondos de reserva, utilidades y documentación requerida",btn("Enviar oferta laboral")],
 [c2("Según el cargo","Anexo 5"),"Solicitud de exámenes médicos y psicológicos","Pedido al profesional externo con CV y funciones del cargo, bajo confidencialidad",btn("Solicitar exámenes")],
 [c2("Tras la firma","Inicio de labores"),"Inicio de labores","Misión y visión, reglamentos interno y de estudiantes, funciones, organigrama, consentimiento de datos y manual de funciones",btn("Enviar correo de inicio de labores")],
 [c2("Primer día","Comunicación institucional"),"Comunicación al personal","Nombre, cargo, funciones y datos de contacto del nuevo colaborador",btn("Comunicar ingreso al personal")]],wide=2)
page("ReclutamientoAdministrativo.html","Reclutamiento administrativo",shell("Reclutamiento de personal administrativo","Reclutamiento",
 '<p class="chips">'+badge("Propuesta · fuera del alcance del contrato actual")+'</p>',
 stages('<b>'+sv(7,3,2,2,0)+' postulantes en proceso</b><span class="sync-ok">Proceso de contratación de nuevo personal · ISO 9001</span>',[
   ("Selección",sv(2,1,0,1,0),"vacante, publicación, pre-screen","var(--info)","Selección"),
   ("Entrevistas y documentos",sv(2,1,1,0,0),"entrevistas, referencias","var(--warn)","Entrevistas"),
   ("Evaluaciones y oferta",sv(2,0,1,1,0),"exámenes, oferta laboral","var(--warn)","Oferta"),
   ("Inducción y contrato",sv(1,0,1,0,0),"inducción, firma, comunicación","var(--ok)","Inducción")]),
 tabs(["Postulantes","Etapas del proceso","Documentación","Correos del proceso","Vacantes"],"Postulantes",counts={"Postulantes":7},panels={
  "Postulantes": filters(search("Buscar","Nombre, título o vacante",w="240px"),sel("Etapa",["Todas","Filtración y preselección","Entrevistas","Verificación de referencias","Evaluaciones y exámenes","Oferta laboral y aceptación","Inducción","Descartado"],w="210px"),sel("Vacante",["Todas","Secretaría administrativa-académica","Asistente contable","Asesora comercial","Recepción","Coordinación académica","Asistente de administración"],w="230px"),actions='<span class="result-count" aria-live="polite"></span>'+btn("Nuevo postulante",None,True)+btn("Publicar vacante administrativa"))+postulantes_tbl+pager(7),
  "Etapas del proceso": card("De la vacante a la incorporación", flow(ETAPAS_RECLUTAMIENTO)+kv(("Gerencia General","aprueba vacantes y contrataciones; firma contratos"),("Administración / Talento Humano","ejecuta el proceso, gestiona documentación y coordina evaluaciones"),("Área solicitante","define el perfil, apoya entrevistas y facilita la inducción"),("Diferencia con profesores","los docentes van por el proceso de servicios profesionales en "+'<a href="ContratacionProfesores.html">Contratación de profesores</a>'))),
  "Documentación": card("Documentación habilitante · formulario de solicitud de empleo", docs_admin+kv(("Formulario","datos personales, formación, experiencia, referencias personales y laborales, documentación entregada"),("Protección de datos","la información se usa solo para el proceso y, si hay contratación, para la relación laboral; no se comparte con terceros"))),
  "Correos del proceso": card("Plantillas del proceso", correos_recl+kv(("Pre-screen telefónico","10 minutos: apertura, contexto, filtros excluyentes (formación, idioma, disponibilidad, expectativa salarial), experiencia, manejo de situaciones, motivación y cierre"))),
  "Vacantes": card("Vacantes abiertas", table(["Vacante","Sede","Publicada en","Postulantes","Presupuesto de publicación","Estado"],[
    [c2("Secretaría administrativa-académica","perfil según manual de funciones"),"Quito","LinkedIn · web","2","$40 · aprobado",badge("En entrevistas","navy")],
    [c2("Asistente contable","medio tiempo"),"Valle","Indeed","1","$0",badge("En evaluaciones","warn")],
    [c2("Asesora comercial","comisión por metas"),"Ambato","LinkedIn · Indeed","1","$40 · aprobado",badge("Oferta enviada","warn")],
    [c2("Recepción","jornada completa"),"Quito","web","1","$0",badge("Recibiendo CV","neutral")],
    [c2("Coordinación académica","reemplazo"),"Valle","LinkedIn","1","$40 · aprobado",badge("Cubierta · inicia 3 nov","ok")]],sede=1,hide=(1,),wide=0)+kv(("Anexo 1","texto de publicación: puesto, sede, funciones, requisitos, perfil, qué ofrecemos y aviso de protección de datos"))),
 }),
 subtitle="Proceso de contratación de nuevo personal (ISO 9001): vacante, publicación, pre-screen, entrevistas, documentos, referencias, exámenes, oferta, inducción y contrato"),"Reclutamiento de personal administrativo")

# 22 Facturas
V2='<a href="DetalleFactura.html">Ver</a>'
credito=table(["Vence","Factura","Estudiante","Plazo","Saldo","Estado","Acción"],[
  ["10 oct",c2("000021080","25 sep · Valle · Diego R."),'<a href="Ficha360.html">Pedro Mora</a>',"15 días","$500.00",badge("Vencida · 2 días","bad"),V2],
  ["18 oct",c2("000021074","18 sep · Quito · Carla M."),'<a href="Ficha360.html">Gabriela Núñez</a>',"30 días","$225.00",badge("Por vencer","warn"),V2],
  ["26 oct",c2("000021095","11 oct · Ambato · Sofía L."),'<a href="Ficha360.html">Mateo Salazar (menor)</a>',"15 días","$420.00",badge("Al día","ok"),V2],
  ["11 nov",c2("000021094","12 oct · Ambato · Sofía L."),'<a href="Ficha360.html">Camila Sánchez</a>',"30 días","$475.00",badge("Al día","ok"),V2]],wide=1)
def fsel(n): return f'<input type="checkbox" class="chk" aria-label="Seleccionar factura {n}">'
def fcode(n,f,sd,ase): return c2(f'<a href="DetalleFactura.html" data-row class="mono">{n}</a>',f"{f} · {sd} · {ase}")
def fmenu(): return rowmenu('<a href="DetalleFactura.html" class="btn" role="menuitem">Ver detalle</a>'+only(COMERCIAL,btn("Registrar pago"),True)+btn("Enviar comprobante")+btn("Descargar PDF")+btn("Descargar XML")+only("ADM,GER,DIR,SUC,SEC",btn("Emitir nota de crédito"),True),"Acciones de la factura")
P_POR_ESTUDIANTE=(
filters(sel("Estudiante",["Pedro Mora","Camila Sánchez","Gabriela Núñez","Mateo Salazar (menor)","María Andrade"],w="260px"),actions=btn("Descargar facturas pendientes",None,True)+btn("Enviar facturas pendientes al estudiante"))
   +table(["Factura","Estudiante","Vence","Total","Pagado","Saldo","Estado","Acción"],[
    [c2("000021080","25 sep · Valle · B1 módulos 7–8 · crédito 15 días"),"Pedro Mora","10 oct","$500.00","$0.00","$500.00",badge("Vencida","bad"),V2],
    [c2("000021012","02 sep · Valle · A2 · anulada con NC-000000311 (pasó a B1)"),"Pedro Mora","—","$250.00","$0.00","$0.00",badge("Anulada","neutral"),V2],
    [c2("000021094","12 oct · Ambato · A2–B1 · crédito 30 días"),"Camila Sánchez","11 nov","$950.00","$475.00","$475.00",badge("Parcial","warn"),V2],
    [c2("000021074","18 sep · Quito · A2 · crédito 30 días"),"Gabriela Núñez","18 oct","$450.00","$225.00","$225.00",badge("Parcial","warn"),V2],
    [c2("000021095","11 oct · Ambato · A1 · crédito 15 días"),"Mateo Salazar (menor)","26 oct","$420.00","$0.00","$420.00",badge("Pendiente","warn"),V2]],wide=0)
   +kv(("Facturas con saldo","2"),("Total adeudado","$750.00"),("Correo del estudiante","p.mora@ejemplo.com"),("Último envío","Nunca")))
P_SIN_VINCULAR=(
table(["Factura","Cliente","Total","Motivo","Acción"],[["000021097","Consumidor final","$45.00","Venta de libro sin matrícula",btn("Vincular a matrícula")],["000021088",c2("Grupo Nova","RUC 1790012345001"),"$1,200.00","Factura B2B sin estudiantes asignados",btn("Vincular a matrícula")],["000021071","Andrés Pazmiño","$195.00","Matrícula anulada y vuelta a crear",btn("Vincular a matrícula")]])
   +kv(("Por qué importa","una factura sin matrícula no descuenta saldo ni paga comisión")))
P_PV=(
flow(["Asesor registra el pago y sube el comprobante","Contabilidad valida en el banco","Secretaría confirma en el sistema"])
   +table(["Pago","Estudiante · venta","Monto","Comprobante","Estado","Acción"],[
    [c2('<span class="mono">PG-1093</span>',"19 oct · Carla M. · Quito"),c2('<a href="DetalleVenta.html">María Andrade</a>',"V-2026-0412"),c2("$600.00","Transferencia"),'<a href="#">transferencia_884512.pdf</a>',badge("Por validar","warn"),only("CON,ADM",btn("Validar pago")+btn("Observar pago"),True)],
    [c2('<span class="mono">PG-1091</span>',"18 oct · Diego R. · Valle"),c2('<a href="Ficha360.html">Pedro Mora</a>',"V-2026-0409"),c2("$250.00","Depósito"),'<a href="#">deposito_55120.jpg</a>',badge("Validado por Contabilidad","navy"),only("SEC,ADM",btn("Confirmar en sistema"),True)],
    [c2('<span class="mono">PG-1088</span>',"17 oct · Ana P. · Cuenca"),c2('<a href="Ficha360.html">Martín Ortega</a>',"V-2026-0405"),c2("$400.00","Transferencia"),'<a href="#">transf_77812.pdf</a>',badge("Observado · monto no coincide","bad"),btn("Ver venta","DetalleVenta.html")],
    [c2('<span class="mono">PG-1085</span>',"17 oct · Sofía L. · Ambato"),c2('<a href="Ficha360.html">Camila Sánchez</a>',"V-2026-0401"),c2("$230.00","Efectivo"),c2("Recibo 0429","entregado a Secretaría"),badge("Confirmado","ok"),btn("Ver venta","DetalleVenta.html")]],wide=1)
   +kv(("Efectivo","se entrega a Secretaría y se confirma con el recibo"),("Depósitos y transferencias","quedan 'Por validar' hasta que Contabilidad los revise")))
P_CONT=(
kv(("Quién","Secretaría matricula en el siguiente módulo y aplica el saldo a favor de la venta"),("Regla","aplicar saldo no es una venta nueva ni un cobro nuevo"))
   +table(["Estudiante","Siguiente módulo","Venta original","Saldo a favor","Estado","Acción"],[
    [c2('<a href="Ficha360.html">María Andrade</a>',"asesor original: Carla M."),c2("Módulo 8 · B1","0001-2026-0767 · inicia 3 nov"),"V-2026-0412","$400.00",badge("Lista para aplicar","warn"),'<a href="MatriculaContinuidad.html">Matricular</a>'],
    [c2('<a href="Ficha360.html">Pedro Mora</a>',"asesor original: Diego R."),c2("Módulo 8 · B1","0001-2026-0767 · inicia 3 nov"),"V-2026-0409","$0.00",badge("Sin saldo · nueva venta","neutral"),'<a href="NuevaVenta.html">Vender</a>'],
    [c2('<a href="Ficha360.html">Camila Sánchez</a>',"asesor original: Sofía L."),c2("Módulo 6 · A2","Teens · inicia 10 nov"),"V-2026-0401","$230.00",badge("Lista para aplicar","warn"),'<a href="MatriculaContinuidad.html">Matricular</a>']],wide=0))
P_CART=(
filters(search("Buscar","Estudiante o matrícula",w="220px"),sel("Estado",["Todas","Vencida","Por vencer"],w="150px"))
   +table(["Estudiante","Cuota","Vence","Pendiente","Días vencidos","Estado","Acción"],[
    [c2('<a href="Ficha360.html">Pedro Mora</a>',"001-202602846/847 · B1 módulos 7–8 · llamado 12 oct, promete pagar el 20 · Diego R."),"1 de 1","10 oct","$500.00","9",badge("Vencida","bad"),'<a href="RegistrarPago.html">Cobrar</a>'],
    [c2('<a href="Ficha360.html">Gabriela Núñez</a>',"001-202602863 · 099 000 0004 · Carla M."),"2 de 2","18 oct","$225.00","1",badge("Vencida","bad"),'<a href="RegistrarPago.html">Cobrar</a>'],
    [c2('<a href="Ficha360.html">Camila Sánchez</a>',"000021094 · 099 000 0008 · Sofía L."),"2 de 2","11 nov","$475.00","—",badge("Por vencer","warn"),'<a href="RegistrarPago.html">Cobrar</a>'],
    [c2('<a href="Ficha360.html">Martín Ortega</a>',"000021098 · 099 000 0009 · Carla M."),"2 de 3","25 oct","$160.00","—",badge("Por vencer","warn"),'<a href="RegistrarPago.html">Cobrar</a>']],wide=0)
   +kv(("Cartera vencida","$725 · 2 cuotas"),("Por vencer en 30 días","$635"),("Seguimiento","cada llamada o mensaje queda anotado en la cuota"))+row(btn("Enviar estado de cuenta"),btn("Exportar")))
P_CAJA=(
filters(sel("Caja",["Quito","Valle","Ambato"],w="140px",col=False),dates("Día","2026-10-19","2026-10-19"))
   +two(card("Cobros por método", table(["Método","Pagos","Monto"],[["Efectivo","6","$640.00"],["Tarjeta de crédito","3","$870.00"],["Transferencia","5","$1,420.00"],["Depósito","1","$230.00"],["Total del día","15","$3,160.00"]])),
        card("Recibos del día", table(["Recibo","Estudiante","Monto","Acción"],[["0431","Martín Ortega","$230.00",btn("Imprimir recibo")],["0430","Camila Sánchez","$475.00",btn("Imprimir recibo")],["0429","Sofía Herrera","$250.00",btn("Imprimir recibo")]])))
   +row(btn("Cerrar caja",None,True),btn("Exportar")))
P_REMAT=(
table(["Estudiante","Siguiente curso","Solicitada","Monto","Pago","Acción"],[[c2('<a href="Ficha360.html">Sofía Herrera</a>',"desde el portal · 12 oct"),c2("ESL · Virtual · Grupal · B1 módulo 7","inicia 3 nov"),"12 oct","$250.00",badge("Transferencia reportada","warn"),row(btn("Confirmar pago",None,True),btn("Ver ficha","Ficha360.html"),gap=8)],[c2('<a href="Ficha360.html">Daniela Ríos</a>',"desde el portal · 11 oct · terminó B1+"),c2("ESL · Presencial · Grupal · B2 módulo 11","inicia 9 ene"),"11 oct","$275.00",badge("Sin pago aún","bad"),row(btn("Enviar recordatorio"),btn("Ver ficha","Ficha360.html"),gap=8)],[c2('<a href="Ficha360.html">Martín Ortega</a>',"desde el portal · 10 oct"),c2("Teens · Virtual · Grupal · A2 módulo 3","inicia 3 nov"),"10 oct","$230.00",badge("Pagado en caja","ok"),row(btn("Confirmar pago",None,True),gap=8)]],wide=0)+kv(("Cómo funciona","el estudiante se rematricula desde el portal cuando el Muro marca avance total y nota ≥ 7; queda 'Pendiente de pago' y Secretaría solo confirma el pago")))
P_NOTAS=(
table(["Nota","Factura origen","Estudiante","Motivo","Monto","Fecha","Estado"],[[c2("NC-000000312","Emitida por Secretaría Quito"),"000021040",c2('<a href="Ficha360.html">Luis Torres</a>',"001-202602601"),"Libro devuelto · vuelve al stock","$40.00","08 oct",badge("Autorizada","ok")],[c2("NC-000000311","Emitida por Dir. Comercial"),"000021012",c2('<a href="Ficha360.html">Pedro Mora</a>',"001-202602846"),"Cambio de curso","$250.00","30 sep",badge("Autorizada","ok")],[c2("NC-000000310","Emitida por Secretaría Ambato"),"000021061",c2('<a href="Ficha360.html">Diego Vargas (menor)</a>',"001-202602790"),"Anulación total","$380.00","06 sep",badge("Autorizada","ok")]],wide=0)+row(btn("Nueva nota de crédito")))
page("Facturas.html","Facturas",shell("Facturación","Facturación",
 kpis([("Facturado hoy",sv("$3,580","$1,500","$1,160","$920","$480"),sv("8 facturas","3 facturas","2 facturas","3 facturas","1 factura")),("Cobrado del mes",sv("$31,200","$16,900","$9,100","$5,200","$3,100"),"71% de lo facturado",{"href":"#go-seg-caja-del-dia"}),("Por cobrar",sv("$1,620","$225","$500","$895","$320"),sv("5 facturas · 1 vencida","1 factura","1 vencida","2 facturas","1 factura"),{"href":"#go-seg-cartera"}),("Sin autorizar SRI",sv("2","1","0","1","0"),"1 rechazada · 1 sin enviar",{"fset":"Vista=Sin autorizar SRI"})]),
 tabs(["Facturas","Cobros","Ajustes"],"Facturas",roles={},counts={"Cobros":2,"Ajustes":3},panels={
  "Facturas": seg(["Lista de facturas","Por estudiante","Sin vincular"],[
   '<div class="quick" data-fgroup role="group" aria-label="Vistas rápidas">'+"".join(f'<button type="button" class="q" data-fset="Vista={v}" aria-pressed="false">{v}</button>' for v in ["Por cobrar","Vencidas","Sin autorizar SRI","Anuladas"])+'</div>'
   +filters('<div hidden>'+sel("Vista",["Todas","Por cobrar","Vencidas","Sin autorizar SRI","Anuladas"],col="Vista")+'</div>',search("Buscar","Nº de factura, estudiante o matrícula",w="280px"),sel("Estado",["Todos","Pagada","Parcial","Pendiente","Vencida","Anulada"],w="150px",col="Cobro"),sel("SRI",["Todos","Autorizada","Sin autorizar","Rechazada"],w="150px"),sel("Asesor",["Todos","Carla M.","Diego R.","Sofía L."],w="150px",col="Factura"),sel("Crédito",["Todos","Sí","No"],w="120px"),dates(),actions='<span class="result-count" aria-live="polite"></span>',show=4)
   +'<div class="bulk"><span>Marca facturas para enviarlas juntas</span>'+btn("Enviar comprobantes seleccionados",kind="ghost")+'</div>'
   +table(["","Factura","Sede","Estudiante","Total","Crédito","SRI","Cobro","Vista",""],[
  [fsel(n),fcode(n,f,sd,ase),sd,est,tot,cr,sri,cob,vis,fmenu()] for n,f,sd,ase,est,tot,cr,sri,cob,vis in [
   ("000021090","28 ago","Quito","Carla M.",c2('<a href="Ficha360.html">María Andrade</a>',"001-202602794 a 797 · módulos 7–10"),"$980.00","Sí · 2 cuotas",badge("Autorizada","ok"),badge("Pagada","ok"),"Todas"),
   ("000021091","12 oct","Valle","Diego R.",c2('<a href="Ficha360.html">Juan Pérez</a>',"001-202603216 · A2"),"$280.00","No",badge("Autorizada","ok"),badge("Pagada","ok"),"Todas"),
   ("000021092","12 oct","Quito","Carla M.",c2('<a href="Ficha360.html">Luis Torres</a>',"Libros · sin matrícula"),"$68.00","No",badge("Sin autorizar · sin enviar","warn"),badge("Pagada","ok"),"Sin autorizar SRI"),
   ("000021093","12 oct","Quito","Carla M.",c2('<a href="Ficha360.html">Ana Ruiz (menor)</a>',"001-202603215 · Kids 2"),"$387.50","No",badge("Autorizada","ok"),badge("Pagada","ok"),"Todas"),
   ("000021094","12 oct","Ambato","Sofía L.",c2('<a href="Ficha360.html">Camila Sánchez</a>',"001-202603217 · A2–B1"),"$950.00","Sí · 30 días",badge("Autorizada","ok"),badge("Parcial · $475 por cobrar","warn"),"Por cobrar"),
   ("000021095","11 oct","Ambato","Sofía L.",c2('<a href="Ficha360.html">Mateo Salazar (menor)</a>',"001-202603220 · A1"),"$420.00","Sí · 15 días",badge("Sin autorizar · rechazada","bad"),badge("Pendiente","warn"),"Por cobrar · Sin autorizar SRI"),
   ("000021096","11 oct","Quito","Carla M.",c2('<a href="Ficha360.html">Valeria Cedeño</a>',"001-202603221 · B2"),"$495.00","No",badge("Autorizada","ok"),badge("Pagada","ok"),"Todas"),
   ("000021099","15 oct","Cuenca","Ana P.",c2('<a href="Ficha360.html">Martín Ortega</a>',"001-202603229 · A2"),"$480.00","Sí · 3 cuotas",badge("Autorizada","ok"),badge("Parcial · $320 por cobrar","warn"),"Por cobrar"),
   ("000021080","25 sep","Valle","Diego R.",c2('<a href="Ficha360.html">Pedro Mora</a>',"001-202602846 · B1"),"$500.00","Sí · 15 días",badge("Autorizada","ok"),badge("Vencida · 9 días","bad"),"Por cobrar · Vencidas"),
   ("000021074","18 sep","Quito","Carla M.",c2('<a href="Ficha360.html">Gabriela Núñez</a>',"001-202602863 · A2"),"$450.00","Sí · 30 días",badge("Autorizada","ok"),badge("Parcial · $225 por cobrar","warn"),"Por cobrar"),
   ("000021061","05 sep","Ambato","Sofía L.",c2('<a href="Ficha360.html">Diego Vargas (menor)</a>',"001-202602790 · Kids 1"),"$380.00","No",badge("Anulada","neutral"),badge("Anulada","neutral"),"Anuladas")]],sede=2,hide=(2,8),wide=3)+pager(sv(76,40,22,14,10)),
   P_POR_ESTUDIANTE, P_SIN_VINCULAR],label="Vistas de facturas"),


  "Cobros": seg(["Pagos por validar","Caja del día","Cartera","Calendario de crédito"],[P_PV,P_CAJA,P_CART,credito],label="Vistas de cobros",counts={"Pagos por validar":2}),
  "Ajustes": seg(["Notas de crédito","Continuidades","Rematrículas por confirmar"],[P_NOTAS,P_CONT,P_REMAT],label="Vistas de ajustes",counts={"Rematrículas por confirmar":3}),
 }),
 ai([("2 facturas de hoy aún no están autorizadas por el SRI: la 000021095 fue rechazada (cédula del cliente inválida) y la 000021092 no se ha enviado.","Ver sin autorizar","Facturas.html"),("La factura 000021080 de Pedro Mora venció hace 2 días con $500 de saldo; su asesor es Diego R.","Ver calendario de crédito","Facturas.html"),("Hoy el 100% de las facturas fueron por transferencia; ninguna en efectivo.","Ver reportes","Reportes.html")],"¿Qué facturas de crédito vencen esta semana?"),
 subtitle="Una factura por venta, con pago, autorización SRI y envío del comprobante",
 actions=only(COMERCIAL,btn("Nueva factura","NuevaVenta.html",True),True)+more_menu(btn("Enviar comprobantes pendientes")+btn("Descargar XML del día")+btn("Exportar"))),"Facturas")

# 23 Detalle factura
page("DetalleFactura.html","Detalle factura",shell("Factura 000021090","Facturación",
 hero([("Fecha","28 ago 2026"),("Estudiante",'<a href="Ficha360.html">María Andrade</a>'),("Matrículas",'<a href="DetalleMatricula.html">001-202602794 a 797</a>'),("Venta","Multi-módulo · B1 y B1+ (módulos 7 a 10)"),("Crédito","Sí · 2 cuotas cada 30 días"),("Sede · asesor","Quito · Carla M."),("Pagada el","27 sep 2026"),("Comprobante","Enviado 28 ago 10:14")],
  only(COMERCIAL,btn("Registrar pago",None,True),True)+btn("Enviar comprobante")+btn("Descargar PDF")+btn("Descargar XML")+only("ADM,GER,DIR,SUC,SEC",btn("Emitir nota de crédito"),True)+only("ADM,GER,DIR",btn("Anular factura"),True),
  tag='<span class="hero-code">000021090</span>'+badge("Pagada","ok")+badge("SRI · Autorizada","navy")),
 two(card("Datos de facturación (cliente)", kv(("Cliente","María Andrade"),("CED / RUC / PAS","CED · 1712345678"),("Dirección","Quito · La Carolina · Av. Amazonas y NN. UU."),("Teléfono","099 000 0001"),("E-mail","maria.andrade@ejemplo.com"),("RUC especial",badge("No","neutral")),("Empresa / convenio","—"))+row(btn("Editar datos del cliente",None,False,"Se editan en esta misma pantalla los datos de facturación (nombre, CED/RUC/PAS, dirección, teléfono y email). Como la factura ya está autorizada por el SRI, el cambio se guarda en la ficha y aplica a las próximas facturas; para corregir esta se emite una nota de crédito y se refactura. "+AUDIT))),
     card("Autorización SRI", kv(("Estado",badge("Autorizada","ok")),("Fecha de autorización","28 ago 2026 · 10:12"),("Clave de acceso","2808202601179234567800110010010000210901234567813"),("Ambiente","Producción"),("Comprobante enviado","Sí · 28 ago 10:14 · maria.andrade@ejemplo.com"))+row(btn("Reintentar autorización"),btn("Enviar comprobante")))),
 card("Ítems", table(["Tipo","Código","Ítem","Cant.","Precio","% dcto.","Descuento","Subtotal","IVA"],[
   ["Servicio","00139",c2("Servicios educativos · Nivel B1","Módulos 7–8 · English for Adults"),"1","$500.00","10%","-$50.00","$450.00","$0.00"],
   ["Servicio","00139",c2("Servicios educativos · Nivel B1+","Módulos 9–10 · English for Adults"),"1","$500.00","10%","-$50.00","$450.00","$0.00"],
   ["Producto","1141",c2("Empower B1 Combo A","ISBN 9781108961516 · descontado del stock Quito"),"1","$40.00","0%","$0.00","$40.00","$0.00"],
   ["Producto","1292",c2("Empower B1+ Combo B","ISBN 9781108961523 · reservado en Quito para el módulo 9"),"1","$40.00","0%","$0.00","$40.00","$0.00"]],wide=2,hide=(1,))
   +kv(("Subtotal","$1,080.00"),("Descuento","-$100.00 (10% referido · dentro del límite del asesor)"),("IVA","$0.00 (servicios educativos 0%)"),("Total","$980.00"))),
 two(card("Pagos", table(["Pago","Monto"],[[c2("Cuota 1 · transferencia · 28 ago 2026","Banco Pichincha · ref. 884512"),"$490.00"],[c2("Cuota 2 · tarjeta de crédito · 27 sep 2026","Caja Quito · recibo 0421 · voucher 55120"),"$490.00"]])+kv(("Total pagado","$980.00"),("Saldo","$0.00"))+only(COMERCIAL,row(btn("Registrar pago",None,True)))),
     card("Efecto en la matrícula", kv(("Saldo antes de la factura","$980.00"),("Saldo después","$0.00"),("Módulos habilitados","7 a 10 · 4 matrículas"),("Comisión","Carla M. · 4% virtual · $39.20 · cierre de septiembre"))+table(["Movimiento","Monto"],[[c2("Factura emitida y autorizada","28 ago 2026"),"$980.00"],[c2("Pagos · cuota 1 y cuota 2","28 ago y 27 sep 2026"),"$980.00"],[c2("Nota de crédito","Ninguna emitida"),"—"]]))),
 card("Historial", table(["Fecha","Usuario","Evento"],[["27 sep 17:20","Secretaría","Pago de la cuota 2 · $490 · tarjeta de crédito"],["28 ago 10:14","Sistema","Comprobante PDF + XML enviado a maria.andrade@ejemplo.com"],["28 ago 10:12","Sistema","Autorizada por el SRI"],["28 ago 10:11","Carla M.","Factura emitida desde Nueva matrícula (venta multi-módulo, 4 matrículas)"]])),
 subtitle="Equivale al registro Invoice de TeamDesk: términos, cliente, montos, pagos, ítems y transacción de la matrícula"),"Detalle de factura")

# 24 Solicitud de descuento
page("SolicitudDescuento.html","Solicitud de descuento",shell("Solicitud de descuento","Nueva matrícula",
 f'<div class="card" style="max-width:640px">'+kv(("Venta","Gabriela Núñez · A2 · módulos 5–6"),("Precio lista","$450"),("Asesor","Carla M."))+form([("Descuento solicitado (%)","42","number",None,True),("Monto resultante","$261.00 · -$189.00","text",None,False,"Automático")])+form([("Motivo","Referido","select",["Referido","Promoción vigente","Convenio empresa","Hermano matriculado","Beneficio cancela 2 módulos","Otro"],True,"Lista cerrada")],1)+form([("Justificación","","textarea",None,True,"Por qué este caso necesita más de 10%")],1)+note("Más de 10% requiere aprobación del Director Comercial. El asesor ve el estado de su solicitud en Notificaciones.","warn")+row(btn("Cancelar","NuevaVenta.html"),btn("Enviar solicitud",None,True))+'</div>',
 subtitle="Reemplaza el campo 'Reason' opcional de TeamDesk"),"Solicitud de descuento")

# 25 Detalle comisión por asesor
def calc_rows(rows):
    """Cálculo paso a paso: [(paso, detalle, monto)]; el último es el total."""
    body="".join(f'<div class="calc-row{" total" if i==len(rows)-1 else ""}"><span class="calc-n">{i+1 if i<len(rows)-1 else "="}</span><div class="calc-txt"><b>{p}</b><small>{d}</small></div><span class="calc-amt">{m}</span></div>' for i,(p,d,m) in enumerate(rows))
    return f'<div class="calc">{body}</div>'
mi_comision=card("Así se calcula tu comisión de octubre",
  calc_rows([("Vendiste 14 niveles","6 virtuales ($5,420) y 8 presenciales ($3,980). Con 11 o más niveles entras al rango más alto: 4% virtual y 5% presencial.","Rango 11+"),
             ("Comisión por ventas virtuales","$5,420 × 4%","$216.80"),
             ("Comisión por ventas presenciales","$3,980 × 5%","$199.00"),
             ("Bono por cumplir la meta","Tu meta era 12 niveles y vendiste 14 (117%).","+$50.00"),
             ("Retenido hasta que el estudiante pague","Tomás Guerrero (A2 presencial, $450) aún no paga: $22.50 se liberan cuando cobre.","-$22.50"),
             ("Tu comisión de octubre","Se paga el 5 de noviembre con el cierre del mes. Lo retenido se suma al mes en que se cobre.","$443.30")]),
  extra=badge("Meta cumplida · 117%","ok"))
meta_card=card("Tu meta del mes", progress(100,"14 de 12 niveles · meta cumplida",CH[0])
  +kv(("Faltan para el siguiente rango","Ya estás en el rango más alto"),("Si vendes 1 nivel presencial más ($500)","+$25 de comisión"),("Si vendes 1 nivel virtual más ($450)","+$18 de comisión"))
  +hbars([("Rango 1–5 niveles · 2% / 3%",5),("Rango 6–10 niveles · 3% / 4%",10),("Rango 11+ niveles · 4% / 5% · estás aquí",14)],unit=""))
ventas_asesor=table(["Fecha","Venta","Modalidad","Monto","Cobrado","Regla","Comisión","Estado"],[
  ["12 oct",c2('<a href="Ficha360.html">Sofía Herrera</a>',"001-202603218 · B1 módulo 7 · rematrícula"),"Virtual","$250","100%","4%","$10.00",badge("Por pagar","warn")],
  ["11 oct",c2('<a href="DetalleMatricula.html">Valeria Cedeño</a>',"001-202603221 · B2 · 1 nivel"),"Virtual","$495","100%","4%","$19.80",badge("Por pagar","warn")],
  ["09 oct",c2('<a href="DetalleMatricula.html">Ana Ruiz (menor)</a>',"001-202603215 · Kids 2 · 2 niveles"),"Presencial","$760","50%","5%","$38.00",badge("Por pagar","warn")],
  ["05 oct",c2('<a href="DetalleMatricula.html">Tomás Guerrero</a>',"001-202603219 · A2 módulos 5–6 · 1 nivel"),"Presencial","$450","0%","5%","$22.50",badge("Retenida · sin cobro","bad")],
  ["03 oct",c2('<a href="DetalleMatricula.html">Gabriela Núñez</a>',"001-202602863 · A2 · 1 nivel"),"Virtual","$261","100%","4%","$10.44",badge("Por pagar","warn")],
  ["10 oct",c2('<a href="DetalleMatricula.html">Martín Ortega</a>',"001-202603223 · Teens A2 módulo 3 · rematrícula"),"Virtual","$230","100%","4%","$9.20",badge("Por pagar","warn")]],wide=1)
page("DetalleComision.html","Detalle comisión",shell("Mi comisión · Octubre 2026","Comisiones",
 hero([("Asesor","Carla M. · Quito"),("Período","1 – 31 oct 2026 · cierra en 19 días"),("Niveles vendidos","14 (6 virtual · 8 presencial)"),("Meta","12 niveles"),("Comisión estimada","$443.30"),("Se paga","5 nov 2026")],
   btn("Exportar detalle")+btn("Ver reglas de comisión","ReglasComision.html"),
   tag='<span class="hero-code">Carla M.</span>'+badge("Meta cumplida","ok")+badge("En revisión · Dir. Comercial","warn")),
 two(mi_comision, meta_card, ratio="1.3fr 1fr"),
 card("Tus ventas del mes", ventas_asesor+kv(("Total ventas","$3,446 cobradas de $3,896"),("Comisión por pagar","$420.80"),("Retenida","$22.50"),("Bono","$50.00"))),
 two(card("Tu historial", vbars([("Jul",[350]),("Ago",[280]),("Sep",[300]),("Oct",[443])],["Comisión"],h=140)), card("Preguntas frecuentes", li(["¿Por qué una comisión aparece retenida? Porque el estudiante todavía no paga; se libera cuando cobre.","¿Cuándo se paga? El 5 de cada mes, después de que Dirección Comercial revisa y aprueba el período.","¿Qué pasa si un estudiante anula? Si se devuelve el dinero, la comisión de esa venta se descuenta del mes siguiente.","¿Los descuentos afectan mi comisión? Sí: la comisión se calcula sobre el valor facturado, después del descuento."]))),
 subtitle="Cada paso del cálculo con tus números; sin fórmulas ocultas"),"Mi comisión")

# 26 Reglas de comisión
page("ReglasComision.html","Reglas de comisión",shell("Reglas de comisión","Comisiones",
 table(["Regla","Condición","Virtual","Presencial","Vigencia","Estado"],[["Rango 1","1–5 niveles / mes","2%","3%","2026","Activa"],["Rango 2","6–10 niveles / mes","3%","4%","2026","Activa"],["Rango 3","11+ niveles / mes","4%","5%","2026","Activa"],["Bono meta","Cumple meta mensual","$50","$50","2026","Activa"]]),
 two(card("Nueva regla", form(["Nombre","Condición (niveles / modalidad / meta)","% o monto","Vigencia"])+row(btn("Guardar regla",None,True))), card("Simulador", filters(sel("Período de prueba",["Septiembre 2026","Agosto 2026"],w="170px"),actions=btn("Simular",None,False,"Se recalculan las comisiones del período elegido con las reglas actuales, sin guardar nada."))+table(["Asesor","Comisión real","Con reglas nuevas","Diferencia"],[["Carla M.","$300","$330","+$30"],["Diego R.","$150","$150","$0"],["Sofía L.","$280","$310","+$30"]])+note("Probar reglas contra las ventas de un mes cerrado antes de activarlas."))),
 subtitle="Configurable sin código; cada cambio queda en el audit log"),"Reglas de comisión")

# 27 Inventario
page("Inventario.html","Inventario",shell("Inventario de libros","Inventario",
 filters(search("Buscar","Título o nivel",w="240px"),sel("Programa",["Todos","Adults","Teens","Kids"],w="130px"),sel("Estado",["Todos","Negativo","Bajo mínimo","OK"],w="150px"),actions=btn("Nuevo pedido a proveedor","NuevoPedido.html",True)+btn("Registrar ingreso de proveedor")),
 kpis([("Ítems con stock negativo",sv(3,0,1,2),"requieren pedido"),("Pedidos en camino",sv(2,1,1,0),"#P-041 llega 8 oct"),("Valor en stock",sv("$6,840","$3,900","$1,760","$1,180"),"a costo del último ingreso"),("Códigos de activación pendientes",sv(13,4,9,0),"comprados, sin asignar")]),
 table(["Producto","Programa","Nivel","Stock por sede","Comprometido","Códigos pendientes","Estado","Acción"],[
  [c2("Empower B1+ Intermediate Combo B (digital pack)","Cód. 1141 · ISBN 9781108961523 · Adults B1+"),"Adults","B1+",c2("4 / -2 / 1","Quito / Valle / Ambato"),"5","1",badge("Negativo","bad"),'<a href="NuevoPedido.html">Pedir 6</a>'],
  [c2("Super Minds 2Ed Level 3 WB with Digital Pack","Cód. 1293 · ISBN 9781108909303 · Kids Kids 2"),"Kids","Kids 2",c2("0 / 3 / -1","Quito / Valle / Ambato"),"4","0",badge("Negativo","bad"),'<a href="NuevoPedido.html">Pedir 4</a>'],
  [c2("Prepare 3 SB with eBook 2E","Cód. 1115 · ISBN 9781009029780 · Teens A2"),"Teens","A2",c2("8 / 2 / 5","Quito / Valle / Ambato"),"3","0",badge("OK","ok"),'—'],
  [c2("Empower A1 Starter SB with digital pack","Cód. 1132 · ISBN 9781108961691 · Adults A1"),"Adults","A1",c2("2 / 1 / 0","Quito / Valle / Ambato"),"6","2",badge("Bajo mínimo","warn"),'<a href="NuevoPedido.html">Pedir 5</a>'],
  [c2("Four Corners 2ED L4 ESB with DP","Cód. 1271 · ISBN 9781009293891 · Adults B2"),"Adults","B2",c2("6 / 4 / 2","Quito / Valle / Ambato"),"2","0",badge("OK","ok"),'—'],
  [c2("Super Minds 2Ed Level 3 SB with eBook","Cód. 1292 · ISBN 9781108812276 · Kids Kids 2"),"Kids","Kids 2",c2("3 / 0 / -2","Quito / Valle / Ambato"),"4","0",badge("Negativo","bad"),'<a href="NuevoPedido.html">Pedir 6</a>'],
  [c2("Prepare 3 WB with Digital Pack 2E","Cód. 1116 · ISBN 9781009030502 · Teens A2"),"Teens","A2",c2("1 / 1 / 1","Quito / Valle / Ambato"),"6","10",badge("Bajo mínimo","warn"),'<a href="NuevoPedido.html">Pedir 4</a>'],
  [c2("Libreta Superpower","Cód. 1999 · ISBN — · — —"),"—","—",c2("25 / 10 / 8","Quito / Valle / Ambato"),"0","—",badge("OK","ok"),'—']],hide=(1,2),wide=0),
 two(card("Correo diario de stock negativo", kv(("Se envía","todos los días a las 07:00"),("Destinatarios","Secretaría de cada sede, Administración de sucursal y Gerencia"),("Incluye","ítems con stock negativo y bajo mínimo por sede, pedidos en camino y códigos digitales sin asignar"),("Último envío",sv("Hoy 07:00 · 3 negativos · 4 bajo mínimo","Hoy 07:00 · 0 negativos · 2 bajo mínimo","Hoy 07:00 · 1 negativo · 1 bajo mínimo","Hoy 07:00 · 2 negativos · 1 bajo mínimo")),("Si no hay novedades","no se envía nada"))+row(btn("Enviar resumen ahora",None,True),btn("Editar destinatarios y hora")),extra=badge("Activo","ok")),
     card("Últimos envíos", table(["Fecha","Negativos","Bajo mínimo","Enviado a","Estado"],[["Hoy 07:00","3","4","5 personas",badge("Enviado","ok")],["Ayer 07:00","2","4","5 personas",badge("Enviado","ok")],["10 oct 07:00","0","3","5 personas",badge("Enviado","ok")],["09 oct","0","0","—",badge("Sin novedades","neutral")]]))),
 card("Activos fijos por sede", filters(sel("Categoría",["Todas","Equipos de cómputo","Mobiliario","Audio y video","Climatización"],w="180px"),sel("Estado",["Todos","En uso","En traspaso","Dado de baja"],w="150px"),actions=btn("Nueva solicitud de activo",None,True)+btn("Registrar traspaso"))
   +table(["Código","Activo","Sede","Categoría","Custodio","Valor","Estado"],[
    [c2('<span class="mono">EQ.01.ACCO.000014</span>',"12 mar 2026 · acta A.E.R. 00031"),c2("Laptop 14'' · 16 GB","Quito · Coord. Académica"),"Quito","Equipos de cómputo","Coord. Académica Quito","$980.00",badge("En uso","ok")],
    [c2('<span class="mono">MB.02.ACCO.000112</span>',"5 ene 2025"),c2("Mesa de trabajo 6 puestos","Valle · aula C-3 · Administración"),"Valle","Mobiliario","Administración Valle","$320.00",badge("En uso","ok")],
    [c2('<span class="mono">AV.03.ACCO.000027</span>',"20 jun 2026 · acta C.T.I. 00007"),c2("Proyector 3500 lm","Ambato · aula A-1 · Coord. Académica"),"Ambato","Audio y video","Coord. Académica Ambato","$640.00",badge("En traspaso · desde Quito","warn")],
    [c2('<span class="mono">EQ.01.ACCO.000009</span>',"2 feb 2023"),c2("Tablet reloj de asistencia","Quito · recepción · CAMB-CLOCK"),"Quito","Equipos de cómputo","Recepción Quito","$210.00",badge("En uso","ok")],
    [c2('<span class="mono">CL.04.ACCO.000003</span>',"9 sep 2021 · vida útil cumplida"),c2("Aire acondicionado 18000 BTU","Quito · aula Q-4 · Administración"),"Quito","Climatización","Administración Quito","$0.00",badge("Dado de baja","neutral")]],sede=2,hide=(2,3,4),wide=1)
   +flow(["Solicitud de activo","Aprobación de Gerencia","2 o 3 cotizaciones · cuadro comparativo","Orden de compra","Acta de entrega y recepción","Factura y registro contable","Inventario · código, ubicación, custodio","Etiqueta y asignación"],horizontal=False)
   +kv(("Traspaso entre sedes","acta de traspaso interno con fecha de salida, fecha de ingreso, nueva ubicación y custodio"),("Baja","al cumplir la vida útil o por daño, con informe y aprobación de Gerencia")),
   extra=badge("Propuesta · fuera del alcance del contrato actual")),
 card("Mercadería", filters(sel("Período",["Este mes","Mes anterior","Este año"],w="140px",col=False),actions=btn("Nueva venta de mercadería","VentaMercaderia.html",True))+table(["Producto","Sede","Existencias","Vendidas en el mes","Importe vendido"],[["Tomatodo Cambridge","Quito","18","11","$132"],["Tomatodo Cambridge","Valle","6","7","$84"],["Camiseta Summer Camp","Quito","4","9","$135"],["Cuaderno Cambridge","Cuenca","0","5","$22.50"]],sede=1)),
 subtitle="Stock por sede con alertas; el resumen de stock negativo llega por correo cada mañana"),"Inventario de libros")

# 28 Movimientos
page("Movimientos.html","Movimientos",shell("Movimientos y pedidos","Movimientos y pedidos",
 tabs(["Ingresos de proveedor","Movimientos","Pedidos a proveedor","Códigos de activación","Notas de crédito"],"Ingresos de proveedor",{
  "Ingresos de proveedor": filters(search("Buscar","Nº de factura del proveedor",w="220px"),sel("Proveedor",["Todos","Books & Bits","Otro"],w="150px"),sel("Estado",["Todos","Recibido","Con pendientes"],w="150px"),dates(),actions=btn("Registrar ingreso de proveedor",None,True))+table(["Ingreso","Proveedor","Sede","Ítems y total","Pendientes","Estado"],[
     [c2("IM202610-02","04 oct · factura 000815787 · Books & Bits · Valle"),"Books & Bits","Valle",c2("4 ítems · $145.30","Comprobante: comprobante_2026-10-04.pdf"),c2("0 libros · 0 códigos","pendientes de entrega"),badge("Recibido","ok")],
     [c2("IM202610-01","01 oct · factura 000814675 · Books & Bits · Valle"),"Books & Bits","Valle",c2("14 ítems · $456.71","Comprobante: comprobante_2026-10-01.pdf"),c2("0 libros · 0 códigos","pendientes de entrega"),badge("Recibido","ok")],
     [c2("IM202609-12","30 sep · factura 000813312 · Books & Bits · Quito"),"Books & Bits","Quito",c2("22 ítems · $772.29","Comprobante: comprobante_2026-09-30.pdf"),c2("0 libros · 0 códigos","pendientes de entrega"),badge("Recibido","ok")],
     [c2("IM202609-11","30 sep · factura Anulación 002-002-000020971 · Books & Bits · Quito"),"Books & Bits","Quito",c2("1 ítems · $85.00","sin comprobante"),c2("1 libros · 0 códigos","pendientes de entrega"),badge("Con pendientes","warn")],
     [c2("IM202609-10","25 sep · factura Libretas Superpower · Otro · Ambato"),"Otro","Ambato",c2("10 ítems · $79.92","sin comprobante"),c2("10 libros · 0 códigos","pendientes de entrega"),badge("Con pendientes","warn")],
     [c2("IM202609-09","24 sep · factura 000809715 · Books & Bits · Ambato"),"Books & Bits","Ambato",c2("9 ítems · $333.03","Comprobante: comprobante_2026-09-24.pdf"),c2("0 libros · 0 códigos","pendientes de entrega"),badge("Recibido","ok")]],sede=2,hide=(1,2),wide=0)
     +card("Detalle del ingreso IM202610-01", kv(("Fecha","1 oct 2026"),("Proveedor","Books & Bits"),("Factura","000814675"),("Subtotal","$456.71"),("Descuento","$0.00"),("Total","$456.71"),("Comprobante","comprobante_books_and_bits_2026-10-01.pdf"))+table(["Código","ISBN","Ítem","Cantidad","Precio","Subtotal"],[["1115","9781009029780","Prepare 3 SB with eBook 2E","3","$34.89","$104.67"],["1116","9781009030502","Prepare 3 WB with Digital Pack 2E","3","$20.03","$60.09"],["1132","9781108961691","Empower A1 Starter SB with digital pack 2nd Ed","1","$62.15","$62.15"],["1141","9781108961523","Empower B1+ Intermediate Combo B with digital pack","1","$35.98","$35.98"],["1292","9781108812276","Super Minds 2Ed Level 3 SB with eBook","1","$31.37","$31.37"],["1271","9781009293891","Four Corners 2ED L4 ESB with DP","2","$35.46","$70.92"]],wide=2)+kv(("Ítems","14"),("Total","$456.71"))+note("Equivale a 'Inventory Management' de TeamDesk: cada ingreso del proveedor con su factura, comprobante de pago, ítems por ISBN y los libros o códigos que quedaron pendientes de entrega.")),
  "Movimientos": filters(search("Buscar","Libro, factura o pedido",w="220px"),sel("Tipo",["Todos","Ingreso","Salida","Traslado","Devolución"],w="140px"),sel("Usuario",["Todos","Carla M.","Secretaría","Diego R."],w="140px"),dates(),actions=btn("Registrar movimiento",None,True)+btn("Exportar"))+table(["Fecha","Tipo","Libro","Cantidad","Sede","Vinculado a","Usuario"],[["04 oct","Salida","Adults B1 Student Book","1","Quito","Factura #1234","Carla M."],["03 oct","Ingreso","Kids 2 Workbook","8","Valle","Pedido #P-040","Secretaría"],["02 oct","Devolución","Teens A2 Student Book","1","Ambato","NC-07","Secretaría"],["01 oct","Traslado","Adults B1 Student Book","3","Quito → Valle","—","Secretaría"],["30 sep","Salida","Adults B2 Student Book","1","Quito","Factura #1240","Carla M."],["29 sep","Salida","Teens A2 Student Book","2","Ambato","Factura #1238","Diego R."],["25 sep","Ingreso","Adults A1 Student Book","10","Quito","Pedido #P-039","Secretaría"]],sede=4),
  "Pedidos a proveedor": table(["Pedido","Proveedor","Ítems","Total","Fecha","Estado"],[["#P-041","Books & Bits","12","$480","02 oct","En camino"],["#P-040","Books & Bits","8","$320","25 sep","Recibido"],["#P-039","Books & Bits","20","$800","10 sep","Recibido"]])+
     two(card("Registrar ingreso", form(["Pedido","Cantidad recibida"])+row(btn("Registrar ingreso",None,True))), card("Forecast de libros (noviembre)", table(["Libro","Cursos por abrir","Cupo","Necesarios","Stock","Pedir"],[["Adults B1 Student Book","2","30","30","3","27"],["Kids 2 Workbook","1","10","10","2","8"],["Teens A2","1","10","10","15","0"]])+note("Cursos que abren el próximo mes × cupo = libros necesarios por sede."))),
  "Códigos de activación": filters(sel("Estado",["Todos","Disponible","Asignado","Vencido"],w="140px"),sel("Producto",["Todos","Empower B1+ digital pack","Prepare 3 WB Digital Pack","Empower A1 digital pack"],w="240px"),actions=btn("Asignar código",None,True))+table(["Producto","ISBN","Código","Ingreso","Sede","Estudiante","Estado"],[["Empower B1+ digital pack","9781108961523","EMP-B1-7K2Q-••••","IM202610-01","Valle","María Andrade",badge("Asignado","ok")],["Prepare 3 WB Digital Pack","9781009030502","PRE-3W-91XA-••••","IM202610-01","Valle","—",badge("Disponible")],["Prepare 3 WB Digital Pack","9781009030502","PRE-3W-91XB-••••","IM202610-01","Valle","—",badge("Disponible")],["Empower A1 digital pack","9781108961691","EMP-A1-22QD-••••","IM202609-12","Quito","—",badge("Disponible")],["Empower A1 digital pack","9781108961691","EMP-A1-18ZZ-••••","IM202508-03","Quito","—",badge("Vencido","bad")]],sede=4)+note("Reemplaza 'Purchased Book Codes' y 'Pending codes' de TeamDesk: el código entra con el ingreso del proveedor y se asigna al estudiante al entregar el material."),
  "Notas de crédito": table(["Nota","Factura origen","Estudiante","Motivo","Monto","Fecha","Estado"],[["NC-07","#1234","María Andrade","Libro devuelto","$45","02 oct","Aplicada"],["NC-06","#1180","Juan Pérez","Cambio de modalidad","$50","20 sep","Aplicada"],["NC-05","#1102","Ana Ruiz","Libro con defecto","$45","05 sep","Pendiente"]])+row(btn("Nueva nota de crédito",None,True),btn("Ver facturas","Facturas.html")),
 }),
 subtitle="Entradas, salidas y devoluciones vinculadas a cursos y facturas"),"Movimientos de inventario")

guardados=[("Estudiantes nuevos por mes","Cuántos entraron, por sede y asesor","Dirección Comercial · cada lunes","New Students Report"),
           ("Quiénes deben dinero","Facturas con saldo y días de atraso","Secretaría · diario","Matrículas con saldos · Saldos negativos"),
           ("Facturación del mes","Facturas, pagos, notas de crédito y XML por sede","Contabilidad · fin de mes","Today's Invoices · Download XML Files · List of Payments"),
           ("Facturas sin autorizar o sin enviar","Estado SRI y comprobantes pendientes","Secretaría · diario","sin enviar"),
           ("Ventas por asesor","Niveles vendidos vs meta y comisión","Dirección Comercial · fin de mes","Commissions Report · Sales Summary"),
           ("Descuentos por asesor","% promedio, monto, motivos y aprobaciones","Dirección Comercial · semanal","Discount (campo Reason de Invoice)"),
           ("Este mes vs el anterior","Ventas, matrículas y cobros comparados","Gerencia · fin de mes","Current Month vs Last Month"),
           ("Cursos terminados sin calificar","Bloquean certificados y rematrícula","Coordinación · semanal","Finished courses with ungraded students"),
           ("Horas y pago por profesor","Sesiones confirmadas y payment sheet","Coordinación · fin de mes","Teachers payment sheet"),
           ("Libros que faltan","Stock por sede y pedidos en camino","Secretaría · semanal","Inventory Management"),
           ("Compras por proveedor","Ingresos, egresos y notas de crédito","Administración · mensual","Product revenue query"),
           ("Reporte anual por sede","Estudiantes, matrículas, ingresos y retención del año","Gerencia · anual","INFO REPORTE ANUAL 2023 / 2024"),
           ("Aprobación vs pérdida de niveles","Aprobados y reprobados por módulo, profesor y sede","Coordinación · al cerrar cada módulo","Aprobación VS Pérdida de niveles"),
           ("Inscripciones: este año vs el anterior","Matrículas nuevas mes a mes comparadas","Gerencia · mensual","Inscripciones Año Actual / Año Pasado · Now vs Then"),
           ("Asistentes por fecha","Quiénes asistieron cada día, por curso y sede","Coordinación · diario","Total Attendees by [Date]"),
           ("Caja del día y pagos","Cobros por método y recibos","Secretaría · diario","1. Cash · List of Payments"),
           ("Cartera por cuotas","Cuotas vencidas y por vencer con seguimiento","Secretaría · semanal","Portfolio (Expired / Unexpired)")]
REP_COMERCIALES={"Quiénes deben dinero","Facturación del mes","Facturas sin autorizar o sin enviar","Ventas por asesor","Descuentos por asesor","Este mes vs el anterior","Reporte anual por sede","Caja del día y pagos","Cartera por cuotas","Estudiantes nuevos por mes","Inscripciones: este año vs el anterior","Compras por proveedor"}
def _rep_rl(t): return ' data-roles="ADM,GER,DIR,SUC"' if t in REP_COMERCIALES else ""
saved_cards="".join(f'<a class="saved" href="ConstructorReportes.html"{_rep_rl(t)}><b>{t}</b><small>{d}</small><span class="saved-meta">{ico("user","nav-ico")} {u}</span><span class="saved-old">Antes en TeamDesk: {o}</span></a>' for t,d,u,o in guardados)
page("ConstructorReportes.html","Reportes self-service",shell("Arma tu reporte","Reportes",
 rep_tabs("Reportes self-service"),
 card("", step(1,"¿Qué quieres saber?",picker_areas(PREG_AREAS,(0,0)),"Elige una pregunta; no necesitas saber nombres de tablas ni columnas")
  +step(2,"¿De cuándo y de dónde?",'<div class="pill-row"><span>Período</span>'+pills(["Este mes","Mes pasado","Últimos 3 meses","Este año","Elegir fechas…"],0)+'</div><div class="pill-row"><span>Sede</span>'+pills(["Todas","Quito","Valle","Ambato"],0)+'</div>')
  +step(3,"¿Cómo lo quieres ver?",'<div class="pill-row"><span>Vista</span>'+pills(["Por mes","Por sede","Por asesor","Lista de estudiantes"],0)+'</div><div class="pill-row"><span>Agregar</span>'+pills(["Teléfono de contacto","Asesor","Programa y nivel","Saldo"],[1],multi=True)+'</div>',"Puedes cambiarlo después sin volver a empezar")
  +row(btn("Ver resultado",None,True),btn("Guardar como reporte"))),
 card("Resultado · Estudiantes nuevos · este mes · todas las sedes",
   '<p class="plain">Este mes entraron <b>52 estudiantes nuevos</b>: 28 en Quito, 15 en Valle y 9 en Ambato. Es <b>8% más</b> que el mes pasado.'+only("ADM,GER,DIR,SUC",' Carla M. trajo 21, Diego R. 17 y Sofía L. 14.',True)+'</p>'
   +two(vbars([("Ago",[32,18,11]),("Sep",[40,22,14]),("Oct",[28,15,9])],["Quito","Valle","Ambato"],h=160),
        table(["Mes","Quito","Valle","Ambato","Total"],[["Agosto","32","18","11","61"],["Septiembre","40","22","14","76"],["Octubre (en curso)","28","15","9","52"]]))
   +row(btn("Exportar Excel"),btn("Exportar PDF"),btn("Enviar por correo"),btn("Ver la lista de estudiantes","Estudiantes.html"))),
 card("Reportes guardados", '<div class="saved-grid">'+saved_cards+'</div>',extra=btn("Nuevo reporte","ConstructorReportes.html")),
 subtitle="Pregunta en tus palabras, elige período y sede, y listo"),"Arma tu reporte")

# 30 Dashboard ejecutivo
page("DashboardEjecutivo.html","Dashboard ejecutivo",shell("Dashboard ejecutivo","Dashboard ejecutivo",
 rep_tabs("Dashboard ejecutivo"),
 filters(sel("Período",["2026 (ene–oct)","2025","Último trimestre"],w="170px"),sel("Comparar con",["2025","Sin comparación"],w="160px"),sel("Programa",["Todos","Adults","Teens","Kids"],w="130px")),
 '<section class="card"><div class="hero-number"><span class="hn-label">Ingresos del año (ene a oct 2026)</span><span class="hn-value">'+sv("$386,400","$204,800","$116,900","$64,700","$22,300")+'</span><span class="hn-sub">+12% frente al mismo período de 2025</span></div>'
 +linechart(["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct"],{"Quito":[18,19,21,20,22,21,19,20,23,24],"Valle":[10,11,12,11,13,12,11,12,13,14],"Ambato":[6,6,7,6,7,7,6,6,7,8]},h=220)+'</section>',
 kpis([("Estudiantes activos",sv(812,420,230,162,38),"+3% vs 2025"),("Ticket promedio por venta",sv("$915","$940","$890","$880","$860"),"2.1 niveles por venta"),("Margen después de profesores y libros",sv("34%","38%","31%","27%","25%"),"por sede")]),
 two(card("Mix por programa y modalidad", stacked([("Adults",58),("Teens",24),("Kids",18)])+stacked([("Presencial",63),("Virtual",37)])),
 card("Funnel comercial (2026)", funnel([("Leads Kommo",2840),("Cotizaciones",1120),("Ventas",640),("Matriculados",598)]))),
 two(card("Retención y avance de niveles", hbars([("Continúan al siguiente nivel",71),("Pausan (vuelven en 6 meses)",14),("Abandonan",15)],"")+progress(71,"Retención objetivo 2026: 75%")),card("Lectura rápida",li(["Quito explica el 53% de los ingresos y crece 9%","Valle mantiene el ticket más alto","Ambato necesita 2 cursos nuevos para llegar a la meta"]))),
 subtitle="Vista gerencial, distinta de la reportería operativa"),"Dashboard ejecutivo")

# 31 Chatbot
chat='<div class="chat"><div class="chat-log">'+ \
 '<div class="msg me">¿Cuántos estudiantes activos tiene Valle en nivel B1?</div>'+ \
 '<div class="msg bot">Valle tiene 23 estudiantes activos en B1, repartidos en 2 cursos (P. Gómez y L. Vega). ¿Quieres ver el listado?</div>'+ \
 '<div class="msg me">¿Qué pagos a profesores están pendientes de aprobar?</div>'+ \
 '<div class="msg bot">La payment sheet de octubre está en borrador con 3 alertas. Solo puedes ver pagos de las sedes que tu rol permite.</div>'+ \
 f'</div><div class="chat-in"><label for="msg" class="sr">Mensaje</label><input id="msg" class="ctl" placeholder="Pregunta sobre estudiantes, cursos, pagos o reportes">{btn("Enviar",None,True)}</div></div>'
page("Chatbot.html","Asistente interno",shell("Asistente interno","Inicio",chat,
 two(card("Qué puede responder", li(["Consultas sobre estudiantes, cursos, profesores, facturas y stock","Estado de aprobaciones y payment sheet","Resúmenes: '¿cuántos estudiantes activos tiene Valle en B1?'"])), card("Límites", li(["Responde solo con datos de la plataforma","Respeta el rol y las sedes del usuario (RBAC)","No modifica datos: para eso enlaza a la pantalla correspondiente"]))),
 subtitle="Consulta ágil para el equipo, sin armar un reporte"),"Asistente interno")

# 32 Integraciones
page("Integraciones.html","Integraciones",shell("Integraciones","Integraciones",
 table(["Sistema","Uso","Estado","Última sincronización","Acción"],[["Kommo (CRM)","Leads → estudiantes","Conectado","Hoy 09:00",btn("Configurar")],["Moodle (LMS)","Matrícula → curso virtual · notas y asistencia","Pendiente de API del proveedor","—",btn("Configurar")],["Dora","Por definir con el cliente","Pendiente","—",btn("Configurar")],["Microsoft 365 (Teams / cuentas)","Enlace de clase virtual y cuenta del estudiante","Fuera del contrato · se evalúa en Fase 1","—",btn("Configurar")],["Email / WhatsApp (plantillas)","Notificaciones a estudiantes (enlace de clase, saldos)","Plantillas migradas de TeamDesk","—",btn("Configurar")],["Google Maps Platform","Dirección del estudiante: autocompletado (Places), posición exacta y provincia/cantón/parroquia por geocodificación inversa (Geocoding), mapa en la ficha (Maps Embed)","Requiere clave de API y facturación de Google (uso bajo: ~1.000 direcciones/mes)","—",btn("Configurar")]]),
 note("Las tablas 'Microsoft Accounts', 'Email Templates', 'Companies' y 'Portfolio' de TeamDesk no están en los 11 módulos del contrato. Se migran como datos y su gestión se confirma con el cliente (Cláusula Tercera, 3.2)."),
 two(card("API keys y webhooks", table(["Clave","Sistema","Creada","Último uso","Estado"],[["kommo-prod-••••7f2a","Kommo","12 ene","Hoy 09:00",badge("Activa","ok")],["moodle-test-••••91c0","Moodle","20 sep","—",badge("Pendiente","warn")]])+table(["Webhook","Evento","URL"],[["Nuevo lead","lead.created","https://api.cambridge.../kommo"],["Matrícula","enrollment.created","https://moodle.cambridge.../enrol"]])+row('<a href="#" style="font-size:13px">Documentación OpenAPI</a>')), card("Log de sincronización", table(["Fecha","Sistema","Resultado"],[["04 oct","Kommo","12 leads importados"],["03 oct","Kommo","1 error: email duplicado"]]))),
 subtitle="Sujeto al esquema de apificación disponible en cada proveedor"),"Integraciones")

# 33 Notificaciones
page("Notificaciones.html","Notificaciones",shell("Notificaciones","Inicio",
 card("Tus avisos", "".join(only(c, notif_table(c)) for c,_,_ in ROLES), extra='<small class="card-hint">Solo ves los avisos de tu rol</small>'),
 card("Preferencias por rol", table(["Notificación","Admin","Dir. Comercial","Coord. Académica","Asesor","Secretaría","Canal"],[["Aprobación pendiente","✓","✓","✓","—","—","Plataforma + email"],["Descuento aprobado / rechazado","—","—","—","✓","—","Plataforma + email"],["Stock negativo","✓","—","—","—","✓","Plataforma"],["Payment sheet lista","✓","—","✓","—","—","Email"],["Profesor aprobado","—","—","✓","—","—","Plataforma"]])),
 subtitle="Centro de avisos que mueve los flujos de aprobación"),"Notificaciones")

# ---------- Pantallas de formulario y acción (todo botón lleva a algún lado) ----------
# 34 Recuperar contraseña
ver=f'''<div class="auth">
<form>
  {logo()}
  <h1 style="margin:0;font-size:22px">Verificar un certificado</h1>
  <label for="cod">Código de verificación</label>
  <input id="cod" type="text" placeholder="CSL-B1-2026-7K2Q" class="ctl">
  {btn("Verificar",None,True)}
  <div class="card">{kv(("Resultado",badge("Certificado válido","ok")),("Titular","María Andrade"),("Nivel","A2 · módulos 3–6"),("Programa","English for Adults (ESL)"),("Emitido","30 jun 2026 · Quito"))}</div>
  <a href="Main.html" style="font-size:13px;text-align:center">Volver al ingreso</a>
</form>
</div>'''
page("VerificarCertificado.html","Verificar certificado",ver,"Verificar certificado")
rec=f'''<div class="auth">
<form>
  {logo()}
  <h1 style="margin:0;font-size:22px">Recuperar contraseña</h1>
  <p style="margin:0;font-size:14px;color:{MUTE}">Te enviamos un enlace temporal al correo registrado. Caduca en 30 minutos.</p>
  <label for="email">Correo</label>
  <input id="email" type="email" placeholder="nombre@cambridge.edu.ec" class="ctl">
  {btn("Enviar enlace",None,True,"Si el correo existe se envía el enlace de recuperación. El intento queda en el audit log.","Main.html")}
  <a href="Main.html" style="font-size:13px;text-align:center">Volver al login</a>
</form>
</div>'''
page("RecuperarContrasena.html","Recuperar contraseña",rec,"Recuperar contraseña")

# 35 Registrar sesión manual
page("RegistrarSesion.html","Registrar sesión",shell("Registrar sesión manual","Sesiones",
 form(title="Sesión", fields=[("Curso","0001-2026-0767 · Adults B1 Virtual",'select',["0001-2026-0767 · Adults B1 Virtual","0001-2026-0620 · Adults A2","0001-2026-0328 · Kids 2 Tarde"],True),("Profesor","P. Gómez · contrato activo",'select',["P. Gómez · contrato activo","L. Vega · contrato activo","R. Salas · contrato vencido"],True,"Se valida contrato activo"),("Fecha","",'date',None,True),("Hora inicio","",'time',None,True),("Hora fin","",'time',None,True),"Horas (calculado)",("Tipo de sesión","Regular",'select',["Regular","Reposición","Clase individual","Día libre del profesor (no suma horas)"]),("Profesor sustituto","— (dicta el titular)",'select',["— (dicta el titular)","L. Vega","M. Castro","S. Jiménez"],False,"Las horas van a la payment sheet de quien dictó"),("Minutos de atraso","0",'number'),("Aula / enlace","Zoom 2")]),
 card("Asistencia", table(["Estudiante","Presente","Observación"],[["María Andrade","☑","—"],["Pedro Mora","☑","—"],["Sofía Herrera","☐","Aviso previo"],["Andrés Pazmiño","☐","—"]])),
 note("Si la fecha u hora no coinciden con el horario del curso, la sesión se marca 'fuera de horario' y pide confirmación de Coordinación.","warn"),
 foot(btn("Guardar sesión",None,True,"La sesión queda registrada como manual, pendiente de confirmación. Al confirmarse suma horas a la payment sheet.","Sesiones.html"),btn("Cancelar","Sesiones.html")),
 subtitle="Para clases que no entran por Moodle: presenciales, reposiciones, individuales"),"Registrar sesión manual")

# 36 Registrar pago
page("RegistrarPago.html","Registrar pago",shell("Registrar pago","Facturación",
 hero([("Estudiante",'<a href="Ficha360.html">Camila Sánchez</a>'),("Factura",'<a href="DetalleFactura.html">000021094</a>'),("Venta","A2–B1 · Ambato"),("Total","$950.00"),("Pagado","$475.00"),("Saldo","$475.00"),("Crédito","Sí · 30 días"),("Vence","11 nov 2026")],tag='<span class="hero-code">000021094</span>'+badge("Parcial","warn")),
 form(title="Nuevo pago", fields=[("Monto","475.00",'number',None,True,"Saldo pendiente $475.00"),("Fecha de pago","",'date',None,True),("Método","Transferencia",'select',["Transferencia","Efectivo","Tarjeta","Depósito"],True),("Referencia / comprobante","Banco Pichincha · ref. 902211"),"Comprobante (archivo)","Observación"]),
 card("Resultado", flow(["Pago registrado","Cubre el saldo → Pagada","Parcial → Pendiente con nuevo saldo","Notificación al asesor"])),
 foot(btn("Registrar pago",None,True,"Se registra el pago, se actualiza el estado de cobro y queda en el audit log.","DetalleFactura.html"),btn("Cancelar","DetalleFactura.html")),
 subtitle="Estado de cobro por factura, no por módulo"),"Registrar pago")

# 37 Nota de crédito
page("NotaCredito.html","Nota de crédito",shell("Nueva nota de crédito","Facturación",
 form(title="Datos", fields=[("Factura origen","000021092 · Luis Torres · $68.00",'select',["000021092 · Luis Torres · $68.00","000021094 · Camila Sánchez · $950.00","000021080 · Pedro Mora · $500.00"],True),"Estudiante (automático: Luis Torres)","Motivo (devolución / cambio de curso / libro con defecto / anulación total / otro)",("Monto","68.00",'number',None,True,"Hasta el total de la factura"),"Devolver libro al stock (sí / no)","Justificación"]),
 two(card("Qué pasa al emitir", flow(["Se vincula a la factura origen","Se envía al SRI y se autoriza","Ajusta saldo o genera devolución","Libro vuelve al stock (si aplica)","Audit log"])),
     card("Reglas del contrato de servicios educativos", table(["Caso","Qué aplica"],[["Inscripción (derecho de matrícula)","No se devuelve"],["Devolución antes de iniciar","Se retiene el 10% del valor del curso; el resto se devuelve en hasta 45 días"],["Curso iniciado","No hay devolución en dinero: cambio de horario o modalidad, o nota de crédito"],["Nota de crédito","Vigencia 12 meses desde su emisión"],["Interrupción de 2 meses","Puede retomar con cambio de horario o modalidad o nota de crédito"],["Interrupción de 6 meses o más","Nuevo contrato y prueba de ubicación"],["Reclamos","Por escrito a Coordinación Administrativa de la sede"]],wide=0))),
 foot(btn("Emitir nota de crédito",None,True,"Se emite la nota de crédito vinculada a la factura. Si marcaste devolución de libro, el stock de la sede se actualiza.","DetalleFactura.html"),btn("Cancelar","DetalleFactura.html")),
 subtitle="Toda devolución o cambio deja rastro contable"),"Nota de crédito")

# 38 Registrar movimiento de inventario
page("RegistrarMovimiento.html","Registrar movimiento",shell("Registrar movimiento de inventario","Movimientos y pedidos",
 form(title="Datos", fields=["Tipo (ingreso / salida / traslado / devolución)","Libro","Cantidad","Sede origen","Sede destino (solo traslado)","Vinculado a (factura / curso / pedido / nota de crédito)","Observación"]),
 note("Una salida sin factura o curso vinculado pide justificación y se marca para revisión.","warn"),
 foot(btn("Registrar movimiento",None,True,"Se actualiza el stock de la sede y el movimiento queda en el historial con tu usuario.","Movimientos.html"),btn("Cancelar","Movimientos.html")),
 subtitle="Reemplaza los ajustes a mano en TeamDesk"),"Registrar movimiento")

# 39 Nuevo pedido a proveedor
page("NuevoPedido.html","Nuevo pedido",shell("Nuevo pedido a proveedor","Movimientos y pedidos",
 form(title="Datos", fields=["Proveedor (Books & Bits)","Sede destino","Fecha estimada de entrega"]),
 card("Ítems", table(["Libro","Stock actual","Comprometido","Sugerido","Cantidad a pedir"],[["Adults B1 Student Book","-2","5","6","6"],["Kids 2 Workbook","-1","4","4","4"],["Teens A2","5","3","—","0"]])+note("Sugerido = comprometido por cursos que abren − stock disponible.")),
 foot(btn("Enviar pedido",None,True,"El pedido queda En camino y se notifica a Secretaría de la sede para registrar el ingreso cuando llegue.","Movimientos.html"),btn("Cancelar","Movimientos.html")),
 subtitle="Pedido con cantidades sugeridas por el forecast de cursos"),"Nuevo pedido a proveedor")

# 40 Nuevo usuario
page("NuevoUsuario.html","Nuevo usuario",shell("Nuevo usuario","Usuarios y roles",
 form(title="Datos", fields=["Nombres y apellidos","Email","Rol (Admin / Dir. Comercial / Coord. Académica / Asesor / Secretaría / Profesor)","Sedes visibles","Estado","2FA obligatorio (sí / no)"]),
 card("Permisos del rol elegido", li(["Crear estudiante · Aplicar descuento hasta 10% · Ver solo su sede","No puede: aprobar profesores, exportar base completa, ver otras sedes"])+note("La matriz completa se edita en Usuarios y roles → Matriz de permisos.")),
 foot(btn("Guardar usuario",None,True,"Se crea el usuario y recibe un correo para definir su contraseña. El alta queda en el audit log.","Usuarios.html",save="usuarios"),btn("Cancelar","Usuarios.html")),
 subtitle="Un usuario, un rol, las sedes que le corresponden"),"Nuevo usuario")

# 41 Nueva sede
page("NuevaSede.html","Nueva sede",shell("Nueva sede","Configuración",
 form(title="Datos", fields=["Nombre","Ciudad","Dirección","Teléfono","Aulas","Responsable","Estado (activa / próxima)"]),
 note("Al crear la sede aparece en el selector global, en filtros y en la matriz de visibilidad por rol. Inventario arranca en cero."),
 foot(btn("Guardar sede",None,True,"La sede queda disponible en toda la plataforma. "+AUDIT,"Configuracion.html"),btn("Cancelar","Configuracion.html")),
 subtitle="Preparado para Quito Norte y las que vengan"),"Nueva sede")

# 42 Nuevo nivel
page("NuevoNivel.html","Nuevo nivel",shell("Nuevo nivel del catálogo","Configuración",
 two(form(title="Datos", fields=[("Programa","English for Adults (ESL)",'select',PROGRAMAS,True),("Nivel","C1",'select',[n for n,_ in NIVELES],True,"Según la tabla nivel ↔ módulo"),("Módulos que lo componen","15–16",'text',None,True,"Automático desde la tabla"),("Horas totales","36",'number',None,True,"18 h por módulo"),("Precio virtual","580",'number',None,True),("Precio presencial","630",'number',None,True),("Libro asociado","Empower C1 Advanced",'text'),"Vigencia del precio"]),
     card("Tabla nivel ↔ módulo vigente", tabla_niveles())),
 note("Los precios tienen vigencia: una venta usa el precio vigente a su fecha. Cambiar el precio no altera facturas emitidas."),
 foot(btn("Guardar nivel",None,True,"El nivel queda disponible para nuevas ventas y cursos. "+AUDIT,"Configuracion.html"),btn("Cancelar","Configuracion.html")),
 subtitle="Catálogo configurable sin desarrollador"),"Nuevo nivel")

# 43 Nueva regla de aprobación
page("NuevaRegla.html","Nueva regla",shell("Nueva regla de aprobación","Configuración",
 form(title="Datos", fields=["Nombre de la regla","Entidad (descuento / profesor / asignación / exportación / tarifa)","Condición (ej. descuento > 10%)","Quién aprueba (rol)","Notificar a","Vigencia","Estado"]),
 note("Toda acción que cumpla la condición queda bloqueada hasta que el rol aprobador decida en la bandeja de aprobaciones."),
 foot(btn("Guardar regla",None,True,"La regla queda activa y se aplica desde ahora. "+AUDIT,"Configuracion.html"),btn("Cancelar","Configuracion.html")),
 subtitle="Las reglas de negocio viven en configuración, no en código"),"Nueva regla de aprobación")

rows=[
 ("Acceso y transversales · todos los roles",[("Main.html","Login"),("RecuperarContrasena.html","Recuperar contraseña"),("VerificarCertificado.html","Verificar certificado (público)"),("PortalEstudiante.html","Portal del estudiante (propuesta fuera de alcance)"),("Home.html","Inicio por rol"),("Notificaciones.html","Notificaciones"),("Chatbot.html","Asistente interno")],"Login → Inicio por rol. El menú, las pestañas y los accesos cambian con el tipo de usuario ('Ver como' en la barra superior). Notificaciones y asistente acompañan todos los flujos."),
 ("Académico · Coordinación, profesores, secretaría",[("Programas.html","Programas, modalidades y tipos de clase"),("Estudiantes.html","Estudiantes"),("NuevoEstudiante.html","Nuevo estudiante"),("Ficha360.html","Ficha 360°"),("DetalleMatricula.html","Detalle de matrícula"),("ImportExport.html","Importar / exportar"),("Cursos.html","Cursos"),("NuevoCurso.html","Nuevo curso"),("DetalleCurso.html","Detalle de curso"),("CalificarCurso.html","Calificar curso (cierre de módulo)"),("ExamenesInternacionales.html","Exámenes internacionales (propuesta)"),("Sesiones.html","Registro de sesiones"),("RegistrarSesion.html","Sesión manual"),("Profesores.html","Profesores"),("FichaProfesor.html","Perfil del profesor"),("AltaProfesor.html","Alta de profesor"),("ContratacionProfesores.html","Contratación de profesores (pipeline)"),("DetalleCandidato.html","Detalle de candidato"),("PaymentSheet.html","Payment sheet")],"Estudiantes → matrículas → cursos con código, aula y profesor validado → sesiones → progreso, pass/fail y certificados. Perfil del profesor con agenda, carga y payment sheet."),
 ("Comercial · Asesores, Dirección Comercial, secretaría",[("Leads.html","Leads y conversión (Kommo)"),("Pedidos.html","Tienda en línea · pedidos WooCommerce"),("DetallePedido.html","Detalle de pedido (seguimiento)"),("TableroComercial.html","Tablero comercial (diario y mensual)"),("DetalleVenta.html","Detalle de venta (compra completa)"),("MatriculaContinuidad.html","Matrícula de continuidad (saldo a favor)"),("NuevaInscripcionExamen.html","Inscripción a examen internacional"),("VentaMercaderia.html","Venta de mercadería"),("InformeComisiones.html","Informe de comisiones del asesor"),("NuevaVenta.html","Nueva matrícula (por módulo)"),("MatriculaLead.html","Matrícula desde un lead (datos precargados)"),("Empresas.html","Empresas y grupos B2B"),("DetalleEmpresa.html","Detalle de empresa B2B"),("NuevaEmpresa.html","Nueva empresa y convenio"),("SolicitudDescuento.html","Solicitud de descuento"),("Aprobaciones.html","Bandeja de aprobaciones"),("Facturas.html","Facturas"),("DetalleFactura.html","Detalle de factura"),("RegistrarPago.html","Registrar pago"),("NotaCredito.html","Nota de crédito"),("Comisiones.html","Período de comisiones"),("DetalleComision.html","Detalle por asesor"),("ReglasComision.html","Reglas de comisión")],"Venta por paquete de niveles → descuento fuera de regla pasa por aprobación → comisión del asesor calculada por reglas y pagada al cobrar."),
 ("Inventario · Secretaría, Administración de sucursal",[("Inventario.html","Stock por sede"),("Movimientos.html","Ingresos, movimientos y pedidos"),("NuevoPedido.html","Nuevo pedido"),("RegistrarMovimiento.html","Registrar movimiento")],"Stock por sede y por ISBN, ingresos del proveedor con factura y comprobante, códigos de activación, pedidos con forecast."),
 ("Dirección · Gerencia, Dirección Comercial",[("Insights.html","Insights de IA"),("Reportes.html","Dashboard por rol"),("ConstructorReportes.html","Constructor de reportes"),("DashboardEjecutivo.html","Dashboard ejecutivo")],"Reportería self-service que reemplaza las vistas de TeamDesk y vista gerencial separada."),
 ("Administración · Administrador General",[("Usuarios.html","Usuarios y roles"),("NuevoUsuario.html","Nuevo usuario"),("Configuracion.html","Configuración"),("DetalleProducto.html","Detalle de producto o servicio"),("NuevaSede.html","Nueva sede"),("NuevoNivel.html","Nuevo nivel"),("NuevaRegla.html","Nueva regla"),("AuditLog.html","Audit log"),("Integraciones.html","Integraciones"),("ReclutamientoAdministrativo.html","Reclutamiento de personal administrativo (propuesta)")],"RBAC, catálogos (sedes, aulas, programas, productos, empresas), reglas configurables, trazabilidad completa e integraciones."),
]
rows=[(t,[(f,n) for f,n in files if f not in HIDDEN],d) for t,files,d in rows]
rows=[r for r in rows if r[1]]
sec=""
N=0
TOTAL=sum(len(f) for _,f,_ in rows)
for t,files,desc in rows:
    cards=""
    for f,n in files:
        N+=1; cards+=f'<a class="card" href="{f}"><span class="num">{N:02d}</span><span>{n}</span></a>'
    arrows=f'<div class="flow">{cards}</div>'
    sec+=f'<section><h2>{t}</h2><p>{desc}</p>{arrows}</section>'
idx=f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Wireframes Plataforma Cambridge</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="style.css">
</head>
<body class="hub">
<header class="hub-head">
<h1>Plataforma Cambridge · Mapa de pantallas</h1>
<p><a href="Main.html">← Entrar al mockup</a> · Mockup navegable con la identidad de Cambridge y datos ficticios. Cada pantalla es navegable: los botones y enlaces llevan a la siguiente pantalla del flujo. {TOTAL} pantallas que cubren los 11 módulos del contrato. Los botones de acción (guardar, aprobar, exportar…) muestran qué pasaría al confirmar. El selector de sede filtra cifras y tablas, y 'Ver como' cambia el tipo de usuario: menú, pestañas y accesos cambian según el rol.</p>
</header>
{sec}
<footer class="hub-foot">Orkesta · Cambridge School of Languages · Fase 0 Discovery y Diseño</footer>
</body>
</html>'''
open(os.path.join(ROOT,"Mapa.html"),"w").write(idx)
open(os.path.join(ROOT,"index.html"),"w").write('''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=Main.html"><title>Plataforma Cambridge</title><link rel="canonical" href="Main.html"></head>
<body style="font-family:sans-serif;padding:24px">Abriendo la plataforma… <a href="Main.html">Entrar</a></body></html>''')
css='''*{box-sizing:border-box}
:root{
  --bg:#F7F7F5;--surface:#FFFFFF;--surface-2:#F1F1EE;
  --ink:#16181D;--ink-2:#3D4350;--mute:#5E6573;
  --line:#E3E5E9;--line-strong:#8A909C;
  --navy:#1D3F8F;--navy-700:#152F6B;--navy-50:#EAF0FB;
  --red:#C4202F;--yellow:#F6C21C;--yellow-50:#FEF6D8;
  --ok:#1E7A4F;--ok-50:#EAF4EE;--warn:#9A5B00;--warn-50:#FDF3E1;--bad:#B42318;--bad-50:#FCEBEA;--info:#1D3F8F;--info-50:#EAF0FB;
  --font-ui:'IBM Plex Sans',system-ui,sans-serif;--font-mono:'IBM Plex Mono',ui-monospace,monospace;--font-display:'Source Serif 4',Georgia,serif;
  --t-12:12px;--t-13:13px;--t-14:14px;--t-16:16px;--t-20:20px;--t-24:24px;--t-32:32px;--lh-tight:1.2;--lh:1.5;
  --s-1:4px;--s-2:8px;--s-3:12px;--s-4:16px;--s-5:24px;--s-6:32px;--s-7:48px;--s-8:64px;
  --r-sm:4px;--r:6px;--r-lg:10px;
  --shadow-pop:0 8px 24px rgba(22,24,29,.12),0 1px 2px rgba(22,24,29,.08);
  --focus:0 0 0 2px #FFFFFF,0 0 0 4px var(--navy);
  --ease:cubic-bezier(.2,.8,.2,1);--dur-1:120ms;--dur-2:200ms;--hit:44px;
  /* alias de compatibilidad */
  --fill:var(--surface-2);--navy2:var(--navy-700);--tint-navy:var(--navy-50);--tint-red:var(--bad-50);--tint-yellow:var(--yellow-50);--tint-sky:var(--info-50);--tint-green:var(--ok-50);--sky:#4FA3DC
}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
html{-webkit-text-size-adjust:100%}
[hidden]{display:none!important}
body{margin:0;font-family:var(--font-ui);color:var(--ink);background:var(--bg);font-size:var(--t-14);line-height:var(--lh)}
a{color:var(--navy);text-underline-offset:2px}a:hover{color:var(--navy-700)}
:focus-visible{outline:none;box-shadow:var(--focus);border-radius:var(--r-sm)}
.sr{position:absolute!important;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
h1,h2,h3,h4{font-weight:600;line-height:var(--lh-tight)}
.mono,.code{font-family:var(--font-mono);font-variant-numeric:tabular-nums}
.num{font-variant-numeric:tabular-nums}

/* ===== shell ===== */
.app{display:flex;min-height:100vh}
.sidebar{width:232px;flex:none;background:var(--surface);border-right:1px solid var(--line);display:flex;flex-direction:column;padding:16px 12px;gap:4px;position:sticky;top:0;height:100vh;overflow:hidden}
.brand{display:flex;align-items:center;padding:4px 8px 16px;text-decoration:none}.brand img{width:100%;max-width:180px;height:auto;display:block}
.brand-dark{justify-content:center}
.sidebar nav{flex:1;overflow-y:auto;min-height:0;scrollbar-width:thin;padding-bottom:12px}
.nav-area{display:flex;align-items:center;justify-content:space-between;min-height:36px;padding:12px 10px 4px;font-size:var(--t-12);letter-spacing:.04em;text-transform:uppercase;color:var(--mute);font-weight:600;cursor:pointer;list-style:none;user-select:none}.nav-area::-webkit-details-marker{display:none}.nav-area:hover{color:var(--ink)}
.nav-caret{width:12px;height:12px;transform:rotate(90deg);transition:transform var(--dur-1) var(--ease);color:var(--mute)}details.nav-group:not([open]) .nav-caret{transform:rotate(0)}
.nav-link{display:flex;align-items:center;gap:10px;min-height:40px;padding:0 10px;border-radius:var(--r);color:var(--ink-2);text-decoration:none;font-size:var(--t-14);font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;border-left:2px solid transparent;transition:background var(--dur-1) var(--ease)}
.nav-link:hover{background:var(--surface-2);color:var(--ink)}.nav-link.active{background:var(--navy-50);color:var(--navy);font-weight:600;border-left-color:var(--navy);border-radius:0 var(--r) var(--r) 0}
.nav-ico{width:18px;height:18px;flex:none;display:inline-flex}.nav-ico svg{width:18px;height:18px;stroke:currentColor;fill:none;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
.sidebar-more{position:absolute;left:0;right:0;bottom:0;height:56px;pointer-events:none;background:linear-gradient(to bottom,rgba(255,255,255,0),#fff 70%);opacity:0;transition:opacity var(--dur-2);display:flex;align-items:flex-end;justify-content:center;padding-bottom:8px;font-size:var(--t-12);color:var(--mute)}.sidebar-more::after{content:"Más opciones"}.sidebar.has-more .sidebar-more{opacity:1}
.sidebar-sede{display:none}
.shell-main{flex:1;min-width:0;display:flex;flex-direction:column}
.topbar{display:flex;align-items:center;gap:12px;min-height:60px;padding:8px 32px;background:var(--surface);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}
.topbar-right{display:flex;align-items:center;gap:8px;margin-left:auto;flex:none}
.topbar .menu-btn{display:none}
.crumbs{display:flex;align-items:center;gap:8px;min-width:0;flex:1 1 auto;font-size:var(--t-13);color:var(--mute)}
.crumbs a{color:var(--ink-2);text-decoration:none}.crumbs a:hover{color:var(--navy);text-decoration:underline}
.crumbs .sep{color:var(--line-strong)}.crumbs .here{color:var(--ink);font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.back{width:36px;height:36px;border-radius:var(--r);border:1px solid var(--line);display:inline-flex;align-items:center;justify-content:center;color:var(--ink);text-decoration:none;flex:none}.back:hover{background:var(--surface-2)}
.search{display:flex;align-items:center;gap:8px;width:220px;background:var(--surface);border:1px solid var(--line-strong);border-radius:var(--r);padding:0 12px;height:40px;color:var(--mute)}
.search input{border:0;background:none;font:inherit;flex:1;outline:none;color:var(--ink);min-width:0}.search:focus-within{box-shadow:var(--focus)}.search svg{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:2}
.ctx-sede{display:inline-flex;align-items:center;gap:6px;height:40px;padding:0 4px 0 10px;border:1px solid var(--line-strong);border-radius:var(--r);color:var(--mute);background:var(--surface)}
.ctx-sede select{border:0;background:transparent;font:inherit;font-size:var(--t-14);color:var(--ink);height:38px}.ctx-sede select:focus{outline:none}.ctx-sede:focus-within{box-shadow:var(--focus)}
.icon-btn{position:relative;width:40px;height:40px;border-radius:var(--r);display:inline-flex;align-items:center;justify-content:center;background:transparent;border:1px solid transparent;text-decoration:none;color:var(--ink-2);cursor:pointer;font:inherit}
.icon-btn:hover{background:var(--surface-2)}.icon-btn svg{width:20px;height:20px;stroke:currentColor;fill:none;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
.icon-btn .dot{position:absolute;top:4px;right:2px;min-width:18px;height:18px;background:var(--red);color:#fff;font-size:12px;font-weight:600;border-radius:9px;padding:0 5px;display:inline-flex;align-items:center;justify-content:center}
.user{display:flex;align-items:center;gap:10px;font-size:var(--t-13);color:var(--ink);white-space:nowrap;background:none;border:0;font:inherit;cursor:pointer;padding:4px 8px;min-height:40px;border-radius:var(--r)}.user:hover{background:var(--surface-2)}.user .nav-caret{transform:rotate(90deg)}
.user #rol-user{display:flex;flex-direction:column;line-height:1.25;max-width:180px;overflow:hidden;text-overflow:ellipsis}.user #rol-user small{color:var(--mute);font-size:var(--t-12)}
.user-menu{position:relative}
.user-pop,.notif-pop,.menu-pop{position:absolute;right:0;top:calc(100% + 8px);background:var(--surface);border-radius:var(--r-lg);box-shadow:var(--shadow-pop);border:1px solid var(--line);z-index:30}
.user-pop{width:260px;padding:12px;display:flex;flex-direction:column;gap:8px;font-size:var(--t-14)}.user-pop[hidden],.notif-pop[hidden],.menu-pop[hidden]{display:none}
.user-pop-title{font-size:var(--t-12);letter-spacing:.04em;text-transform:uppercase;color:var(--mute);font-weight:600}
.user-pop label{display:flex;flex-direction:column;gap:4px;font-size:var(--t-13);color:var(--ink-2);font-weight:500}.user-pop select{height:40px;border:1px solid var(--line-strong);border-radius:var(--r);background:#fff;font:inherit;color:var(--ink);padding:0 8px}
.user-pop a{color:var(--ink);text-decoration:none;padding:10px 8px;border-radius:var(--r)}.user-pop a:hover{background:var(--surface-2)}.user-pop-foot{font-size:var(--t-12);color:var(--mute);padding:6px 8px 0;border-top:1px solid var(--line)}
.avatar{display:inline-flex;align-items:center;justify-content:center;border-radius:50%;background:var(--navy-50);color:var(--navy);font-weight:600;flex:none}
.avatar.sm{width:32px;height:32px;font-size:var(--t-13)}.avatar.lg{width:72px;height:72px;font-size:24px}
.main{padding:24px 32px 120px;display:flex;flex-direction:column;gap:32px;min-width:0;width:100%;max-width:1344px}
.page-head{display:flex;align-items:flex-end;gap:16px;flex-wrap:wrap}
.page-head h1{margin:0;font-family:var(--font-display);font-size:var(--t-24);font-weight:600;letter-spacing:-.01em;color:var(--ink)}
.page-head p{margin:4px 0 0;color:var(--mute);font-size:var(--t-14);max-width:760px}
.page-head-actions{margin-left:auto;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.scrim{display:none}

/* ===== componentes base ===== */
.grid{display:grid;gap:24px}.g-cell{min-width:0;display:flex;flex-direction:column;gap:16px}.grid-2{grid-template-columns:repeat(2,minmax(0,1fr))}.grid-r{grid-template-columns:var(--cols)}
.row{display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:24px;display:flex;flex-direction:column;gap:16px;min-width:0}
.card-head{display:flex;align-items:center;gap:12px;flex-wrap:wrap}.card-head h2{margin:0;font-size:var(--t-16);font-weight:600}.card-head>*:last-child:not(h2){margin-left:auto}
.card-hint{font-size:var(--t-13);color:var(--mute);margin-left:auto}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:var(--hit);padding:0 16px;border-radius:var(--r);border:1px solid var(--line-strong);background:var(--surface);color:var(--ink);font:inherit;font-size:var(--t-14);font-weight:500;text-decoration:none;cursor:pointer;white-space:nowrap;transition:background var(--dur-1) var(--ease),border-color var(--dur-1) var(--ease)}
a.btn:hover,.btn:hover{background:var(--surface-2);color:var(--ink)}.btn:active{background:var(--surface-2);border-color:var(--ink-2)}
.btn-primary{background:var(--navy);color:#fff;border-color:var(--navy)}a.btn-primary:hover,.btn-primary:hover{background:var(--navy-700);border-color:var(--navy-700);color:#fff}
.btn-ghost{border-color:transparent;background:transparent;color:var(--navy)}a.btn-ghost:hover,.btn-ghost:hover{background:var(--navy-50);color:var(--navy)}
.btn-danger{color:var(--red)}a.btn-danger:hover,.btn-danger:hover{background:var(--bad-50);color:var(--red)}
.btn[aria-disabled=true],.btn:disabled{background:var(--surface-2);color:var(--mute);border-color:var(--line);cursor:not-allowed}
.btn .nav-ico,.btn .nav-ico svg{width:16px;height:16px}
@media (pointer:fine){.filters .btn,.tbl .btn,.hero-actions .btn,.page-head-actions .btn{min-height:40px}}
.more{position:relative;display:inline-flex}
.menu-pop{min-width:220px;padding:6px;display:flex;flex-direction:column}
.menu-pop>*{width:100%;justify-content:flex-start;border:0!important;background:none;min-height:var(--hit);text-align:left}
.menu-pop>*:hover{background:var(--surface-2)}
.menu-pop [data-roles]{display:flex}
.kebab{width:var(--hit);height:var(--hit);padding:0;border-color:transparent;background:transparent;font-size:20px;line-height:1;color:var(--ink-2)}
.chev{display:inline-block;width:14px;height:14px;flex:none;background:currentColor;-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M9 5l7 7-7 7' fill='none' stroke='%23000' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M9 5l7 7-7 7' fill='none' stroke='%23000' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat}
.chev-l{transform:rotate(180deg)}.chev-d{transform:rotate(90deg)}

/* estado: punto + texto */
.badge{display:inline-flex;align-items:center;gap:6px;font-size:var(--t-13);font-weight:500;line-height:1.3;color:var(--ink-2);white-space:normal;text-align:left}
.badge::before{content:"";width:8px;height:8px;border-radius:50%;background:currentColor;flex:none}
.badge-ok{color:var(--ok)}.badge-warn{color:var(--warn)}.badge-bad{color:var(--bad)}.badge-navy,.badge-info{color:var(--info)}.badge-neutral{color:var(--mute)}
.tag{display:inline-flex;align-items:center;padding:2px 8px;border-radius:var(--r-sm);font-size:var(--t-12);font-weight:600;background:var(--surface-2);color:var(--ink-2);border:1px solid var(--line);white-space:normal;max-width:100%;overflow-wrap:anywhere}
.tag-warn{background:var(--warn-50);color:var(--warn);border-color:transparent}.tag-info{background:var(--info-50);color:var(--info);border-color:transparent}
.count{display:inline-flex;align-items:center;justify-content:center;min-width:20px;height:20px;padding:0 6px;border-radius:var(--r-sm);background:var(--surface-2);color:var(--ink-2);font-size:var(--t-12);font-weight:600}
.tab.on .count,[aria-selected=true] .count{background:var(--navy-50);color:var(--navy)}

/* franja de resumen */
.summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));background:var(--surface);border:1px solid var(--line);border-radius:var(--r)}
.sum-item{display:flex;flex-direction:column;gap:2px;padding:16px 20px;border-left:1px solid var(--line);min-width:0;text-align:left;font:inherit;color:inherit;background:none;border-top:0;border-right:0;border-bottom:0;text-decoration:none}
.sum-item:first-child{border-left:0}
button.sum-item,a.sum-item{cursor:pointer;transition:background var(--dur-1) var(--ease)}button.sum-item:hover,a.sum-item:hover{background:var(--surface-2);color:inherit}
.sum-item[aria-pressed=true]{background:var(--navy-50);box-shadow:inset 0 -2px 0 var(--navy)}
.sum-label{font-size:var(--t-13);color:var(--mute);font-weight:500}
.sum-value{font-size:var(--t-24);font-weight:500;font-variant-numeric:tabular-nums;line-height:1.25;color:var(--ink);overflow-wrap:anywhere}
.sum-sub{font-size:var(--t-13);color:var(--mute)}.sum-sub.is-bad{color:var(--bad)}.sum-sub.is-warn{color:var(--warn)}
.sum-sub.is-bad::before,.sum-sub.is-warn::before{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;background:currentColor;margin-right:6px;vertical-align:1px}
/* compatibilidad: kpi suelto */
.kpi-label{font-size:var(--t-13);color:var(--mute)}.kpi-value{font-size:var(--t-24);font-weight:500;font-variant-numeric:tabular-nums}.kpi-sub{font-size:var(--t-13);color:var(--mute)}

/* formularios */
.field{display:flex;flex-direction:column;gap:6px;font-size:var(--t-13);color:var(--ink-2);font-weight:500;min-width:0}
.field label{font-weight:500;color:var(--ink);font-size:var(--t-13)}.field label em{color:var(--red);font-style:normal;margin-left:2px}
.field-head{display:flex;flex-direction:column;gap:2px}
/* dirección con Google Maps */
.field-span{grid-column:1/-1}
.gmap{border:1px solid var(--line);border-radius:var(--r);background:var(--surface);overflow:hidden;display:flex;flex-direction:column}
.gmap-search{display:flex;gap:8px;align-items:center;padding:10px;border-bottom:1px solid var(--line)}.gmap-search .ctl{flex:1;min-width:0}.gmap-search .cico{flex:0 0 auto}
.gmap-canvas{position:relative;height:220px;background:#EEF0EA;overflow:hidden}
.gmap-road{position:absolute;background:#fff;border:1px solid #E1E3DC}
.gmap-road.r1{left:0;right:0;top:48%;height:14px}.gmap-road.r2{top:0;bottom:0;left:38%;width:12px}.gmap-road.r3{top:0;bottom:0;left:72%;width:8px}
.gmap-park{position:absolute;left:44%;top:12%;width:24%;height:34%;background:#D9E8CF;border-radius:6px}
.gmap-pin{position:absolute;left:55%;top:52%;transform:translate(-50%,-100%);color:var(--navy);cursor:grab}.gmap-pin svg{width:32px;height:32px}
.gmap-label{position:absolute;left:46%;top:16%;font-size:var(--t-13);color:var(--mute)}
.gmap-attrib{position:absolute;right:8px;bottom:6px;font-size:11px;color:var(--mute)}
.gmap-foot{display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center;padding:10px;font-size:var(--t-13)}.gmap-foot .field-hint{flex:1 1 240px}
@media (max-width:600px){.gmap-canvas{height:160px}}
.mod.is-new{animation:wizin var(--dur-2) var(--ease)}
.field-hint.is-warn{color:var(--warn)}
.review-facts{padding:4px 0}
.wf-row.is-new{background:var(--ok-50)}
@media print{.sidebar,.topbar,.ai-fab,.ai-panel,.form-foot,.filters,.filters-actions,.back,#wf-toast,dialog,.page-actions,.btn,.seg,.tabs{display:none !important}.main{padding:0}.card,.tbl-wrap{break-inside:avoid;border:0}body{background:#fff}.wf-table{font-size:11px}.panel[hidden]{display:none}}
.field-hint{font-size:var(--t-13);color:var(--mute);font-weight:400;order:3}
.ctl{min-height:var(--hit);padding:0 12px;border:1px solid var(--line-strong);border-radius:var(--r);font:inherit;font-size:var(--t-14);font-weight:400;background:var(--surface);color:var(--ink);width:100%;transition:box-shadow var(--dur-1) var(--ease)}
.ctl:focus{outline:none;box-shadow:var(--focus)}.ctl[aria-invalid=true]{border-color:var(--bad)}
.field-error{color:var(--bad);font-size:var(--t-13);font-weight:400}
textarea.ctl{padding:10px 12px;resize:vertical;min-height:88px}select.ctl{appearance:auto}
.ctl-file{display:flex;align-items:center;justify-content:space-between;gap:12px;cursor:pointer;color:var(--mute)}.ctl-file b{font-weight:500;color:var(--navy)}
.form-grid{display:grid;gap:16px 24px;align-items:start}.cols-1{grid-template-columns:minmax(0,1fr)}.cols-2{grid-template-columns:repeat(2,minmax(0,1fr))}.cols-3{grid-template-columns:repeat(3,minmax(0,1fr))}.cols-4{grid-template-columns:repeat(4,minmax(0,1fr))}
.form-foot{display:flex;gap:8px;align-items:center;flex-wrap:wrap;position:sticky;bottom:0;background:var(--surface);border-top:1px solid var(--line);padding:12px 24px;margin:0 -32px -120px;z-index:15;box-shadow:0 -8px 24px rgba(22,24,29,.06)}
.form-foot .btn-primary{order:10;margin-left:auto}
.upload{border:1px dashed var(--line-strong);border-radius:var(--r);padding:20px;display:flex;flex-direction:column;align-items:flex-start;gap:6px;font-size:var(--t-14);width:100%;background:var(--surface)}.upload label{font-weight:500}
.upload .kpi-sub{font-size:var(--t-13)}

/* filtros */
.filters{display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end;position:relative}
.filters>.field{min-width:160px}
.filters>.field:has(input[type=search]){flex:1 1 240px;min-width:240px;max-width:420px}
.filters-actions{margin-left:auto;display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.btn-more{align-self:flex-end}
.btn-more[aria-expanded=true]{background:var(--navy-50);border-color:var(--navy);color:var(--navy)}
.filters-more{position:absolute;top:calc(100% + 8px);left:0;z-index:25;background:var(--surface);border:1px solid var(--line);border-radius:var(--r-lg);box-shadow:var(--shadow-pop);padding:16px;display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end;max-width:min(720px,calc(100vw - 32px))}
.filters-more[hidden]{display:none}
.chips-active{flex-basis:100%;display:flex;flex-wrap:wrap;gap:8px;align-items:center;min-height:0}
.chips-active:empty{display:none}
.fchip{display:inline-flex;align-items:center;gap:6px;min-height:32px;padding:0 4px 0 10px;border:1px solid var(--line-strong);border-radius:var(--r-sm);background:var(--surface);font:inherit;font-size:var(--t-13);color:var(--ink);cursor:pointer}
.fchip b{font-weight:600}.fchip span{display:inline-flex;width:24px;height:24px;align-items:center;justify-content:center;color:var(--mute);font-size:16px}
.fchip:hover{background:var(--surface-2)}
.fclear{background:none;border:0;color:var(--navy);font:inherit;font-size:var(--t-13);cursor:pointer;min-height:32px;text-decoration:underline}
.result-count{font-size:var(--t-13);color:var(--mute)}

/* tablas */
.tbl-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:var(--r);background:var(--surface)}
.tbl{display:grid;min-width:min(100%,640px)}
.wf-row{display:contents}.wf-row[hidden]{display:none}
.td-hide{display:none!important}
.th{padding:0 16px;min-height:40px;display:flex;align-items:center;font-weight:600;font-size:var(--t-12);color:var(--mute);text-transform:uppercase;letter-spacing:.04em;border-bottom:1px solid var(--line);background:var(--surface)}
.td{padding:12px 16px;min-height:48px;font-size:var(--t-14);border-bottom:1px solid var(--line);display:flex;align-items:center;min-width:0;overflow-wrap:normal;word-break:normal;transition:background var(--dur-1) var(--ease)}
.td.td-wide{overflow-wrap:anywhere}
.wf-row:hover .td{background:var(--surface-2)}
.wf-row[data-href] .td{cursor:pointer}
.wf-row[data-href]:focus-within .td{background:var(--navy-50)}
.wf-row:last-of-type .td{border-bottom:0}
.td.is-num{justify-content:flex-end;font-family:var(--font-mono);font-size:var(--t-13)}
.c2{display:flex;flex-direction:column;gap:2px;min-width:0}.c2>span{font-weight:500}.c2 small{color:var(--mute);font-size:var(--t-13);line-height:1.4}
.row-go{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:var(--r);color:var(--mute);text-decoration:none}
.row-go:hover{background:var(--navy-50);color:var(--navy)}
.row-link{display:inline-flex;align-items:center;gap:6px;font-weight:500;text-decoration:none;white-space:nowrap}.row-link:hover{text-decoration:underline}
.wf-empty{padding:24px;text-align:center;color:var(--mute)}
.pager{display:flex;align-items:center;gap:12px;font-size:var(--t-13);color:var(--mute);flex-wrap:wrap}.pages{margin-left:auto;display:flex;gap:4px}
.pg{min-width:40px;min-height:40px;padding:0 8px;border:1px solid var(--line);border-radius:var(--r);text-decoration:none;color:var(--ink);background:var(--surface);display:inline-flex;align-items:center;justify-content:center}.pg.on{background:var(--navy-50);color:var(--navy);border-color:var(--navy);font-weight:600}
.chk{width:18px;height:18px;accent-color:var(--navy)}

/* pestañas */
.tabs{display:flex;flex-wrap:wrap;gap:4px;border-bottom:1px solid var(--line);align-items:flex-end;position:relative}
.tab{display:inline-flex;align-items:center;gap:8px;min-height:var(--hit);padding:0 12px;font:inherit;font-size:var(--t-14);color:var(--ink-2);background:none;border:0;border-bottom:2px solid transparent;margin-bottom:-1px;cursor:pointer;text-decoration:none;font-weight:500;white-space:nowrap;transition:color var(--dur-1) var(--ease)}
.tab:hover{color:var(--ink)}.tab.on{color:var(--navy);border-bottom-color:var(--navy);font-weight:600}
.tab-more{position:relative;display:inline-flex}.tab-more .menu-pop{left:0;right:auto}
.panel{flex-direction:column;gap:24px}
.seg{display:inline-flex;align-self:flex-start;max-width:100%;flex-wrap:wrap;border:1px solid var(--line-strong);border-radius:var(--r);overflow:hidden;background:var(--surface)}
.seg button{min-height:40px;padding:0 14px;border:0;border-left:1px solid var(--line);background:none;font:inherit;font-size:var(--t-14);color:var(--ink-2);cursor:pointer;display:inline-flex;align-items:center;gap:6px}
.seg button:first-child{border-left:0}.seg button[aria-checked=true]{background:var(--navy-50);color:var(--navy);font-weight:600}
.seg-panel[hidden]{display:none}
.quick{display:flex;align-self:flex-start;flex-wrap:wrap;gap:8px;align-items:center}
.quick .q{min-height:40px;padding:0 12px;border:1px solid var(--line-strong);border-radius:var(--r-sm);background:var(--surface);font:inherit;font-size:var(--t-13);color:var(--ink-2);cursor:pointer}
.quick .q[aria-pressed=true]{background:var(--navy-50);border-color:var(--navy);color:var(--navy);font-weight:600}
.bulk{display:flex;align-items:center;gap:12px;flex-wrap:wrap;font-size:var(--t-13);color:var(--mute)}

/* kv y cabecera de detalle */
.kv{display:flex;flex-wrap:wrap;gap:8px 24px;font-size:var(--t-14);align-items:baseline}.kv .k{color:var(--mute)}.kv b{font-weight:500;overflow-wrap:anywhere}.kv>span{min-width:0;max-width:100%}
.hero{gap:20px}
.hero-top{display:flex;flex-wrap:wrap;align-items:center;gap:12px 16px}
.hero-tag{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.hero-code{font-family:var(--font-mono);font-weight:500;font-size:var(--t-16);color:var(--ink)}
.hero-actions{display:flex;flex-wrap:wrap;gap:8px;margin-left:auto;align-items:center}
.facts{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:16px 24px;margin:0}
.fact{min-width:0;margin:0}.fact dt{font-size:var(--t-13);color:var(--mute);margin-bottom:2px}.fact dd{margin:0;font-weight:500;font-size:var(--t-14);overflow-wrap:anywhere}
.prog{display:flex;flex-direction:column;gap:6px;font-size:var(--t-13);color:var(--ink-2)}.prog-head{display:flex;justify-content:space-between;gap:12px}.prog-head b{font-weight:500;font-variant-numeric:tabular-nums}
.prog-track{height:6px;background:var(--surface-2);border-radius:3px;overflow:hidden}.prog-fill{height:100%;border-radius:3px;transition:width var(--dur-2) var(--ease)}
.td .prog{min-width:90px;width:100%}
.list{margin:0;padding-left:18px;font-size:var(--t-14);line-height:1.8}
.note{display:none}

/* pasos de proceso (reemplaza pastillas con flechas) */
.proc{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;counter-reset:proc}
.proc li{position:relative;display:grid;grid-template-columns:28px 1fr auto;gap:2px 12px;padding:0 0 16px;counter-increment:proc;align-items:start}
.proc li::before{content:counter(proc);width:28px;height:28px;border-radius:50%;border:1px solid var(--line-strong);background:var(--surface);color:var(--ink-2);font-size:var(--t-13);font-weight:600;display:inline-flex;align-items:center;justify-content:center;grid-row:span 2;position:relative;z-index:1}
.proc li:not(:last-child)::after{content:"";position:absolute;left:13.5px;top:28px;bottom:0;width:1px;background:var(--line)}
.proc li:last-child{padding-bottom:0}
.proc .p-t{font-weight:600;font-size:var(--t-14);padding-top:3px}.proc .p-d{grid-column:2;font-size:var(--t-13);color:var(--mute)}.proc .p-s{grid-row:1;grid-column:3;font-size:var(--t-13);padding-top:3px}
.proc li.is-done::before{background:var(--navy);border-color:var(--navy);color:#fff}
.proc li.is-now::before{border:2px solid var(--navy);color:var(--navy)}
.proc-h{flex-direction:row;gap:0}.proc-h li{flex:1;grid-template-columns:28px 1fr;padding:0 16px 0 0}
.proc-h li:not(:last-child)::after{left:36px;right:16px;top:14px;bottom:auto;width:auto;height:1px}
.proc-h .p-t{background:var(--bg);padding-right:8px;position:relative;z-index:1;justify-self:start}
.card .proc-h .p-t{background:var(--surface)}

/* asistente de pasos (wizard) */
.wizard{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:24px;align-items:start}
.wizard>.wiz-main{min-width:0;display:flex;flex-direction:column;gap:24px}
.stepper{list-style:none;margin:0;padding:0;display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:0}
.stepper li{position:relative}
.stepper li:not(:last-child)::after{content:"";position:absolute;top:22px;left:calc(50% + 22px);right:calc(-50% + 22px);height:2px;background:var(--line)}
.stepper li.is-done:not(:last-child)::after{background:var(--navy)}
.stepper button{display:flex;flex-direction:column;align-items:center;gap:8px;width:100%;background:none;border:0;font:inherit;color:var(--mute);cursor:pointer;padding:0 4px;min-height:var(--hit)}
.stepper button:disabled{cursor:default}
.stepper .s-n{width:44px;height:44px;border-radius:50%;border:1px solid var(--line-strong);background:var(--surface);display:inline-flex;align-items:center;justify-content:center;font-weight:600;font-size:var(--t-14);color:var(--mute);position:relative;z-index:1;transition:all var(--dur-2) var(--ease)}
.stepper .s-n svg{width:20px;height:20px;stroke:#fff;fill:none;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
.stepper .s-t{font-size:var(--t-13);text-align:center;line-height:1.3;font-weight:500}
.stepper li.is-done .s-n{background:var(--navy);border-color:var(--navy)}
.stepper li.is-done .s-t{color:var(--ink-2)}
.stepper li[aria-current=step] .s-n{border:2px solid var(--navy);color:var(--navy)}
.stepper li[aria-current=step] .s-t{color:var(--ink);font-weight:600}
.stepper li.is-error .s-n{border:2px solid var(--bad);color:var(--bad)}
.stepper li.is-error .s-t::after{content:" · Revisar";color:var(--bad)}
.wiz-progress{height:3px;margin-top:14px;background:var(--surface-2);border-radius:2px;overflow:hidden}.wiz-progress i{display:block;height:100%;background:var(--navy);transition:width var(--dur-2) var(--ease)}
.wiz-mobile{display:none;align-items:center;gap:12px;font-size:var(--t-14)}.wiz-mobile b{font-weight:600}
.wiz-step{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:24px;display:flex;flex-direction:column;gap:24px}
.wizard.is-on .wiz-step{display:none}.wizard.is-on .wiz-step.on{display:flex;animation:wizin var(--dur-2) var(--ease)}
@keyframes wizin{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
.wiz-step>h3{margin:0;font-size:var(--t-20);font-weight:600;outline:none}
.wiz-step>h3 small{display:block;font-size:var(--t-14);color:var(--mute);font-weight:400;margin-top:4px}
.wiz-summary{position:sticky;top:84px;background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:0}
.wiz-summary>summary{list-style:none;padding:16px 20px;font-weight:600;font-size:var(--t-16);cursor:default;display:flex;justify-content:space-between;gap:8px}
.wiz-summary>summary::-webkit-details-marker{display:none}
.wiz-sum-body{padding:0 20px 20px;display:flex;flex-direction:column;gap:12px;font-size:var(--t-14)}
.wiz-sum-body dl{margin:0;display:grid;grid-template-columns:1fr auto;gap:6px 12px}.wiz-sum-body dt{color:var(--mute)}.wiz-sum-body dd{margin:0;text-align:right;font-weight:500;font-variant-numeric:tabular-nums}
.wiz-sum-body hr{border:0;border-top:1px solid var(--line);margin:4px 0}
.wiz-sum-body .tot dd{font-size:var(--t-20)}
.wiz-saved{font-size:var(--t-13);color:var(--mute)}
.review{display:flex;flex-direction:column}.review>div{display:grid;grid-template-columns:200px 1fr auto;gap:12px;padding:12px 0;border-bottom:1px solid var(--line);align-items:start}.review>div:last-child{border-bottom:0}.review dt{color:var(--mute);font-size:var(--t-13)}.review dd{margin:0}
/* paso clásico (lista vertical, p. ej. constructor de reportes) */
.step{display:flex;gap:16px;padding:20px 0;border-top:1px solid var(--line)}.step:first-child{border-top:0;padding-top:0}
.step-n{flex:none;width:28px;height:28px;border-radius:50%;border:1px solid var(--navy);color:var(--navy);font-weight:600;display:inline-flex;align-items:center;justify-content:center;font-size:var(--t-13)}
.step-body{flex:1;min-width:0;display:flex;flex-direction:column;gap:16px}.step-body h3{margin:0;font-size:var(--t-16);display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}.step-body h3 small{font-size:var(--t-13);color:var(--mute);font-weight:400}
/* módulos seleccionables (paso 2) */
.mod-group{border:1px solid var(--line);border-radius:var(--r);overflow:hidden}
.mod-group>header{padding:10px 16px;background:var(--surface-2);font-size:var(--t-13);font-weight:600;color:var(--ink-2)}
.mod{display:grid;grid-template-columns:110px minmax(0,1fr) auto;gap:4px 16px;align-items:start;min-height:68px;padding:12px 16px;border-top:1px solid var(--line)}
.mod>:nth-child(1){grid-row:span 2}.mod>:nth-child(3){grid-column:2;grid-row:2}.mod>:nth-child(4){grid-column:3;grid-row:2;text-align:right}.mod>:nth-child(5){grid-column:3;grid-row:1;text-align:right}
.mod .mono{white-space:nowrap}.mod>:nth-child(3) small,.mod>:nth-child(4) small{display:inline;margin-left:6px}
.mod:first-of-type{border-top:0}
.mod .m-n b{display:block;font-weight:600}.mod .m-n small,.mod small{color:var(--mute);font-size:var(--t-13);display:block}
.mod .code{font-size:var(--t-13)}
/* libro contable */
.ledger{display:grid;grid-template-columns:minmax(180px,1fr) max-content max-content max-content;border:1px solid var(--line);border-radius:var(--r);overflow:hidden;background:var(--surface)}
.ledger>div{padding:12px 16px;border-bottom:1px solid var(--line);font-size:var(--t-14)}
.ledger .lh{font-size:var(--t-12);font-weight:600;color:var(--mute);text-transform:uppercase;letter-spacing:.04em;padding-top:10px;padding-bottom:10px}
.ledger .n{text-align:right;font-family:var(--font-mono);font-size:var(--t-13);white-space:nowrap}
.ledger .lt{border-top:3px double var(--ink-2);border-bottom:0;font-weight:600}
.ledger small{display:block;color:var(--mute);font-size:var(--t-13)}

/* franja de etapas (embudo) */
.stages{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));background:var(--surface);border:1px solid var(--line);border-radius:var(--r)}
.stages-head{grid-column:1/-1;display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding:12px 20px;border-bottom:1px solid var(--line);font-size:var(--t-14)}
.stages-head b{font-weight:600}
.stage{display:flex;flex-direction:column;gap:4px;padding:16px 20px;border:0;border-left:1px solid var(--line);background:none;font:inherit;color:inherit;text-align:left;cursor:pointer;min-height:var(--hit)}
.stages-head+.stage{border-left:0}
.stage:hover{background:var(--surface-2)}.stage[aria-pressed=true]{background:var(--navy-50);box-shadow:inset 0 -2px 0 var(--navy)}
.stage .st-name{display:inline-flex;align-items:center;gap:8px;font-weight:500;font-size:var(--t-14)}
.stage .st-name i{width:8px;height:8px;border-radius:50%;background:var(--sc,var(--mute))}
.stage .st-count{font-size:var(--t-24);font-weight:500;font-variant-numeric:tabular-nums}
.stage .st-rate{font-size:var(--t-13);color:var(--mute)}
.sync-ok{display:inline-flex;align-items:center;gap:6px;color:var(--ok);font-size:var(--t-13)}.sync-ok::before{content:"";width:8px;height:8px;border-radius:50%;background:currentColor}

/* gráficos */
.hbars{display:flex;flex-direction:column;gap:10px}.hbar{display:grid;grid-template-columns:minmax(100px,160px) 1fr 56px;gap:12px;align-items:center;font-size:var(--t-14)}.hbar-track{height:8px;background:var(--surface-2);border-radius:2px;overflow:hidden}.hbar-fill{height:100%;background:var(--navy);border-radius:2px}.hbar b{text-align:right;font-weight:500;font-variant-numeric:tabular-nums}
.chart{display:flex;flex-direction:column;gap:10px}.vbars{display:flex;gap:8px;padding:18px 0 6px;position:relative;align-items:flex-end}
.yaxis{position:absolute;left:0;top:18px;bottom:28px;display:flex;flex-direction:column;justify-content:space-between;font-size:var(--t-12);color:var(--mute)}.vbars.axed{padding-left:32px}
.vgroup{display:flex;flex-direction:column;align-items:center;gap:8px;flex:1;min-width:0}.vbars-stack{display:flex;align-items:flex-end;gap:4px}.vbar{width:22px;border-radius:2px 2px 0 0;position:relative}.vbar span{position:absolute;top:-18px;left:50%;transform:translateX(-50%);font-size:var(--t-12);color:var(--mute)}
.vlabel{font-size:var(--t-12);color:var(--mute);text-align:center}
.sbar{position:relative;width:26px}.sbar-track{position:absolute;inset:0;background:var(--surface-2);border-radius:2px}.sbar-fill{position:absolute;left:0;right:0;bottom:0;display:flex;flex-direction:column-reverse;gap:1px;overflow:hidden;border-radius:2px}
.legend{display:flex;flex-wrap:wrap;gap:16px;font-size:var(--t-13);color:var(--mute)}.leg{display:inline-flex;align-items:center;gap:6px}.leg i{width:10px;height:10px;border-radius:2px;display:inline-block}
.funnel{display:flex;flex-direction:column;gap:8px}.funnel-row{display:flex;align-items:center;gap:12px;font-size:var(--t-14)}.funnel-bar{min-width:72px;color:#fff;padding:8px 12px;font-weight:500;border-radius:var(--r-sm);font-variant-numeric:tabular-nums}
.stack{display:flex;height:10px;border-radius:2px;overflow:hidden;gap:2px;background:var(--surface-2)}
.gauge{display:flex;flex-direction:column;align-items:center;gap:2px;min-width:0}.gauge svg{max-width:100%}.gauges{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:6px}

/* ruta de niveles (portal) */
.route{list-style:none;margin:0;padding:0;display:flex;gap:6px}
.route li{display:flex;flex-direction:column;gap:6px;min-width:0}
.route .r-bar{height:8px;border-radius:2px;background:var(--line);overflow:hidden;position:relative}
.route .r-bar i{display:block;height:100%;background:var(--navy)}
.route .is-done .r-bar{background:var(--ok)}
.route .is-paid .r-bar{background:none;border:1px dashed var(--line-strong);height:8px}
.route .r-name{display:flex;align-items:center;gap:6px;font-weight:600;font-size:var(--t-14)}
.route .r-name svg{width:14px;height:14px;stroke:var(--ok);fill:none;stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round}
.route .r-det{font-size:var(--t-13);color:var(--mute)}
.route .is-now .r-name{color:var(--navy)}
.route .r-here{font-size:var(--t-12);font-weight:600;color:var(--navy);text-transform:uppercase;letter-spacing:.04em}
.route .is-todo .r-name{color:var(--mute);font-weight:500}
.route .r-paid{color:var(--ink-2)}
.level-big{font-family:var(--font-display);font-size:var(--t-32);font-weight:600;line-height:1;color:var(--navy)}
.prog-top{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:32px;align-items:start}
.prog-who{display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;margin-bottom:20px}
.prog-who .p-prog{font-size:var(--t-14);color:var(--mute)}
.stat-line{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;margin-top:20px;padding-top:16px;border-top:1px solid var(--line)}
.stat-line div{display:flex;flex-direction:column}.stat-line span{font-size:var(--t-13);color:var(--mute)}.stat-line b{font-size:var(--t-20);font-weight:500;font-variant-numeric:tabular-nums}
.next-class{border-left:1px solid var(--line);padding-left:32px;display:flex;flex-direction:column;gap:8px}
.next-class .nc-when{font-family:var(--font-display);font-size:var(--t-24);font-weight:600}
.checklist{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px}
.checklist li{display:flex;align-items:center;gap:10px;font-size:var(--t-14)}
.checklist svg{width:18px;height:18px;stroke:var(--ok);fill:none;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round;flex:none}
.opts{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;border:0;margin:0;padding:0}
.opt{display:flex;gap:12px;align-items:flex-start;padding:16px;border:1px solid var(--line-strong);border-radius:var(--r);background:var(--surface);cursor:pointer;min-height:var(--hit)}
.opt input{margin-top:3px;accent-color:var(--navy);width:18px;height:18px}
.opt b{display:block;font-weight:600}.opt small{display:block;color:var(--mute);font-size:var(--t-13)}
.opts[disabled] .opt,.opt.is-disabled{background:var(--surface-2);color:var(--mute);cursor:not-allowed;border-color:var(--line)}
.why{font-size:var(--t-13);color:var(--mute)}

/* tareas (inicio) */
.tasks{list-style:none;margin:0;padding:0;border:1px solid var(--line);border-radius:var(--r);background:var(--surface)}
.tasks li{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:16px;align-items:center;padding:12px 20px;border-top:1px solid var(--line);min-height:56px}
.tasks li:first-child{border-top:0}
.tasks a{font-weight:500;text-decoration:none}.tasks a:hover{text-decoration:underline}.tasks small{display:block;color:var(--mute);font-size:var(--t-13)}
.hero-number{display:flex;flex-direction:column;gap:4px}.hero-number .hn-label{font-size:var(--t-14);color:var(--mute)}.hero-number .hn-value{font-size:40px;font-weight:500;font-variant-numeric:tabular-nums;line-height:1.1}.hero-number .hn-sub{font-size:var(--t-14);color:var(--ok)}

/* ficha / perfil */
.profile{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);overflow:hidden;display:flex;flex-direction:column}
.profile-cover{display:none}
.profile-body{padding:24px;display:flex;flex-direction:column;align-items:flex-start;gap:8px;text-align:left}
.profile h2{margin:6px 0 0;font-size:var(--t-20);font-family:var(--font-display)}.profile .actions{display:flex;gap:8px;width:100%;margin-top:6px;flex-wrap:wrap}.profile .actions .btn{flex:1}
.profile .section{width:100%;text-align:left;margin-top:12px;padding-top:16px;border-top:1px solid var(--line)}.profile .section h3{margin:0 0 10px;font-size:var(--t-14)}
.clist{display:flex;flex-direction:column;gap:10px;font-size:var(--t-14)}.clist div{display:flex;gap:12px;align-items:center}
.cico{width:32px;height:32px;border-radius:var(--r);background:var(--surface-2);color:var(--ink-2);display:inline-flex;align-items:center;justify-content:center;flex:none}.cico svg{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}.clist b{display:block;color:var(--mute);font-weight:400;font-size:var(--t-13)}
.awards{display:flex;flex-direction:column;gap:8px;font-size:var(--t-14)}.awards div{display:flex;gap:10px;align-items:center}.awards i{width:8px;height:8px;border-radius:50%;background:var(--ok);flex:none;font-size:0}
.hours{display:flex;align-items:baseline;gap:6px}.hours b{font-size:28px;font-weight:500}.hours span{color:var(--mute);font-size:var(--t-14)}
.chips{display:flex;flex-wrap:wrap;gap:12px}.chip{padding:10px 12px;border:1px solid var(--line);border-radius:var(--r);font-size:var(--t-13);color:var(--mute);flex:1;min-width:120px;background:var(--surface)!important}.chip b{display:block;font-size:var(--t-14);color:var(--ink)}
.perf{display:flex;gap:20px;align-items:center;flex-wrap:wrap}.perf-legend{display:flex;flex-direction:column;gap:8px;font-size:var(--t-14);flex:1;min-width:180px}.perf-legend div{display:flex;align-items:center;gap:8px}.perf-legend i{width:8px;height:8px;border-radius:50%;display:inline-block}.perf-legend b{margin-left:auto;font-weight:500;color:var(--ink-2)}
.trend{position:relative;border-top:1px solid var(--line);padding:48px 0 0}.trend .big{position:absolute;left:0;top:12px;font-size:var(--t-13);color:var(--mute)}.trend .big b{font-size:var(--t-20);color:var(--ink);font-weight:500}.trend .big .up{color:var(--ok);font-size:var(--t-13);margin-left:6px;font-weight:500}
.quote{border-left:2px solid var(--yellow);padding:4px 0 4px 14px;font-size:var(--t-14);line-height:1.5;color:var(--ink-2)}
.course{display:grid;grid-template-columns:40px minmax(170px,2fr) 90px 52px max-content 64px;gap:16px;align-items:center;padding:12px 0;border-bottom:1px solid var(--line);font-size:var(--t-14)}.course:last-child{border-bottom:0}
.course-ico{width:40px;height:40px;border-radius:var(--r);display:inline-flex;align-items:center;justify-content:center;background:var(--surface-2)!important;color:var(--ink-2)!important}.course-ico svg{width:20px;height:20px;stroke:currentColor;fill:none;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
.course-name a{font-weight:600;text-decoration:none}.course-name small{display:block;color:var(--mute);margin-top:2px;font-size:var(--t-13)}
.course-meta{display:flex;flex-direction:column;gap:4px;color:var(--mute);font-size:var(--t-13)}.course-meta span{display:inline-flex;align-items:center;gap:5px}.course-meta svg{width:14px;height:14px;stroke:currentColor;fill:none;stroke-width:2}
.course-state{display:flex;flex-direction:column;align-items:flex-start;gap:4px}.course-state small{color:var(--mute);font-size:var(--t-12);text-transform:uppercase;letter-spacing:.04em;margin-top:2px}
.course-grade{font-size:var(--t-16);font-weight:500;font-variant-numeric:tabular-nums}.course-grade small{color:var(--mute);font-weight:400;font-size:var(--t-13)}
.journey-stats .kv{display:grid;grid-template-columns:repeat(4,minmax(0,1fr))}

/* constructor de reportes */
.picker-areas{display:flex;flex-direction:column;gap:16px}.pick-area h4{margin:0 0 8px;font-size:var(--t-12);letter-spacing:.04em;text-transform:uppercase;color:var(--mute);font-weight:600}
.picker{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}
.pick{display:flex;flex-direction:column;align-items:flex-start;gap:6px;text-align:left;padding:14px 16px;border-radius:var(--r);border:1px solid var(--line-strong);background:var(--surface);font:inherit;cursor:pointer;color:var(--ink);min-height:104px}
.pick b{font-size:var(--t-14);line-height:1.3}.pick small{font-size:var(--t-13);color:var(--mute);line-height:1.4}.pick:hover{background:var(--surface-2)}.pick.on{border-color:var(--navy);background:var(--navy-50);box-shadow:inset 0 0 0 1px var(--navy)}
.pick-ico{width:20px;height:20px;color:var(--navy)}.pick-ico svg{width:20px;height:20px;stroke:currentColor;fill:none;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
.pills{display:inline-flex;flex-wrap:wrap;border:1px solid var(--line-strong);border-radius:var(--r);overflow:hidden}
.pill{min-height:40px;padding:0 14px;border:0;border-left:1px solid var(--line);background:var(--surface);font:inherit;font-size:var(--t-14);color:var(--ink-2);cursor:pointer}.pill:first-child{border-left:0}.pill:hover{background:var(--surface-2)}.pill.on{background:var(--navy-50);color:var(--navy);font-weight:600}
.pill-row{display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin-top:12px}.pill-row>span{font-size:var(--t-13);color:var(--mute);min-width:64px}
.plain{margin:0;font-size:var(--t-16);line-height:1.6;border-left:2px solid var(--navy);padding:4px 0 4px 16px}
.saved-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}
.saved{display:flex;flex-direction:column;gap:4px;padding:16px;border-radius:var(--r);border:1px solid var(--line);text-decoration:none;color:var(--ink);background:var(--surface)}.saved:hover{border-color:var(--navy);background:var(--surface-2)}
.saved b{font-size:var(--t-14)}.saved small{font-size:var(--t-13);color:var(--mute)}.saved-meta{display:inline-flex;align-items:center;gap:6px;font-size:var(--t-13);color:var(--navy);margin-top:6px}.saved-meta .nav-ico,.saved-meta .nav-ico svg{width:14px;height:14px}.saved-old{font-size:var(--t-12);color:var(--mute)}
.calc{display:flex;flex-direction:column}.calc-row{display:flex;align-items:center;gap:16px;padding:12px 0;border-bottom:1px solid var(--line)}.calc-row:last-child{border-bottom:0}
.calc-n{flex:none;width:28px;height:28px;border-radius:50%;border:1px solid var(--line-strong);color:var(--ink-2);font-weight:600;font-size:var(--t-13);display:inline-flex;align-items:center;justify-content:center}
.calc-txt{flex:1;min-width:0}.calc-txt b{display:block;font-size:var(--t-14)}.calc-txt small{display:block;color:var(--mute);font-size:var(--t-13);line-height:1.45;margin-top:2px}
.calc-amt{flex:none;font-family:var(--font-mono);font-size:var(--t-14);min-width:96px;text-align:right}
.calc-row.total{border-top:3px double var(--ink-2);border-bottom:0;margin-top:4px;padding-top:14px}.calc-row.total .calc-n{background:var(--navy);border-color:var(--navy);color:#fff}.calc-row.total .calc-amt{font-size:var(--t-20);color:var(--ink);font-weight:500}
.tree,.tree ul{list-style:none;margin:0;padding:0}.tree ul{margin-left:16px;border-left:1px solid var(--line);padding-left:16px}.tree li{margin:6px 0}
.tree-node{display:inline-flex;flex-direction:column;padding:8px 12px;border-radius:var(--r);border:1px solid var(--line);background:var(--surface);min-width:260px}.tree-node b{font-size:var(--t-14)}.tree-node small{color:var(--mute);font-size:var(--t-13)}
.tree>li>.tree-node{border-color:var(--navy);color:var(--navy)}
.cal{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:var(--r);overflow:hidden}.cal div{min-height:90px;padding:10px;font-size:var(--t-13);background:var(--surface)}

/* asistente */
.sched{display:flex;flex-direction:column;gap:12px}.ai-fab{position:fixed;right:24px;bottom:84px;width:52px;height:52px;border-radius:50%;border:0;background:var(--navy);color:#fff;box-shadow:var(--shadow-pop);cursor:pointer;display:flex;align-items:center;justify-content:center;z-index:40}
.ai-fab .nav-ico,.ai-fab .nav-ico svg{width:22px;height:22px}.ai-fab:hover{background:var(--navy-700)}.ai-fab.on{background:var(--ink)}
.ai-fab-dot{position:absolute;top:4px;right:4px;width:10px;height:10px;border-radius:50%;background:var(--yellow);border:2px solid #fff}
.ai-panel{position:fixed;right:24px;bottom:148px;width:380px;max-width:calc(100vw - 32px);max-height:min(620px,calc(100vh - 170px));background:var(--surface);border-radius:var(--r-lg);box-shadow:var(--shadow-pop);display:flex;flex-direction:column;z-index:40;overflow:hidden;border:1px solid var(--line)}
.ai-panel[hidden]{display:none}
.ai-panel-head{display:flex;align-items:center;gap:10px;padding:12px 16px;border-bottom:1px solid var(--line)}.ai-panel-head b{display:block;font-size:var(--t-14)}.ai-panel-head small{color:var(--mute);font-size:var(--t-13)}.ai-panel-head .icon-btn{margin-left:auto;font-size:20px}
.ai-spark{width:32px;height:32px;border-radius:var(--r);background:var(--navy-50);color:var(--navy);display:inline-flex;align-items:center;justify-content:center;flex:none}.ai-spark .nav-ico,.ai-spark svg{width:18px;height:18px}
.ai-log{flex:1;overflow:auto;padding:14px;display:flex;flex-direction:column;gap:10px;min-height:160px}.ai-log .msg{max-width:88%}.typing{color:var(--mute)}
.ai-chips{display:flex;flex-wrap:wrap;gap:6px;padding:0 14px 10px}
.chipq{border:1px solid var(--line-strong);background:var(--surface);border-radius:var(--r-sm);padding:6px 10px;font:inherit;font-size:var(--t-13);color:var(--ink-2);cursor:pointer;text-align:left;min-height:32px}.chipq:hover{background:var(--surface-2)}
.chipq-main{background:var(--navy)!important;color:#fff!important;border-color:var(--navy)!important;display:inline-flex;align-items:center;gap:6px}.chipq-main .nav-ico,.chipq-main .nav-ico svg{width:14px;height:14px}
.ai-in{display:flex;gap:8px;padding:12px 14px;border-top:1px solid var(--line)}
.btn-ask{border-style:dashed}
.chat{width:100%;background:var(--surface);border:1px solid var(--line);border-radius:var(--r);display:flex;flex-direction:column;height:calc(100vh - 220px);min-height:480px}.chat-log{flex:1;padding:18px;display:flex;flex-direction:column;gap:12px;overflow:auto}
.msg{max-width:min(70%,720px);padding:10px 14px;border-radius:var(--r-lg);font-size:var(--t-14);line-height:1.5}.msg.me{align-self:flex-end;background:var(--navy);color:#fff}.msg.bot{align-self:flex-start;background:var(--surface-2)}.chat-in{display:flex;gap:8px;padding:12px;border-top:1px solid var(--line)}

/* insights */
.insights{display:flex;flex-direction:column;border:1px solid var(--line);border-radius:var(--r);background:var(--surface)}
.insight{display:grid;grid-template-columns:140px 1fr;gap:16px;padding:16px 20px;border-top:1px solid var(--line)}.insight:first-child{border-top:0}
.insight-side{display:flex;flex-direction:column;gap:6px;align-items:flex-start}.insight-side small{color:var(--mute);font-size:var(--t-13)}
.insight-area{display:block;color:var(--mute);font-size:var(--t-12);text-transform:uppercase;letter-spacing:.04em;margin-bottom:4px;font-weight:600}
.insight-body b{display:block;font-size:var(--t-16);margin-bottom:4px;font-weight:600}.insight-body p{margin:0 0 12px;color:var(--ink-2);font-size:var(--t-14);line-height:1.55}
.insight-actions{display:flex;flex-wrap:wrap;gap:8px}

/* notificaciones */
.notif{position:relative}.notif-pop{width:360px;overflow:hidden}
.notif-head{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid var(--line);font-size:var(--t-14)}.notif-head a{font-size:var(--t-13);text-decoration:none;font-weight:600}
.notif-item{display:flex;gap:12px;align-items:flex-start;padding:12px 16px;text-decoration:none;color:var(--ink);border-bottom:1px solid var(--line)}.notif-item:last-child{border-bottom:0}.notif-item:hover{background:var(--surface-2)}.notif-item.read{color:var(--ink-2)}.notif-item.read b{font-weight:500}
.notif-item b{display:block;font-size:var(--t-14);font-weight:600;line-height:1.35}.notif-item small{color:var(--mute);font-size:var(--t-13)}
.notif-ico{flex:none;width:8px;height:8px;margin-top:7px;border-radius:50%;background:var(--mute)}
.notif-ico.nt-red{background:var(--bad)}.notif-ico.nt-yellow{background:var(--warn)}.notif-ico.nt-navy{background:var(--info)}.notif-ico.nt-green{background:var(--ok)}

/* diálogo, toast */
#wf-dialog{border:1px solid var(--line);border-radius:var(--r-lg);box-shadow:var(--shadow-pop);padding:24px;max-width:480px;font-family:var(--font-ui);color:var(--ink)}#wf-dialog::backdrop{background:rgba(22,24,29,.4)}
#wf-dialog h2{font-size:var(--t-20)!important}#wf-dialog p{color:var(--ink-2)!important}
#wf-toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:var(--ink);color:#fff;padding:12px 20px;border-radius:var(--r);font-size:var(--t-14);display:none;z-index:60;box-shadow:var(--shadow-pop)}

/* acceso y portal */
.auth{min-height:100vh;display:flex;align-items:center;justify-content:center;background:var(--bg);padding:24px}
.auth form{width:100%;max-width:420px;background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:32px;display:flex;flex-direction:column;gap:14px}
.auth h1{margin:4px 0 0;font-size:var(--t-24)!important;font-family:var(--font-display)}.auth label{font-size:var(--t-13);font-weight:500}
.auth .card{padding:16px}
.portal{min-height:100vh;background:var(--bg)}
.portal-top{display:flex;align-items:center;gap:16px;flex-wrap:wrap;padding:10px 32px;background:var(--surface);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
.portal-top img{height:36px;display:block}.portal-title{display:flex;flex-direction:column;min-width:0}.portal-title b{font-size:var(--t-16);font-family:var(--font-display)}.portal-title small{font-size:var(--t-13);color:var(--mute)}
.portal-user{margin-left:auto;display:flex;align-items:center;gap:10px;font-size:var(--t-14);flex-wrap:wrap;min-width:0}.portal-user span{display:flex;flex-direction:column;line-height:1.25}.portal-user small{color:var(--mute);font-size:var(--t-13)}
.portal-main{max-width:1180px;margin:0 auto;padding:24px 32px 80px;display:flex;flex-direction:column;gap:32px}
.section-title{margin:0;font-size:var(--t-16);font-weight:600}

/* hub */
.hub{max-width:1100px;margin:0 auto;padding:40px 24px}.hub h1{font-family:var(--font-display)}.hub-head p{color:var(--mute);font-size:var(--t-16);line-height:1.6;max-width:820px}
.hub section{margin-top:40px;border-top:1px solid var(--line);padding-top:24px}.hub h2{margin:0 0 4px;font-size:var(--t-20);color:var(--ink)}.hub section p{margin:0 0 16px;color:var(--mute);font-size:var(--t-14);max-width:820px}
.flow{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:0;border:1px solid var(--line);border-radius:var(--r);background:var(--surface);overflow:hidden}
.hub .card{border:0;border-radius:0;border-bottom:1px solid var(--line);border-right:1px solid var(--line);padding:14px 16px;gap:2px;text-decoration:none;color:var(--ink);font-weight:500;min-height:0}
.hub .card .num{font-size:var(--t-12);color:var(--mute);font-weight:400;font-family:var(--font-mono)}.hub .card:hover{background:var(--surface-2)}
.hub-foot{margin-top:60px;color:var(--mute);font-size:var(--t-13)}

/* ===== responsive ===== */
@media (max-width:1280px){.search{width:180px}}
@media (max-width:1180px){.user #rol-user{display:none}.wizard{grid-template-columns:minmax(0,1fr)}.wiz-summary{position:static}.wiz-summary>summary{cursor:pointer}.wiz-summary>summary::after{content:"Ver";color:var(--navy);font-weight:500;font-size:var(--t-14)}.wiz-summary[open]>summary::after{content:"Ocultar"}.prog-top{grid-template-columns:1fr}.next-class{border-left:0;padding-left:0;border-top:1px solid var(--line);padding-top:16px}}
@media (max-width:1024px){
  .topbar .menu-btn{display:inline-flex}
  .sidebar{position:fixed;left:0;top:0;bottom:0;z-index:50;transform:translateX(-105%);transition:transform var(--dur-2) var(--ease);box-shadow:var(--shadow-pop);width:280px}
  body.nav-open .sidebar{transform:none}
  body.nav-open .scrim{display:block;position:fixed;inset:0;background:rgba(22,24,29,.4);z-index:45}
  .search{width:auto;padding:0;border:0;background:none}.search input{display:none}.search svg{width:20px;height:20px}
  .search{width:40px;height:40px;justify-content:center;border-radius:var(--r)}.search:hover{background:var(--surface-2)}
  .topbar{padding:8px 24px}.main{padding:24px 24px 120px}.form-foot{margin:0 -24px -120px}
  .grid-2,.grid-r,.grid[style]{grid-template-columns:1fr!important}
  .cols-3,.cols-4{grid-template-columns:repeat(2,minmax(0,1fr))}
  .summary{grid-template-columns:repeat(2,minmax(0,1fr))}.sum-item{border-top:1px solid var(--line)}.sum-item:nth-child(-n+2){border-top:0}.sum-item:nth-child(odd){border-left:0}
  .course{grid-template-columns:40px 1fr 70px}.course>*:nth-child(n+4):not(.course-grade){display:none}
  .stat-line{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media (max-width:600px){
  .topbar{padding:8px 12px;gap:4px}.crumbs .back,.crumbs .sep,.crumbs .crumb-parent{display:none}
  .topbar .ctx-sede,.topbar .search,.topbar a.icon-btn{display:none}
  .sidebar-sede{display:flex;margin:0 0 12px}.sidebar-sede .ctx-sede{width:100%}.sidebar-sede select{flex:1}
  .main{padding:16px 16px 140px;gap:24px}.form-foot{margin:0 -16px -140px;padding:12px 16px}
  .form-foot .btn{flex:1 1 100%}.form-foot .btn-primary{order:-1;margin-left:0}
  .page-head-actions{margin-left:0;width:100%}.page-head-actions .btn{flex:1}
  .card{padding:16px}.wiz-step{padding:16px}
  .cols-2,.cols-3,.cols-4{grid-template-columns:1fr}
  .summary{display:flex;flex-direction:column}.sum-item{border-left:0!important;border-top:1px solid var(--line);flex-direction:row;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:4px 12px;padding:12px 16px}.sum-item:first-child{border-top:0}
  .sum-value{font-size:var(--t-20)}.sum-sub{flex-basis:100%}
  .filters>.field,.filters>.field:has(input[type=search]){flex:1 1 100%;width:100%!important;max-width:none}
  .filters-actions{margin-left:0;width:100%}
  .tabs{overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;flex-wrap:nowrap;-webkit-mask:linear-gradient(90deg,#000 85%,transparent)}
  .tabs::-webkit-scrollbar{display:none}.tab{scroll-snap-align:start}
  .tab-more>.btn{display:none}.tab-more .menu-pop{display:contents!important}.tab-more .menu-pop>*{width:auto;min-height:var(--hit)}
  .tbl-wrap{border:0;background:none;overflow:visible}
  .tbl{display:block;min-width:0}.tbl .th{display:none}
  .wf-row{display:flex;flex-direction:column;gap:4px;background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:12px 16px;margin-bottom:8px;position:relative}
  .wf-row .td{display:flex;padding:0;min-height:0;border:0;background:none!important;gap:8px;font-size:var(--t-14)}
  .wf-row .td:not(.td-wide):not(:last-child)::before{content:attr(data-label);color:var(--mute);font-size:var(--t-13);min-width:96px;flex:none}
  .wf-row .td.td-wide{order:-1;font-size:var(--t-16);padding-right:40px}
  .wf-row .td.is-num{justify-content:flex-start}.wf-row .td[data-label=""]::before{display:none}.wf-row .td[data-label=""]:has(.chk){order:-2}
  .wf-row .td:last-child{position:absolute;right:8px;top:8px}
  .wf-row .td:last-child:not(:has(.row-go)):not(:has(.kebab)){position:static}
  .wf-empty{background:var(--surface);border:1px solid var(--line);border-radius:var(--r)}
  .icon-btn{width:44px;height:44px}.user{min-height:44px}.quick .q,.pg,.seg button,.pill,.fchip,.fclear{min-height:44px}.ctx-sede{height:44px}.ctx-sede select{height:42px}
  .tabs{flex-wrap:nowrap}
  .stepper{display:none}.stepper.is-open{display:grid;grid-auto-flow:row;gap:8px}.stepper.is-open li::after{display:none}
  .stepper.is-open button{flex-direction:row;justify-content:flex-start}.stepper.is-open .s-n{width:32px;height:32px}
  .wiz-mobile{display:flex}
  .mod{grid-template-columns:1fr auto;gap:4px 12px}.mod>:nth-child(1){grid-row:auto;grid-column:1}.mod>:nth-child(2),.mod>:nth-child(3){grid-column:1/-1;grid-row:auto}.mod>:nth-child(4){grid-column:1;grid-row:auto;text-align:left}.mod>:nth-child(5){grid-column:2;grid-row:1}
  .ledger{grid-template-columns:minmax(0,1fr) auto}.ledger .ld{display:none}
  .review>div{grid-template-columns:1fr auto}.review dd{grid-column:1}
  .route{flex-direction:column;gap:12px}.route li{flex:none!important;display:grid;grid-template-columns:72px 1fr;gap:4px 12px;align-items:center}.route .r-bar{grid-column:1/-1;order:3}
  .stat-line{grid-template-columns:repeat(2,minmax(0,1fr))}
  .stages{grid-template-columns:1fr}.stage{border-left:0;border-top:1px solid var(--line);flex-direction:row;flex-wrap:wrap;align-items:baseline;gap:4px 12px}.stage .st-count{font-size:var(--t-20);margin-left:auto}.stage .st-rate{flex-basis:100%}
  .tasks li{grid-template-columns:1fr auto;padding:12px 16px}.tasks li>:nth-child(3){grid-column:1/-1}
  .insight{grid-template-columns:1fr}
  .portal-top{padding:10px 16px}.portal-main{padding:16px 16px 80px}.portal-user span{display:none}
  .portal-title small{white-space:normal}
  .hbar{grid-template-columns:100px 1fr 48px}
  .proc-h{flex-direction:column}.proc-h li{grid-template-columns:28px 1fr;padding:0 0 16px}.proc-h li:not(:last-child)::after{left:13.5px;top:28px;bottom:0;width:1px;height:auto;right:auto}
  .perf{flex-direction:column;align-items:flex-start}
  .ai-fab{right:16px;bottom:88px}
  .notif-pop{position:fixed;left:8px;right:8px;top:60px;width:auto}
  .user-pop{position:fixed;right:8px;top:60px}
  .hub{padding:24px 16px}
  .pager .pages{margin-left:0}
  .chat{height:calc(100vh - 200px)}
  .msg{max-width:90%}
}
'''
open(os.path.join(ROOT,"style.css"),"w").write(css)
open(os.path.join(ROOT,".nojekyll"),"w").write("")
open(os.path.join(ROOT,"README.md"),"w").write("# Wireframes Plataforma Cambridge\n\nWireframes estáticos de alto nivel (HTML/CSS, sin build) publicados con GitHub Pages.\n\n- `index.html`: mapa de pantallas por flujo\n- Una página por pantalla (`Main.html` = login)\n\nPublicación: GitHub Pages desde `main` / root (Settings → Pages → Deploy from a branch) o con el workflow `.github/workflows/pages.yml` (Source: GitHub Actions). URL: https://crpozo.github.io/cambridge-wireframes/\n")
