import json, os
import sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W,H=1280,820

INK="#1f2937"; MUTE="#6b7280"; LINE="#9ca3af"; FILL="#e5e7eb"; FILL2="#f3f4f6"; ACC="#1d4ed8"

def box(label, h=120, extra="", dashed=True, w="100%"):
    b = f"2px {'dashed' if dashed else 'solid'} {LINE}"
    return f'<div style="width:{w};height:{h}px;box-sizing:border-box;border:{b};background:{FILL2};display:flex;align-items:center;justify-content:center;color:{MUTE};font-size:14px;text-align:center;padding:8px;{extra}">{label}</div>'

def btn(label, href=None, primary=False):
    st=f"display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:0 18px;border:2px solid {INK};font-size:14px;font-weight:600;text-decoration:none;box-sizing:border-box;"
    st+= f"background:{INK};color:#fff;" if primary else f"background:#fff;color:{INK};"
    if href: return f'<a href="{href}" style="{st}">{label}</a>'
    return f'<button type="button" style="{st}cursor:pointer">{label}</button>'

def nav(active):
    items=[("Inicio","Home.html"),("Estudiantes","Estudiantes.html"),("Cursos","Cursos.html"),("Profesores","Profesores.html"),("Facturación","Facturas.html"),("Comisiones","Comisiones.html"),("Inventario","Inventario.html"),("Reportes","Reportes.html"),("Aprobaciones","Aprobaciones.html"),("Configuración","Configuracion.html")]
    out=""
    for n,h in items:
        st=f"display:block;padding:12px 16px;font-size:14px;text-decoration:none;color:{INK};"
        if n==active: st+=f"background:{FILL};font-weight:700;"
        out+= f'<a href="{h}" style="{st}">{n}</a>' if h else f'<div style="{st}color:{MUTE}">{n}</div>'
    return out

def shell(title, active, *parts, subtitle=""):
    body="".join(parts)
    return f'''<div style="min-height:{H}px;display:flex;flex-direction:column;font-family:'IBM Plex Sans',sans-serif;color:{INK};background:#fff">
<header style="display:flex;flex-wrap:wrap;align-items:center;gap:16px;padding:12px 24px;border-bottom:2px solid {INK}">
  <div style="font-weight:700;font-size:16px">Plataforma Cambridge</div>
  <div style="display:flex;align-items:center;gap:8px;margin-left:auto;font-size:13px">
    <label for="sede" style="color:{MUTE}">Sede</label>
    <select id="sede" style="min-height:44px;padding:0 12px;border:2px solid {LINE};background:#fff;font-size:13px"><option>Todas</option><option>Quito</option><option>Valle</option><option>Ambato</option></select>
  </div>
  <a href="Notificaciones.html" style="font-size:13px">Notificaciones (3)</a><a href="Chatbot.html" style="font-size:13px">Asistente</a><div style="font-size:13px;color:{MUTE}">Estefanía · Admin</div>
</header>
<div style="display:flex;flex-wrap:wrap;flex:1">
  <nav style="width:200px;border-right:2px solid {INK};padding:8px 0">{nav(active)}</nav>
  <main style="flex:999 1 560px;min-width:0;padding:24px;display:flex;flex-direction:column;gap:20px">
    <div><h1 style="margin:0;font-size:24px">{title}</h1>{f'<p style="margin:4px 0 0;color:{MUTE};font-size:14px">{subtitle}</p>' if subtitle else ''}</div>
    {body}
  </main>
</div>
</div>'''

def page(fname, title, inner, lang_title):
    html=f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{lang_title} · Wireframes Plataforma Cambridge</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap">
<link rel="stylesheet" href="style.css">
</head>
<body>
<div class="wf-bar"><a href="index.html">← Mapa de pantallas</a><span>{lang_title}</span><span class="wf-tag">WIREFRAME · alto nivel</span></div>
{inner}
</body>
</html>'''
    open(os.path.join(ROOT,fname),"w").write(html)

def table(cols, rows, h=46):
    hd="".join(f'<div style="padding:10px 12px;font-weight:700;font-size:13px;border-bottom:2px solid {INK}">{c}</div>' for c in cols)
    body=""
    for r in rows:
        body+="".join(f'<div style="padding:12px;font-size:13px;border-bottom:1px solid {LINE};min-height:{h}px;box-sizing:border-box;display:flex;align-items:center">{c}</div>' for c in r)
    return f'<div style="display:grid;grid-template-columns:repeat({len(cols)}, minmax(0, 1fr));border:2px solid {INK}">{hd}{body}</div>'

def tabs(items, active):
    out=""
    for t in items:
        st=f"padding:10px 16px;font-size:14px;border-bottom:3px solid {'#1f2937' if t==active else 'transparent'};font-weight:{700 if t==active else 400}"
        out+=f'<div style="{st}">{t}</div>'
    return f'<div style="display:flex;flex-wrap:wrap;gap:4px;border-bottom:2px solid {LINE}">{out}</div>'

def kpis(labels):
    return f'<div style="display:grid;grid-template-columns:repeat({len(labels)}, minmax(0, 1fr));gap:16px">'+"".join(box(l,110) for l in labels)+'</div>'

def row(*cells, gap=16):
    return f'<div style="display:flex;flex-wrap:wrap;gap:{gap}px;align-items:center">'+"".join(cells)+'</div>'

def two(a,b, ratio="1fr 1fr"):
    return f'<div style="display:grid;grid-template-columns:{ratio};gap:20px">{a}{b}</div>'

def card(title, inner):
    return f'<section style="border:2px solid {INK};padding:16px;display:flex;flex-direction:column;gap:12px"><h2 style="margin:0;font-size:16px">{title}</h2>{inner}</section>'

def li(items):
    return '<ul style="margin:0;padding-left:18px;font-size:14px;line-height:1.7">'+"".join(f"<li>{i}</li>" for i in items)+'</ul>'

# 1 Login
login=f'''<div style="min-height:{H}px;display:flex;align-items:center;justify-content:center;font-family:'IBM Plex Sans',sans-serif;color:{INK};background:{FILL2}">
<form style="width:100%;max-width:420px;background:#fff;border:2px solid {INK};padding:40px;display:flex;flex-direction:column;gap:18px;box-sizing:border-box">
  {box("Logo Cambridge",64)}
  <h1 style="margin:0;font-size:22px">Ingresar</h1>
  <label for="email" style="font-size:13px;font-weight:600">Correo</label>
  <input id="email" type="email" placeholder="nombre@cambridge.edu.ec" style="min-height:44px;padding:0 12px;border:2px solid {LINE};font-size:14px">
  <label for="pass" style="font-size:13px;font-weight:600">Contraseña</label>
  <input id="pass" type="password" placeholder="••••••••" style="min-height:44px;padding:0 12px;border:2px solid {LINE};font-size:14px">
  {btn("Ingresar","Home.html",True)}
  <a href="#recuperar" style="font-size:13px;text-align:center">Olvidé mi contraseña</a>
  <p style="margin:0;font-size:12px;color:{MUTE};text-align:center">2FA opcional · el rol define qué módulos y sedes se ven al entrar</p>
