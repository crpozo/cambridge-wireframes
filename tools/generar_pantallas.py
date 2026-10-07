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
 "Nuevo estudiante":"NuevoEstudiante.html","Importar / Exportar":"ImportExport.html","Nuevo curso":"NuevoCurso.html","Editar curso":"NuevoCurso.html",
 "Registrar sesión":"RegistrarSesion.html","Registrar sesión manual":"RegistrarSesion.html","Reglas de comisión":"ReglasComision.html",
 "Nuevo usuario":"NuevoUsuario.html","Nueva sede":"NuevaSede.html","Nuevo nivel":"NuevoNivel.html","Nueva regla":"NuevaRegla.html",
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
 "Descargar plantilla":("Se descarga la plantilla CSV con las columnas esperadas y un ejemplo.",None),
 "Guardar cambios":("Se validan los campos obligatorios y se guarda. "+AUDIT,None),
 "Guardar regla":("La regla queda activa desde su vigencia y se aplica en el próximo cálculo. "+AUDIT,None),
 "Guardar como reporte":("El reporte se guarda con sus filtros y columnas para volver a ejecutarlo desde 'Reportes guardados'.",None),
 "Generar":("Se ejecuta el reporte con los filtros elegidos y el resultado se muestra abajo.",None),
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
 "Calificar curso":("Se registra pass/fail y nota final por estudiante. Al cerrar, cada aprobado consume un módulo de su paquete y recibe su certificado.",None),
 "Anular matrícula":("Requiere aprobación. Se revierte la matrícula, se genera nota de crédito por el saldo pagado y el libro vuelve al stock.",None),
 "Emitir certificado":("Se genera el certificado del nivel aprobado en PDF y queda en Archivos del estudiante.",None),
 "Ver matrícula":"DetalleMatricula.html","Ver curso":"DetalleCurso.html","Nueva matrícula":"NuevaVenta.html",
 "Registrar ingreso de proveedor":"NuevoPedido.html",
 "Asignar código":("Se asigna el código de activación del material digital al estudiante y se marca como entregado.",None),
 "Marcar como atendido":("El insight pasa a 'atendido' con tu usuario y fecha; deja de aparecer en Inicio y en el asistente.",None),
 "Descartar":("El insight se descarta con un motivo; el asistente aprende a no repetirlo para este caso.",None),
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
HIDDEN={"Facturas.html","DetalleFactura.html","RegistrarPago.html","NotaCredito.html"}

# Tipos de usuario (RBAC). Código → (nombre del rol, usuario de ejemplo)
ROLES=[("ADM","Administrador General","Estefanía"),("GER","Gerente General","Gerencia"),("DIR","Director Comercial","Dir. Comercial"),("SUC","Administrador de Sucursal","Admin. Valle"),("COO","Coordinador Académico","Coord. Académica"),("ASE","Asesor Comercial","Carla M."),("SEC","Secretaría","Secretaría"),("PRO","Profesor (consulta)","P. Gómez")]
ALL="ADM,GER,DIR,SUC,COO,ASE,SEC,PRO"
COMERCIAL="ADM,GER,DIR,SUC,ASE,SEC"
ACADEMICO="ADM,GER,SUC,COO,PRO"
APROBADORES="ADM,GER,DIR,SUC,COO"
def only(roles, html, inline=False):
    """Envuelve html para que solo lo vean esos roles (códigos separados por coma)."""
    return f'<{"span" if inline else "div"} data-roles="{roles}" style="display:contents">{html}</{"span" if inline else "div"}>'

# Menú lateral agrupado por áreas. Cada ítem: (nombre, archivo, roles que lo ven). Un área desaparece si el rol no ve ninguno de sus ítems.
NAV=[
 ("",[("Inicio","Home.html",ALL)]),
 ("Académico",[("Estudiantes","Estudiantes.html",ALL),("Cursos","Cursos.html",ALL),("Sesiones","Sesiones.html",ACADEMICO+",SEC"),("Profesores","Profesores.html","ADM,GER,DIR,SUC,COO")]),
 ("Comercial",[("Nueva matrícula","NuevaVenta.html",COMERCIAL),("Facturación","Facturas.html",COMERCIAL),("Comisiones","Comisiones.html","ADM,GER,DIR,ASE"),("Aprobaciones","Aprobaciones.html",APROBADORES)]),
 ("Inventario",[("Stock por sede","Inventario.html","ADM,GER,SUC,COO,SEC"),("Movimientos y pedidos","Movimientos.html","ADM,GER,SUC,SEC")]),
 ("Dirección",[("Insights de IA","Insights.html","ADM,GER,DIR,SUC,COO"),("Reportes","Reportes.html","ADM,GER,DIR,SUC,COO"),("Dashboard ejecutivo","DashboardEjecutivo.html","ADM,GER,DIR")]),
 ("Administración",[("Usuarios y roles","Usuarios.html","ADM,GER"),("Configuración","Configuracion.html","ADM,GER"),("Audit log","AuditLog.html","ADM,GER,SUC"),("Integraciones","Integraciones.html","ADM")]),
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
    <select id="sede" style="height:30px;padding:0 6px;border:1px solid {LINE};border-radius:4px;background:#fff;font:inherit;font-size:13px;color:{INK};outline-offset:1px"><option>Todas</option><option>Quito</option><option>Valle</option><option>Ambato</option></select>
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
 "Home.html":[("¿Qué debo atender hoy?","Hoy: 3 aprobaciones pendientes (la más antigua de ayer), 3 sesiones sin confirmar y 2 cursos terminados sin calificar. Lo más urgente es el descuento del 42% de María Andrade: la matrícula espera desde ayer."),("¿Cómo va la meta del mes?","Octubre lleva 76 niveles vendidos sobre una meta de 70 (109%). Quito aporta 40, Valle 22 y Ambato 14. Ambato lleva 2 semanas sin matrículas nuevas.")],
 "Cursos.html":[("¿Qué cursos están por abrir sin profesor?","Dos: Teens A2 (Ambato, Vi 15:00) y Tailored · Inglés corporativo (Ambato, Ma-Ju 07:00). Ambos inician en menos de 3 semanas. P. Gómez y M. Castro tienen horas libres compatibles."),("¿Cuáles tienen estudiantes con saldo?","9 cursos suman $2,840 pendientes. El mayor saldo está en B1 Virtual (0001-2026-0767): 2 estudiantes deben $303. Cuatro de esos cursos terminan en noviembre."),("¿Qué cursos terminaron sin calificar?","Adults A1 Sábados (0001-2026-0430) terminó hace 5 días con 14 estudiantes sin nota, y Teens A2 2025 (Valle). Hasta que se califiquen no se emiten certificados ni pueden matricularse en el siguiente nivel.")],
 "Estudiantes.html":[("¿Cuántos estudiantes activos hay por sede?","812 activos: Quito 420, Valle 230 y Ambato 162. Este mes entraron 52 nuevos y 14 están en transición entre niveles."),("¿Quiénes tienen asistencia menor a 75%?","14 estudiantes están en riesgo. Los 4 más críticos están en B1 Virtual (Quito) con menos de 60%. Puedo listarlos con su teléfono de contacto si quieres llamarlos."),("¿Hay duplicados entre sedes?","La migración detectó 23 posibles duplicados por cédula entre Quito y Valle. 18 ya están unificados; 5 esperan confirmación de Secretaría.")],
 "Profesores.html":[("¿Quién puede cubrir Teens B1 Virtual?","P. Gómez: dicta B1 Virtual en Quito con 88% de asistencia, tiene libres Lu-Ma-Mi-Ju 17:00–19:00 y le quedan 6 h antes del máximo de su contrato. S. Jiménez ya está al tope (20 h)."),("¿Qué profesores no tienen contrato vigente?","R. Salas (Ambato) tiene el contrato vencido y 8 h registradas este mes; D. Paredes (Valle) está pendiente de aprobación. Ninguno puede entrar en la payment sheet hasta resolverlo.")],
 "FichaProfesor.html":[("¿Cuántas horas lleva este mes?","P. Gómez lleva 48 h en octubre (24 sesiones). Su payment sheet suma $336 y coincide con su factura. Tiene 2 sesiones manuales fuera de horario pendientes de confirmar.")],
 "Ficha360.html":[("¿Qué nivel le toca y cuándo abre?","María está en el módulo 7 (B1). Al aprobarlo pasa al módulo 8 del mismo curso; su siguiente nivel comprado es B2, que abre en marzo de 2027. Tiene 3 niveles pagados y 2 consumidos."),("¿Tiene saldo pendiente?","No. Su matrícula 001-202602794 está pagada ($980). Su descuento del 10% fue por referido y lo aprobó Dirección Comercial.")],
 "Inventario.html":[("¿Qué libros hay que pedir?","Tres productos con stock negativo: Empower B1+ (Valle −2), Super Minds 3 WB (Ambato −1) y Super Minds 3 SB (Ambato −2). El pedido sugerido a Books & Bits suma 16 libros."),("¿Cuántos códigos de activación quedan?","13 códigos comprados sin asignar: 9 en Valle y 4 en Quito. Uno de Empower A1 venció.")],
 "PaymentSheet.html":[("¿Por qué no puedo aprobar la payment sheet?","Hay 3 alertas: L. Vega facturó $26 más que las horas registradas, R. Salas tiene contrato vencido con 8 h, y D. Paredes entregó factura sin sesiones. Resueltas esas tres, el total a pagar es $1,145.60.")],
 "Comisiones.html":[("¿Cuánto gana cada asesor este mes?","Carla M. $420 (14 niveles, bono incluido), Sofía L. $330 (11) y Diego R. $180 (9, no llegó a la meta de 12). Solo se paga la comisión de ventas cobradas.")],
 "Aprobaciones.html":[("¿Qué pasa si apruebo el descuento del 42%?","La matrícula de María Andrade se cerraría en $580 en lugar de $980 y la comisión de Carla M. bajaría a $23. La regla permite hasta 10% sin aprobación; 42% queda en el audit log con tu justificación.")],
 "Configuracion.html":[("¿Qué aulas están libres el sábado en la mañana?","En Valle: C-2 (9 estudiantes) y C-7 (5). En Quito, Q-1 está ocupada al 60%. La capacidad se calcula con la norma SETEC.")],
 "Insights.html":[("¿Qué insight es el más urgente?","El descuento del 42% pendiente desde ayer bloquea una matrícula de $980. Después, los 14 estudiantes de A1 Sábados sin calificar: no pueden pasar a A2 y hay 3 cupos esperándolos.")],
}
AI_DEFAULT=[("¿Qué puedo hacer en esta pantalla?","Te explico lo que ves aquí y qué acciones tienes según tu rol. También puedo buscar un estudiante, curso o profesor por nombre o código."),("¿Hay algo pendiente que deba revisar?","Reviso aprobaciones, sesiones sin confirmar, saldos y alertas de inventario relacionados con esta pantalla y te digo qué es urgente.")]

def page(fname, title, inner, lang_title):
    html=f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{lang_title} · Wireframes Plataforma Cambridge</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="style.css">
</head>
<body>
{inner}
<button type="button" class="ai-fab" id="ai-fab" aria-label="Abrir asistente">{ico("spark","nav-ico")}<span class="ai-fab-dot"></span></button>
<aside class="ai-panel" id="ai-panel" hidden aria-label="Asistente">
  <div class="ai-panel-head"><span class="ai-spark">✦</span><div><b>Asistente Cambridge</b><small>Estás en: <span id="ai-ctx">{lang_title}</span></small></div><button type="button" class="icon-btn" id="ai-close" aria-label="Cerrar">×</button></div>
  <div class="ai-log" id="ai-log"><div class="msg bot">Hola. Veo que estás en <b>{lang_title}</b>. Puedo responder sobre lo que tienes en pantalla o sobre cualquier dato de la plataforma, siempre según tu rol y sede.</div></div>
  <div class="ai-chips" id="ai-chips">{"".join(f'<button type="button" class="chipq" data-a="{a.replace(chr(34),"&quot;")}">{q}</button>' for q,a in AI_CTX.get(fname,[])+AI_DEFAULT)}</div>
  <form class="ai-in" id="ai-form"><label for="ai-input" class="sr">Pregunta</label><input id="ai-input" class="ctl" placeholder="Pregunta sobre {lang_title.lower()}…" autocomplete="off"><button type="submit" class="btn btn-primary">Enviar</button></form>
</aside>
<dialog id="wf-dialog">
  <h2 id="wf-dialog-title" style="margin:0 0 8px;font-size:18px"></h2>
  <p id="wf-dialog-text" style="margin:0 0 20px;font-size:14px;line-height:1.5;color:#5B6B8A"></p>
  <div style="display:flex;gap:12px;justify-content:flex-end"><button type="button" id="wf-cancel" class="btn">Cancelar</button><button type="button" id="wf-ok" class="btn btn-primary">Confirmar</button></div>