</form>
</div>'''
page("Main.html","Login",login,"Login")

# 2 Home
home=shell("Inicio","Inicio",
 kpis(["Estudiantes activos","Ventas del mes (niveles)","Cobros pendientes","Aprobaciones pendientes"])+
 two(card("Pendientes de aprobación", li(["Descuento 42% · estudiante · asesor","Alta de profesor · coordinación","Asignación profesor sin contrato activo"])+row(btn("Ir a aprobaciones","Aprobaciones.html"))),
     card("Accesos rápidos", row(btn("Nueva venta","NuevaVenta.html",True),btn("Nuevo estudiante","Estudiantes.html"),btn("Payment sheet","PaymentSheet.html"),btn("Comisiones","Comisiones.html")))),
 card("Actividad reciente (audit log)", box("Últimas acciones: quién, qué, cuándo, desde qué sede",90)),
 subtitle="Vista por rol: Gerencia, Dirección Comercial, Coordinación Académica, Asesor, Secretaría")
page("Home.html","Inicio",home,"Inicio por rol")

# 3 Estudiantes
est=shell("Estudiantes","Estudiantes",
 row(box("Buscar: nombre, cédula, email",44,w="320px"),box("Filtro sede",44,w="140px"),box("Filtro estado",44,w="140px"),box("Filtro nivel",44,w="140px"),'<div style="margin-left:auto"></div>',btn("Nuevo estudiante",None,True),btn("Importar / Exportar")),
 table(["Nombre","Cédula","Sede","Nivel actual","Estado","Acción"],[
  ["María Andrade","17xxxxxxxx","Quito","B1","Activo",'<a href="Ficha360.html">Ver ficha</a>'],
  ["Juan Pérez","17xxxxxxxx","Valle","A2","En transición",'<a href="Ficha360.html">Ver ficha</a>'],
  ["Luis Torres","18xxxxxxxx","Ambato","A1","Inactivo",'<a href="Ficha360.html">Ver ficha</a>'],
  ["Ana Ruiz (menor)","17xxxxxxxx","Quito","Kids 2","Activo",'<a href="Ficha360.html">Ver ficha</a>']]),
 box("Paginación · 800 registros consolidados de las 3 sedes",44),
 subtitle="Una sola base para Quito, Valle y Ambato · exportar queda registrado en el audit log")
page("Estudiantes.html","Estudiantes",est,"Listado de estudiantes")

# 4 Ficha 360
ficha=shell("María Andrade","Estudiantes",
 row(box("Sede: Quito · Estado: Activo · Asesor: Carla M.",44,w="460px"),'<div style="margin-left:auto"></div>',btn("Nueva venta","NuevaVenta.html",True),btn("Editar")),
 tabs(["Datos","Cursos y notas","Niveles / crédito","Facturas y pagos","Archivos","Historial"],"Niveles / crédito"),
 two(card("Niveles comprados vs consumidos", box("Pagó 4 niveles · consumió 2 · 1 en curso · 1 pendiente",120)+box("Barra de progreso del paquete",40)),
     card("Resumen financiero", box("Factura consolidada #1234 · $980 · pagado",60)+box("Saldo pendiente: $0 · descuento aplicado: 10% (aprobado)",60))),
 card("Cursos tomados", table(["Curso","Nivel","Profesor","Estado","Nota"],[["Adults B1 Virtual","B1","P. Gómez","En curso","—"],["Adults A2","A2","L. Vega","Pass","85"]])),
 subtitle="Ficha 360°: todo lo del estudiante en una sola vista")
page("Ficha360.html","Ficha estudiante",ficha,"Ficha 360 del estudiante")

# 5 Nueva venta
steps=["1 Estudiante","2 Niveles","3 Descuento","4 Pago","5 Factura"]
stepper='<div style="display:grid;grid-template-columns:repeat(5, minmax(0, 1fr));gap:8px">'+"".join(f'<div style="padding:10px;text-align:center;font-size:13px;font-weight:600;border:2px solid {INK};background:{"#1f2937" if i==2 else "#fff"};color:{"#fff" if i==2 else INK}">{s}</div>' for i,s in enumerate(steps))+'</div>'
venta=shell("Nueva venta por niveles","Facturación",
 stepper,
 two(card("Estudiante y niveles", box("María Andrade · Quito",48)+box("Niveles seleccionados: B1, B2 (2 niveles = 4 módulos)",72)+box("Modalidad: Virtual · Precio lista: $1,000",48)),
     card("Descuento", row(box("Descuento %",44,w="120px"),box("Motivo (obligatorio)",44,w="260px"))+box("Regla: hasta 10% lo aplica el asesor. Más de 10% requiere aprobación del Director Comercial",72)+row(btn("Solicitar aprobación","Aprobaciones.html")))),
 card("Resultado", box("Una sola factura consolidada por el paquete de niveles (reemplaza las 8 facturas por módulo) · método de pago · estado de cobro",72)+row(btn("Atrás"),btn("Emitir factura y matricular","Ficha360.html",True))),
 subtitle="Reemplaza la facturación 1:1 por módulo")
page("NuevaVenta.html","Nueva venta",venta,"Nueva venta por niveles")

# 6 Aprobaciones
apr=shell("Bandeja de aprobaciones","Aprobaciones",
 tabs(["Todas (3)","Descuentos","Profesores","Asignaciones"],"Todas (3)"),
 table(["Tipo","Detalle","Solicitado por","Fecha","Acción"],[
  ["Descuento","42% · María Andrade · motivo: referido","Carla M. (asesor)","Hoy",row(btn("Aprobar",None,True),btn("Rechazar"),gap=8)],
  ["Alta profesor","Nuevo profesor · tarifa $7/h · contrato por horas","Coordinación académica","Ayer",row(btn("Aprobar",None,True),btn("Rechazar"),gap=8)],
  ["Asignación","Profesor sin contrato activo en curso B1","Coordinación académica","Ayer",row(btn("Aprobar",None,True),btn("Rechazar"),gap=8)]],h=64),
 card("Trazabilidad", box("Cada decisión queda en el audit log: quién aprobó, cuándo, con qué justificación · el solicitante recibe notificación",72)),
 subtitle="Control preventivo: nada sensible pasa sin un segundo par de ojos")
page("Aprobaciones.html","Aprobaciones",apr,"Bandeja de aprobaciones")

# 7 Cursos
cursos=shell("Cursos","Cursos",
 row(box("Buscar curso",44,w="260px"),box("Programa",44,w="140px"),box("Nivel",44,w="120px"),box("Modalidad",44,w="140px"),box("Estado",44,w="120px"),'<div style="margin-left:auto"></div>',btn("Nuevo curso",None,True)),
 table(["Curso","Sede","Nivel","Modalidad","Profesor","Estudiantes","Acción"],[
  ["Adults B1 Virtual","Quito","B1","Virtual","P. Gómez","12/15",'<a href="DetalleCurso.html">Ver</a>'],
  ["Kids 2 Tarde","Valle","Kids 2","Presencial","L. Vega","8/10",'<a href="DetalleCurso.html">Ver</a>'],
  ["Teens A2","Ambato","A2","Presencial","(sin asignar)","5/10",'<a href="DetalleCurso.html">Ver</a>']]),
 subtitle="Programa, nivel, modalidad, horario y aula por sede")
page("Cursos.html","Cursos",cursos,"Listado de cursos")

# 8 Detalle curso
det=shell("Adults B1 Virtual · Quito","Cursos",
 row(box("Lun-Mié-Vie 18:00–20:00 · 36 h · 60% completado",44,w="420px"),'<div style="margin-left:auto"></div>',btn("Registrar sesión",None,True),btn("Editar curso")),
 two(card("Profesor asignado", box("P. Gómez · contrato activo ✓ · tarifa $7/h",60)+box("Cambiar profesor → valida contrato activo, si no, va a aprobación",60)),
     card("Sesiones", table(["Fecha","Horas","Registro"],[["01 oct","2","Automático"],["03 oct","2","Manual"],["06 oct","2","Pendiente"]]))),
 card("Estudiantes del curso", table(["Estudiante","Asistencia","Nota","Estado"],[["María Andrade","90%","—","En curso"],["Juan Pérez","70%","—","En curso"],["Luis Torres","40%","—","Riesgo"]])),
 subtitle="Las sesiones registradas aquí alimentan la payment sheet del profesor y el progreso del estudiante")
page("DetalleCurso.html","Detalle curso",det,"Detalle de curso y sesiones")

# 9 Profesores
prof=shell("Profesores","Profesores",
 row(box("Buscar profesor",44,w="260px"),box("Estado",44,w="140px"),box("Sede",44,w="140px"),'<div style="margin-left:auto"></div>',btn("Alta de profesor","Aprobaciones.html",True),btn("Payment sheet","PaymentSheet.html")),
 table(["Profesor","Contrato","Tarifa/h","Cursos activos","Estado","Acción"],[
  ["P. Gómez","Por horas · vigente","$7.00","3","Activo","Ver ficha"],
  ["L. Vega","Por horas · vigente","$6.50","2","Activo","Ver ficha"],
  ["R. Salas","Vencido","$5.70","0","Inactivo","Ver ficha"]]),
 card("Alta de profesor (flujo)", box("Formulario de alta → queda en estado 'Pendiente de aprobación' → Dirección aprueba → recién puede recibir cursos y pagos",72)),
 subtitle="Nadie crea un profesor que pueda cobrar sin aprobación (el caso del profesor falso)")
page("Profesores.html","Profesores",prof,"Listado de profesores")

# 10 Payment sheet
ps=shell("Payment sheet · Octubre 2026","Profesores",
 row(box("Mes",44,w="160px"),box("Sede",44,w="140px"),box("Estado: Borrador",44,w="160px"),'<div style="margin-left:auto"></div>',btn("Exportar"),btn("Aprobar pagos",None,True)),
 table(["Profesor","Sesiones","Horas","Tarifa","A pagar","Factura prof.","Alerta"],[
  ["P. Gómez","24","48","$7.00","$336","$336","—"],
  ["L. Vega","18","36","$6.50","$234","$260","Diferencia +$26"],
  ["R. Salas","4","8","$5.70","$45.60","—","Contrato vencido"]]),
 card("Cómo se calcula", box("Sesiones registradas en los cursos × tarifa hora = monto · se compara contra la factura que entrega el profesor · diferencias y profesores sin contrato se marcan antes de aprobar",72)),
 subtitle="Reemplaza el Excel + Drive de 2 días al mes")
page("PaymentSheet.html","Payment sheet",ps,"Payment sheet de profesores")

# 11 Comisiones
com=shell("Comisiones · Octubre 2026","Comisiones",
 row(box("Período",44,w="160px"),box("Estado: En revisión (draft → revisión → aprobado)",44,w="380px"),'<div style="margin-left:auto"></div>',btn("Reglas de comisión"),btn("Exportar"),btn("Aprobar período",None,True)),
 table(["Asesor","Niveles vendidos","Virtual / Presencial","Meta","Real","Comisión"],[
  ["Carla M.","14","6 / 8","12","14","$420"],
  ["Diego R.","9","4 / 5","12","9","$180"],
  ["Sofía L.","11","7 / 4","10","11","$330"]]),
 two(card("Meta vs real por asesor", box("Gráfico de barras: meta vs real",140)),
     card("Reglas activas", li(["Rango 1–5 niveles: X% · 6–10: Y% · 11+: Z%","Virtual y presencial con tasa distinta","Bono por cumplir meta mensual"]))),
 subtitle="Cálculo automático al cierre de mes, con historial y detalle exportable")
page("Comisiones.html","Comisiones",com,"Motor de comisiones")

# 12 Reportes
rep=shell("Reportes y dashboards","Reportes",
 tabs(["Dashboard por rol","Reportes self-service","Dashboard ejecutivo"],"Dashboard por rol"),
 kpis(["Ventas por nivel (real)","Matrículas del mes","Cobros vs pendientes","Ocupación de cursos"]),
 two(card("Ventas por sede y modalidad", box("Gráfico",160)),card("Pipeline comercial (Kommo → venta → matrícula)", box("Gráfico",160))),
 card("Reportes self-service", row(box("Entidad: estudiantes / ventas / cursos / profesores",44,w="360px"),box("Filtros + columnas",44,w="260px"),box("Rango de fechas",44,w="180px"),'<div style="margin-left:auto"></div>',btn("Generar",None,True),btn("Exportar"))+box("Cada exportación queda registrada en el audit log (datos de menores · LOPDP)",48)),
 subtitle="Estefanía arma sus propios reportes sin pedirle nada a un desarrollador")
page("Reportes.html","Reportes",rep,"Reportes y dashboards")


def form(fields, cols=2):
    out=""
    for i,f in enumerate(fields):
        out+=f'<div style="display:flex;flex-direction:column;gap:6px"><label for="f{i}" style="font-size:13px;font-weight:600">{f}</label><input id="f{i}" style="min-height:44px;padding:0 12px;border:2px solid {LINE};font-size:14px"></div>'
    return f'<div style="display:grid;grid-template-columns:repeat({cols}, minmax(0, 1fr));gap:16px">{out}</div>'

# 13 Usuarios y roles
page("Usuarios.html","Usuarios",shell("Usuarios y roles","Configuración",
 row(box("Buscar usuario",44,w="260px"),box("Rol",44,w="160px"),box("Sede",44,w="140px"),'<div style="margin-left:auto"></div>',btn("Nuevo usuario",None,True)),
 table(["Usuario","Rol","Sedes visibles","Estado","Acción"],[["Estefanía","Administrador General","Todas","Activo","Editar"],["Carla M.","Asesor Comercial","Quito","Activo","Editar"],["Coord. Académica","Coordinador Académico","Valle","Activo","Editar"],["P. Gómez","Profesor (consulta)","Quito","Activo","Editar"]]),
 card("Matriz de permisos por rol", table(["Acción","Admin","Dir. Comercial","Coord. Académica","Asesor","Secretaría"],[["Crear estudiante","✓","✓","—","✓","✓"],["Aplicar descuento >10%","✓","✓","—","—","—"],["Aprobar profesor","✓","✓","—","—","—"],["Exportar base completa","✓","—","—","—","—"],["Ver otras sedes","✓","✓","—","—","—"]])),
 subtitle="RBAC: roles, permisos por acción y visibilidad multi-sede"),"Usuarios y roles")

# 14 Audit log
page("AuditLog.html","Audit log",shell("Audit log","Configuración",
 row(box("Usuario",44,w="180px"),box("Acción",44,w="160px"),box("Entidad",44,w="160px"),box("Rango de fechas",44,w="200px"),box("Sede",44,w="120px"),'<div style="margin-left:auto"></div>',btn("Exportar log")),
 table(["Fecha/hora","Usuario","Acción","Entidad","Detalle","IP / sede"],[["04 oct 10:12","Carla M.","Creó","Estudiante","María Andrade","Quito"],["04 oct 09:40","Dir. Comercial","Aprobó","Descuento","42% → rechazado, 10% aprobado","Quito"],["03 oct 17:05","Secretaría","Exportó","Estudiantes","120 registros (filtro Valle)","Valle"],["03 oct 15:30","Estefanía","Modificó","Tarifa","P. Gómez $6.50 → $7.00","Quito"]]),
 card("Alertas", box("Exportaciones masivas, cambios de tarifa y descuentos fuera de regla se marcan para revisión (LOPDP, datos de menores)",64)),
 subtitle="Quién hizo qué, cuándo y desde dónde. Nada se borra."),"Audit log")

# 15 Configuración
page("Configuracion.html","Configuración",shell("Configuración","Configuración",
 tabs(["Sedes","Catálogo de niveles y precios","Tarifas de profesores","Reglas de aprobación","Parámetros"],"Catálogo de niveles y precios"),
 table(["Programa","Nivel","Módulos","Precio virtual","Precio presencial","Estado"],[["Adults","A1","2","$450","$500","Activo"],["Adults","B1","2","$500","$550","Activo"],["Kids","Kids 2","2","$380","$420","Activo"],["Teens","A2","2","$420","$470","Activo"]]),
 two(card("Sedes", li(["Quito centro","Valle de los Chillos","Ambato","Quito Norte (próxima)"])), card("Reglas de aprobación", li(["Descuento > 10% → Director Comercial","Alta de profesor → Dirección","Asignación sin contrato activo → Coordinación"]))),
 row(btn("Guardar cambios",None,True)),
 subtitle="Todo lo que hoy está hardcodeado en TeamDesk, configurable sin desarrollador"),"Configuración")

# 16 Nuevo estudiante
page("NuevoEstudiante.html","Nuevo estudiante",shell("Nuevo estudiante","Estudiantes",
 form(["Nombres","Apellidos","Cédula / ID","Fecha de nacimiento","Email","Teléfono","Dirección","Sede","Ocupación / empresa","Cómo nos conoció (lead Kommo)"]),
 card("Si es menor de edad", form(["Nombre del representante","Cédula del representante","Teléfono del representante","Autorización firmada (archivo)"])+box("Marcador automático de dato sensible: menor de edad · discapacidad",44)),
 row(btn("Cancelar","Estudiantes.html"),btn("Guardar estudiante","Ficha360.html",True)),
 subtitle="Un solo formulario para las 3 sedes, con validación de duplicados por cédula"),"Nuevo estudiante")

# 17 Importar / exportar
page("ImportExport.html","Importar / exportar",shell("Importar / exportar estudiantes","Estudiantes",
 two(card("Importar", box("Arrastrar archivo CSV / Excel",120)+box("Vista previa: 120 filas · 3 duplicados detectados · 2 con cédula inválida",64)+row(btn("Descargar plantilla"),btn("Importar",None,True))),
     card("Exportar", row(box("Filtro sede",44,w="140px"),box("Estado",44,w="140px"),box("Columnas",44,w="160px"))+box("Aviso: la exportación queda registrada en el audit log con tu usuario",64)+row(btn("Exportar CSV",None,True)))),
 subtitle="Carga masiva con validación y exportación auditada"),"Importar / exportar")

# 18 Nuevo curso
page("NuevoCurso.html","Nuevo curso",shell("Nuevo curso","Cursos",
 form(["Nombre del curso","Programa (Adults / Kids / Teens)","Nivel","Modalidad (virtual / presencial)","Tipo (grupo / individual)","Sede","Aula / enlace virtual","Fecha inicio","Fecha fin","Días y horario","Total de horas","Cupo máximo"]),
 card("Profesor", row(box("Seleccionar profesor",44,w="300px"),box("Validación: contrato activo ✓",44,w="260px"))+box("Si el profesor no tiene contrato activo, la asignación queda pendiente de aprobación",48)),
 row(btn("Cancelar","Cursos.html"),btn("Crear curso","DetalleCurso.html",True)),
 subtitle="Al crear el curso se descuenta el stock de libros por cupo (inventario)"),"Nuevo curso")

# 19 Sesiones
cal="".join(f'<div style="border:1px solid {LINE};min-height:90px;padding:6px;font-size:12px"><b>{d}</b><br>{c}</div>' for d,c in [("Lun 5","B1 Virtual 18:00<br>Kids 2 15:00"),("Mar 6","Teens A2 16:00"),("Mié 7","B1 Virtual 18:00<br>Kids 2 15:00"),("Jue 8","Teens A2 16:00"),("Vie 9","B1 Virtual 18:00"),("Sáb 10","Intensivo A1 09:00"),("Dom 11","")])
page("Sesiones.html","Sesiones",shell("Registro de sesiones","Cursos",
 row(box("Semana 5–11 oct",44,w="200px"),box("Sede",44,w="140px"),box("Profesor",44,w="160px"),'<div style="margin-left:auto"></div>',btn("Registrar sesión manual",None,True)),
 f'<div style="display:grid;grid-template-columns:repeat(7, minmax(0, 1fr));gap:4px">{cal}</div>',
 two(card("Sesión seleccionada", box("B1 Virtual · Lun 5 oct 18:00–20:00 · P. Gómez · 2 h · asistencia 12/15",64)+row(btn("Confirmar sesión",None,True),btn("Marcar no dictada"))),
     card("Alertas", li(["Sesión fuera del horario programado","Profesor con contrato vencido","Curso sin sesiones registradas esta semana"]))),
 subtitle="Las sesiones confirmadas alimentan progreso y payment sheet"),"Registro de sesiones")

# 20 Ficha profesor
page("FichaProfesor.html","Ficha profesor",shell("P. Gómez","Profesores",
 row(box("Contrato por horas · vigente hasta dic 2026 · Quito y Valle",44,w="460px"),'<div style="margin-left:auto"></div>',btn("Editar"),btn("Ver payment sheet","PaymentSheet.html")),
 tabs(["Datos","Contrato y tarifa","Cursos","Sesiones","Historial de pagos"],"Contrato y tarifa"),
 two(card("Contrato", box("Tipo: por horas · Tarifa: $7.00/h · Vigencia: ene–dic 2026 · Aprobado por Dirección el 10-ene",80)+box("Documento de contrato (archivo)",48)),
     card("Historial de pagos", table(["Mes","Horas","Monto","Estado"],[["Sep 2026","44","$308","Pagado"],["Ago 2026","40","$280","Pagado"],["Oct 2026","48","$336","Borrador"]]))),
 subtitle="Ficha única del profesor con su historial de contratos, cursos y pagos"),"Ficha del profesor")

# 21 Alta profesor
page("AltaProfesor.html","Alta de profesor",shell("Alta de profesor","Profesores",
 form(["Nombres y apellidos","Cédula / ID","Fecha de nacimiento","Email","Teléfono","Sede(s)","Tipo de contrato","Tarifa por hora","Vigencia del contrato","Contrato firmado (archivo)"]),
 card("Qué pasa al guardar", box("El profesor se crea en estado 'Pendiente de aprobación' → notificación a Dirección → recién al aprobarse puede recibir cursos y aparecer en la payment sheet",72)),
 row(btn("Cancelar","Profesores.html"),btn("Enviar a aprobación","Aprobaciones.html",True)),
 subtitle="Control preventivo contra el caso del profesor falso"),"Alta de profesor")

# 22 Facturas
page("Facturas.html","Facturas",shell("Facturas","Facturación",
 row(box("Buscar factura / estudiante",44,w="280px"),box("Sede",44,w="140px"),box("Estado de cobro",44,w="160px"),box("Rango de fechas",44,w="200px"),'<div style="margin-left:auto"></div>',btn("Nueva venta","NuevaVenta.html",True),btn("Exportar")),
 kpis(["Facturado del mes","Cobrado","Pendiente","Notas de crédito"]),
 table(["Factura","Estudiante","Sede","Niveles","Monto","Estado","Acción"],[["#1234","María Andrade","Quito","B1, B2","$980","Pagada",'<a href="DetalleFactura.html">Ver</a>'],["#1235","Juan Pérez","Valle","A2","$450","Pendiente",'<a href="DetalleFactura.html">Ver</a>'],["#1236","Luis Torres","Ambato","A1","$420","Nota de crédito",'<a href="DetalleFactura.html">Ver</a>']]),
 subtitle="Una factura por paquete de niveles, con estado de cobro"),"Facturas")

# 23 Detalle factura
page("DetalleFactura.html","Detalle factura",shell("Factura #1234","Facturación",
 two(card("Datos", box("María Andrade · Quito · 02 oct 2026 · Asesor: Carla M.",48)+table(["Concepto","Cant.","Precio","Total"],[["Nivel B1 (2 módulos)","1","$500","$500"],["Nivel B2 (2 módulos)","1","$500","$500"],["Descuento 10% (aprobado por Dir. Comercial)","","","-$100"],["Libros B1 + B2","2","$40","$80"]])+box("Total: $980 · Método: transferencia · Estado: pagada",48)),
     card("Notas de crédito y cambios", box("Sin notas de crédito",48)+row(btn("Emitir nota de crédito"),btn("Cambio de curso"))+box("Una devolución o cambio de curso genera nota de crédito vinculada y revierte el libro al stock",64))),
 row(btn("Volver","Facturas.html"),btn("Descargar PDF"),btn("Registrar pago",None,True)),
 subtitle="Factura consolidada con su trazabilidad completa"),"Detalle de factura")

# 24 Solicitud de descuento
page("SolicitudDescuento.html","Solicitud de descuento",shell("Solicitud de descuento","Facturación",
 f'<div style="max-width:640px;border:2px solid {INK};padding:24px;display:flex;flex-direction:column;gap:16px">'+box("Venta: María Andrade · B1 + B2 · $1,000",48)+form(["Descuento solicitado (%)","Monto resultante"])+form(["Motivo (obligatorio, lista cerrada: referido, promoción, convenio, otro)"],1)+form(["Justificación"],1)+box("Regla: >10% requiere aprobación del Director Comercial · el asesor ve el estado en su bandeja",56)+row(btn("Cancelar","NuevaVenta.html"),btn("Enviar solicitud","Aprobaciones.html",True))+'</div>',
 subtitle="Reemplaza el campo 'Reason' opcional de TeamDesk"),"Solicitud de descuento")

# 25 Detalle comisión por asesor
page("DetalleComision.html","Detalle comisión",shell("Comisiones · Carla M. · Octubre 2026","Comisiones",
 kpis(["Niveles vendidos: 14","Meta: 12","Cumplimiento: 117%","Comisión: $420"]),
 table(["Fecha","Estudiante","Niveles","Modalidad","Monto venta","Regla aplicada","Comisión"],[["02 oct","María Andrade","2","Virtual","$1,000","Rango 11+ · 4%","$40"],["05 oct","Juan Pérez","1","Presencial","$450","Rango 11+ · 5%","$22.50"],["09 oct","Ana Ruiz","2","Presencial","$760","Rango 11+ · 5%","$38"]]),
 two(card("Bonos", box("Bono por meta cumplida: $50",48)), card("Historial", box("Sep: $300 · Ago: $280 · Jul: $350",48))),
 row(btn("Volver","Comisiones.html"),btn("Exportar detalle")),
 subtitle="Cada comisión muestra qué regla la generó"),"Detalle de comisión")

# 26 Reglas de comisión
page("ReglasComision.html","Reglas de comisión",shell("Reglas de comisión","Comisiones",
 table(["Regla","Condición","Virtual","Presencial","Vigencia","Estado"],[["Rango 1","1–5 niveles / mes","2%","3%","2026","Activa"],["Rango 2","6–10 niveles / mes","3%","4%","2026","Activa"],["Rango 3","11+ niveles / mes","4%","5%","2026","Activa"],["Bono meta","Cumple meta mensual","$50","$50","2026","Activa"]]),
 two(card("Nueva regla", form(["Nombre","Condición (niveles / modalidad / meta)","% o monto","Vigencia"])+row(btn("Guardar regla",None,True))), card("Simulador", box("Probar reglas contra las ventas del mes pasado antes de activarlas",100))),
 subtitle="Configurable sin código; cada cambio queda en el audit log"),"Reglas de comisión")

# 27 Inventario
page("Inventario.html","Inventario",shell("Inventario de libros","Inventario",
 row(box("Buscar libro",44,w="240px"),box("Sede",44,w="140px"),box("Estado de stock",44,w="160px"),'<div style="margin-left:auto"></div>',btn("Nuevo pedido a proveedor","Movimientos.html",True)),
 kpis(["Ítems con stock negativo: 3","Pedidos en camino: 2","Valor en stock","Alertas"]),
 table(["Libro","Nivel","Quito","Valle","Ambato","Comprometido","Alerta"],[["Adults B1 Student Book","B1","4","-2","1","5","Pedir 6"],["Kids 2 Workbook","Kids 2","0","3","-1","4","Pedir 4"],["Teens A2","A2","8","2","5","3","—"]]),
 subtitle="Reemplaza el email diario de notify@teamdesk con alertas inteligentes"),"Inventario de libros")

# 28 Movimientos
page("Movimientos.html","Movimientos",shell("Movimientos y pedidos","Inventario",
 tabs(["Movimientos","Pedidos a proveedor","Notas de crédito"],"Pedidos a proveedor"),
 table(["Pedido","Proveedor","Ítems","Total","Fecha","Estado"],[["#P-041","Books & Bits","12","$480","02 oct","En camino"],["#P-040","Books & Bits","8","$320","25 sep","Recibido"],["#P-039","Books & Bits","20","$800","10 sep","Recibido"]]),
 two(card("Registrar ingreso", form(["Pedido","Cantidad recibida"])+row(btn("Registrar ingreso",None,True))), card("Forecast", box("Cursos que abren el próximo mes × cupo = libros necesarios por sede",100))),
 subtitle="Entradas, salidas y devoluciones vinculadas a cursos y facturas"),"Movimientos de inventario")

# 29 Constructor de reportes
page("ConstructorReportes.html","Reportes self-service",shell("Constructor de reportes","Reportes",
 two(card("Definir reporte", form(["Entidad (estudiantes / ventas / cursos / profesores / comisiones)","Columnas"],1)+form(["Filtro sede","Filtro estado","Desde","Hasta"])+row(btn("Generar",None,True),btn("Guardar como reporte"))),
     card("Reportes guardados", li(["Nuevos estudiantes por mes (reemplaza New Students Report)","Ventas por nivel y sede","Cobros pendientes por asesor","Profesores activos y horas"]))),
 card("Resultado", table(["Mes","Quito","Valle","Ambato","Total"],[["Ago","32","18","11","61"],["Sep","40","22","14","76"],["Oct","28","15","9","52"]])+row(btn("Exportar Excel"),btn("Exportar PDF"))),
 subtitle="El reporte que hoy hay que pedirle al desarrollador, en minutos"),"Constructor de reportes")

# 30 Dashboard ejecutivo
page("DashboardEjecutivo.html","Dashboard ejecutivo",shell("Dashboard ejecutivo","Reportes",
 row(box("Período: 2026",44,w="160px"),box("Comparar con 2025",44,w="180px"),box("Sede: Todas",44,w="140px")),
 kpis(["Ingresos YTD","Estudiantes activos","Ticket promedio por paquete","Margen por sede"]),
 two(card("Ingresos por mes y sede", box("Gráfico de líneas",180)), card("Mix por programa y modalidad", box("Gráfico de torta / barras",180))),
 two(card("Funnel comercial", box("Leads (Kommo) → cotizaciones → ventas → matrículas",120)), card("Retención y avance de niveles", box("% de estudiantes que continúan al siguiente nivel",120))),
 subtitle="Vista gerencial, distinta de la reportería operativa"),"Dashboard ejecutivo")

# 31 Chatbot
chat=f'<div style="max-width:760px;border:2px solid {INK};display:flex;flex-direction:column;height:520px"><div style="flex:1;padding:16px;display:flex;flex-direction:column;gap:12px;overflow:auto">'+ \
 f'<div style="align-self:flex-end;max-width:70%;padding:10px 14px;background:{INK};color:#fff;font-size:14px">¿Cuántos estudiantes activos tiene Valle en nivel B1?</div>'+ \
 f'<div style="align-self:flex-start;max-width:70%;padding:10px 14px;background:{FILL};font-size:14px">Valle tiene 23 estudiantes activos en B1, repartidos en 2 cursos (P. Gómez y L. Vega). ¿Quieres ver el listado?</div>'+ \
 f'<div style="align-self:flex-end;max-width:70%;padding:10px 14px;background:{INK};color:#fff;font-size:14px">¿Qué pagos a profesores están pendientes de aprobar?</div>'+ \
 f'<div style="align-self:flex-start;max-width:70%;padding:10px 14px;background:{FILL};font-size:14px">La payment sheet de octubre está en borrador con 2 alertas. Solo puedes ver pagos de las sedes que tu rol permite.</div>'+ \
 f'</div><div style="display:flex;gap:8px;padding:12px;border-top:2px solid {LINE}"><label for="msg" style="position:absolute;left:-9999px">Mensaje</label><input id="msg" placeholder="Pregunta sobre estudiantes, cursos, pagos o reportes" style="flex:1;min-height:44px;padding:0 12px;border:2px solid {LINE};font-size:14px">{btn("Enviar",None,True)}</div></div>'
page("Chatbot.html","Asistente interno",shell("Asistente interno","Inicio",chat,
 box("Responde solo con datos de la plataforma y respeta los permisos del usuario (RBAC). No expone datos de otras sedes.",56),
 subtitle="Consulta ágil para el equipo, sin armar un reporte"),"Asistente interno")

# 32 Integraciones
page("Integraciones.html","Integraciones",shell("Integraciones","Configuración",
 table(["Sistema","Uso","Estado","Última sincronización","Acción"],[["Kommo (CRM)","Leads → estudiantes","Conectado","Hoy 09:00","Configurar"],["Moodle (LMS)","Matrícula → curso virtual","Pendiente de API del proveedor","—","Configurar"],["Dora","Por definir con el cliente","Pendiente","—","Configurar"]]),
 two(card("API keys y webhooks", box("Claves por sistema · webhooks de notificación · documentación OpenAPI",100)), card("Log de sincronización", table(["Fecha","Sistema","Resultado"],[["04 oct","Kommo","12 leads importados"],["03 oct","Kommo","1 error: email duplicado"]]))),
 subtitle="Sujeto al esquema de apificación disponible en cada proveedor"),"Integraciones")

# 33 Notificaciones
page("Notificaciones.html","Notificaciones",shell("Notificaciones","Inicio",
 table(["Tipo","Mensaje","Fecha","Acción"],[["Aprobación","Descuento 42% pendiente de tu aprobación","Hoy",'<a href="Aprobaciones.html">Revisar</a>'],["Inventario","Stock negativo: Adults B1 en Valle","Hoy",'<a href="Inventario.html">Ver</a>'],["Pagos","Payment sheet de octubre lista para revisión","Ayer",'<a href="PaymentSheet.html">Ver</a>'],["Alta","Profesor nuevo aprobado: puede recibir cursos","Ayer",'<a href="Profesores.html">Ver</a>']]),
 card("Preferencias", box("Qué notificaciones recibe cada rol, por email y en la plataforma",64)),
 subtitle="Centro de avisos que mueve los flujos de aprobación"),"Notificaciones")

rows=[
 ("Acceso y navegación",[("Main.html","01 Login"),("Home.html","02 Inicio por rol"),("Notificaciones.html","03 Notificaciones"),("Chatbot.html","04 Asistente interno")],"Login → Inicio por rol. Las notificaciones y el asistente son transversales y acompañan todos los flujos."),
 ("Estudiantes",[("Estudiantes.html","05 Listado"),("NuevoEstudiante.html","06 Nuevo estudiante"),("Ficha360.html","07 Ficha 360°"),("ImportExport.html","08 Importar / exportar")],"Buscar o crear estudiante → ficha 360° con niveles, facturas y archivos. Importación con validación de duplicados, exportación auditada."),
 ("Flujo comercial",[("NuevaVenta.html","09 Nueva venta por niveles"),("SolicitudDescuento.html","10 Solicitud de descuento"),("Aprobaciones.html","11 Bandeja de aprobaciones"),("Facturas.html","12 Facturas"),("DetalleFactura.html","13 Detalle de factura")],"Venta por paquete de niveles → descuento fuera de regla pasa por aprobación → una factura consolidada con su estado de cobro y notas de crédito."),
 ("Flujo académico",[("Cursos.html","14 Cursos"),("NuevoCurso.html","15 Nuevo curso"),("DetalleCurso.html","16 Detalle de curso"),("Sesiones.html","17 Registro de sesiones")],"Curso con profesor validado → sesiones registradas (automáticas o manuales) → alimentan progreso del estudiante y payment sheet."),
 ("Flujo profesores",[("Profesores.html","18 Profesores"),("AltaProfesor.html","19 Alta con aprobación"),("FichaProfesor.html","20 Ficha del profesor"),("PaymentSheet.html","21 Payment sheet")],"Alta pasa por aprobación antes de poder cobrar. Payment sheet = sesiones × tarifa, comparada contra la factura del profesor."),
 ("Comisiones",[("Comisiones.html","22 Período de comisiones"),("DetalleComision.html","23 Detalle por asesor"),("ReglasComision.html","24 Reglas de comisión")],"Cierre de mes: cálculo automático por reglas configurables (draft → revisión → aprobado), con detalle por asesor."),
 ("Inventario",[("Inventario.html","25 Stock por sede"),("Movimientos.html","26 Movimientos y pedidos")],"Stock por sede, pedidos a Books & Bits, ingresos y notas de crédito vinculadas a cursos y facturas."),
 ("Reportes y dashboards",[("Reportes.html","27 Dashboard por rol"),("ConstructorReportes.html","28 Constructor de reportes"),("DashboardEjecutivo.html","29 Dashboard ejecutivo")],"Reportería operativa self-service y vista gerencial separada."),
 ("Administración y gobierno",[("Usuarios.html","30 Usuarios y roles"),("Configuracion.html","31 Configuración"),("AuditLog.html","32 Audit log"),("Integraciones.html","33 Integraciones")],"RBAC, catálogos y reglas configurables, trazabilidad completa e integraciones con Kommo, Moodle y Dora."),
]
sec=""
for t,files,desc in rows:
    cards="".join(f'<a class="card" href="{f}"><span class="num">{n.split(" ")[0]}</span><span>{" ".join(n.split(" ")[1:])}</span></a>' for f,n in files)
    arrows=f'<div class="flow">{cards}</div>'
    sec+=f'<section><h2>{t}</h2><p>{desc}</p>{arrows}</section>'
idx=f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Wireframes Plataforma Cambridge</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap">
<link rel="stylesheet" href="style.css">
</head>
<body class="hub">
<header class="hub-head">
<h1>Plataforma Cambridge · Wireframes</h1>
<p>Versión de alto nivel para validar el flujo, no el diseño. Cada pantalla es navegable: los botones y enlaces llevan a la siguiente pantalla del flujo. 33 pantallas que cubren los 11 módulos del contrato.</p>
</header>
{sec}
<footer class="hub-foot">Orkesta · Cambridge School of Languages · Fase 0 Discovery y Diseño</footer>
</body>
</html>'''
open(os.path.join(ROOT,"index.html"),"w").write(idx)
css=f'''*{{box-sizing:border-box}}
body{{margin:0;font-family:'IBM Plex Sans',sans-serif;color:{INK};background:#fff}}
a{{color:{ACC}}}a:hover{{color:#1e40af}}
.wf-bar{{display:flex;flex-wrap:wrap;gap:16px;align-items:center;padding:8px 24px;background:#fff7d6;border-bottom:1px solid #e0c66b;font-size:13px}}
.wf-bar span:nth-child(2){{font-weight:600}}
.wf-tag{{margin-left:auto;color:#8a6d00;letter-spacing:.06em;font-size:11px}}
.hub{{max-width:1100px;margin:0 auto;padding:40px 24px}}
.hub-head p{{color:{MUTE};font-size:15px;line-height:1.6;max-width:820px}}
.hub section{{margin-top:40px}}
.hub h2{{margin:0 0 4px;font-size:20px}}
.hub section p{{margin:0 0 16px;color:{MUTE};font-size:14px;max-width:820px}}
.flow{{display:flex;flex-wrap:wrap;gap:12px;align-items:center}}
.card{{display:flex;flex-direction:column;gap:6px;width:200px;min-height:96px;padding:16px;border:2px solid {INK};text-decoration:none;color:{INK};font-weight:600;background:#fff;position:relative}}
.card .num{{font-size:12px;color:{MUTE};font-weight:400}}
.card:hover{{background:{FILL2}}}
.card+.card::before{{content:"→";position:absolute;left:-16px;top:40px;color:{MUTE}}}
.hub-foot{{margin-top:60px;color:{MUTE};font-size:12px}}
@media (max-width:640px){{.card+.card::before{{display:none}}}}
'''
open(os.path.join(ROOT,"style.css"),"w").write(css)
open(os.path.join(ROOT,".nojekyll"),"w").write("")
open(os.path.join(ROOT,"README.md"),"w").write("# Wireframes Plataforma Cambridge\n\nWireframes estáticos de alto nivel (HTML/CSS, sin build) publicados con GitHub Pages.\n\n- `index.html`: mapa de pantallas por flujo\n- Una página por pantalla (`Main.html` = login)\n\nPublicar: Settings → Pages → Deploy from branch `main` / root.\n")