</dialog>
<div id="wf-toast" role="status"></div>
<script>
(function(){{
  var dlg=document.getElementById('wf-dialog'),title=document.getElementById('wf-dialog-title'),text=document.getElementById('wf-dialog-text'),toast=document.getElementById('wf-toast'),cur=null;
  document.querySelectorAll('[data-action]').forEach(function(b){{
    b.addEventListener('click',function(){{cur=b;title.textContent=b.textContent.trim();text.textContent=b.dataset.action;dlg.showModal();}});
  }});
  document.getElementById('wf-cancel').addEventListener('click',function(){{dlg.close();}});
  document.getElementById('wf-ok').addEventListener('click',function(){{
    dlg.close();toast.textContent='✓ '+cur.textContent.trim()+' · hecho';toast.style.display='block';
    setTimeout(function(){{toast.style.display='none';if(cur.dataset.next)location.href=cur.dataset.next;}},1100);
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
        r.style.display=ok?'contents':'none'; if(ok) shown++;
      }});
      var e=t.querySelector('.wf-empty'); if(e) e.style.display=shown?'none':'block';
      var pg=host.nextElementSibling; if(pg&&pg.classList.contains('wf-pager')){{var sp=pg.querySelector('.wf-shown'); if(sp) sp.textContent=' · '+shown+' en pantalla';}}
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
    document.querySelectorAll('[data-roles]').forEach(function(e){{
      var ok=e.getAttribute('data-roles').split(',').indexOf(r)>=0;
      if(e.hasAttribute('data-panel')){{ if(!ok){{e.dataset.wfHidden='1';e.style.display='none';}} else {{delete e.dataset.wfHidden;}} return; }}
      if(e.dataset.wfD===undefined) e.dataset.wfD=e.style.display||'';
      e.style.display=ok?e.dataset.wfD:'none';
    }});
    (function(){{var nb=document.getElementById('notif-btn'),np=document.getElementById('notif-pop');if(!nb)return;nb.addEventListener('click',function(e){{e.stopPropagation();var o=np.hidden;np.hidden=!o;nb.setAttribute('aria-expanded',o);}});document.addEventListener('click',function(e){{if(!np.hidden&&!np.contains(e.target))np.hidden=true;}});document.addEventListener('keydown',function(e){{if(e.key==='Escape')np.hidden=true;}});}})();
document.querySelectorAll('.btn-more').forEach(function(b){{b.addEventListener('click',function(){{var t=document.getElementById(b.getAttribute('aria-controls'));var open=b.getAttribute('aria-expanded')==='true';b.setAttribute('aria-expanded',!open);t.hidden=open;b.textContent=(open?'Más filtros':'Menos filtros')+b.textContent.slice(b.textContent.indexOf(' ('));}});}});
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
      btns.forEach(function(x){{var on=x===b;x.setAttribute('aria-selected',on);x.classList.toggle('on',on);}});
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
  document.querySelectorAll('.chipq').forEach(function(c){{c.addEventListener('click',function(){{answer(c.textContent,c.getAttribute('data-a'));}});}});
  form.addEventListener('submit',function(e){{e.preventDefault();var q=inp.value.trim();if(!q)return;inp.value='';var m=[].find.call(document.querySelectorAll('.chipq'),function(c){{return q.toLowerCase().split(' ').filter(function(w){{return w.length>4}}).some(function(w){{return c.textContent.toLowerCase().indexOf(w)>=0;}});}});answer(q,m?m.getAttribute('data-a'):null);}});
  document.querySelectorAll('.btn-ask').forEach(function(b){{b.addEventListener('click',function(){{open();inp.value=b.getAttribute('data-ask')||'';}});}});
}})();
if(window.wfApplyRole) window.wfApplyRole();
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
SEDES=["Todas","Quito","Valle","Ambato"]
def sv(todas,quito,valle,ambato):
    """Valor que cambia con el selector de sede global."""
    import json as _j
    d=_j.dumps({"Todas":str(todas),"Quito":str(quito),"Valle":str(valle),"Ambato":str(ambato)},ensure_ascii=False).replace("'","&#39;")
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
    axis="".join(f'<text x="{xs[i]:.0f}" y="{h-4}" font-size="11" text-anchor="middle" fill="{MUTE}">{l}</text>' for i,l in enumerate(labels))
    grid="".join(f'<line x1="40" x2="{W-20}" y1="{h-20-(h-40)*f:.0f}" y2="{h-20-(h-40)*f:.0f}" stroke="{FILL}"/><text x="36" y="{h-16-(h-40)*f:.0f}" font-size="10" text-anchor="end" fill="{MUTE}">{mx*f:.0f}</text>' for f in (0,.5,1))
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
    """Acordeón 'Asistente': cerrado muestra el conteo; abierto, hasta 3 observaciones con enlace."""
    items=items[:3]
    lis="".join(f'<li><span class="ai-dot" aria-hidden="true"></span><span class="ai-text">{t}</span><a class="ai-link" href="{h}">{l}</a></li>' for t,l,h in items)
    return (f'<details class="ai"{" open" if open_ else ""}><summary><span class="ai-spark" aria-hidden="true">✦</span><span class="ai-title"><b>Asistente</b><small>{len(items)} observaciones para ti · según tu rol y sede</small></span><span class="ai-caret" aria-hidden="true">›</span></summary>'
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
ICON={"Insights de IA":"spark","Inicio":"home","Estudiantes":"users","Cursos":"book","Sesiones":"cal","Profesores":"grad","Nueva matrícula":"plus","Facturación":"doc","Comisiones":"coin","Aprobaciones":"check","Stock por sede":"box","Movimientos y pedidos":"swap","Reportes":"chart","Dashboard ejecutivo":"trend","Usuarios y roles":"lock","Configuración":"cog","Audit log":"compass","Integraciones":"plug"}
_ICON_OLD={"Inicio":"⌂","Estudiantes":"👥","Cursos":"📚","Sesiones":"🗓","Profesores":"🎓","Nueva matrícula":"➕","Facturación":"🧾","Comisiones":"💰","Aprobaciones":"✅","Stock por sede":"📦","Movimientos y pedidos":"🔄","Reportes":"📊","Dashboard ejecutivo":"📈","Usuarios y roles":"🔐","Configuración":"⚙","Audit log":"🧭","Integraciones":"🔌"}

def btn(label, href=None, primary=False, action=None, next=None):
    if href is None and action is None:
        a=ACTIONS.get(label)
        if isinstance(a,str): href=a
        elif a: action,next=a
    cls="btn btn-primary" if primary else ("btn btn-danger" if label in ("Rechazar","Anular matrícula","Marcar no dictada") else "btn")
    if href: return f'<a href="{href}" class="{cls}">{label}</a>'
    if action is None: raise ValueError(f"Botón sin destino ni acción: {label}")
    nx=f' data-next="{next}"' if next else ""
    return f'<button type="button" class="{cls}" data-action="{action}"{nx}>{label}</button>'

def nav(active):
    active=NAV_ALIAS.get(active,active); out=""
    for area,items in NAV:
        items=[(n,h,r) for n,h,r in items if h not in HIDDEN]
        if not items: continue
        roles=",".join(sorted({c for _,_,r in items for c in r.split(",")}))
        links="".join(f'<a href="{h}" data-roles="{r}" class="nav-link{" active" if n==active else ""}">{ico(ICON.get(n,"doc"))}{n}</a>' for n,h,r in items)
        head=f'<div class="nav-area">{area}</div>' if area else ""
        out+=f'<div data-roles="{roles}" style="display:contents">{head}{links}</div>'
    return out

def shell(title, active, *parts, subtitle=""):
    body="".join(parts)
    act=NAV_ALIAS.get(active,active)
    parent=next(((n,h) for _,items in NAV for n,h,_ in items if n==act),None)
    path=(f'<a href="{parent[1]}">{parent[0]}</a> / {title}' if parent and not title.startswith(parent[0]) else (subtitle or ""))
    back=parent[1] if parent and parent[0]!=title else "Home.html"
    return f'''<div class="app">
<aside class="sidebar"><a class="brand" href="Home.html"><img src="assets/logo.webp" alt="Cambridge School of Languages"></a><nav>{nav(active)}</nav><div class="sidebar-ctx"><div class="sidebar-ctx-title">Contexto de prueba</div><label>Sede<select id="sede"><option>Todas</option><option>Quito</option><option>Valle</option><option>Ambato</option></select></label><label>Ver como<select id="rol">{"".join(f'<option value="{c}" data-user="{u}">{n}</option>' for c,n,u in ROLES)}</select></label></div><div class="sidebar-foot">Plataforma Cambridge · mockup v1</div></aside>
<div class="shell-main">
<header class="topbar">
  <div class="crumbs">{'' if active=="Inicio" else f'<a href="{back}" class="back" aria-label="Volver">‹</a>'}<div><h1>{title}</h1><div class="path">{path}</div></div></div>
  <div class="topbar-right">
  <form class="search" action="Estudiantes.html" role="search">{ico("search","nav-ico")}<label for="gsearch" class="sr">Buscar</label><input id="gsearch" name="q" placeholder="Buscar… (Enter)"></form>
  <div class="notif"><button type="button" class="icon-btn" id="notif-btn" aria-label="Notificaciones (3)" aria-expanded="false">{ico("bell","nav-ico")}<span class="dot">3</span></button>
    <div class="notif-pop" id="notif-pop" hidden><div class="notif-head"><b>Notificaciones</b><a href="Notificaciones.html">Ver todas</a></div>
      <a href="Aprobaciones.html" class="notif-item"><span class="notif-ico" style="background:var(--tint-yellow);color:#B45309">!</span><span><b>Descuento 42% pendiente de tu aprobación</b><small>María Andrade · Carla M. · hace 1 día</small></span></a>
      <a href="Inventario.html" class="notif-item"><span class="notif-ico" style="background:var(--tint-red);color:#B91C1C">−</span><span><b>Stock negativo: Empower B1+ en Valle</b><small>Inventario · hoy 08:10</small></span></a>
      <a href="PaymentSheet.html" class="notif-item"><span class="notif-ico" style="background:var(--tint-navy);color:var(--navy)">$</span><span><b>Payment sheet de octubre lista para revisión</b><small>3 alertas · ayer 17:30</small></span></a>
      <a href="Profesores.html" class="notif-item read"><span class="notif-ico" style="background:var(--tint-green);color:#15803D">✓</span><span><b>Profesor M. Castro aprobado</b><small>Ya puede recibir cursos · ayer 11:05</small></span></a>
    </div></div>
  <a href="Chatbot.html" class="icon-btn" aria-label="Asistente">{ico("spark","nav-ico")}</a>
  <div class="user"><span class="avatar sm">E</span><span id="rol-user">Estefanía<small>Administrador General</small></span></div>
  </div>
</header>
<main class="main">
  {f'<p class="kpi-sub" style="margin:0">{subtitle}</p>' if subtitle and parent and not title.startswith(parent[0]) else ''}
  {body}
</main>
</div>
</div>'''

def c2(main, sub):
    """Celda de dos líneas: dato principal + detalle secundario en gris."""
    return f'<span class="c2"><span>{main}</span><small>{sub}</small></span>'
def table(cols, rows, h=46, sede=None, hide=(), wide=0):
    """sede: índice de la columna de sede (filtro global). hide: índices que no se muestran pero siguen filtrando. wide: columna principal."""
    import json as _j, re as _re
    n=len(cols); hide=set(hide)
    def cls(i): return ' td-hide' if i in hide else ''
    hd="".join(f'<div class="th{cls(i)}">{c}</div>' for i,c in enumerate(cols)); body=""
    for r in rows:
        cells="".join(f'<div class="td{cls(i)}" style="min-height:{h}px">{c}</div>' for i,c in enumerate(r))
        sd=""
        if sede is not None:
            m=_re.search(r"Quito|Valle|Ambato|Todas", str(r[sede]))
            if m: sd=f' data-sede="{m.group(0)}"'
        body+=f'<div class="wf-row" style="display:contents"{sd}>{cells}</div>'
    empty='<div class="wf-empty" style="display:none;grid-column:1/-1">Sin resultados con estos filtros</div>'
    tpl=" ".join(("minmax(220px,2.2fr)" if i==wide else ("max-content" if cols[i] in ("Acción","Estado") else "minmax(0,1fr)")) for i in range(n) if i not in hide)
    return f'<div class="tbl-wrap"><div class="wf-table tbl" data-cols=\'{_j.dumps(cols,ensure_ascii=False)}\' style="grid-template-columns:{tpl}">{hd}{body}{empty}</div></div>'

def tabs(items, active, panels=None, roles=None):
    panels=panels or {}; roles=roles or {}; bar=""; body=""
    for t in items:
        label,href = t if isinstance(t,tuple) else (t,None); on=label==active
        rl=f' data-roles="{roles[label]}"' if label in roles else ""
        if href: bar+=f'<a href="{href}" role="tab"{rl} class="tab{" on" if on else ""}">{label}</a>'
        else: bar+=f'<button type="button" role="tab" data-tab="{label}"{rl} aria-selected="{"true" if on else "false"}" class="tab{" on" if on else ""}">{label}</button>'
    for label,content in panels.items():
        on=label==active; rl=f' data-roles="{roles[label]}"' if label in roles else ""
        body+=f'<div role="tabpanel" data-panel="{label}"{rl} class="panel" style="display:{"flex" if on else "none"}">{content}</div>'
    return f'<div class="tabs" role="tablist">{bar}</div>{body}'

def form(fields, cols=2):
    out="".join(f'<div class="field"><label for="f{i}">{f}</label><input id="f{i}" class="ctl"></div>' for i,f in enumerate(fields))
    return f'<div class="grid" style="grid-template-columns:repeat({cols}, minmax(0, 1fr))">{out}</div>'

def kpi(label, value, sub="", tone=0):
    return f'<div class="kpi"><span class="kpi-bar" style="background:{CH[tone%4]}"></span><span class="kpi-label">{label}</span><span class="kpi-value">{value}</span>{f"<span class=kpi-sub>{sub}</span>" if sub else ""}</div>'
def kpis(items):
    return '<div class="grid" style="grid-template-columns:repeat(%d, minmax(0, 1fr))">'%len(items)+"".join(kpi(*i,tone=k) for k,i in enumerate(items))+'</div>'

def sel(label, options, w="160px", col=None):
    i=_nid(); fc="" if col is False else f' data-fcol="{col or label}"'
    return f'<label class="field" style="width:{w}">{label}<select id="{i}"{fc} class="ctl">{"".join(f"<option>{o}</option>" for o in options)}</select></label>'
def search(label, placeholder, w="280px"):
    i=_nid(); return f'<label class="field" style="width:{w}">{label}<input id="{i}" type="search" data-fcol="*" placeholder="{placeholder}" class="ctl"></label>'
def dates(label="Rango de fechas", a="2026-10-01", b="2026-10-31"):
    i=_nid(); return f'<div class="field"><label for="{i}">{label}</label><div style="display:flex;gap:6px;align-items:center"><input id="{i}" type="date" value="{a}" class="ctl" style="width:150px"><span>a</span><input type="date" value="{b}" aria-label="Hasta" class="ctl" style="width:150px"></div></div>'
def filters(*ctrls, actions="", show=3):
    """Los primeros `show` controles se ven siempre; el resto se pliega bajo 'Más filtros'."""
    ctrls=[c for c in ctrls if c]
    main="".join(ctrls[:show]); more=ctrls[show:]
    i=_nid()
    extra=(f'<button type="button" class="btn btn-more" aria-expanded="false" aria-controls="{i}">Más filtros ({len(more)})</button>' if more else "")
    hidden=(f'<div id="{i}" class="filters-more" hidden>{"".join(more)}</div>' if more else "")
    return f'<div class="wf-filters filters">{main}{extra}'+(f'<div class="filters-actions">{actions}</div>' if actions else '')+f'{hidden}</div>'

def note(text, kind="info"):
    return ""  # las notas explicativas se quitaron del mockup a pedido del cliente; la explicación vive en docs/
def kv(*pairs):
    return '<div class="kv">'+"".join(f'<span><span class="k">{k}</span> <b>{v}</b></span>' for k,v in pairs)+'</div>'
def badge(text, kind="neutral"):
    return f'<span class="badge badge-{kind}">{text}</span>'
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
    axis="".join(f'<text x="{xs[i]:.0f}" y="{h-4}" font-size="11" text-anchor="middle" fill="{MUTE}">{l}</text>' for i,l in enumerate(labels))
    grid="".join(f'<line x1="40" x2="{W-20}" y1="{h-20-(h-40)*f:.0f}" y2="{h-20-(h-40)*f:.0f}" stroke="{LINE}"/><text x="36" y="{h-16-(h-40)*f:.0f}" font-size="10" text-anchor="end" fill="{MUTE}">{mx*f:.0f}</text>' for f in (0,.5,1))
    leg="".join(f'<span class="leg"><i style="background:{CH[k%4]};height:3px"></i>{n}</span>' for k,n in enumerate(series))
    return f'<div class="chart"><svg viewBox="0 0 {W} {h}" style="width:100%;height:auto" role="img" aria-label="Gráfico de líneas">{grid}{paths}{axis}</svg><div class="legend">{leg}</div></div>'
def areachart(labels, values, h=150, color=None, unit="%"):
    """Una serie con relleno suave, como el gráfico de tendencia de la referencia."""
    W=600; c=color or CH[0]; mx=max(values) or 1; n=len(labels); xs=[36+i*(W-56)/(n-1) for i in range(n)]
    pts=[(xs[i], h-24-(v/mx)*(h-44)) for i,v in enumerate(values)]
    line=" ".join(f"{x:.0f},{y:.0f}" for x,y in pts); area=f"{pts[0][0]:.0f},{h-24} "+line+f" {pts[-1][0]:.0f},{h-24}"
    gid=_nid()
    axis="".join(f'<text x="{xs[i]:.0f}" y="{h-6}" font-size="11" text-anchor="middle" fill="{MUTE}">{l}</text>' for i,l in enumerate(labels))
    grid="".join(f'<line x1="36" x2="{W-20}" y1="{h-24-(h-44)*f:.0f}" y2="{h-24-(h-44)*f:.0f}" stroke="{LINE}"/><text x="32" y="{h-20-(h-44)*f:.0f}" font-size="10" text-anchor="end" fill="{MUTE}">{mx*f:.0f}{unit}</text>' for f in (0,.5,1))
    last=pts[-1]
    return f'<svg viewBox="0 0 {W} {h}" style="width:100%;height:auto" role="img" aria-label="Tendencia"><defs><linearGradient id="g{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c}" stop-opacity=".35"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></linearGradient></defs>{grid}<polygon points="{area}" fill="url(#g{gid})"/><polyline fill="none" stroke="{c}" stroke-width="2.5" stroke-linejoin="round" points="{line}"/><circle cx="{last[0]:.0f}" cy="{last[1]:.0f}" r="5" fill="{c}" stroke="#fff" stroke-width="2"/>{axis}</svg>'
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
    return f'<div class="wf-pager pager"><span>{total} registros · {per} por página<span class="wf-shown"></span></span><span class="pages">{pages}<a href="#" aria-label="Siguiente" class="pg">›</a></span></div>'
def logo():
    return '<div class="brand brand-dark"><img src="assets/logo.webp" alt="Cambridge School of Languages" style="width:240px"></div>'
def flow(steps):
    return '<ol class="flow-steps">'+"".join((f'<li>{st}</li>'+('<li class="arr" aria-hidden="true">→</li>' if i<len(steps)-1 else '')) for i,st in enumerate(steps))+'</ol>'
def row(*cells, gap=16):
    return f'<div class="row" style="gap:{gap}px">'+"".join(cells)+'</div>'
def two(a,b, ratio="1fr 1fr"):
    return f'<div class="grid" style="grid-template-columns:{ratio}">{a}{b}</div>'
def card(title, inner, extra=""):
    return f'<section class="card"><div class="card-head"><h2>{title}</h2>{extra}</div>{inner}</section>'
def li(items):
    return '<ul class="list">'+"".join(f"<li>{i}</li>" for i in items)+'</ul>'
def course_item(name, meta, pct, status, grade, cert, href="DetalleMatricula.html", tone=0, sessions="", hours=""):
    """Fila de curso matriculado: ícono tintado, nombre, meta, sesiones/horas, anillo, estado, nota, certificado."""
    tints=["var(--tint-navy)","var(--tint-red)","var(--tint-sky)","var(--tint-yellow)"]; inks=[NAVY,RED,"#1B6FA8","#B45309"]
    g=grade.split("/") if "/" in grade else [grade,""]
    return (f'<div class="course"><span class="course-ico" style="background:{tints[tone%4]};color:{inks[tone%4]}"><svg viewBox="0 0 24 24">{SVG["book"]}</svg></span>'
            f'<div class="course-name"><a href="{href}">{name}</a><small>{meta}</small></div>'
            f'<div class="course-meta"><span><svg viewBox="0 0 24 24">{SVG["play"]}</svg>{sessions}</span><span><svg viewBox="0 0 24 24">{SVG["clock"]}</svg>{hours}</span></div>'
            f'{ring(pct,inks[tone%4])}{status}<span class="course-grade">{g[0].strip()}{f"<small>/{g[1].strip()}</small>" if g[1] else ""}</span><span class="cert">Certificado: {cert}</span></div>')
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
  <p style="margin:0;font-size:12px;color:{MUTE};text-align:center">2FA opcional · el rol define qué módulos y sedes se ven al entrar</p>
</form>
</div>'''
page("Main.html","Login",login,"Login")

# 2 Home
home=shell("Inicio","Inicio",
 only("ADM,GER,DIR,SUC,SEC", kpis([("Estudiantes activos",sv(812,420,230,162),"+3% vs mes anterior"),("Ventas del mes (niveles)",sv(76,40,22,14),"meta 70"),("Matrículas con saldo",sv("$12,450","$6,200","$4,100","$2,150"),sv("31 matrículas","15 matrículas","10 matrículas","6 matrículas")),("Aprobaciones pendientes",sv(3,2,1,0),"la más antigua: ayer")]))+
 only("COO,PRO", kpis([("Cursos en curso",sv(41,22,12,7),"esta semana"),("Sesiones por confirmar",sv(3,1,1,1),"de esta semana"),("Terminados sin calificar",sv(2,1,1,0),"bloquean certificados"),("Estudiantes en riesgo",sv(14,6,5,3),"asistencia < 75%")]))+
 only("ASE", kpis([("Mis matrículas del mes",sv(14,14,0,0),"meta 12 · 117%"),("Mis leads Kommo",sv(23,23,0,0),"5 sin contactar"),("Mis matrículas con saldo",sv("$1,420","$1,420","$0","$0"),"4 estudiantes"),("Comisión estimada",sv("$420","$420","$0","$0"),"se paga al cobrar")])),
 only("ADM,GER,DIR,SUC", two(card("Matrículas por mes (niveles vendidos)", areachart(["May","Jun","Jul","Ago","Sep","Oct"],[58,61,55,64,70,76],h=150,unit="")), card("Mix del mes", stacked([("Adults",58),("Teens",24),("Kids",18)])+stacked([("Presencial",63),("Virtual",37)])+'<div class="gauges">'+gauge(71,"Cobrado del mes")+gauge(82,"Ocupación de cursos",CH[2])+gauge(109,"Meta de niveles",CH[3])+'</div>'))) ,
 two(only(APROBADORES, card("Pendientes de aprobación", li(["Descuento 42% · estudiante · asesor","Alta de profesor · coordinación","Asignación profesor sin contrato activo"])+row(btn("Ir a aprobaciones","Aprobaciones.html"))))
     +only("ASE,SEC", card("Mis pendientes", li(["Solicitud de descuento 42% · María Andrade · esperando a Dir. Comercial","4 matrículas con saldo vencido · llamar esta semana","Lead Kommo sin contactar: 5"])+row(btn("Ver estudiantes","Estudiantes.html"))))
     +only("PRO", card("Mis clases de hoy", li(["B1 Virtual · 19:00–21:00 · Zoom 2 · 12 estudiantes","Adults A2 · 18:00–20:00 · C-5 · 9 estudiantes"])+row(btn("Registrar sesión",None,True),btn("Ver mis cursos","Cursos.html")))),
     card("Accesos rápidos", row(only(COMERCIAL,btn("Nueva matrícula",None,True),True),only("ADM,GER,DIR,SUC,ASE,SEC",btn("Nuevo estudiante","NuevoEstudiante.html"),True),only("ADM,GER,SUC,COO",btn("Nuevo curso","NuevoCurso.html"),True),only("ADM,GER,SUC,COO,PRO",btn("Registrar sesión",None,False),True),only("ADM,GER,SUC,COO",btn("Payment sheet","PaymentSheet.html"),True),only("ADM,GER,DIR,ASE",btn("Comisiones","Comisiones.html"),True),only("ADM,GER,SUC,COO,SEC",btn("Inventario","Inventario.html"),True),only("ADM,GER,DIR,SUC,COO",btn("Reportes","Reportes.html"),True)))),
 only("ADM,GER,DIR,SUC", ai([("Octubre va 9% sobre la meta de niveles, pero Ambato lleva 2 semanas sin matrículas nuevas y tiene 2 cursos por abrir con menos de 5 inscritos.","Ver cursos de Ambato","Cursos.html"),("Hay $12,450 en matrículas con saldo; el 60% está en 4 cursos que terminan en noviembre. Conviene cobrar antes del cierre.","Ver matrículas con saldo","Cursos.html"),("La payment sheet de octubre tiene 3 alertas: una diferencia de $26 y una factura de profesor sin sesiones registradas.","Revisar payment sheet","PaymentSheet.html"),("Stock negativo en 3 libros de cursos que ya están en curso: 4 estudiantes sin material.","Ver inventario","Inventario.html")],"Pregunta: ¿qué cursos terminan este mes con saldo pendiente?"))+
 only("COO,PRO", ai([("Hoy hay 3 sesiones sin confirmar; dos son de P. Gómez y la tercera (Teens A2, Ambato) lleva 2 días pendiente.","Confirmar sesiones","Sesiones.html"),("Adults A1 Sábados terminó hace 5 días y sigue sin calificar: 14 estudiantes esperan su certificado y no pueden matricularse en A2.","Calificar curso","DetalleCurso.html"),("Teens B1 Virtual abre en 2 semanas sin profesor. P. Gómez tiene libre Lu-Ma-Mi-Ju 17:00–19:00 y ya dicta B1.","Ver perfil de P. Gómez","FichaProfesor.html"),("4 estudiantes con asistencia menor a 60% en B1 Virtual: riesgo de perder el módulo.","Ver estudiantes del curso","DetalleCurso.html")],"Pregunta: ¿qué profesores tienen horas libres el sábado?"))+
 only("ASE,SEC", ai([("Tienes 5 leads de Kommo sin contactar desde hace más de 3 días; dos preguntaron por B1 Virtual, que abre el 3 de noviembre con 3 cupos.","Ver leads","Estudiantes.html"),("4 estudiantes tuyos tienen saldo vencido ($1,420). Dos de ellos terminan curso en noviembre.","Ver matrículas con saldo","Cursos.html"),("Tu solicitud de descuento del 42% para María Andrade sigue pendiente desde ayer; con 10% la matrícula se puede cerrar hoy.","Ver solicitud","SolicitudDescuento.html")],"Pregunta: ¿cuántos niveles me faltan para el bono del mes?")),
 subtitle="Resumen del día según tu rol")
page("Home.html","Inicio",home,"Inicio por rol")

# 3 Estudiantes
est=shell("Estudiantes","Estudiantes",
 filters(search("Buscar","Nombre, cédula o email",w="300px"),sel("Estado",["Todos","Activo","En transición","Inactivo"],w="150px"),sel("Programa",["Todos","Adults","Teens","Kids"],w="130px"),sel("Nivel",["Todos","A1","A2","B1","B2","Kids 1","Kids 2"],w="120px"),sel("Asesor",["Todos","Carla M.","Diego R.","Sofía L."],w="130px"),sel("Vista",["Alumnos activos","Alumnos inactivos","Duplicados entre sedes","Matrículas con saldo","Nuevos este mes"],w="190px",col=False),actions=only(COMERCIAL,btn("Nuevo estudiante",None,True),True)+only("ADM,GER,SUC,SEC",btn("Importar / Exportar"),True)),
 note("Las vistas guardadas reemplazan las de TeamDesk (Alumnos indexados activos / inactivos / x cruzar). Un nivel = 2 módulos; se muestra el nivel comercial y el módulo académico en curso."),
 table(["Nombre","Cédula","Sede","Programa","Nivel","Asesor","Estado","Acción"],[
  [c2("María Andrade","1712345678 · Quito · English for Adults · asesor Carla M."),"1712345678","Quito","Adults","B1 · módulo 7","Carla M.",badge("Activo","ok"),'<a href="Ficha360.html">Ver ficha</a>'],
  [c2("Juan Pérez","1723456789 · Valle · English for Adults · asesor Diego R."),"1723456789","Valle","Adults","A2 · módulo 4","Diego R.",badge("En transición","warn"),'<a href="Ficha360.html">Ver ficha</a>'],
  [c2("Luis Torres","1834567890 · Ambato · English for Adults · asesor Sofía L."),"1834567890","Ambato","Adults","A1 · módulo 1","Sofía L.",badge("Inactivo","neutral"),'<a href="Ficha360.html">Ver ficha</a>'],
  [c2("Ana Ruiz (menor)","1745678901 · Quito · English for Kids · asesor Carla M."),"1745678901","Quito","Kids","Kids 2","Carla M.",badge("Activo","ok"),'<a href="Ficha360.html">Ver ficha</a>'],
  [c2("Pedro Mora","1756789012 · Valle · English for Adults · asesor Diego R."),"1756789012","Valle","Adults","B1 · módulo 8","Diego R.",badge("Activo","ok"),'<a href="Ficha360.html">Ver ficha</a>'],
  [c2("Camila Sánchez","1867890123 · Ambato · English for Teens · asesor Sofía L."),"1867890123","Ambato","Teens","A2 · módulo 10","Sofía L.",badge("Activo","ok"),'<a href="Ficha360.html">Ver ficha</a>'],
  [c2("Diego Vargas (menor)","1778901234 · Valle · English for Kids · asesor Diego R."),"1778901234","Valle","Kids","Kids 1","Diego R.",badge("Activo","ok"),'<a href="Ficha360.html">Ver ficha</a>'],
  [c2("Valeria Cedeño","1789012345 · Quito · English for Adults · asesor Carla M."),"1789012345","Quito","Adults","B2 · módulo 11","Carla M.",badge("Activo","ok"),'<a href="Ficha360.html">Ver ficha</a>'],
  [c2("Mateo Salazar (menor)","1890123456 · Ambato · English for Teens · asesor Sofía L."),"1890123456","Ambato","Teens","A1 · módulo 2","Sofía L.",badge("En transición","warn"),'<a href="Ficha360.html">Ver ficha</a>'],
  [c2("Gabriela Núñez","1701234567 · Quito · English for Adults · asesor Carla M."),"1701234567","Quito","Adults","A2 · módulo 3","Carla M.",badge("Inactivo","neutral"),'<a href="Ficha360.html">Ver ficha</a>']],sede=2,hide=(1,2,3),wide=0),
 pager(sv(812,420,230,162)),
 subtitle="Una sola base para Quito, Valle y Ambato · exportar queda registrado en el audit log")
page("Estudiantes.html","Estudiantes",est,"Listado de estudiantes")

# 4 Ficha 360
ficha=shell("María Andrade","Estudiantes",
 f'''<div class="grid" style="grid-template-columns:320px 1fr">
  <aside class="profile"><div class="profile-cover"></div><div class="profile-body">{avatar("MA")}<div class="chips" style="justify-content:center;gap:8px"><span class="badge badge-navy">EST-00412</span>{badge("Activa","bad").replace("badge-bad","badge-bad")}</div><h2>María Andrade</h2><span class="kpi-sub">Matriculada el 12 ene 2026 · Quito</span>
    <div class="actions"><button type="button" class="btn" style="flex:0 0 46px" aria-label="Llamar" data-action="Se abre el marcador con el teléfono del estudiante y se registra el contacto en su historial.">{ico("phone")}</button><button type="button" class="btn" style="flex:0 0 46px" aria-label="Email" data-action="Se abre un correo con la plantilla de contacto y queda registrado en el historial.">{ico("mail")}</button><button type="button" class="btn" style="background:var(--tint-navy);border-color:var(--tint-navy)" data-action="Se abre WhatsApp con la plantilla elegida (enlace de clase, recordatorio de saldo, certificado listo).">{ico("chat")}&nbsp;WhatsApp</button></div>
    <div class="section"><h3>Contacto</h3><div class="clist"><div><span class="cico">{ico("mail","")}</span><span><b>Email</b>maria.andrade@example.com</span></div><div><span class="cico">{ico("phone","")}</span><span><b>Teléfono</b>099 000 0001</span></div><div><span class="cico">{ico("pin","")}</span><span><b>Dirección</b>Quito · La Carolina</span></div><div><span class="cico">{ico("id","")}</span><span><b>Cédula · ID legado</b>1712345678 · TeamDesk Quito 001-2026xxxxx</span></div><div><span class="cico">{ico("grad","")}</span><span><b>Programa · asesor</b>English for Adults · B1 (módulo 7 de 16) · Carla M.</span></div></div></div>
    <div class="section"><h3>Logros y certificados</h3><div class="awards"><div><i>🏅</i>Certificado A1 · dic 2025</div><div><i>🏅</i>Certificado A2 · jun 2026 · nota 85</div><div><i>🏅</i>Asistencia perfecta · módulo 5</div><div><i>🏅</i>Mejor progreso del grupo · módulo 6</div><div><i>🏅</i>Referido: trajo a 1 estudiante</div></div></div>
    <div class="actions">{btn("Nueva matrícula",None,True)}<a href="NuevoEstudiante.html" class="btn">{ico("edit")}&nbsp;Editar</a></div></div></aside>
  <div style="display:flex;flex-direction:column;gap:20px;min-width:0">
    <div class="grid" style="grid-template-columns:1.25fr 1fr">
      {card("Actividad de aprendizaje", '<div class="hours"><b>6</b><span>horas</span><b>30</b><span>minutos esta semana</span></div>'+stackbars(["Lu","Ma","Mi","Ju","Vi","Sa","Do"],{"B1 Virtual":[2,2,2,2,0,0,0],"Club de conversación":[0,1,0,0,0,0,0],"Moodle":[0.5,0,0.5,0,1,0,0]},h=160)+'<div class="chips"><span class="chip" style="background:var(--tint-navy)"><b>8 h</b>B1 Virtual · P. Gómez</span><span class="chip" style="background:var(--tint-red)"><b>1 h</b>Club de conversación</span><span class="chip" style="background:var(--tint-sky)"><b>2 h</b>Tareas en Moodle</span></div>', sel("Período",["Esta semana","Últimas 4 semanas","Módulo actual"],w="160px",col=False))}
      {card("Rendimiento", '<div class="perf">'+gauge(84,"Puntaje total",segments=True)+'<div class="perf-legend"><div><i style="background:#16A34A"></i>Participación<b>55%</b></div><div><i style="background:#F6C21C"></i>Quiz en clase<b>15%</b></div><div><i style="background:#F59E0B"></i>Examen<b>10%</b></div><div><i style="background:#D62839"></i>Ausencias<b>10%</b></div></div></div><div class="trend"><div class="big"><b>84% <span class="up">+3.4%</span></b>últimos 6 meses</div>'+areachart(["May","Jun","Jul","Ago","Sep","Oct"],[72,78,75,81,83,84],h=140)+'</div><div class="quote">Va al día con el módulo 7 y mejoró 12 puntos desde mayo. Si mantiene la asistencia, cierra B1 en noviembre con certificado. 💪</div>', sel("Período",["Últimos 6 meses","Módulo actual","Todo"],w="160px",col=False))}
    </div>
    {card("Cursos matriculados", course_item("English for Adults B1 Virtual","Adults · B1 · módulo 7 · P. Gómez",60,badge("En curso","warn"),"84 / 100",badge("Pendiente"),tone=0,sessions="18",hours="36 h")+course_item("English for Adults A2","Adults · A2 · módulos 3–6 · L. Vega",100,badge("Completado","bad"),"85 / 100",badge("A2.pdf","navy"),tone=2,sessions="36",hours="72 h")+course_item("English for Adults A1","Adults · A1 · módulos 1–2 · L. Vega",100,badge("Completado","bad"),"80 / 100",badge("A1.pdf","navy"),tone=3,sessions="18",hours="36 h")+course_item("Club de conversación B1","Extracurricular · sábados · S. Jiménez",35,badge("En curso","warn"),"—",badge("Ninguno"),tone=1,sessions="4",hours="4 h")+course_item("English for Adults B2 · por abrir","Adults · B2 · módulos 11–14 · inicia mar 2027",0,badge("Pendiente"),"—",badge("Ninguno"),tone=0,sessions="0",hours="0 h"), filters(search("Buscar","Curso, categoría…",w="240px"),sel("Estado",["Todos","En curso","Completado","Pendiente"],w="130px",col=False),actions='<a href="Cursos.html" class="btn btn-primary">Ver todos</a>'))}
  </div>
</div>''',
 tabs(["Datos","Matrículas y notas","Niveles / crédito","Facturas y pagos","Archivos y certificados","Historial"],"Matrículas y notas",roles={"Niveles / crédito":COMERCIAL,"Facturas y pagos":COMERCIAL,"Historial":"ADM,GER,DIR,SUC,COO,SEC"},panels={
  "Datos": two(card("Datos personales", form(["Nombres","Apellidos","Cédula / ID","Fecha de nacimiento","Email","Teléfono","Dirección","Sede"])),
               card("Comercial y origen", form(["Asesor asignado","Lead Kommo (origen)","Ocupación / empresa","Cómo nos conoció"])+note("Mayor de edad: no requiere representante. Si fuera menor, aquí van nombre, cédula y teléfono del representante y la autorización firmada.")))+row(btn("Guardar cambios",None,True)),
  "Matrículas y notas": table(["Matrícula","Curso","Horario","Módulo","Total","Pagado","Saldo","Asistencia","Nota","Estado","Acción"],[
     ["001-202602794","0001-2026-0767 · English for Adults B1 Virtual","Lu-Ma-Mi-Ju 19:00–21:00","7","$230","$230","$0","90%","—",badge("En curso","ok"),'<a href="DetalleMatricula.html">Ver</a>'],
     ["001-202601245","0001-2026-0620 · English for Adults A2","Lu-Mi 18:00–20:00","4","$240","$240","$0","95%","85 · Pass",badge("Aprobado","ok"),'<a href="DetalleMatricula.html">Ver</a>'],
     ["001-202601102","0001-2026-0512 · English for Adults A2","Lu-Mi 18:00–20:00","3","$240","$240","$0","92%","88 · Pass",badge("Aprobado","ok"),'<a href="DetalleMatricula.html">Ver</a>'],
     ["001-202500811","0001-2025-0430 · English for Adults A1","Sa 09:00–13:00","2","$495","$455","$0","88%","80 · Pass",badge("Aprobado","ok"),'<a href="DetalleMatricula.html">Ver</a>']])
     +kv(("Matrículas","4"),("Módulos aprobados","6"),("Asistencia promedio","91%"),("Saldo total","$0"))
     +note("Cada matrícula conserva su número y código de curso de TeamDesk (migración). Notas y asistencia se sincronizan desde Moodle cada noche; nota mínima para Pass: 70."),
  "Niveles / crédito": two(card("Niveles comprados vs consumidos", kv(("Comprados","4 niveles (A1, A2, B1, B2)"),("Consumidos","2"),("En curso","1 (B1)"),("Pendiente","1 (B2)"))+progress(56,"Avance del paquete · 9 de 16 módulos")+table(["Nivel","Estado","Curso","Cierre"],[["A1",badge("Pass","ok"),"Adults A1 · L. Vega","dic 2025"],["A2",badge("Pass","ok"),"Adults A2 · L. Vega","jun 2026"],["B1",badge("En curso"),"Adults B1 Virtual · P. Gómez","—"],["B2",badge("Pendiente","warn"),"Sin asignar","—"]])),
     card("Resumen financiero", kv(("Factura","#1234 (B1–B2)"),("Total","$980"),("Pagado","$980"),("Saldo","$0"),("Descuento","10% aprobado por Dir. Comercial"))+hbars([("Facturado",1880),("Cobrado",1880),("Notas de crédito",45)],"$")+row('<a href="DetalleFactura.html" style="font-size:13px">Ver factura #1234</a>')))+
     card("Cursos tomados", table(["Curso","Nivel","Profesor","Estado","Nota"],[["Adults B1 Virtual","B1","P. Gómez","En curso","—"],["Adults A2","A2","L. Vega","Pass","85"]])),
  "Facturas y pagos": table(["Factura","Concepto","Total","Pagado","Saldo","Estado","Acción"],[["#1234","Paquete B1–B2 (2 niveles)","$980","$980","$0","Pagada",btn("Ver","DetalleFactura.html")],["#1102","Paquete A1–A2 (2 niveles)","$900","$900","$0","Pagada",btn("Ver","DetalleFactura.html")],["NC-07","Nota de crédito · libro devuelto","-$45","—","—","Aplicada",btn("Ver","DetalleFactura.html")]])+row(btn("Nueva venta","NuevaVenta.html",True),btn("Registrar pago")),
  "Archivos y certificados": two(card("Archivos", table(["Archivo","Tipo","Subido por","Fecha"],[["cedula_maria_andrade.pdf","Identificación","Carla M.","12 ene"],["contrato_matricula_2026.pdf","Contrato de matrícula","Carla M.","02 oct"],["comprobante_transferencia_884512.pdf","Comprobante de pago","Secretaría","02 oct"]])+row(upload("Adjuntar archivo","PDF, JPG o PNG · máx. 10 MB"),btn("Subir archivo",None,True))),
     card("Certificados emitidos", table(["Nivel","Nota","Emitido","Acción"],[["A1","80 · Pass","dic 2025",btn("Descargar PDF")],["A2","85 · Pass","jun 2026",btn("Descargar PDF")]])+row(btn("Emitir certificado"))+note("Los exámenes internacionales (tabla International Exams de TeamDesk) no están en los 11 módulos del contrato: se migran como archivo histórico y se confirma con el cliente si se gestionan aquí."))),
  "Historial": table(["Fecha/hora","Usuario","Acción","Detalle"],[["04 oct 10:12","Carla M.","Creó venta","Paquete B1–B2 · 10% descuento"],["04 oct 09:40","Dir. Comercial","Aprobó descuento","42% rechazado → 10% aprobado"],["30 jun 16:00","Sistema","Cerró nivel","A2 · Pass · nota 85"],["12 ene 11:05","Secretaría","Creó estudiante","Alta desde lead Kommo"]])+note("Vista filtrada del audit log para este estudiante. El registro completo está en Configuración → Audit log."),
 }),
 only("ADM,GER,DIR,SUC,COO,ASE,SEC", ai([("Lleva 4 módulos aprobados con 91% de asistencia; al ritmo actual termina B2 en junio 2027. Buen candidato para ofrecer el paquete B2–C1 antes del cierre de B1.","Nueva matrícula","NuevaVenta.html"),("Faltó 2 veces seguidas la semana pasada en B1 Virtual (antes nunca). Vale la pena un mensaje antes de que afecte el módulo.","Ver asistencia","DetalleMatricula.html"),("Su descuento del 10% fue por referido: trajo a Pedro Mora, que ya está matriculado.","Ver detalle de comisión","DetalleComision.html")],"Pregunta: ¿qué nivel le toca y cuándo abre el próximo curso?")),
 subtitle="Ficha 360°: todo lo del estudiante en una sola vista")
page("Ficha360.html","Ficha estudiante",ficha,"Ficha 360 del estudiante")

# 5 Nueva venta
steps=["1 Estudiante","2 Niveles y curso","3 Descuento","4 Pago","5 Matrícula"]
stepper='<div class="stepper">'+"".join(f'<div class="step{" on" if i==2 else (" done" if i<2 else "")}">{s}</div>' for i,s in enumerate(steps))+'</div>'
venta=shell("Nueva matrícula · venta por niveles","Nueva matrícula",
 stepper,
 two(card("Estudiante, niveles y curso", kv(("Estudiante","María Andrade"),("Sede","Quito"),("Asesor (vendor)","Carla M."))+table(["Nivel","Módulos","Modalidad","Precio"],[["B1","7 y 8","Virtual","$500"],["B2","9 y 10","Virtual","$500"]])+filters(sel("Curso para el primer módulo",["0001-2026-0767 · Adults B1 Virtual · Lu-Ma-Mi-Ju 19:00–21:00 · 12/15","0001-2026-0772 · Adults B1 · Sa 09:00–13:00 · 9/12"],w="100%",col=False),sel("Plan de pago",["Contado","2 cuotas","4 cuotas"],w="140px",col=False),sel("Facturar a",["Estudiante","Empresa Andina S.A. (convenio 15%)","Clínica Valle (convenio 10%)","Otra empresa…"],w="260px",col=False))+kv(("Niveles","2 (4 módulos)"),("Precio lista","$1,000"),("Libros","B1 + B2 · $80"),("Inicio","3 nov 2026"))),
     card("Descuento", filters(sel("Descuento %",["0%","5%","10%","15%","20%"],w="120px"),sel("Motivo (obligatorio)",["Referido","Promoción","Convenio empresa","Otro"],w="220px"))+note("Hasta 10% lo aplica el asesor. Más de 10% pasa a aprobación del Director Comercial y la venta queda en espera.","warn")+row(btn("Solicitar aprobación","SolicitudDescuento.html")))),
 card("Resultado", table(["Concepto","Cant.","Precio","Descuento","Total"],[["Matrícula (tuition fee)","1","$0","—","$0"],["Nivel B1 (módulos 7–8)","1","$500","10% · referido","$450"],["Nivel B2 (módulos 9–10)","1","$500","10% · referido","$450"],["Libros / materiales B1 + B2","2","$40","—","$80"]])+filters(sel("Método de pago",["Transferencia","Efectivo","Tarjeta","Crédito directo"],w="180px"),actions=kv(("Subtotal","$1,080"),("Descuento","-$100"),("Total","$980")))+note("Una sola matrícula y una factura consolidada por el paquete (en TeamDesk hoy son 4 enrollments y 4 facturas por módulo). Al confirmar: el estudiante queda en el curso elegido, se comprometen 2 libros y se registra la comisión del asesor en estado pendiente.")+row(btn("Atrás"),btn("Confirmar matrícula y emitir factura","DetalleMatricula.html",True))),
 subtitle="Reemplaza la facturación 1:1 por módulo")
page("NuevaVenta.html","Nueva matrícula",venta,"Nueva matrícula (venta por niveles)")

# 5b Detalle de matrícula (equivalente al Enrollment de TeamDesk, pero por paquete de niveles)
page("DetalleMatricula.html","Detalle matrícula",shell("Matrícula 001-202602794","Estudiantes",
 row(kv(("Estudiante",'<a href="Ficha360.html">María Andrade</a>'),("Curso",'<a href="DetalleCurso.html">0001-2026-0767 · English for Adults B1 Virtual</a>'),("Horario","Lu-Ma-Mi-Ju 19:00–21:00"),("Inicio","3 nov 2026"),("Fin","20 feb 2027"),("Asesor (vendor)","Carla M."),("Plan de pago","Contado"),("Estado",badge("En curso","ok"))),'<div style="margin-left:auto"></div>',only(COMERCIAL+",COO",btn("Cambio de curso"),True),only(ACADEMICO+",SEC",btn("Enviar enlace de clase"),True),only(ACADEMICO+",SEC",btn("Hoja de asistencia"),True),only("ADM,GER,DIR,SUC",btn("Anular matrícula"),True)),
 only(COMERCIAL,
 two(card("Resumen", kv(("Subtotal","$1,080"),("Descuento","-$100 (10% referido)"),("Total","$980"),("Pagado","$980"),("Saldo","$0"))+progress(50,"Paquete · módulo 7 de 10 comprados (B1–B2)")),
     card("Cargos y descuentos", table(["Concepto","Monto","Descuento","Subtotal","Observación"],[["Matrícula (tuition fee)","$0","—","$0","—"],["Nivel B1 (módulos 7–8)","$500","10%","$450","Beneficio referido · aprobado Dir. Comercial"],["Nivel B2 (módulos 9–10)","$500","10%","$450","—"],["Libros / materiales","$80","—","$80","Empower B1+ SB + WB"]])))),
 only("COO,PRO", card("Resumen académico", kv(("Paquete","B1–B2 · módulos 7 a 10"),("Módulo en curso","7"),("Asistencia","18/20 · 90%"),("Nota parcial","—"),("Estado",badge("En curso","ok")))+progress(50,"Paquete · módulo 7 de 10"))),
 tabs(["Facturas y pagos","Códigos de libros","Asistencia","Certificados","Comisión"],"Facturas y pagos",roles={"Facturas y pagos":COMERCIAL,"Comisión":"ADM,GER,DIR,ASE"},panels={
  "Facturas y pagos": table(["Factura","Fecha","Monto","Pagado","Saldo","Estado","Acción"],[["#1234","02 oct 2026","$980","$980","$0",badge("Pagada","ok"),'<a href="DetalleFactura.html">Ver</a>']])+row(btn("Registrar pago"),btn("Emitir nota de crédito")),
  "Códigos de libros": table(["Material","ISBN","Código de activación","Entregado","Acción"],[["Empower B1+ Intermediate Combo B SB (digital pack)","9781108961523","EMP-B1-7K2Q-••••","02 oct 2026",badge("Activado","ok")],["Empower B1+ Workbook","9781108961530","Pendiente","—",btn("Asignar código",None,False)]])+note("Los códigos de activación de material digital se compran a Books & Bits con el pedido y se asignan al estudiante al entregar el libro (hoy: 'Purchased Book Codes' en TeamDesk)."),
  "Asistencia": table(["Sesión","Fecha","Presente","Observación"],[["1","3 nov · 19:00","✓","—"],["2","4 nov · 19:00","✓","—"],["3","5 nov · 19:00","✗","Aviso previo"],["4","6 nov · 19:00","✓","—"]])+kv(("Asistencia","18/20 · 90%"),("Mínimo para aprobar","75%")),
  "Certificados": table(["Nivel","Nota","Emitido","Acción"],[["B1","Pendiente de cierre","—",btn("Emitir certificado")]]),
  "Comisión": kv(("Asesor","Carla M."),("Regla","Rango 11+ · 4% virtual"),("Monto","$40"),("Estado",badge("Pendiente · se paga en el cierre de octubre","warn")))+row('<a href="DetalleComision.html" style="font-size:13px">Ver detalle de comisiones del asesor</a>'),
 }),
 subtitle="Una matrícula por paquete de niveles: reemplaza al Enrollment por módulo de TeamDesk"),"Detalle de matrícula")

# 6 Aprobaciones
apr=shell("Bandeja de aprobaciones","Aprobaciones",
 tabs(["Todas (3)","Descuentos","Profesores","Asignaciones"],"Todas (3)",{
  "Todas (3)": table(["Tipo","Detalle","Solicitado por","Fecha","Acción"],[["Descuento","42% · María Andrade · motivo: referido","Carla M. (asesor)","Hoy",row(btn("Aprobar",None,True),btn("Rechazar"),gap=8)],["Alta profesor","Nuevo profesor · tarifa $7/h · contrato por horas","Coordinación académica","Ayer",row(btn("Aprobar",None,True),btn("Rechazar"),gap=8)],["Asignación","Profesor sin contrato activo en curso B1","Coordinación académica","Ayer",row(btn("Aprobar",None,True),btn("Rechazar"),gap=8)]],h=64),
  "Descuentos": table(["Tipo","Detalle","Solicitado por","Fecha","Acción"],[["Descuento","42% · María Andrade · motivo: referido","Carla M. (asesor)","Hoy",row(btn("Aprobar",None,True),btn("Rechazar"),gap=8)]],h=64)+note("Regla vigente: hasta 10% lo aplica el asesor. Más de 10% requiere Director Comercial."),
  "Profesores": table(["Tipo","Detalle","Solicitado por","Fecha","Acción"],[["Alta profesor","Nuevo profesor · tarifa $7/h · contrato por horas","Coordinación académica","Ayer",row(btn("Aprobar",None,True),btn("Rechazar"),gap=8)]],h=64)+note("El profesor queda 'Pendiente de aprobación' hasta que Dirección apruebe. Recién ahí puede recibir cursos y aparecer en la payment sheet."),
  "Asignaciones": table(["Tipo","Detalle","Solicitado por","Fecha","Acción"],[["Asignación","Profesor sin contrato activo en curso B1","Coordinación académica","Ayer",row(btn("Aprobar",None,True),btn("Rechazar"),gap=8)]],h=64)+note("Se bloquea la asignación de un profesor sin contrato vigente hasta que Coordinación apruebe la excepción.","warn"),
 }),
 card("Decisiones recientes", table(["Fecha","Tipo","Detalle","Decisión","Por","Justificación"],[["Ayer 16:20","Descuento","15% · Ana Ruiz","Aprobado","Dir. Comercial","Convenio empresa"],["Ayer 11:05","Alta profesor","M. Castro · $6.50/h","Aprobado","Dirección","Contrato firmado adjunto"],["02 oct","Descuento","30% · Luis Torres","Rechazado","Dir. Comercial","Sin motivo válido"]])+note("Cada decisión queda en el audit log con quién, cuándo y justificación. El solicitante recibe notificación en la plataforma y por email.")),
 subtitle="Control preventivo: nada sensible pasa sin un segundo par de ojos")
page("Aprobaciones.html","Aprobaciones",apr,"Bandeja de aprobaciones")

# 7 Cursos
V='<a href="DetalleCurso.html">Ver</a>'
cursos=shell("Cursos","Cursos",
 filters(search("Buscar","Código, nombre o profesor",w="240px"),sel("Vista",["Todos los cursos","Cursos abiertos por horario","Disponibilidad (cupos libres)","Cursos con saldos de estudiantes","Terminados sin calificar","Próximos a iniciar","Cerrados"],w="230px",col=False),sel("Programa",["Todos","Adults","Teens","Kids","Tailored"],w="130px"),sel("Nivel",["Todos","A1","A2","B1","B2","Kids 1","Kids 2"],w="110px"),sel("Modalidad",["Todas","Virtual","Presencial"],w="130px"),sel("Profesor",["Todos","P. Gómez","L. Vega","M. Castro","(sin asignar)"],w="150px"),sel("Estado",["Todos","En curso","Por abrir","Sin calificar","Cerrado"],w="160px"),actions=only("ADM,GER,SUC,COO",btn("Nuevo curso",None,True),True)),
 kpis([("Cursos en curso",sv(41,22,12,7),"esta semana"),("Por abrir",sv(6,2,3,1),"inician en 30 días"),("Con saldos de estudiantes",sv(9,4,3,2),sv("$2,840 pendientes","$1,320","$980","$540")),("Terminados sin calificar",sv(2,1,1,0),"bloquean certificados")]),
 table(["Curso","Sede","Programa","Modalidad","Nivel","Profesor","Cupo","Avance","Estado","Acción"],[
  [c2("English for Adults B1 Virtual","0001-2026-0767 · Quito · Zoom 2 · Lu-Ma-Mi-Ju 19:00–21:00 · Virtual"),"Quito","Adults","Virtual","B1","P. Gómez","12/15",progress(60),badge("En curso","ok"),V],
  [c2("English for Kids 2 Tarde","0001-2026-0328 · Valle · C-3 · Sa 09:00–13:00 · Presencial"),"Valle","Kids","Presencial","Kids 2","L. Vega","8/10",progress(55),badge("En curso","ok"),V],
  [c2("English for Teens A2","0001-2026-0192 · Ambato · A-1 · Vi 15:00–19:00 · Presencial"),"Ambato","Teens","Presencial","A2","(sin asignar)","5/10",progress(0),badge("Por abrir","warn"),V],
  [c2("English for Adults A2","0001-2026-0620 · Valle · C-5 · Lu-Mi 18:00–20:00 · Presencial"),"Valle","Adults","Presencial","A2","P. Gómez","9/12",progress(59),badge("En curso","ok"),V],
  [c2("English for Kids 1 Mañana","0001-2026-0518 · Ambato · A-2 · Lu-Mi 16:00–18:00 · Presencial"),"Ambato","Kids","Presencial","Kids 1","M. Castro","7/10",progress(28),badge("En curso","ok"),V],
  [c2("English for Adults B2 Intensivo","0001-2026-0538 · Quito · Q-4 · Sa 09:00–13:00 · Presencial"),"Quito","Adults","Presencial","B2","L. Vega","11/12",progress(46),badge("En curso","ok"),V],
  [c2("English for Adults A1 Sábados","0001-2026-0430 · Quito · Q-1 · Sa 09:00–13:00 · Presencial"),"Quito","Adults","Presencial","A1","L. Vega","14/15",progress(100),badge("Sin calificar","bad"),V],
  [c2("English for Teens B1 Virtual","0001-2026-0772 · Valle · Teams 1 · Lu-Ma-Mi-Ju 19:00–21:00 · Virtual"),"Valle","Teens","Virtual","B1","P. Gómez","6/12",progress(0),badge("Por abrir","warn"),V],
  [c2("English for Kids 2 Mañana","0001-2026-0599 · Quito · Q-2 · Sa 09:00–13:00 · Presencial"),"Quito","Kids","Presencial","Kids 2","M. Castro","10/10",progress(53),badge("En curso","ok"),V],
  [c2("Tailored · Inglés corporativo","0001-2026-0608 · Ambato · Zoom 1 · Ma-Ju 07:00–08:30 · Virtual"),"Ambato","Tailored","Virtual","B1","(sin asignar)","3/12",progress(0),badge("Por abrir","warn"),V],
  [c2("English for Teens A2","0001-2025-0330 · Valle · C-2 · Vi 15:00–19:00 · Presencial"),"Valle","Teens","Presencial","A2","L. Vega","9/10",progress(100),badge("Cerrado"),V]],sede=1,hide=(1,2,3),wide=0),
 pager(sv(58,29,18,11)),
 note("El código de curso conserva el formato de TeamDesk (0001-AAAA-NNNN) para la migración y la reconciliación. Avance = % de horas dictadas sobre el total."),
 only("ADM,GER,SUC,COO", ai([("Adults A1 Sábados terminó hace 5 días sin calificar: 14 estudiantes no pueden matricularse en A2 y hay 3 cupos esperándolos en 0001-2026-0620.","Calificar","DetalleCurso.html"),("Dos cursos 'por abrir' en Ambato tienen menos de 5 inscritos a 2 semanas del inicio. Históricamente no abren con menos de 6.","Ver cursos de Ambato","Cursos.html"),("El aula Q-1 está al 60% de ocupación y C-2 (Valle) al 0%: el nuevo Kids 2 podría ir a C-2 el sábado.","Ver aulas","Configuracion.html")],"Pregunta: ¿qué cursos abren en noviembre y cuántos libros necesitan?")),
 subtitle="Programa, nivel, modalidad, horario y aula por sede")
page("Cursos.html","Cursos",cursos,"Listado de cursos")

# 8 Detalle curso
det=shell("0001-2026-0767 · English for Adults B1 Virtual · Quito","Cursos",
 row(kv(("Programa","English for Adults"),("Nivel","B1 · módulos 7–8"),("Horario","Lu-Ma-Mi-Ju 19:00–21:00"),("Inicio","1 sep 2026"),("Fin","20 nov 2026"),("Aula","Zoom 2"),("Cupo","12/15"),("Libro","Empower B1+ Intermediate Combo B")),'<div style="margin-left:auto"></div>',btn("Registrar sesión",None,True),btn("Enviar enlace de clase"),btn("Hoja de asistencia"),btn("Editar curso")),
 progress(60,"Avance del curso · 22 de 36 horas dictadas · termina en 7 semanas"),
 two(card("Profesor asignado", kv(("Profesor",'<a href="FichaProfesor.html">P. Gómez</a>'),("Contrato",badge("Activo hasta dic 2026","ok")),("Tarifa","$7.00/h"),("Horas en este curso","22 h · $154"))+filters(sel("Cambiar profesor",["P. Gómez","L. Vega","M. Castro","R. Salas (contrato vencido)"],w="260px"),actions=btn("Cambiar",None,False,"Si el nuevo profesor no tiene contrato activo, el cambio queda pendiente de aprobación de Coordinación."))+note("Cambiar profesor valida contrato activo. Si no lo tiene, la asignación va a la bandeja de aprobaciones.")),
     card("Sesiones", table(["Fecha","Horas","Registro"],[["01 oct","2","Automático"],["03 oct","2","Manual"],["06 oct","2","Pendiente"]]))),
 card("Estudiantes matriculados", filters(sel("Mostrar",["Todos","Con saldo pendiente","En riesgo (asistencia < 75%)"],w="220px",col=False),actions=only(ACADEMICO,btn("Calificar curso",None,True),True)+only("ADM,GER,DIR,SUC,COO",btn("Exportar"),True))+table(["Matrícula","Estudiante","Asistencia","Total","Pagado","Saldo","Teléfono contacto","Nota","Estado","Acción"],[
  ["001-202602794",'<a href="Ficha360.html">María Andrade</a>',"90%","$230","$230","$0","099 000 0001","—",badge("En curso","ok"),'<a href="DetalleMatricula.html">Ver</a>'],
  ["001-202602846",'<a href="Ficha360.html">Pedro Mora</a>',"85%","$230","$122","$108","099 000 0002","—",badge("Saldo pendiente","warn"),'<a href="DetalleMatricula.html">Ver</a>'],
  ["001-202602860",'<a href="Ficha360.html">Valeria Cedeño</a>',"70%","$230","$230","$0","099 000 0003","—",badge("Riesgo asistencia","bad"),'<a href="DetalleMatricula.html">Ver</a>'],
  ["001-202602863",'<a href="Ficha360.html">Gabriela Núñez</a>',"40%","$195","$0","$195","099 000 0004","—",badge("Sin pago · riesgo","bad"),'<a href="DetalleMatricula.html">Ver</a>']])+kv(("Matriculados","12/15"),("Saldo pendiente del curso","$303"),("Asistencia promedio","84%"))+note("Al terminar las 36 horas el curso queda 'Terminado sin calificar' hasta que el profesor registre pass/fail. Reemplaza las vistas 'Matrículas con saldos' y 'Finished courses with ungraded students' de TeamDesk.")),
 subtitle="Las sesiones registradas aquí alimentan la payment sheet del profesor y el progreso del estudiante")
page("DetalleCurso.html","Detalle curso",det,"Detalle de curso y sesiones")

# 9 Profesores
prof=shell("Profesores","Profesores",
 filters(search("Buscar","Nombre o cédula",w="260px"),sel("Estado",["Todos","Activo","Pendiente de aprobación","Inactivo"],w="200px"),sel("Contrato",["Todos","Por horas","Nómina","Vencido"],w="140px"),sel("Vista",["Todos","Dictando ahora","Con horas libres","Sin contrato vigente"],w="170px",col=False),actions=btn("Alta de profesor","AltaProfesor.html",True)+btn("Payment sheet","PaymentSheet.html")),
 kpis([("Profesores activos",sv(36,18,11,7),"de 100 registrados"),("Dictando ahora",sv(5,3,1,1),"sesiones en curso"),("Horas esta semana",sv(412,210,124,78),"programadas"),("Sin contrato vigente con clases",sv(1,0,0,1),"bloquea pago")]),
 table(["Profesor","Sede","Contrato","Cursos activos","Clases hoy","Horas / semana","Asistencia","Estado","Acción"],[
  [c2("P. Gómez","Quito · Por horas · vigente · $7.00/h"),"Quito","Por horas · vigente","3",c2("2","B1 Virtual 19:00, A2 18:00"),"14 h",progress(88),badge("Activo","ok"),'<a href="FichaProfesor.html">Ver perfil</a>'],
  [c2("L. Vega","Valle · Por horas · vigente · $6.50/h"),"Valle","Por horas · vigente","2",c2("1","Kids 2 Tarde 15:00"),"10 h",progress(91),badge("Activo","ok"),'<a href="FichaProfesor.html">Ver perfil</a>'],
  [c2("R. Salas","Ambato · Vencido · $5.70/h"),"Ambato","Vencido","0",c2("0","sin clases hoy"),"0 h","—",badge("Inactivo","bad"),'<a href="FichaProfesor.html">Ver perfil</a>'],
  [c2("M. Castro","Ambato · Por horas · vigente · $6.50/h"),"Ambato","Por horas · vigente","2",c2("1","Kids 1 Mañana 16:00"),"8 h",progress(84),badge("Activo","ok"),'<a href="FichaProfesor.html">Ver perfil</a>'],
  [c2("S. Jiménez","Quito · Nómina · —/h"),"Quito","Nómina","4",c2("2","A1 Sábados, B2 Intensivo"),"20 h",progress(93),badge("Activo","ok"),'<a href="FichaProfesor.html">Ver perfil</a>'],
  [c2("D. Paredes","Valle · Por horas · pendiente · $6.00/h"),"Valle","Por horas · pendiente","0",c2("0","sin clases hoy"),"0 h","—",badge("Pendiente de aprobación","warn"),'<a href="FichaProfesor.html">Ver perfil</a>']],sede=1,hide=(1,2),wide=0),
 ai([("Teens B1 Virtual (Valle) abre en 2 semanas sin profesor. P. Gómez dicta B1 Virtual en Quito con 88% de asistencia y tiene libres Lu-Ma-Mi-Ju 17:00–19:00.","Ver perfil","FichaProfesor.html"),("S. Jiménez está en 20 h/semana, el máximo de su contrato de nómina. No asignarle el curso nuevo de sábado.","Ver carga","FichaProfesor.html"),("R. Salas tiene contrato vencido y 8 h registradas este mes: la payment sheet no se puede aprobar hasta renovar o anular esas sesiones.","Renovar contrato","AltaProfesor.html")],"Pregunta: ¿quién puede cubrir Kids 2 Tarde el miércoles?"),
 card("Alta de profesor (flujo)", flow(["Formulario de alta","Pendiente de aprobación","Dirección aprueba","Puede recibir cursos","Aparece en payment sheet"])+note("Nadie puede crear un profesor que cobre sin pasar por aprobación. Hoy hay 1 alta pendiente (D. Paredes).")),
 subtitle="Nadie crea un profesor que pueda cobrar sin aprobación (el caso del profesor falso)")
page("Profesores.html","Profesores",prof,"Listado de profesores")

# 10 Payment sheet
ps=shell("Payment sheet · Octubre 2026","Profesores",
 filters(sel("Mes",["Octubre 2026","Septiembre 2026","Agosto 2026"],w="170px"),sel("Contrato",["Todos","Por horas","Nómina"],w="150px"),sel("Alerta",["Todas","Diferencia","Contrato vencido","Factura sin sesiones"],w="190px"),actions=kv(("Estado",badge("Borrador","warn")),("Total a pagar","$1,145.60"),("Alertas","3"))+btn("Exportar")+btn("Aprobar pagos",None,True)),
 table(["Profesor","Sede","Contrato","Sesiones","Horas","Tarifa","A pagar","Factura prof.","Alerta"],[
  ["P. Gómez","Quito","Por horas","24","48","$7.00","$336","$336","—"],
  ["L. Vega","Valle","Por horas","18","36","$6.50","$234","$260",badge("Diferencia +$26","warn")],
  ["R. Salas","Ambato","Por horas","4","8","$5.70","$45.60","—",badge("Contrato vencido","bad")],
  ["M. Castro","Ambato","Por horas","20","40","$6.50","$260","$260","—"],
  ["S. Jiménez","Quito","Nómina","30","60","—","Salario","—","—"],
  ["D. Paredes","Valle","Por horas","0","0","$6.00","$0","$120",badge("Factura sin sesiones","bad")]],sede=1),
 two(card("Cómo se calcula", flow(["Sesiones confirmadas","× tarifa/hora","Monto a pagar","vs factura del profesor","Alertas"])+note("Diferencias y profesores sin contrato vigente bloquean la aprobación hasta resolverse.")),
     card("Alertas del mes", table(["Profesor","Alerta","Acción"],[["L. Vega","Factura $260 vs calculado $234 (+$26)",'<a href="FichaProfesor.html">Revisar sesiones</a>'],["R. Salas","Contrato vencido · 8 h registradas",'<a href="AltaProfesor.html">Renovar contrato</a>']]))),
 subtitle="Reemplaza el Excel + Drive de 2 días al mes")
page("PaymentSheet.html","Payment sheet",ps,"Payment sheet de profesores")

# 11 Comisiones
com=shell("Comisiones · Octubre 2026","Comisiones",
 filters(sel("Período",["Octubre 2026","Septiembre 2026","Agosto 2026"],w="170px"),actions=kv(("Estado",badge("En revisión","warn")),("Total comisiones","$930"),("Niveles vendidos","34"))+btn("Reglas de comisión")+btn("Exportar")+btn("Aprobar período",None,True)),
 flow(["Borrador (cálculo automático)","En revisión (Dir. Comercial)","Aprobado (se paga)"]),
 table(["Asesor","Niveles vendidos","Virtual / Presencial","Meta","Real","Comisión","Acción"],[
  ["Carla M.","14","6 / 8","12","14","$420",'<a href="DetalleComision.html">Ver detalle</a>'],
  ["Diego R.","9","4 / 5","12","9","$180",'<a href="DetalleComision.html">Ver detalle</a>'],
  ["Sofía L.","11","7 / 4","10","11","$330",'<a href="DetalleComision.html">Ver detalle</a>']]),
 two(card("Meta vs real por asesor", vbars([("Carla M.",[12,14]),("Diego R.",[12,9]),("Sofía L.",[10,11])],["Meta","Real"])),
     card("Reglas activas", li(["Rango 1–5 niveles: 2% virtual · 3% presencial","Rango 6–10 niveles: 3% virtual · 4% presencial","Rango 11+ niveles: 4% virtual · 5% presencial","Bono $50 por cumplir meta mensual"])+row('<a href="ReglasComision.html" style="font-size:13px">Editar reglas</a>'))),
 subtitle="Cálculo automático al cierre de mes, con historial y detalle exportable")
page("Comisiones.html","Comisiones",com,"Motor de comisiones")

# 11b Insights de IA (M9 + M8): todas las observaciones del asistente, por área, con prioridad y acción
def insight(area, sev, title, text, link, href, when="hoy"):
    k={"alta":"bad","media":"warn","baja":"neutral"}[sev]
    return (f'<div class="insight"><div class="insight-side"><span class="badge badge-{k}">{sev}</span><small>{when}</small></div><div class="insight-body"><small class="insight-area">{area}</small><b>{title}</b><p>{text}</p>'
            f'<div class="insight-actions"><a href="{href}" class="btn btn-primary">{link}</a>{btn("Marcar como atendido")}{btn("Descartar")}</div></div></div>')
INSIGHTS=[
 ("Comercial","alta","Descuento del 42% bloquea una matrícula de $980","La solicitud de Carla M. para María Andrade espera desde ayer. Con 10% la matrícula cierra hoy; con 42% la comisión baja a $23 y requiere justificación.","Resolver en Aprobaciones","Aprobaciones.html","hace 1 día"),
 ("Académico","alta","14 estudiantes de A1 Sábados sin calificar","El curso 0001-2026-0430 terminó hace 5 días. Sin notas no se emiten certificados y los estudiantes no pueden matricularse en A2, donde hay 3 cupos esperándolos.","Calificar curso","DetalleCurso.html","hace 5 días"),
 ("Pagos a profesores","alta","Payment sheet de octubre con 3 alertas","L. Vega facturó $26 más que sus horas; R. Salas tiene contrato vencido con 8 h; D. Paredes entregó factura sin sesiones. Bloquean la aprobación.","Revisar payment sheet","PaymentSheet.html","hoy"),
 ("Académico","media","Teens B1 Virtual abre en 2 semanas sin profesor","P. Gómez tiene libres Lu-Ma-Mi-Ju 17:00–19:00, dicta B1 con 88% de asistencia y le quedan 6 h de contrato. Es el mejor candidato.","Ver perfil y asignar","FichaProfesor.html","hoy"),
 ("Cobranza","media","$12,450 en matrículas con saldo; el 60% vence con cursos que terminan en noviembre","4 cursos concentran $7,470. Conviene contactar antes del cierre: después del fin de curso la recuperación cae a la mitad.","Ver matrículas con saldo","Cursos.html","hoy"),
 ("Inventario","media","Stock negativo en 3 libros de cursos en marcha","Empower B1+ (Valle −2), Super Minds 3 WB y SB (Ambato). 4 estudiantes están sin material. Pedido sugerido a Books & Bits: 16 libros.","Crear pedido","NuevoPedido.html","hoy"),
 ("Comercial","media","Ambato lleva 2 semanas sin matrículas nuevas","Tiene 2 cursos por abrir con menos de 5 inscritos. Históricamente no abren con menos de 6. Hay 5 leads de Kommo sin contactar en esa sede.","Ver cursos de Ambato","Cursos.html","hace 3 días"),
 ("Académico","media","4 estudiantes de B1 Virtual con asistencia menor a 60%","Riesgo de perder el módulo 7. Dos de ellos nunca habían faltado antes de la semana pasada.","Ver estudiantes del curso","DetalleCurso.html","hoy"),
 ("Operación","baja","Aula Q-1 al 60% y C-2 (Valle) al 0% el sábado","El nuevo Kids 2 de sábado podría ir a C-2 sin chocar con otro curso.","Ver aulas","Configuracion.html","hoy"),
 ("Dirección","baja","Octubre va 9% sobre la meta de niveles","76 niveles vendidos sobre 70. Quito empuja (+15%); Ambato es la única sede bajo meta.","Ver dashboard ejecutivo","DashboardEjecutivo.html","hoy"),
]
_ins_rows="".join(insight(*i) for i in INSIGHTS)
page("Insights.html","Insights de IA",shell("Insights de IA","Insights de IA",
 kpis([("Insights abiertos","10","3 de prioridad alta"),("Atendidos esta semana","7","tiempo medio de atención: 1.4 días"),("Impacto estimado","$21,300","matrículas y cobros en juego"),("Cobertura","5 áreas","académico · comercial · pagos · inventario · dirección")]),
 two(card("Insights por área", hbars([("Académico",3),("Comercial",2),("Pagos a profesores",1),("Cobranza",1),("Inventario",1),("Operación",1),("Dirección",1)],"")), card("Evolución (últimas 8 semanas)", linechart(["S1","S2","S3","S4","S5","S6","S7","S8"],{"Nuevos":[6,8,7,9,8,11,9,10],"Atendidos":[4,7,6,8,9,9,8,7]},h=150)+'<span class="kpi-sub">El asistente analiza cada noche la base unificada y propone acciones. Solo lectura: nada cambia sin que alguien lo confirme.</span>')),
 filters(sel("Área",["Todas","Académico","Comercial","Pagos a profesores","Cobranza","Inventario","Operación","Dirección"],w="180px",col=False),sel("Prioridad",["Todas","alta","media","baja"],w="130px",col=False),sel("Estado",["Abiertos","Atendidos","Descartados"],w="140px",col=False),actions=btn("Preguntar al asistente",None,False,action="",next=None) if False else '<button type="button" class="btn btn-ask" data-ask="¿Qué insight es el más urgente?">✦&nbsp;Preguntar al asistente</button>'),
 f'<div class="insights">{_ins_rows}</div>',
 subtitle="Todo lo que el asistente detectó en la base unificada, por área y prioridad"),"Insights de IA")

# 12 Reportes · las tres vistas comparten la misma barra de pestañas (cada una es una pantalla)
def rep_tabs(active):
    return tabs([("Dashboard por rol","Reportes.html"),("Reportes self-service","ConstructorReportes.html"),("Dashboard ejecutivo","DashboardEjecutivo.html")],active)
rep=shell("Reportes y dashboards","Reportes",
 rep_tabs("Dashboard por rol"),
 kpis([("Ventas del mes (niveles)",sv(76,40,22,14),"meta 70 · 109%"),("Matrículas del mes",sv(52,28,15,9),"+8% vs sep"),("Cobrado / pendiente",sv("$31,200 / $12,450","$16,900 / $6,200","$9,100 / $4,100","$5,200 / $2,150"),"71% cobrado"),("Ocupación de cursos",sv("82%","86%","78%","75%"),sv("41 cursos activos","22 cursos","12 cursos","7 cursos"))]),
 two(card("Ventas por sede y modalidad (niveles, octubre)", vbars([("Quito",[24,16]),("Valle",[14,8]),("Ambato",[9,5])],["Presencial","Virtual"])),
     card("Pipeline comercial (Kommo → venta → matrícula)", funnel([("Leads Kommo",310),("Contactados",205),("Cotizaciones",120),("Ventas",76),("Matriculados",52)]))),
 card("Reportes self-service", filters(sel("Entidad",["Estudiantes","Ventas","Cursos","Profesores","Comisiones"],w="180px"),sel("Agrupar por",["Mes","Sede","Nivel","Asesor"],w="140px"),dates(),actions=btn("Generar",None,True)+btn("Exportar"))+note("Cada exportación queda registrada en el audit log. Los reportes con datos de menores se marcan como sensibles (LOPDP).")+row('<a href="ConstructorReportes.html" style="font-size:13px">Abrir el constructor completo</a>')),
 subtitle="Estefanía arma sus propios reportes sin pedirle nada a un desarrollador")
page("Reportes.html","Reportes",rep,"Reportes y dashboards")


# 13 Usuarios y roles
page("Usuarios.html","Usuarios",shell("Usuarios y roles","Usuarios y roles",
 filters(search("Buscar","Nombre o email",w="260px"),sel("Rol",["Todos","Administrador General","Gerente General","Director Comercial","Administrador de Sucursal","Coordinador Académico","Asesor Comercial","Secretaría","Profesor (consulta)"],w="220px"),sel("Estado",["Todos","Activo","Inactivo"],w="130px"),actions=btn("Nuevo usuario",None,True)),
 table(["Usuario","Rol","Sedes visibles","Estado","Acción"],[["Estefanía","Administrador General","Todas","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Carla M.","Asesor Comercial","Quito","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Coord. Académica","Coordinador Académico","Valle","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["P. Gómez","Profesor (consulta)","Quito","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Diego R.","Asesor Comercial","Valle","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Sofía L.","Asesor Comercial","Ambato","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Dir. Comercial","Director Comercial","Todas","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Secretaría Ambato","Secretaría","Ambato","Inactivo",'<a href="NuevoUsuario.html">Editar</a>'],["Admin. Sucursal Valle","Administrador de Sucursal","Valle","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Gerencia","Gerente General","Todas","Activo",'<a href="NuevoUsuario.html">Editar</a>']],sede=2),
 note("Los empleados de TeamDesk (tabla Employees: p. ej. 'Administrador de Sucursal') se migran como usuarios con rol; los datos personales del empleado (cédula, teléfono, cumpleaños) quedan en su ficha de usuario, no en una tabla aparte."),
 card("Matriz de permisos por rol", table(["Acción","Admin General","Gerente","Dir. Comercial","Admin. Sucursal","Coord. Académica","Asesor","Secretaría"],[["Crear estudiante / matrícula","✓","—","✓","✓","—","✓","✓"],["Aplicar descuento >10%","✓","—","✓","—","—","—","—"],["Aprobar profesor","✓","✓","✓","—","—","—","—"],["Calificar curso (pass/fail)","✓","—","—","—","✓","—","—"],["Aprobar payment sheet","✓","✓","—","✓","—","—","—"],["Exportar base completa","✓","—","—","—","—","—","—"],["Ver otras sedes","✓","✓","✓","—","—","—","—"],["Dashboard ejecutivo","✓","✓","✓","—","—","—","—"]])),
 subtitle="RBAC: roles, permisos por acción y visibilidad multi-sede"),"Usuarios y roles")

# 14 Audit log
page("AuditLog.html","Audit log",shell("Audit log","Audit log",
 filters(sel("Usuario",["Todos","Estefanía","Carla M.","Dir. Comercial","Secretaría","Coord. Académica"],w="160px"),sel("Acción",["Todas","Creó","Modificó","Aprobó","Rechazó","Exportó","Eliminó"],w="130px"),sel("Entidad",["Todas","Estudiante","Factura","Descuento","Profesor","Tarifa","Curso","Inventario"],w="140px"),dates(),actions=btn("Exportar log")),
 table(["Fecha/hora","Usuario","Acción","Entidad","Detalle","IP / sede"],[["04 oct 10:12","Carla M.","Creó","Estudiante","María Andrade","Quito"],["04 oct 09:40","Dir. Comercial","Aprobó","Descuento","42% → rechazado, 10% aprobado","Quito"],["03 oct 17:05","Secretaría","Exportó","Estudiantes","120 registros (filtro Valle)","Valle"],["03 oct 15:30","Estefanía","Modificó","Tarifa","P. Gómez $6.50 → $7.00","Quito"],["03 oct 11:20","Coord. Académica","Creó","Curso","Teens B1 Virtual · Valle","Valle"],["02 oct 16:45","Carla M.","Rechazó","Descuento","Solicitud 30% · Luis Torres (retirada)","Quito"],["02 oct 10:05","Secretaría","Modificó","Inventario","Traslado 3 × Adults B1 Quito → Valle","Valle"],["01 oct 09:30","Dir. Comercial","Aprobó","Profesor","M. Castro · $6.50/h","Ambato"],["30 sep 18:00","Estefanía","Eliminó","Curso","Kids 1 Tarde (sin inscritos)","Ambato"]],sede=5),
 pager(sv("4,120","2,210","1,180","730"),50),
 card("Alertas marcadas para revisión", table(["Fecha","Alerta","Usuario","Estado"],[["03 oct 17:05","Exportación masiva: 120 estudiantes (incluye menores)","Secretaría",badge("Revisada","ok")],["03 oct 15:30","Cambio de tarifa de profesor","Estefanía",badge("Pendiente","warn")],["02 oct 11:00","Descuento fuera de regla (42%)","Carla M.",badge("Rechazado","bad")]])+note("Exportaciones masivas, cambios de tarifa y descuentos fuera de regla se marcan automáticamente (LOPDP, datos de menores). Nada se borra.")),
 subtitle="Quién hizo qué, cuándo y desde dónde. Nada se borra."),"Audit log")

# 15 Configuración
page("Configuracion.html","Configuración",shell("Configuración","Configuración",
 tabs(["Sedes","Aulas","Programas y niveles","Productos y materiales","Empresas y convenios","Tarifas de profesores","Reglas de aprobación","Parámetros"],"Programas y niveles",{
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
  "Programas y niveles": two(card("Programas", table(["Programa","Edades","Módulos","Horas por módulo","Estado"],[["English for Adults","18+","16 (A1–C1)","18 h","Activo"],["English for Teens","12–17","12","18 h","Activo"],["English for Kids","6–11","8","16 h","Activo"],["Tailored (corporativo / individual)","—","a medida","a medida","Activo"]])),
     card("Regla nivel ↔ módulo", note("1 nivel comercial = 2 módulos académicos. Se vende y factura por nivel; se dicta y califica por módulo. Un módulo aprobado consume medio nivel del paquete del estudiante.")+table(["Nivel","Módulos","Libro"],[["A1","1–2","Empower A1 Starter"],["A2","3–6","Empower A2 Elementary"],["B1","7–8","Empower B1 Pre-intermediate"],["B1+","9–10","Empower B1+ Intermediate"],["B2","11–14","Empower B2 Upper-intermediate"]])))+
     table(["Programa","Nivel","Módulos","Precio virtual","Precio presencial","Vigencia","Estado"],[["Adults","A1","1–2","$450","$500","2026","Activo"],["Adults","A2","3–6","$460","$500","2026","Activo"],["Adults","B1","7–8","$500","$550","2026","Activo"],["Adults","B1+","9–10","$500","$550","2026","Activo"],["Teens","A2","9–10","$420","$470","2026","Activo"],["Kids","Kids 2","3–4","$380","$420","2026","Activo"]])+row(btn("Nuevo nivel",None,True),btn("Editar precios")),
  "Productos y materiales": filters(search("Buscar","Código, ISBN o título",w="260px"),sel("Programa",["Todos","Adults","Teens","Kids"],w="130px"),sel("Tipo",["Todos","Student Book","Workbook","Digital pack","Otro"],w="150px"),actions=btn("Nuevo producto",None,True,"Se crea el producto con código, ISBN, precio de compra y de venta, y el nivel al que corresponde.","Configuracion.html"))+table(["Código","ISBN","Producto","Programa","Nivel","Tipo","Costo","Precio venta","Estado"],[
     ["1132","9781108961691","Empower A1 Starter SB with digital pack 2nd Ed","Adults","A1","Student Book","$62.15","$70.00",badge("Activo","ok")],
     ["1141","9781108961523","Empower B1+ Intermediate Combo B with digital pack","Adults","B1+","Student Book","$35.98","$40.00",badge("Activo","ok")],
     ["1115","9781009029780","Prepare 3 SB with eBook 2E","Teens","A2","Student Book","$34.89","$40.00",badge("Activo","ok")],
     ["1116","9781009030502","Prepare 3 WB with Digital Pack 2E","Teens","A2","Workbook","$20.03","$24.00",badge("Activo","ok")],
     ["1292","9781108812276","Super Minds 2Ed Level 3 SB with eBook","Kids","Kids 2","Student Book","$31.37","$36.00",badge("Activo","ok")],
     ["1271","9781009293891","Four Corners 2ED L4 ESB with DP","Adults","B2","Digital pack","$35.46","$40.00",badge("Activo","ok")],
     ["1999","—","Libreta Superpower","—","—","Otro","$7.99","$10.00",badge("Activo","ok")]])+note("Equivale a la tabla Products/Services de TeamDesk. El costo viene del último ingreso del proveedor; el precio de venta se usa en la matrícula."),
  "Tarifas de profesores": table(["Tipo de contrato","Tarifa base / hora","Modalidad","Vigencia","Estado"],[["Por horas","$7.00","Presencial","2026","Activa"],["Por horas","$6.50","Virtual","2026","Activa"],["Nómina","Salario mensual","Ambas","2026","Activa"]])+note("La tarifa individual se fija en la ficha del profesor y requiere aprobación de Dirección."),
  "Reglas de aprobación": table(["Regla","Condición","Aprueba","Estado"],[["Descuento fuera de regla","> 10%","Director Comercial","Activa"],["Alta de profesor","Siempre","Dirección","Activa"],["Asignación sin contrato","Profesor sin contrato vigente","Coordinación Académica","Activa"],["Exportar base completa","Siempre","Administrador General","Activa"]])+row(btn("Nueva regla",None,True)),
  "Parámetros": form(["Moneda","Zona horaria","Días de vencimiento de factura","Umbral de alerta de stock","Email de notificaciones","Proveedor de libros por defecto"]),
 }),
 row(btn("Guardar cambios",None,True)),
 subtitle="Todo lo que hoy está hardcodeado en TeamDesk, configurable sin desarrollador"),"Configuración")

# 16 Nuevo estudiante
page("NuevoEstudiante.html","Nuevo estudiante",shell("Nuevo estudiante","Estudiantes",
 form(["Nombres","Apellidos","Cédula / ID","Fecha de nacimiento","Email","Teléfono","Dirección","Sede","Ocupación / empresa","Cómo nos conoció (lead Kommo)"]),
 card("Si es menor de edad", form(["Nombre del representante","Cédula del representante","Teléfono del representante","Autorización firmada (archivo)"])+note("Marcador automático de dato sensible: menor de edad · discapacidad. Estos registros exigen autorización firmada y se marcan en toda exportación (LOPDP).","warn")),
 row(btn("Cancelar","Estudiantes.html"),btn("Guardar estudiante","Ficha360.html",True)),
 subtitle="Un solo formulario para las 3 sedes, con validación de duplicados por cédula"),"Nuevo estudiante")

# 17 Importar / exportar
page("ImportExport.html","Importar / exportar",shell("Importar / exportar estudiantes","Estudiantes",
 two(card("Importar", upload("Arrastrar archivo CSV o Excel","Columnas: nombres, apellidos, cédula, fecha de nacimiento, email, teléfono, sede")+kv(("Archivo","estudiantes_valle.xlsx"),("Filas","120"),("Válidas",badge("115","ok")),("Duplicados",badge("3","warn")),("Cédula inválida",badge("2","bad")))+table(["Fila","Nombre","Cédula","Problema"],[["17","Juan Pérez","1712345678","Ya existe (Valle)"],["42","Ana Ruiz","1798765432","Ya existe (Quito)"],["88","Pedro Mora","17-ABC","Cédula inválida"]])+row(btn("Descargar plantilla"),btn("Importar",None,True))),
     card("Exportar", filters(sel("Estado",["Todos","Activo","En transición","Inactivo"],w="150px"),sel("Programa",["Todos","Adults","Teens","Kids"],w="130px"),sel("Columnas",["Básicas (nombre, cédula, sede, nivel)","Completas","Contacto"],w="260px"))+kv(("Registros a exportar",sv(812,420,230,162)),("Incluye menores","sí (marcado sensible)"))+note("La exportación queda registrada en el audit log con tu usuario, filtros y cantidad de registros.","warn")+row(btn("Exportar CSV",None,True)))),
 subtitle="Carga masiva con validación y exportación auditada"),"Importar / exportar")

# 18 Nuevo curso
page("NuevoCurso.html","Nuevo curso",shell("Nuevo curso","Cursos",
 form(["Código (automático: 0001-2026-0773)","Programa (English for Adults / Teens / Kids / Tailored)","Nivel (módulos que cubre)","Modalidad (virtual / presencial)","Tipo (grupo / individual / corporativo)","Sede","Aula (valida capacidad SETEC) o enlace virtual","Fecha inicio","Fecha fin (calculada por horas)","Días y horario","Total de horas","Cupo máximo (≤ capacidad del aula)","Libro / material del nivel","Precio del nivel (desde catálogo)"]),
 card("Profesor", filters(sel("Seleccionar profesor",["P. Gómez · contrato activo","L. Vega · contrato activo","M. Castro · pendiente de aprobación","R. Salas · contrato vencido"],w="320px"),actions=kv(("Validación",badge("Contrato activo ✓","ok"))))+note("Si el profesor no tiene contrato activo, la asignación queda pendiente de aprobación de Coordinación y el curso se crea sin profesor.")),
 row(btn("Cancelar","Cursos.html"),btn("Crear curso","DetalleCurso.html",True)),
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
page("FichaProfesor.html","Ficha profesor",shell("P. Gómez","Profesores",
 row(kv(("Cédula","1709876543"),("Contrato",badge("Por horas · vigente hasta dic 2026","ok")),("Tarifa","$7.00/h"),("Sedes","Quito y Valle"),("Especialidad","Adults · B1–C1 · certificación CELTA"),("Desde","feb 2024")),'<div style="margin-left:auto"></div>',only("ADM,GER,SUC,COO",btn("Editar","AltaProfesor.html"),True),only("ADM,GER,SUC,COO",btn("Ver payment sheet","PaymentSheet.html"),True),only("ADM,GER,SUC,COO",btn("Asignar a curso",None,False,"Se elige un curso sin profesor compatible con su disponibilidad; si el contrato no está vigente la asignación va a aprobación."),True)),
 '<div class="grid" style="grid-template-columns:1.2fr 1fr 1fr 1fr">'+kpi("Dictando ahora","B1 Virtual · Zoom 2","19:00–21:00 · 12 estudiantes conectados")+'<div class="card" style="align-items:center">'+gauge(70,"Carga · 14 de 20 h")+'</div><div class="card" style="align-items:center">'+gauge(88,"Asistencia de sus cursos",CH[2])+'</div><div class="card" style="align-items:center">'+gauge(94,"Pass últimos 3 módulos",CH[3])+'</div></div>',
 tabs(["Agenda y carga","Datos","Contrato y tarifa","Cursos","Sesiones","Historial de pagos"],"Agenda y carga",roles={"Contrato y tarifa":"ADM,GER,DIR,SUC,COO","Historial de pagos":"ADM,GER,SUC,COO"},panels={
  "Agenda y carga": two(card("Clases de hoy · martes 6 oct", table(["Hora","Curso","Sede / aula","Estudiantes","Sesión"],[["18:00–20:00","0001-2026-0620 · Adults A2","Valle · C-5","9/12",badge("Confirmada","ok")],["19:00–21:00","0001-2026-0767 · Adults B1 Virtual","Quito · Zoom 2","12/15",badge("En curso ahora","warn")]])+note("Mañana: B1 Virtual 19:00. Jueves: A2 18:00 y B1 Virtual 19:00. Sábado libre.")),
     card("Carga semanal (horas)", vbars([("Lu",[4]),("Ma",[4]),("Mi",[2]),("Ju",[4]),("Vi",[0]),("Sa",[0])],["Horas dictadas"],h=120)+kv(("Total","14 h"),("Máximo contrato","20 h"),("Disponible","Lu-Ma-Mi-Ju 17:00–19:00 · Vi · Sa"))))
     +card("Cursos que dicta ahora", table(["Código","Curso","Sede","Horario","Aula","Estudiantes","Asistencia","Avance","Termina"],[["0001-2026-0767","English for Adults B1 Virtual","Quito","Lu-Ma-Mi-Ju 19:00–21:00","Zoom 2","12/15","90%","60%","20 nov"],["0001-2026-0620","English for Adults A2","Valle","Lu-Mi 18:00–20:00","C-5","9/12","85%","59%","5 dic"],["0001-2026-0772","English for Teens B1 Virtual (propuesto)","Valle","Lu-Ma-Mi-Ju 17:00–19:00","Teams 1","6/12","—","—","inicia 20 oct"]],sede=2))
     +ai([("Su asistencia promedio (88%) está 4 puntos sobre el promedio de la sede; el módulo 7 de B1 Virtual va al día con el programa.","Ver curso","DetalleCurso.html"),("Tiene 6 h libres entre semana a las 17:00: puede tomar Teens B1 Virtual sin pasar las 20 h del contrato.","Asignar","NuevoCurso.html"),("Registró 2 sesiones manuales fuera de horario en septiembre; Coordinación debe confirmarlas antes del cierre de la payment sheet.","Ver sesiones","Sesiones.html")],"Pregunta: ¿cuántas horas lleva este mes y cuánto suma su payment sheet?"),
  "Datos": form(["Nombres y apellidos","Cédula / ID","Fecha de nacimiento","Email","Teléfono","Sede(s)","Especialidad / certificaciones","Estado"])+row(btn("Guardar cambios",None,True)),
  "Contrato y tarifa": two(card("Contrato", kv(("Tipo","Por horas"),("Tarifa","$7.00/h"),("Vigencia","1 ene – 31 dic 2026"),("Aprobado por","Dirección · 10 ene 2026"),("Modalidades","Virtual y presencial"))+table(["Documento","Subido por","Fecha"],[["contrato_pgomez_2026.pdf","Coord. Académica","8 ene 2026"],["cedula_pgomez.pdf","Coord. Académica","8 ene 2026"]])),
     card("Historial de contratos", table(["Vigencia","Tipo","Tarifa","Aprobó"],[["2026","Por horas","$7.00/h","Dirección"],["2025","Por horas","$6.50/h","Dirección"]]))),
  "Cursos": table(["Código","Curso","Sede","Nivel","Modalidad","Horario","Estudiantes","Asistencia","Pass","Estado"],[["0001-2026-0767","English for Adults B1 Virtual","Quito","B1","Virtual","Lu-Ma-Mi-Ju 19:00–21:00","12","90%","—",badge("En curso","ok")],["0001-2026-0620","English for Adults A2","Valle","A2","Presencial","Lu-Mi 18:00–20:00","9","85%","—",badge("En curso","ok")],["0001-2026-0512","English for Adults A2","Quito","A2","Presencial","Lu-Mi 18:00–20:00","11","92%","100%",badge("Cerrado")],["0001-2025-0430","English for Adults A1","Quito","A1","Presencial","Sa 09:00–13:00","14","88%","93%",badge("Cerrado")],["0001-2025-0210","English for Adults B1","Quito","B1","Presencial","Ma-Ju 19:00–21:00","10","86%","90%",badge("Cerrado")]],sede=2)+kv(("Cursos dictados","5"),("Estudiantes acumulados","56"),("Pass promedio","94%"))+row(btn("Ver cursos","Cursos.html")),
  "Sesiones": table(["Fecha","Curso","Duración","Origen","Estado"],[["03 oct","Adults B1 Virtual","2 h","Automática (Moodle)","Confirmada"],["02 oct","Adults A2","2 h","Manual","Confirmada"],["01 oct","Adults B1 Virtual","2 h","Automática (Moodle)","Pendiente"]])+row(btn("Registrar sesión","Sesiones.html",True)),
  "Historial de pagos": table(["Mes","Horas","Tarifa","Monto","Estado","Acción"],[["Oct 2026","48","$7.00","$336","Borrador",btn("Ver","PaymentSheet.html")],["Sep 2026","44","$7.00","$308","Pagado",btn("Ver","PaymentSheet.html")],["Ago 2026","40","$7.00","$280","Pagado",btn("Ver","PaymentSheet.html")]]),
 }),
 subtitle="Ficha única del profesor con su historial de contratos, cursos y pagos"),"Ficha del profesor")

# 21 Alta profesor
page("AltaProfesor.html","Alta de profesor",shell("Alta de profesor","Profesores",
 form(["Nombres y apellidos","Cédula / ID","Fecha de nacimiento","Email","Teléfono","Sede(s)","Tipo de contrato","Tarifa por hora","Vigencia del contrato","Contrato firmado (archivo)"]),
 card("Qué pasa al guardar", flow(["Se crea 'Pendiente de aprobación'","Notificación a Dirección","Dirección aprueba o rechaza","Puede recibir cursos y aparecer en payment sheet"])),
 row(btn("Cancelar","Profesores.html"),btn("Enviar a aprobación","Aprobaciones.html",True)),
 subtitle="Control preventivo contra el caso del profesor falso"),"Alta de profesor")

# 22 Facturas
page("Facturas.html","Facturas",shell("Facturas","Facturación",
 filters(search("Buscar","Nº de factura o estudiante",w="260px"),sel("Estado",["Todos","Pagada","Pendiente","Parcial","Vencida","Nota de crédito"],w="160px"),sel("Asesor",["Todos","Carla M.","Diego R.","Sofía L."],w="140px"),dates(),actions=btn("Nueva venta","NuevaVenta.html",True)+btn("Exportar")),
 kpis([("Facturado del mes",sv("$43,650","$23,100","$13,200","$7,350"),sv("76 facturas","40 facturas","22 facturas","14 facturas")),("Cobrado",sv("$31,200","$16,900","$9,100","$5,200"),"71%"),("Pendiente",sv("$12,450","$6,200","$4,100","$2,150"),sv("31 facturas","15 facturas","10 facturas","6 facturas")),("Notas de crédito",sv("$140","$45","$50","$45"),"3 emitidas")]),
 table(["Factura","Fecha","Estudiante","Sede","Asesor","Niveles","Monto","Saldo","Estado","Acción"],[
  ["#1234","02 oct","María Andrade","Quito","Carla M.","B1, B2","$980","$0",badge("Pagada","ok"),'<a href="DetalleFactura.html">Ver</a>'],
  ["#1235","03 oct","Juan Pérez","Valle","Diego R.","A2","$450","$450",badge("Pendiente","warn"),'<a href="DetalleFactura.html">Ver</a>'],
  ["#1236","03 oct","Luis Torres","Ambato","Sofía L.","A1","$420","$0",badge("Nota de crédito"),'<a href="DetalleFactura.html">Ver</a>'],
  ["#1237","04 oct","Pedro Mora","Valle","Diego R.","B1","$500","$0",badge("Pagada","ok"),'<a href="DetalleFactura.html">Ver</a>'],
  ["#1238","04 oct","Camila Sánchez","Ambato","Sofía L.","A2, B1","$950","$475",badge("Parcial","warn"),'<a href="DetalleFactura.html">Ver</a>'],
  ["#1239","05 oct","Ana Ruiz","Quito","Carla M.","Kids 2","$380","$380",badge("Pendiente","warn"),'<a href="DetalleFactura.html">Ver</a>'],
  ["#1240","05 oct","Valeria Cedeño","Quito","Carla M.","B2","$550","$0",badge("Pagada","ok"),'<a href="DetalleFactura.html">Ver</a>'],
  ["#1241","05 oct","Mateo Salazar","Ambato","Sofía L.","A1","$420","$420",badge("Vencida","bad"),'<a href="DetalleFactura.html">Ver</a>'],
  ["#1242","06 oct","Gabriela Núñez","Quito","Carla M.","A2","$450","$225",badge("Parcial","warn"),'<a href="DetalleFactura.html">Ver</a>']],sede=3),
 pager(sv(76,40,22,14)),
 subtitle="Una factura por paquete de niveles, con estado de cobro"),"Facturas")

# 23 Detalle factura
page("DetalleFactura.html","Detalle factura",shell("Factura #1234","Facturación",
 two(card("Datos", kv(("Estudiante",'<a href="Ficha360.html">María Andrade</a>'),("Sede","Quito"),("Fecha","02 oct 2026"),("Asesor","Carla M."),("Vence","17 oct 2026"))+table(["Concepto","Cant.","Precio","Total"],[["Nivel B1 (2 módulos)","1","$500","$500"],["Nivel B2 (2 módulos)","1","$500","$500"],["Descuento 10% (aprobado por Dir. Comercial)","","","-$100"],["Libros B1 + B2","2","$40","$80"]])+kv(("Total","$980"),("Pagado","$980"),("Saldo","$0"),("Estado",badge("Pagada","ok")))),
     card("Pagos, notas de crédito y cambios", table(["Fecha","Tipo","Detalle","Monto"],[["02 oct","Pago","Transferencia · ref. 884512","$980"],["—","Nota de crédito","Ninguna emitida","—"]])+row(btn("Emitir nota de crédito"),btn("Cambio de curso"))+note("Una devolución o cambio de curso genera una nota de crédito vinculada a esta factura y revierte el libro al stock de la sede."))),
 row(btn("Volver","Facturas.html"),btn("Descargar PDF"),btn("Registrar pago",None,True)),
 subtitle="Factura consolidada con su trazabilidad completa"),"Detalle de factura")

# 24 Solicitud de descuento
page("SolicitudDescuento.html","Solicitud de descuento",shell("Solicitud de descuento","Nueva matrícula",
 f'<div class="card" style="max-width:640px">'+kv(("Venta","María Andrade · B1 + B2"),("Precio lista","$1,000"),("Asesor","Carla M."))+form(["Descuento solicitado (%)","Monto resultante"])+form(["Motivo (obligatorio, lista cerrada: referido, promoción, convenio, otro)"],1)+form(["Justificación"],1)+note("Más de 10% requiere aprobación del Director Comercial. El asesor ve el estado de su solicitud en Notificaciones.","warn")+row(btn("Cancelar","NuevaVenta.html"),btn("Enviar solicitud","Aprobaciones.html",True))+'</div>',
 subtitle="Reemplaza el campo 'Reason' opcional de TeamDesk"),"Solicitud de descuento")

# 25 Detalle comisión por asesor
page("DetalleComision.html","Detalle comisión",shell("Comisiones · Carla M. · Octubre 2026","Comisiones",
 kpis([("Niveles vendidos","14","6 virtual · 8 presencial"),("Meta","12","asignada por Dir. Comercial"),("Cumplimiento","117%","bono activado"),("Comisión","$420","$370 + bono $50")]),
 table(["Fecha","Matrícula","Estudiante","Niveles","Modalidad","Monto venta","Cobrado","Regla aplicada","Comisión","Estado"],[["02 oct","001-202602794","María Andrade","2","Virtual","$980","100%","Rango 11+ · 4%","$39.20",badge("Por pagar","warn")],["05 oct","001-202602846","Juan Pérez","1","Presencial","$450","0%","Rango 11+ · 5%","$22.50",badge("Retenida · sin cobro","bad")],["09 oct","001-202602863","Ana Ruiz","2","Presencial","$760","50%","Rango 11+ · 5%","$38",badge("Por pagar","warn")],["12 sep","001-202602350","Pedro Mora","1","Presencial","$500","100%","Rango 6–10 · 4%","$20",badge("Pagada","ok")]])+note("La comisión se calcula al matricular pero solo se paga cuando la venta está cobrada (regla configurable). Reemplaza el campo 'Vendor's commission: PAID' de cada enrollment en TeamDesk."),
 two(card("Bonos", table(["Bono","Condición","Estado","Monto"],[["Meta mensual","≥ 12 niveles","Cumplida (14)","$50"]])), card("Historial de comisiones", hbars([("Jul",350),("Ago",280),("Sep",300),("Oct",420)],"$"))),
 row(btn("Volver","Comisiones.html"),btn("Exportar detalle")),
 subtitle="Cada comisión muestra qué regla la generó"),"Detalle de comisión")

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
 note("Equivale a Inventory Management + Products/Services de TeamDesk. 'Códigos pendientes' = códigos de activación de material digital comprados y aún no asignados a un estudiante (hoy 'Pending codes')."),
 subtitle="Reemplaza el email diario de notify@teamdesk con alertas inteligentes"),"Inventario de libros")

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
     +card("Detalle del ingreso IM202610-01", kv(("Fecha","1 oct 2026"),("Proveedor","Books & Bits"),("Factura","000814675"),("Subtotal","$456.71"),("Descuento","$0.00"),("Total","$456.71"),("Comprobante","comprobante_books_and_bits_2026-10-01.pdf"))+table(["Código","ISBN","Ítem","Cantidad","Precio","Subtotal"],[["1115","9781009029780","Prepare 3 SB with eBook 2E","3","$34.89","$104.67"],["1116","9781009030502","Prepare 3 WB with Digital Pack 2E","3","$20.03","$60.09"],["1132","9781108961691","Empower A1 Starter SB with digital pack 2nd Ed","1","$62.15","$62.15"],["1141","9781108961523","Empower B1+ Intermediate Combo B with digital pack","1","$35.98","$35.98"],["1292","9781108812276","Super Minds 2Ed Level 3 SB with eBook","1","$31.37","$31.37"],["1271","9781009293891","Four Corners 2ED L4 ESB with DP","2","$35.46","$70.92"]])+kv(("Ítems","14"),("Total","$456.71"))+note("Equivale a 'Inventory Management' de TeamDesk: cada ingreso del proveedor con su factura, comprobante de pago, ítems por ISBN y los libros o códigos que quedaron pendientes de entrega.")),
  "Movimientos": filters(search("Buscar","Libro, factura o pedido",w="220px"),sel("Tipo",["Todos","Ingreso","Salida","Traslado","Devolución"],w="140px"),sel("Usuario",["Todos","Carla M.","Secretaría","Diego R."],w="140px"),dates(),actions=btn("Registrar movimiento",None,True)+btn("Exportar"))+table(["Fecha","Tipo","Libro","Cantidad","Sede","Vinculado a","Usuario"],[["04 oct","Salida","Adults B1 Student Book","1","Quito","Factura #1234","Carla M."],["03 oct","Ingreso","Kids 2 Workbook","8","Valle","Pedido #P-040","Secretaría"],["02 oct","Devolución","Teens A2 Student Book","1","Ambato","NC-07","Secretaría"],["01 oct","Traslado","Adults B1 Student Book","3","Quito → Valle","—","Secretaría"],["30 sep","Salida","Adults B2 Student Book","1","Quito","Factura #1240","Carla M."],["29 sep","Salida","Teens A2 Student Book","2","Ambato","Factura #1238","Diego R."],["25 sep","Ingreso","Adults A1 Student Book","10","Quito","Pedido #P-039","Secretaría"]],sede=4),
  "Pedidos a proveedor": table(["Pedido","Proveedor","Ítems","Total","Fecha","Estado"],[["#P-041","Books & Bits","12","$480","02 oct","En camino"],["#P-040","Books & Bits","8","$320","25 sep","Recibido"],["#P-039","Books & Bits","20","$800","10 sep","Recibido"]])+
     two(card("Registrar ingreso", form(["Pedido","Cantidad recibida"])+row(btn("Registrar ingreso",None,True))), card("Forecast de libros (noviembre)", table(["Libro","Cursos por abrir","Cupo","Necesarios","Stock","Pedir"],[["Adults B1 Student Book","2","30","30","3","27"],["Kids 2 Workbook","1","10","10","2","8"],["Teens A2","1","10","10","15","0"]])+note("Cursos que abren el próximo mes × cupo = libros necesarios por sede."))),
  "Códigos de activación": filters(sel("Estado",["Todos","Disponible","Asignado","Vencido"],w="140px"),sel("Producto",["Todos","Empower B1+ digital pack","Prepare 3 WB Digital Pack","Empower A1 digital pack"],w="240px"),actions=btn("Asignar código",None,True))+table(["Producto","ISBN","Código","Ingreso","Sede","Estudiante","Estado"],[["Empower B1+ digital pack","9781108961523","EMP-B1-7K2Q-••••","IM202610-01","Valle","María Andrade",badge("Asignado","ok")],["Prepare 3 WB Digital Pack","9781009030502","PRE-3W-91XA-••••","IM202610-01","Valle","—",badge("Disponible")],["Prepare 3 WB Digital Pack","9781009030502","PRE-3W-91XB-••••","IM202610-01","Valle","—",badge("Disponible")],["Empower A1 digital pack","9781108961691","EMP-A1-22QD-••••","IM202609-12","Quito","—",badge("Disponible")],["Empower A1 digital pack","9781108961691","EMP-A1-18ZZ-••••","IM202508-03","Quito","—",badge("Vencido","bad")]],sede=4)+note("Reemplaza 'Purchased Book Codes' y 'Pending codes' de TeamDesk: el código entra con el ingreso del proveedor y se asigna al estudiante al entregar el material."),
  "Notas de crédito": table(["Nota","Factura origen","Estudiante","Motivo","Monto","Fecha","Estado"],[["NC-07","#1234","María Andrade","Libro devuelto","$45","02 oct","Aplicada"],["NC-06","#1180","Juan Pérez","Cambio de modalidad","$50","20 sep","Aplicada"],["NC-05","#1102","Ana Ruiz","Libro con defecto","$45","05 sep","Pendiente"]])+row(btn("Nueva nota de crédito",None,True),btn("Ver facturas","Facturas.html")),
 }),
 subtitle="Entradas, salidas y devoluciones vinculadas a cursos y facturas"),"Movimientos de inventario")

# 29 Constructor de reportes
page("ConstructorReportes.html","Reportes self-service",shell("Constructor de reportes","Reportes",
 rep_tabs("Reportes self-service"),
 two(card("Definir reporte", form(["Entidad (estudiantes / matrículas / cursos / profesores / comisiones / inventario)","Columnas"],1)+form(["Filtro sede","Filtro estado","Desde","Hasta"])+row(btn("Generar",None,True),btn("Guardar como reporte"))),
     card("Reportes guardados (reemplazan las vistas de TeamDesk)", table(["Reporte","Vista TeamDesk que reemplaza","Entidad"],[["Nuevos estudiantes por mes","New Students Report · New Students Enrolled Monthly 1-3","Estudiantes"],["Alumnos activos / inactivos consolidados","Alumnos indexados activos / inactivos / x cruzar","Estudiantes"],["Matrículas con saldo","Matrículas con saldos · Saldos negativos","Matrículas"],["Matrículas sin pago en cursos activos","Matrículas sin pago en cursos activos","Matrículas"],["Mes actual vs mes anterior","Current Month vs Last Month · Now vs Then","Ventas"],["Inscripciones por año","Inscripciones Año Actual / Año Pasado","Matrículas"],["Aprobación vs pérdida de niveles","Aprobación VS Pérdida de niveles","Cursos"],["Comisiones por asesor","Commissions Report","Comisiones"],["Cursos terminados sin calificar","Finished courses with ungraded students","Cursos"],["Disponibilidad de cursos","Disponibilidad de Cursos · Open courses grouped by schedule","Cursos"],["Egresos de productos por proveedor","Reporte de egresos de productos · Product revenue query","Inventario"]]))),
 card("Resultado", table(["Mes","Quito","Valle","Ambato","Total"],[["Ago","32","18","11","61"],["Sep","40","22","14","76"],["Oct","28","15","9","52"]])+row(btn("Exportar Excel"),btn("Exportar PDF"))),
 subtitle="El reporte que hoy hay que pedirle al desarrollador, en minutos"),"Constructor de reportes")

# 30 Dashboard ejecutivo
page("DashboardEjecutivo.html","Dashboard ejecutivo",shell("Dashboard ejecutivo","Dashboard ejecutivo",
 rep_tabs("Dashboard ejecutivo"),
 filters(sel("Período",["2026 (ene–oct)","2025","Último trimestre"],w="170px"),sel("Comparar con",["2025","Sin comparación"],w="160px"),sel("Programa",["Todos","Adults","Teens","Kids"],w="130px")),
 kpis([("Ingresos YTD",sv("$386,400","$204,800","$116,900","$64,700"),"+12% vs 2025"),("Estudiantes activos",sv(812,420,230,162),"+3% vs 2025"),("Ticket promedio por paquete",sv("$915","$940","$890","$880"),"2.1 niveles por venta"),("Margen por sede",sv("34%","38%","31%","27%"),"después de profesores y libros")]),
 two(card("Ingresos por mes (miles de $)", linechart(["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct"],{"Quito":[18,19,21,20,22,21,19,20,23,24],"Valle":[10,11,12,11,13,12,11,12,13,14],"Ambato":[6,6,7,6,7,7,6,6,7,8]})), card("Mix por programa y modalidad", stacked([("Adults",58),("Teens",24),("Kids",18)])+stacked([("Presencial",63),("Virtual",37)]))),
 two(card("Funnel comercial (2026)", funnel([("Leads Kommo",2840),("Cotizaciones",1120),("Ventas",640),("Matriculados",598)])), card("Retención y avance de niveles", hbars([("Continúan al siguiente nivel",71),("Pausan (vuelven en 6 meses)",14),("Abandonan",15)],"")+progress(71,"Retención objetivo 2026: 75%"))),
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
 table(["Sistema","Uso","Estado","Última sincronización","Acción"],[["Kommo (CRM)","Leads → estudiantes","Conectado","Hoy 09:00",btn("Configurar")],["Moodle (LMS)","Matrícula → curso virtual · notas y asistencia","Pendiente de API del proveedor","—",btn("Configurar")],["Dora","Por definir con el cliente","Pendiente","—",btn("Configurar")],["Microsoft 365 (Teams / cuentas)","Enlace de clase virtual y cuenta del estudiante","Fuera del contrato · se evalúa en Fase 1","—",btn("Configurar")],["Email / WhatsApp (plantillas)","Notificaciones a estudiantes (enlace de clase, saldos)","Plantillas migradas de TeamDesk","—",btn("Configurar")]]),
 note("Las tablas 'Microsoft Accounts', 'Email Templates', 'Companies' y 'Portfolio' de TeamDesk no están en los 11 módulos del contrato. Se migran como datos y su gestión se confirma con el cliente (Cláusula Tercera, 3.2)."),
 two(card("API keys y webhooks", table(["Clave","Sistema","Creada","Último uso","Estado"],[["kommo-prod-••••7f2a","Kommo","12 ene","Hoy 09:00",badge("Activa","ok")],["moodle-test-••••91c0","Moodle","20 sep","—",badge("Pendiente","warn")]])+table(["Webhook","Evento","URL"],[["Nuevo lead","lead.created","https://api.cambridge.../kommo"],["Matrícula","enrollment.created","https://moodle.cambridge.../enrol"]])+row('<a href="#" style="font-size:13px">Documentación OpenAPI</a>')), card("Log de sincronización", table(["Fecha","Sistema","Resultado"],[["04 oct","Kommo","12 leads importados"],["03 oct","Kommo","1 error: email duplicado"]]))),
 subtitle="Sujeto al esquema de apificación disponible en cada proveedor"),"Integraciones")

# 33 Notificaciones
page("Notificaciones.html","Notificaciones",shell("Notificaciones","Inicio",
 table(["Tipo","Mensaje","Fecha","Acción"],[["Aprobación","Descuento 42% pendiente de tu aprobación","Hoy",'<a href="Aprobaciones.html">Revisar</a>'],["Inventario","Stock negativo: Adults B1 en Valle","Hoy",'<a href="Inventario.html">Ver</a>'],["Pagos","Payment sheet de octubre lista para revisión","Ayer",'<a href="PaymentSheet.html">Ver</a>'],["Alta","Profesor nuevo aprobado: puede recibir cursos","Ayer",'<a href="Profesores.html">Ver</a>']]),
 card("Preferencias por rol", table(["Notificación","Admin","Dir. Comercial","Coord. Académica","Asesor","Secretaría","Canal"],[["Aprobación pendiente","✓","✓","✓","—","—","Plataforma + email"],["Descuento aprobado / rechazado","—","—","—","✓","—","Plataforma + email"],["Stock negativo","✓","—","—","—","✓","Plataforma"],["Payment sheet lista","✓","—","✓","—","—","Email"],["Profesor aprobado","—","—","✓","—","—","Plataforma"]])),
 subtitle="Centro de avisos que mueve los flujos de aprobación"),"Notificaciones")

# ---------- Pantallas de formulario y acción (todo botón lleva a algún lado) ----------
# 34 Recuperar contraseña
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
 form(["Curso","Profesor (se valida contrato activo)","Fecha","Hora inicio","Hora fin","Horas (calculado)","Modalidad","Aula / enlace"]),
 card("Asistencia", table(["Estudiante","Presente","Observación"],[["María Andrade","☑","—"],["Juan Pérez","☑","—"],["Luis Torres","☐","Aviso previo"]])),
 note("Si la fecha u hora no coinciden con el horario del curso, la sesión se marca 'fuera de horario' y pide confirmación de Coordinación.","warn"),
 row(btn("Cancelar","Sesiones.html"),btn("Guardar sesión",None,True,"La sesión queda registrada como manual, pendiente de confirmación. Al confirmarse suma horas a la payment sheet.","Sesiones.html")),
 subtitle="Para clases que no entran por Moodle: presenciales, reposiciones, individuales"),"Registrar sesión manual")

# 36 Registrar pago
page("RegistrarPago.html","Registrar pago",shell("Registrar pago · Factura #1235","Facturación",
 kv(("Estudiante","Juan Pérez"),("Sede","Valle"),("Factura","#1235 · Nivel A2"),("Total","$450"),("Pagado","$0"),("Saldo","$450"),("Vence","20 oct 2026")),
 form(["Monto","Fecha de pago","Método (efectivo / transferencia / tarjeta)","Referencia / comprobante","Comprobante (archivo)","Observación"]),
 card("Resultado", flow(["Pago registrado","Cubre el saldo → Pagada","Parcial → Pendiente con nuevo saldo","Notificación al asesor"])),
 row(btn("Cancelar","DetalleFactura.html"),btn("Registrar pago",None,True,"Se registra el pago, se actualiza el estado de cobro y queda en el audit log.","DetalleFactura.html")),
 subtitle="Estado de cobro por factura, no por módulo"),"Registrar pago")

# 37 Nota de crédito
page("NotaCredito.html","Nota de crédito",shell("Nueva nota de crédito","Facturación",
 form(["Factura origen","Estudiante (automático)","Motivo (devolución / cambio de curso / libro con defecto / otro)","Monto","Devolver libro al stock (sí / no)","Justificación"]),
 card("Qué pasa al emitir", flow(["Se vincula a la factura origen","Ajusta saldo o genera devolución","Libro vuelve al stock (si aplica)","Audit log"])),
 row(btn("Cancelar","DetalleFactura.html"),btn("Emitir nota de crédito",None,True,"Se emite la nota de crédito vinculada a la factura. Si marcaste devolución de libro, el stock de la sede se actualiza.","DetalleFactura.html")),
 subtitle="Toda devolución o cambio deja rastro contable"),"Nota de crédito")

# 38 Registrar movimiento de inventario
page("RegistrarMovimiento.html","Registrar movimiento",shell("Registrar movimiento de inventario","Movimientos y pedidos",
 form(["Tipo (ingreso / salida / traslado / devolución)","Libro","Cantidad","Sede origen","Sede destino (solo traslado)","Vinculado a (factura / curso / pedido / nota de crédito)","Observación"]),
 note("Una salida sin factura o curso vinculado pide justificación y se marca para revisión.","warn"),
 row(btn("Cancelar","Movimientos.html"),btn("Registrar movimiento",None,True,"Se actualiza el stock de la sede y el movimiento queda en el historial con tu usuario.","Movimientos.html")),
 subtitle="Reemplaza los ajustes a mano en TeamDesk"),"Registrar movimiento")

# 39 Nuevo pedido a proveedor
page("NuevoPedido.html","Nuevo pedido",shell("Nuevo pedido a proveedor","Movimientos y pedidos",
 form(["Proveedor (Books & Bits)","Sede destino","Fecha estimada de entrega"]),
 card("Ítems", table(["Libro","Stock actual","Comprometido","Sugerido","Cantidad a pedir"],[["Adults B1 Student Book","-2","5","6","6"],["Kids 2 Workbook","-1","4","4","4"],["Teens A2","5","3","—","0"]])+note("Sugerido = comprometido por cursos que abren − stock disponible.")),
 row(btn("Cancelar","Movimientos.html"),btn("Enviar pedido",None,True,"El pedido queda En camino y se notifica a Secretaría de la sede para registrar el ingreso cuando llegue.","Movimientos.html")),
 subtitle="Pedido con cantidades sugeridas por el forecast de cursos"),"Nuevo pedido a proveedor")

# 40 Nuevo usuario
page("NuevoUsuario.html","Nuevo usuario",shell("Nuevo usuario","Usuarios y roles",
 form(["Nombres y apellidos","Email","Rol (Admin / Dir. Comercial / Coord. Académica / Asesor / Secretaría / Profesor)","Sedes visibles","Estado","2FA obligatorio (sí / no)"]),
 card("Permisos del rol elegido", li(["Crear estudiante · Aplicar descuento hasta 10% · Ver solo su sede","No puede: aprobar profesores, exportar base completa, ver otras sedes"])+note("La matriz completa se edita en Usuarios y roles → Matriz de permisos.")),
 row(btn("Cancelar","Usuarios.html"),btn("Guardar usuario",None,True,"Se crea el usuario y recibe un correo para definir su contraseña. El alta queda en el audit log.","Usuarios.html")),
 subtitle="Un usuario, un rol, las sedes que le corresponden"),"Nuevo usuario")

# 41 Nueva sede
page("NuevaSede.html","Nueva sede",shell("Nueva sede","Configuración",
 form(["Nombre","Ciudad","Dirección","Teléfono","Aulas","Responsable","Estado (activa / próxima)"]),
 note("Al crear la sede aparece en el selector global, en filtros y en la matriz de visibilidad por rol. Inventario arranca en cero."),
 row(btn("Cancelar","Configuracion.html"),btn("Guardar sede",None,True,"La sede queda disponible en toda la plataforma. "+AUDIT,"Configuracion.html")),
 subtitle="Preparado para Quito Norte y las que vengan"),"Nueva sede")

# 42 Nuevo nivel
page("NuevoNivel.html","Nuevo nivel",shell("Nuevo nivel del catálogo","Configuración",
 form(["Programa (Adults / Kids / Teens)","Nivel","Módulos que lo componen","Horas totales","Precio virtual","Precio presencial","Libro asociado","Vigencia del precio"]),
 note("Los precios tienen vigencia: una venta usa el precio vigente a su fecha. Cambiar el precio no altera facturas emitidas."),
 row(btn("Cancelar","Configuracion.html"),btn("Guardar nivel",None,True,"El nivel queda disponible para nuevas ventas y cursos. "+AUDIT,"Configuracion.html")),
 subtitle="Catálogo configurable sin desarrollador"),"Nuevo nivel")

# 43 Nueva regla de aprobación
page("NuevaRegla.html","Nueva regla",shell("Nueva regla de aprobación","Configuración",
 form(["Nombre de la regla","Entidad (descuento / profesor / asignación / exportación / tarifa)","Condición (ej. descuento > 10%)","Quién aprueba (rol)","Notificar a","Vigencia","Estado"]),
 note("Toda acción que cumpla la condición queda bloqueada hasta que el rol aprobador decida en la bandeja de aprobaciones."),
 row(btn("Cancelar","Configuracion.html"),btn("Guardar regla",None,True,"La regla queda activa y se aplica desde ahora. "+AUDIT,"Configuracion.html")),
 subtitle="Las reglas de negocio viven en configuración, no en código"),"Nueva regla de aprobación")

rows=[
 ("Acceso y transversales · todos los roles",[("Main.html","Login"),("RecuperarContrasena.html","Recuperar contraseña"),("Home.html","Inicio por rol"),("Notificaciones.html","Notificaciones"),("Chatbot.html","Asistente interno")],"Login → Inicio por rol. El menú, las pestañas y los accesos cambian con el tipo de usuario ('Ver como' en la barra superior). Notificaciones y asistente acompañan todos los flujos."),
 ("Académico · Coordinación, profesores, secretaría",[("Estudiantes.html","Estudiantes"),("NuevoEstudiante.html","Nuevo estudiante"),("Ficha360.html","Ficha 360°"),("DetalleMatricula.html","Detalle de matrícula"),("ImportExport.html","Importar / exportar"),("Cursos.html","Cursos"),("NuevoCurso.html","Nuevo curso"),("DetalleCurso.html","Detalle de curso"),("Sesiones.html","Registro de sesiones"),("RegistrarSesion.html","Sesión manual"),("Profesores.html","Profesores"),("FichaProfesor.html","Perfil del profesor"),("AltaProfesor.html","Alta con aprobación"),("PaymentSheet.html","Payment sheet")],"Estudiantes → matrículas → cursos con código, aula y profesor validado → sesiones → progreso, pass/fail y certificados. Perfil del profesor con agenda, carga y payment sheet."),
 ("Comercial · Asesores, Dirección Comercial, secretaría",[("NuevaVenta.html","Nueva matrícula (venta por niveles)"),("SolicitudDescuento.html","Solicitud de descuento"),("Aprobaciones.html","Bandeja de aprobaciones"),("Facturas.html","Facturas"),("DetalleFactura.html","Detalle de factura"),("RegistrarPago.html","Registrar pago"),("NotaCredito.html","Nota de crédito"),("Comisiones.html","Período de comisiones"),("DetalleComision.html","Detalle por asesor"),("ReglasComision.html","Reglas de comisión")],"Venta por paquete de niveles → descuento fuera de regla pasa por aprobación → comisión del asesor calculada por reglas y pagada al cobrar."),
 ("Inventario · Secretaría, Administración de sucursal",[("Inventario.html","Stock por sede"),("Movimientos.html","Ingresos, movimientos y pedidos"),("NuevoPedido.html","Nuevo pedido"),("RegistrarMovimiento.html","Registrar movimiento")],"Stock por sede y por ISBN, ingresos del proveedor con factura y comprobante, códigos de activación, pedidos con forecast."),
 ("Dirección · Gerencia, Dirección Comercial",[("Insights.html","Insights de IA"),("Reportes.html","Dashboard por rol"),("ConstructorReportes.html","Constructor de reportes"),("DashboardEjecutivo.html","Dashboard ejecutivo")],"Reportería self-service que reemplaza las vistas de TeamDesk y vista gerencial separada."),
 ("Administración · Administrador General",[("Usuarios.html","Usuarios y roles"),("NuevoUsuario.html","Nuevo usuario"),("Configuracion.html","Configuración"),("NuevaSede.html","Nueva sede"),("NuevoNivel.html","Nuevo nivel"),("NuevaRegla.html","Nueva regla"),("AuditLog.html","Audit log"),("Integraciones.html","Integraciones")],"RBAC, catálogos (sedes, aulas, programas, productos, empresas), reglas configurables, trazabilidad completa e integraciones."),
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
:root{--navy:#1D3F8F;--navy2:#152F6B;--red:#D62839;--yellow:#F6C21C;--sky:#4FA3DC;--ink:#1A2142;--mute:#6B7280;--line:#E6E9F2;--fill:#EEF1F8;--bg:#F6F7FB;--ok:#16A34A;--warn:#D97706;--tint-navy:#E8EEFF;--tint-red:#FDE8EC;--tint-yellow:#FFF4D6;--tint-sky:#E3F2FC;--tint-green:#E7F7EE;--r:16px;--sh:0 1px 2px rgba(26,33,66,.04),0 8px 24px rgba(26,33,66,.05)}
body{margin:0;font-family:'Poppins','IBM Plex Sans',sans-serif;color:var(--ink);background:var(--bg);font-size:14px}
a{color:var(--navy)}a:hover{color:var(--navy2)}
.sr{position:absolute;left:-9999px}
h1,h2,h3{font-weight:600}
/* layout */
.app{display:flex;min-height:100vh}
.sidebar{width:232px;overflow-y:auto;flex:none;background:#fff;color:var(--ink);display:flex;flex-direction:column;padding:20px 14px;gap:4px;position:sticky;top:0;height:100vh;border-right:1px solid var(--line)}
.brand{display:flex;align-items:center;padding:6px 8px 18px;text-decoration:none}.brand img{width:100%;max-width:196px;height:auto;display:block}.brand b{display:block;font-size:16px;letter-spacing:.08em;color:var(--navy)}.brand small{display:block;font-size:8.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--mute)}
.brand-mark{width:34px;height:26px;border-radius:5px;background:linear-gradient(180deg,var(--red) 0 33%,#fff 33% 66%,var(--navy) 66%);border:2px solid var(--navy);flex:none}
.brand-dark{justify-content:center}
.nav-area{padding:16px 12px 6px;font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--mute);font-weight:600}
.nav-link{display:flex;align-items:center;gap:12px;padding:10px 12px;border-radius:12px;color:var(--mute);text-decoration:none;font-size:13.5px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.nav-link:hover{background:var(--bg);color:var(--ink)}.nav-link.active{background:var(--tint-navy);color:var(--navy);font-weight:600}
.nav-ico{width:20px;height:20px;flex:none;display:inline-flex}.nav-ico svg{width:20px;height:20px;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.sidebar nav{flex:1;overflow-y:auto;min-height:0;scrollbar-width:thin}.sidebar-ctx{margin-top:8px;padding:12px;border-radius:12px;background:var(--bg);display:flex;flex-direction:column;gap:8px;flex:none}.sidebar-ctx-title{font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--mute);font-weight:600}.sidebar-ctx label{display:flex;flex-direction:column;gap:3px;font-size:11px;color:var(--mute)}.sidebar-ctx select{height:34px;border:1px solid var(--line);border-radius:8px;background:#fff;font:inherit;font-size:12.5px;color:var(--ink);padding:0 6px}.sidebar-foot{margin-top:8px;font-size:11px;color:var(--mute);padding:8px 12px;line-height:1.5;white-space:nowrap;flex:none}.sidebar-foot a{color:var(--mute)}
.shell-main{flex:1;min-width:0;display:flex;flex-direction:column;overflow-x:clip}
.topbar{display:flex;flex-wrap:wrap;align-items:center;gap:10px 12px;padding:18px 32px 8px;background:var(--bg);position:sticky;top:0;z-index:5}.topbar-right{display:flex;align-items:center;gap:10px;margin-left:auto;flex:none}
.crumbs{display:flex;align-items:center;gap:12px;margin-right:auto;min-width:0;flex:1 1 220px}.crumbs>div{min-width:0}.back{width:36px;height:36px;border-radius:50%;background:#fff;border:1px solid var(--line);display:inline-flex;align-items:center;justify-content:center;text-decoration:none;color:var(--ink);font-size:18px}
.crumbs h1{margin:0;font-size:20px;line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:min(38vw,460px)}.crumbs .path{font-size:12.5px;color:var(--mute);margin-top:2px;max-width:360px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.crumbs .path a{color:var(--navy);text-decoration:none}
.search{display:flex;align-items:center;gap:8px;width:220px;flex:0 1 220px;min-width:140px;background:#fff;border:1px solid var(--line);border-radius:12px;padding:0 14px;height:42px;color:var(--mute)}
.search input{border:0;background:none;font:inherit;flex:1;outline:none;color:var(--ink);min-width:0}.search svg{width:18px;height:18px;stroke:currentColor;fill:none;stroke-width:2}
.topbar-ctl{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--mute);white-space:nowrap;background:#fff;border:1px solid var(--line);border-radius:12px;padding:0 6px 0 12px;height:42px}
.topbar-ctl select{height:38px;border:0;background:none;font:inherit;font-size:13px;color:var(--ink);font-weight:500;max-width:170px}
.icon-btn{position:relative;width:42px;height:42px;border-radius:12px;display:inline-flex;align-items:center;justify-content:center;background:#fff;border:1px solid var(--line);text-decoration:none;color:var(--ink)}
.icon-btn svg{width:20px;height:20px;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.icon-btn .dot{position:absolute;top:-5px;right:-5px;background:var(--red);color:#fff;font-size:10px;font-weight:700;border-radius:999px;padding:1px 5px}
.user{display:flex;align-items:center;gap:10px;font-size:13px;color:var(--ink);white-space:nowrap;min-width:0}.user #rol-user{overflow:hidden;text-overflow:ellipsis;max-width:180px}.user #rol-user{display:flex;flex-direction:column;line-height:1.2}.user #rol-user small{color:var(--mute);font-size:12px}
.avatar{display:inline-flex;align-items:center;justify-content:center;border-radius:50%;background:linear-gradient(135deg,var(--navy),var(--sky));color:#fff;font-weight:600}
.avatar.sm{width:38px;height:38px;font-size:14px}.avatar.lg{width:96px;height:96px;font-size:32px;border:5px solid #fff;box-shadow:0 6px 20px rgba(26,33,66,.12)}
.main{padding:12px 32px 120px;display:flex;flex-direction:column;gap:26px;min-width:0}
.page-head{display:none}
/* componentes */
.grid{display:grid;gap:20px}.row{display:flex;flex-wrap:wrap;align-items:center}
.card{background:#fff;border-radius:var(--r);box-shadow:var(--sh);padding:22px 24px;display:flex;flex-direction:column;gap:14px;min-width:0}
.card-head{display:flex;align-items:center;gap:12px}.card-head h2{margin:0;font-size:17px}.card-head>*:last-child:not(h2){margin-left:auto}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:0 18px;border-radius:12px;border:1.5px solid var(--line);background:#fff;color:var(--navy);font:inherit;font-size:14px;font-weight:500;text-decoration:none;cursor:pointer;white-space:nowrap}
a.btn:hover,.btn:hover{background:var(--tint-navy);border-color:var(--tint-navy);color:var(--navy)}.btn-primary{background:var(--navy);color:#fff;border-color:var(--navy)}a.btn-primary:hover,.btn-primary:hover{background:var(--navy2);border-color:var(--navy2);color:#fff}.btn-danger{color:var(--red)}a.btn-danger:hover,.btn-danger:hover{background:var(--tint-red);border-color:var(--tint-red);color:var(--red)}
.tbl-wrap{overflow-x:auto;border-radius:var(--r);box-shadow:var(--sh);background:#fff}.tbl{display:grid;background:#fff;border-radius:var(--r);min-width:min(100%,640px)}.td-hide{display:none!important}.c2{display:flex;flex-direction:column;gap:2px;min-width:0}.c2>span{font-weight:500}.c2 small{color:var(--mute);font-size:12px;line-height:1.35}
.th{padding:13px 14px;font-weight:600;font-size:11.5px;color:var(--mute);text-transform:uppercase;letter-spacing:.06em;border-bottom:1px solid var(--line)}
.td{padding:14px 16px;font-size:13.5px;border-bottom:1px solid var(--fill);display:flex;align-items:center;min-width:0;overflow-wrap:anywhere}
.wf-row:hover .td{background:#F8F9FE}.wf-row:last-of-type .td{border-bottom:0}.td>a:only-child{display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border-radius:10px;border:1.5px solid var(--navy);background:#fff;color:var(--navy);text-decoration:none;font-weight:600;font-size:12.5px;white-space:nowrap}.td>a:only-child::after{content:'›';font-size:15px;line-height:1}.td>a:only-child:hover{background:var(--navy);color:#fff}.wf-empty{padding:24px;text-align:center;color:var(--mute)}
.kpi{background:#fff;border-radius:var(--r);box-shadow:var(--sh);padding:18px 20px;display:flex;flex-direction:column;gap:4px;position:relative;min-width:0;overflow:hidden}
.kpi-bar{position:absolute;left:0;top:18px;bottom:18px;width:4px;border-radius:0 4px 4px 0}.kpi-label{font-size:12px;color:var(--mute);font-weight:500}.kpi-value{font-size:26px;font-weight:600;line-height:1.15}.kpi-sub{font-size:12px;color:var(--mute)}
.field{display:flex;flex-direction:column;gap:5px;font-size:12px;color:var(--mute)}.field label{font-weight:500;color:var(--ink);font-size:13px}
.ctl{min-height:42px;padding:0 12px;border:1px solid var(--line);border-radius:12px;font:inherit;font-size:14px;background:#fff;color:var(--ink);width:100%}.ctl:focus{outline:2px solid var(--sky);outline-offset:1px}
.filters{display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end}.filters-more{flex-basis:100%;display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end;padding-top:4px}.btn-more{align-self:flex-end;color:var(--mute);border-style:dashed}.btn-more[aria-expanded=true]{color:var(--navy)}.filters-actions{margin-left:auto;display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.note{margin:0;padding:2px 0 2px 12px;border-left:3px solid var(--line);font-size:12.5px;line-height:1.5;color:var(--mute);background:none}.note-warn{border-left-color:var(--yellow)}.note-ok{border-left-color:var(--ok)}
.kv{display:flex;flex-wrap:wrap;gap:6px 22px;font-size:14px;align-items:center}.kv .k{color:var(--mute)}
.badge{display:inline-block;padding:4px 12px;border-radius:999px;font-size:12px;font-weight:500;background:var(--fill);color:var(--ink);line-height:1.3;overflow-wrap:normal;word-break:normal;text-align:center}
.badge-ok{background:var(--tint-green);color:#15803D}.badge-warn{background:var(--tint-yellow);color:#B45309}.badge-bad{background:var(--tint-red);color:#B91C1C}.badge-navy{background:var(--tint-navy);color:var(--navy)}
.prog{display:flex;flex-direction:column;gap:4px;font-size:13px}.prog-head{display:flex;justify-content:space-between}.td .prog{min-width:90px;width:100%}.td .prog-head{font-size:12px}.prog-track{height:10px;background:var(--fill);border-radius:999px;overflow:hidden}.prog-fill{height:100%;border-radius:999px}
.hbars{display:flex;flex-direction:column;gap:10px}.hbar{display:grid;grid-template-columns:140px 1fr 56px;gap:12px;align-items:center;font-size:13px}.hbar-track{height:8px;background:var(--fill);border-radius:999px;overflow:hidden}.hbar-fill{height:100%;background:var(--navy);border-radius:999px}.hbar b{text-align:right;font-weight:500}
.chart{display:flex;flex-direction:column;gap:10px}.vbars{display:flex;gap:8px;padding:18px 0 6px;position:relative;align-items:flex-end}
.yaxis{position:absolute;left:0;top:18px;bottom:28px;display:flex;flex-direction:column;justify-content:space-between;font-size:11px;color:var(--mute)}.vbars.axed{padding-left:30px}
.vgroup{display:flex;flex-direction:column;align-items:center;gap:8px;flex:1;min-width:0}.vbars-stack{display:flex;align-items:flex-end;gap:4px}.vbar{width:24px;border-radius:8px 8px 4px 4px;position:relative}.vbar span{position:absolute;top:-16px;left:50%;transform:translateX(-50%);font-size:11px;color:var(--mute)}
.vlabel{font-size:12px;color:var(--mute);text-align:center}
.sbar{position:relative;width:28px}.sbar-track{position:absolute;inset:0;background:var(--fill);border-radius:10px}.sbar-fill{position:absolute;left:0;right:0;bottom:0;display:flex;flex-direction:column-reverse;gap:2px;border-radius:10px;overflow:hidden}.sbar-fill div:last-child{border-radius:10px 10px 0 0}
.legend{display:flex;flex-wrap:wrap;gap:14px;font-size:12px;color:var(--mute)}.leg{display:inline-flex;align-items:center;gap:6px}.leg i{width:10px;height:10px;border-radius:50%;display:inline-block}
.funnel{display:flex;flex-direction:column;gap:8px}.funnel-row{display:flex;align-items:center;gap:12px;font-size:13px}.funnel-bar{min-width:70px;color:#fff;padding:8px 12px;font-weight:600;border-radius:10px}
.stack{display:flex;height:14px;border-radius:999px;overflow:hidden;gap:2px;background:var(--fill)}
.gauge{display:flex;flex-direction:column;align-items:center;gap:2px;min-width:0}.gauge svg{max-width:100%}.gauges{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:6px}
.upload{border:2px dashed var(--line);border-radius:var(--r);padding:22px;display:flex;flex-direction:column;align-items:center;gap:8px;text-align:center;font-size:13px;width:100%;background:var(--bg)}.upload label{font-weight:500}
.pager{display:flex;align-items:center;gap:12px;font-size:13px;color:var(--mute)}.pages{margin-left:auto;display:flex;gap:4px}.pg{padding:5px 11px;border:1px solid var(--line);border-radius:8px;text-decoration:none;color:var(--ink);background:#fff}.pg.on{background:var(--navy);color:#fff;border-color:var(--navy)}
.tabs{display:flex;flex-wrap:wrap;gap:6px;background:#fff;border-radius:14px;padding:6px;box-shadow:var(--sh);width:fit-content;max-width:100%;box-sizing:border-box}.tab{padding:9px 16px;font:inherit;font-size:13.5px;color:var(--mute);background:none;border:0;border-radius:10px;cursor:pointer;text-decoration:none;font-weight:500}.tab.on{color:var(--navy);background:var(--tint-navy);font-weight:600}
.panel{flex-direction:column;gap:20px}
.list{margin:0;padding-left:18px;font-size:14px;line-height:1.8}
.flow-steps{margin:0;padding:0;list-style:none;display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:13px}.flow-steps li{padding:7px 14px;border-radius:999px;background:var(--tint-navy);color:var(--navy);font-weight:500}.flow-steps .arr{background:none;color:var(--mute);padding:0}
.ai{border-radius:var(--r);padding:0;border:1px solid #DCE6FF;background:linear-gradient(135deg,#F3F6FF,#fff 55%);box-shadow:var(--sh)}.ai summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:14px;padding:16px 22px;border-radius:var(--r)}.ai summary:hover{background:rgba(29,63,143,.04)}.ai summary::-webkit-details-marker{display:none}.ai-title{display:flex;flex-direction:column;line-height:1.2}.ai-title b{font-size:15px}.ai-title small{color:var(--mute);font-size:12.5px}.ai-caret{margin-left:auto;width:32px;height:32px;border-radius:50%;background:#fff;border:1px solid var(--line);display:inline-flex;align-items:center;justify-content:center;font-size:18px;color:var(--mute);transition:transform .2s}.ai[open] .ai-caret{transform:rotate(90deg)}.ai ul{padding:4px 22px 0}.ai .ai-ask{padding:14px 22px 18px}
.ai-spark{width:38px;height:38px;border-radius:12px;background:var(--navy);color:var(--yellow);display:inline-flex;align-items:center;justify-content:center;font-size:18px;flex:none}
.ai ul{margin:0;list-style:none;display:flex;flex-direction:column;gap:8px;font-size:13.5px;line-height:1.5}.ai li{display:flex;gap:12px;align-items:center;background:#fff;border:1px solid var(--line);border-radius:12px;padding:12px 14px}.ai-dot{flex:none;width:10px;height:10px;border-radius:50%;background:var(--navy)}.ai li:nth-child(2) .ai-dot{background:var(--sky)}.ai li:nth-child(3) .ai-dot{background:var(--yellow)}.ai-text{flex:1;min-width:0;color:#2B3555}.ai-link{flex:none;white-space:nowrap;font-weight:600;text-decoration:none;font-size:12.5px;padding:7px 12px;border-radius:10px;background:var(--tint-navy);color:var(--navy)}.ai-link::after{content:' ›'}.ai-link:hover{background:var(--navy);color:#fff}
.ai-ask{display:flex;gap:8px;align-items:center}.ai-ask .ctl{max-width:520px}
/* dashboard ficha */
.profile{background:#fff;border-radius:var(--r);box-shadow:var(--sh);overflow:hidden;display:flex;flex-direction:column}
.profile-cover{height:100px;background:linear-gradient(120deg,#DCE6FF,#E3F2FC)}
.profile-body{padding:0 22px 22px;display:flex;flex-direction:column;align-items:center;gap:8px;margin-top:-48px;text-align:center}
.profile h2{margin:6px 0 0;font-size:20px}.profile .actions{display:flex;gap:8px;width:100%;margin-top:6px}.profile .actions .btn{flex:1;padding:0}
.profile .section{width:100%;text-align:left;margin-top:12px;padding-top:14px;border-top:1px solid var(--fill)}.profile .section h3{margin:0 0 10px;font-size:15px}
.clist{display:flex;flex-direction:column;gap:10px;font-size:13px}.clist div{display:flex;gap:12px;align-items:center}.cico{width:34px;height:34px;border-radius:10px;background:var(--tint-navy);color:var(--navy);display:inline-flex;align-items:center;justify-content:center;flex:none}.cico svg{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}.clist b{display:block;color:var(--mute);font-weight:400;font-size:12px}
.awards{display:flex;flex-direction:column;gap:9px;font-size:13px}.awards div{display:flex;gap:10px;align-items:center}.awards i{width:22px;height:22px;border-radius:50%;background:var(--tint-yellow);color:#B45309;display:inline-flex;align-items:center;justify-content:center;font-style:normal;font-size:12px;flex:none}
.hours{display:flex;align-items:baseline;gap:6px}.hours b{font-size:30px;font-weight:600}.hours span{color:var(--mute);font-size:14px}
.chips{display:flex;flex-wrap:wrap;gap:10px}.chip{padding:12px 14px;border-radius:12px;font-size:12px;color:var(--mute);flex:1;min-width:120px}.chip b{display:block;font-size:14px;color:var(--ink)}
.perf{display:flex;gap:18px;align-items:center}.perf-legend{display:flex;flex-direction:column;gap:8px;font-size:13px;flex:1}.perf-legend div{display:flex;align-items:center;gap:8px}.perf-legend i{width:9px;height:9px;border-radius:50%;display:inline-block}.perf-legend b{margin-left:auto;font-weight:500;color:var(--mute)}
.trend{position:relative;background:#F7F8FF;border-radius:12px;padding:44px 8px 0}.trend .big{position:absolute;left:50%;top:14px;transform:translateX(-50%);text-align:center;font-size:12px;color:var(--mute)}.trend .big b{display:block;font-size:22px;color:var(--ink)}.trend .big .up{background:var(--tint-green);color:#15803D;border-radius:6px;padding:1px 6px;font-size:11px;margin-left:6px}
.quote{background:var(--tint-yellow);border-radius:12px;padding:12px 16px;font-size:13.5px;line-height:1.5}
.course{display:grid;grid-template-columns:52px 1.5fr 150px 70px 110px 70px 150px;gap:16px;align-items:center;padding:14px 0;border-bottom:1px solid var(--fill);font-size:13px}.course:last-child{border-bottom:0}
.course-ico{width:52px;height:52px;border-radius:14px;display:inline-flex;align-items:center;justify-content:center}.course-ico svg{width:24px;height:24px;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.course-name a{font-weight:600;text-decoration:none;font-size:14px}.course-name small{display:block;color:var(--mute);margin-top:2px}
.course-meta{display:flex;gap:14px;color:var(--mute);font-size:12.5px}.course-meta span{display:inline-flex;align-items:center;gap:5px}.course-meta svg{width:14px;height:14px;stroke:currentColor;fill:none;stroke-width:2}
.course-grade{font-size:16px;font-weight:600}.course-grade small{color:var(--mute);font-weight:400;font-size:12px}
.cert{display:inline-flex;align-items:center;gap:6px;color:var(--mute);font-size:12.5px}.cert .badge{padding:3px 10px}
/* asistente flotante */
.ai-fab{position:fixed;right:28px;bottom:28px;width:56px;height:56px;border-radius:50%;border:0;background:var(--navy);color:#fff;box-shadow:0 10px 30px rgba(29,63,143,.35);cursor:pointer;display:flex;align-items:center;justify-content:center;z-index:40}
.ai-fab .nav-ico,.ai-fab .nav-ico svg{width:24px;height:24px}.ai-fab:hover{background:var(--navy2)}.ai-fab.on{background:var(--ink)}
.ai-fab-dot{position:absolute;top:4px;right:4px;width:12px;height:12px;border-radius:50%;background:var(--yellow);border:2px solid #fff}
.ai-panel{position:fixed;right:28px;bottom:96px;width:380px;max-width:calc(100vw - 40px);max-height:min(620px,calc(100vh - 120px));background:#fff;border-radius:18px;box-shadow:0 24px 70px rgba(26,33,66,.25);display:flex;flex-direction:column;z-index:40;overflow:hidden;border:1px solid var(--line)}
.ai-panel[hidden]{display:none}.filters-more[hidden]{display:none}
.ai-panel-head{display:flex;align-items:center;gap:10px;padding:14px 16px;border-bottom:1px solid var(--line);background:linear-gradient(135deg,#F3F6FF,#fff)}.ai-panel-head b{display:block;font-size:14px}.ai-panel-head small{color:var(--mute);font-size:12px}.ai-panel-head .icon-btn{margin-left:auto;width:34px;height:34px;font-size:20px}
.ai-log{flex:1;overflow:auto;padding:14px;display:flex;flex-direction:column;gap:10px;min-height:160px}.ai-log .msg{max-width:88%;font-size:13.5px}.typing{color:var(--mute)}
.ai-chips{display:flex;flex-wrap:wrap;gap:6px;padding:0 14px 10px}.chipq{border:1px solid var(--line);background:#fff;border-radius:999px;padding:6px 12px;font:inherit;font-size:12px;color:var(--navy);cursor:pointer;text-align:left}.chipq:hover{background:var(--tint-navy);border-color:var(--tint-navy)}
.ai-in{display:flex;gap:8px;padding:12px 14px;border-top:1px solid var(--line)}.ai-in .btn{padding:0 14px}
.btn-ask{border-style:dashed}
/* insights */
.insights{display:flex;flex-direction:column;gap:12px}
.insight{display:grid;grid-template-columns:110px 1fr;gap:16px;background:#fff;border-radius:var(--r);box-shadow:var(--sh);padding:18px 20px}
.insight-side{display:flex;flex-direction:column;gap:6px;align-items:flex-start}.insight-side small{color:var(--mute);font-size:12px}
.insight-area{display:block;color:var(--mute);font-size:11.5px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px}
.insight-body b{display:block;font-size:15px;margin-bottom:4px}.insight-body p{margin:0 0 12px;color:#3B4663;font-size:13.5px;line-height:1.55}
.insight-actions{display:flex;flex-wrap:wrap;gap:8px}.insight-actions .btn{min-height:36px;padding:0 14px;font-size:13px}
/* notificaciones */
.notif{position:relative}.notif-pop{position:absolute;right:0;top:50px;width:360px;background:#fff;border-radius:16px;box-shadow:0 20px 60px rgba(26,33,66,.2);border:1px solid var(--line);z-index:30;overflow:hidden}.notif-pop[hidden]{display:none}
.notif-head{display:flex;align-items:center;justify-content:space-between;padding:14px 16px;border-bottom:1px solid var(--line);font-size:14px}.notif-head a{font-size:12.5px;text-decoration:none;font-weight:600}
.notif-item{display:flex;gap:12px;align-items:flex-start;padding:12px 16px;text-decoration:none;color:var(--ink);border-bottom:1px solid var(--fill)}.notif-item:last-child{border-bottom:0}.notif-item:hover{background:var(--bg)}.notif-item.read{opacity:.6}
.notif-item b{display:block;font-size:13px;font-weight:600;line-height:1.35}.notif-item small{color:var(--mute);font-size:12px}
.notif-ico{flex:none;width:30px;height:30px;border-radius:10px;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:14px}
/* diálogo / toast */
#wf-dialog{border:0;border-radius:var(--r);box-shadow:0 20px 60px rgba(26,33,66,.3);padding:26px;max-width:480px;font-family:'Poppins',sans-serif;color:var(--ink)}#wf-dialog::backdrop{background:rgba(26,33,66,.45)}
#wf-toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:var(--ink);color:#fff;padding:12px 20px;border-radius:999px;font-size:14px;display:none;z-index:10;box-shadow:var(--sh)}
/* login */
.auth{min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#E8EEFF 0%,#F6F7FB 50%,#E3F2FC 100%);padding:24px}
.auth form{width:100%;max-width:420px;background:#fff;border-radius:20px;padding:36px;display:flex;flex-direction:column;gap:14px;box-shadow:0 30px 80px rgba(26,33,66,.12)}.auth h1{margin:4px 0 0;font-size:22px}.auth label{font-size:13px;font-weight:500}
.stepper{display:grid;grid-template-columns:repeat(5, minmax(0, 1fr));gap:8px}.step{padding:10px;text-align:center;font-size:13px;font-weight:500;border-radius:12px;background:#fff;border:1px solid var(--line);color:var(--mute)}.step.done{color:var(--navy);border-color:var(--navy)}.step.on{background:var(--navy);color:#fff;border-color:var(--navy)}
.cal{display:grid;grid-template-columns:repeat(7, minmax(0, 1fr));gap:8px}.cal div{border-radius:12px;min-height:90px;padding:10px;font-size:12px;background:var(--bg)}
.chat{max-width:760px;background:#fff;border-radius:var(--r);box-shadow:var(--sh);display:flex;flex-direction:column;height:520px}.chat-log{flex:1;padding:18px;display:flex;flex-direction:column;gap:12px;overflow:auto}.msg{max-width:70%;padding:10px 14px;border-radius:16px;font-size:14px}.msg.me{align-self:flex-end;background:var(--navy);color:#fff;border-bottom-right-radius:4px}.msg.bot{align-self:flex-start;background:var(--bg);border-bottom-left-radius:4px}.chat-in{display:flex;gap:8px;padding:12px;border-top:1px solid var(--line)}
/* hub */
.hub{max-width:1100px;margin:0 auto;padding:40px 24px}.hub-head p{color:var(--mute);font-size:15px;line-height:1.6;max-width:820px}
.hub section{margin-top:40px}.hub h2{margin:0 0 4px;font-size:20px;color:var(--navy)}.hub section p{margin:0 0 16px;color:var(--mute);font-size:14px;max-width:820px}
.flow{display:flex;flex-wrap:wrap;gap:12px;align-items:center}
.hub .card{display:flex;flex-direction:column;gap:6px;width:200px;min-height:96px;padding:16px;text-decoration:none;color:var(--ink);font-weight:500;position:relative}.hub .card .num{font-size:12px;color:var(--mute);font-weight:400}.hub .card:hover{transform:translateY(-2px)}
.hub-foot{margin-top:60px;color:var(--mute);font-size:12px}
.crumbs .path{max-width:300px}
@media (max-width:1400px){.search{width:200px;flex-basis:200px}}
@media (max-width:1180px){.search{display:none}.user #rol-user{display:none}.crumbs .path{display:none}}
@media (max-width:900px){.sidebar{display:none}.course{grid-template-columns:52px 1fr 70px}.course>*:nth-child(n+4){display:none}.search{display:none}}
'''
open(os.path.join(ROOT,"style.css"),"w").write(css)
open(os.path.join(ROOT,".nojekyll"),"w").write("")
open(os.path.join(ROOT,"README.md"),"w").write("# Wireframes Plataforma Cambridge\n\nWireframes estáticos de alto nivel (HTML/CSS, sin build) publicados con GitHub Pages.\n\n- `index.html`: mapa de pantallas por flujo\n- Una página por pantalla (`Main.html` = login)\n\nPublicación: GitHub Pages desde `main` / root (Settings → Pages → Deploy from a branch) o con el workflow `.github/workflows/pages.yml` (Source: GitHub Actions). URL: https://crpozo.github.io/cambridge-wireframes/\n")
