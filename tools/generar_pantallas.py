import json, os
import sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W,H=1280,820

INK="#1f2937"; MUTE="#6b7280"; LINE="#9ca3af"; FILL="#e5e7eb"; FILL2="#f3f4f6"; ACC="#1d4ed8"

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

def nav(active):
    items=[("Inicio","Home.html"),("Estudiantes","Estudiantes.html"),("Cursos","Cursos.html"),("Profesores","Profesores.html"),("Facturación","Facturas.html"),("Comisiones","Comisiones.html"),("Inventario","Inventario.html"),("Reportes","Reportes.html"),("Aprobaciones","Aprobaciones.html"),("Configuración","Configuracion.html")]
    items=[(n,h) for n,h in items if h not in HIDDEN]
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
    <select id="sede" style="height:30px;padding:0 6px;border:1px solid {LINE};border-radius:4px;background:#fff;font:inherit;font-size:13px;color:{INK};outline-offset:1px"><option>Todas</option><option>Quito</option><option>Valle</option><option>Ambato</option></select>
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
<dialog id="wf-dialog" style="border:2px solid #1f2937;padding:24px;max-width:480px;font-family:'IBM Plex Sans',sans-serif;color:#1f2937">
  <h2 id="wf-dialog-title" style="margin:0 0 8px;font-size:18px"></h2>
  <p id="wf-dialog-text" style="margin:0 0 20px;font-size:14px;line-height:1.5;color:#6b7280"></p>
  <div style="display:flex;gap:12px;justify-content:flex-end"><button type="button" id="wf-cancel" style="min-height:44px;padding:0 18px;border:2px solid #1f2937;background:#fff;color:#1f2937;font:inherit;font-weight:600;cursor:pointer">Cancelar</button><button type="button" id="wf-ok" style="min-height:44px;padding:0 18px;border:2px solid #1f2937;background:#1f2937;color:#fff;font:inherit;font-weight:600;cursor:pointer">Confirmar</button></div>
</dialog>
<div id="wf-toast" role="status" style="position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:#1f2937;color:#fff;padding:12px 20px;font-size:14px;display:none;z-index:10"></div>
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
      var f=t.previousElementSibling; while(f&&!f.classList.contains('wf-filters')&&!f.classList.contains('wf-table')) f=f.previousElementSibling;
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
      var pg=t.nextElementSibling; if(pg&&pg.classList.contains('wf-pager')){{var sp=pg.querySelector('.wf-shown'); if(sp) sp.textContent=' · '+shown+' en pantalla';}}
    }});
  }}
  if(sel){{
    var saved=null; try{{saved=localStorage.getItem('wf-sede');}}catch(e){{}}
    if(saved&&[].some.call(sel.options,function(o){{return o.value===saved;}})) sel.value=saved;
    sel.addEventListener('change',function(){{try{{localStorage.setItem('wf-sede',sel.value);}}catch(e){{}}refresh();}});
  }}
  document.querySelectorAll('[data-fcol]').forEach(function(c){{c.addEventListener('input',refresh);c.addEventListener('change',refresh);}});
  refresh();
}})();
document.querySelectorAll('.tabs').forEach(function(bar){{
  var btns=bar.querySelectorAll('[data-tab]');
  btns.forEach(function(b){{
    b.addEventListener('click',function(){{
      btns.forEach(function(x){{var on=x===b;x.setAttribute('aria-selected',on);x.style.borderBottomColor=on?'{INK}':'transparent';x.style.fontWeight=on?700:400;}});
      var el=bar.nextElementSibling;
      while(el&&el.hasAttribute('data-panel')){{el.style.display=el.getAttribute('data-panel')===b.dataset.tab?'flex':'none';el=el.nextElementSibling;}}
    }});
  }});
}});
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

def tabs(items, active, panels=None):
    """items: lista de etiquetas o (etiqueta, href). panels: dict etiqueta -> html del panel.
    Las pestañas con panel cambian de contenido en la misma página; las que tienen href navegan."""
    panels=panels or {}
    bar=""; body=""
    for t in items:
        label,href = t if isinstance(t,tuple) else (t,None)
        on = label==active
        st=f"padding:10px 16px;font-size:14px;font-family:inherit;color:{INK};background:none;border:0;border-bottom:3px solid {INK if on else 'transparent'};font-weight:{700 if on else 400};cursor:pointer;text-decoration:none"
        if href:
            bar+=f'<a href="{href}" role="tab" style="{st}">{label}</a>'
        else:
            bar+=f'<button type="button" role="tab" data-tab="{label}" aria-selected="{"true" if on else "false"}" style="{st}">{label}</button>'
    for label,content in panels.items():
        on = label==active
        body+=f'<div role="tabpanel" data-panel="{label}" style="display:{"flex" if on else "none"};flex-direction:column;gap:20px">{content}</div>'
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

# 1 Login
login=f'''<div style="min-height:{H}px;display:flex;align-items:center;justify-content:center;font-family:'IBM Plex Sans',sans-serif;color:{INK};background:{FILL2}">
<form style="width:100%;max-width:420px;background:#fff;border:2px solid {INK};padding:40px;display:flex;flex-direction:column;gap:18px;box-sizing:border-box">
  {logo()}
  <h1 style="margin:0;font-size:22px">Ingresar</h1>
  <label for="email" style="font-size:13px;font-weight:600">Correo</label>
  <input id="email" type="email" placeholder="nombre@cambridge.edu.ec" style="min-height:44px;padding:0 12px;border:2px solid {LINE};font-size:14px">
  <label for="pass" style="font-size:13px;font-weight:600">Contraseña</label>
  <input id="pass" type="password" placeholder="••••••••" style="min-height:44px;padding:0 12px;border:2px solid {LINE};font-size:14px">
  {btn("Ingresar","Home.html",True)}
  <a href="RecuperarContrasena.html" style="font-size:13px;text-align:center">Olvidé mi contraseña</a>
  <p style="margin:0;font-size:12px;color:{MUTE};text-align:center">2FA opcional · el rol define qué módulos y sedes se ven al entrar</p>
</form>
</div>'''
page("Main.html","Login",login,"Login")

# 2 Home
home=shell("Inicio","Inicio",
 kpis([("Estudiantes activos",sv(812,420,230,162),"+3% vs mes anterior"),("Ventas del mes (niveles)",sv(76,40,22,14),"meta 70"),("Matrículas con saldo",sv("$12,450","$6,200","$4,100","$2,150"),sv("31 matrículas","15 matrículas","10 matrículas","6 matrículas")),("Aprobaciones pendientes",sv(3,2,1,0),"la más antigua: ayer")])+
 two(card("Pendientes de aprobación", li(["Descuento 42% · estudiante · asesor","Alta de profesor · coordinación","Asignación profesor sin contrato activo"])+row(btn("Ir a aprobaciones","Aprobaciones.html"))),
     card("Accesos rápidos", row(btn("Nueva venta","NuevaVenta.html",True),btn("Nuevo estudiante","NuevoEstudiante.html"),btn("Payment sheet","PaymentSheet.html"),btn("Comisiones","Comisiones.html")))),
 card("Actividad reciente (audit log)", table(["Fecha/hora","Usuario","Acción","Detalle","Sede"],[["Hoy 10:12","Carla M.","Creó venta","María Andrade · B1–B2 · 10% desc.","Quito"],["Hoy 09:40","Dir. Comercial","Aprobó descuento","42% rechazado → 10% aprobado","Quito"],["Ayer 17:05","Secretaría","Registró ingreso","Kids 2 Workbook × 8 · pedido #P-040","Valle"],["Ayer 15:30","Coord. Académica","Confirmó sesión","Teens A2 · 2 h · 9/10 asistencia","Ambato"]],sede=4)+row('<a href="AuditLog.html" style="font-size:13px">Ver todo el audit log</a>')),
 subtitle="Vista por rol: Gerencia, Dirección Comercial, Coordinación Académica, Asesor, Secretaría")
page("Home.html","Inicio",home,"Inicio por rol")

# 3 Estudiantes
est=shell("Estudiantes","Estudiantes",
 filters(search("Buscar","Nombre, cédula o email",w="300px"),sel("Estado",["Todos","Activo","En transición","Inactivo"],w="150px"),sel("Programa",["Todos","Adults","Teens","Kids"],w="130px"),sel("Nivel",["Todos","A1","A2","B1","B2","Kids 1","Kids 2"],w="120px"),sel("Asesor",["Todos","Carla M.","Diego R.","Sofía L."],w="130px"),sel("Vista",["Alumnos activos","Alumnos inactivos","Duplicados entre sedes","Matrículas con saldo","Nuevos este mes"],w="190px",col=False),actions=btn("Nuevo estudiante",None,True)+btn("Importar / Exportar")),
 note("Las vistas guardadas reemplazan las de TeamDesk (Alumnos indexados activos / inactivos / x cruzar). Un nivel = 2 módulos; se muestra el nivel comercial y el módulo académico en curso."),
 table(["Nombre","Cédula","Sede","Programa","Nivel","Asesor","Estado","Acción"],[
  ["María Andrade","1712345678","Quito","Adults","B1 · módulo 7","Carla M.","Activo",'<a href="Ficha360.html">Ver ficha</a>'],
  ["Juan Pérez","1723456789","Valle","Adults","A2 · módulo 4","Diego R.","En transición",'<a href="Ficha360.html">Ver ficha</a>'],
  ["Luis Torres","1834567890","Ambato","Adults","A1 · módulo 1","Sofía L.","Inactivo",'<a href="Ficha360.html">Ver ficha</a>'],
  ["Ana Ruiz (menor)","1745678901","Quito","Kids","Kids 2","Carla M.","Activo",'<a href="Ficha360.html">Ver ficha</a>'],
  ["Pedro Mora","1756789012","Valle","Adults","B1 · módulo 8","Diego R.","Activo",'<a href="Ficha360.html">Ver ficha</a>'],
  ["Camila Sánchez","1867890123","Ambato","Teens","A2 · módulo 10","Sofía L.","Activo",'<a href="Ficha360.html">Ver ficha</a>'],
  ["Diego Vargas (menor)","1778901234","Valle","Kids","Kids 1","Diego R.","Activo",'<a href="Ficha360.html">Ver ficha</a>'],
  ["Valeria Cedeño","1789012345","Quito","Adults","B2 · módulo 11","Carla M.","Activo",'<a href="Ficha360.html">Ver ficha</a>'],
  ["Mateo Salazar (menor)","1890123456","Ambato","Teens","A1 · módulo 2","Sofía L.","En transición",'<a href="Ficha360.html">Ver ficha</a>'],
  ["Gabriela Núñez","1701234567","Quito","Adults","A2 · módulo 3","Carla M.","Inactivo",'<a href="Ficha360.html">Ver ficha</a>']],sede=2),
 pager(sv(812,420,230,162)),
 subtitle="Una sola base para Quito, Valle y Ambato · exportar queda registrado en el audit log")
page("Estudiantes.html","Estudiantes",est,"Listado de estudiantes")

# 4 Ficha 360
ficha=shell("María Andrade","Estudiantes",
 row(kv(("Cédula","1712345678"),("Sede","Quito"),("Estado",badge("Activo","ok")),("Asesor","Carla M."),("Nivel actual","B1 · módulo 7 de 16"),("Alta","12 ene 2026"),("ID legado TeamDesk","Valle · 001-2026xxxxx")),'<div style="margin-left:auto"></div>',btn("Nueva matrícula",None,True),btn("Editar","NuevoEstudiante.html")),
 tabs(["Datos","Matrículas y notas","Niveles / crédito","Facturas y pagos","Archivos y certificados","Historial"],"Matrículas y notas",{
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
 subtitle="Ficha 360°: todo lo del estudiante en una sola vista")
page("Ficha360.html","Ficha estudiante",ficha,"Ficha 360 del estudiante")

# 5 Nueva venta
steps=["1 Estudiante","2 Niveles y curso","3 Descuento","4 Pago","5 Matrícula"]
stepper='<div style="display:grid;grid-template-columns:repeat(5, minmax(0, 1fr));gap:8px">'+"".join(f'<div style="padding:10px;text-align:center;font-size:13px;font-weight:600;border:2px solid {INK};background:{"#1f2937" if i==2 else "#fff"};color:{"#fff" if i==2 else INK}">{s}</div>' for i,s in enumerate(steps))+'</div>'
venta=shell("Nueva matrícula · venta por niveles","Estudiantes",
 stepper,
 two(card("Estudiante, niveles y curso", kv(("Estudiante","María Andrade"),("Sede","Quito"),("Asesor (vendor)","Carla M."))+table(["Nivel","Módulos","Modalidad","Precio"],[["B1","7 y 8","Virtual","$500"],["B2","9 y 10","Virtual","$500"]])+filters(sel("Curso para el primer módulo",["0001-2026-0767 · Adults B1 Virtual · Lu-Ma-Mi-Ju 19:00–21:00 · 12/15","0001-2026-0772 · Adults B1 · Sa 09:00–13:00 · 9/12"],w="100%",col=False),sel("Plan de pago",["Contado","2 cuotas","4 cuotas"],w="140px",col=False),sel("Facturar a",["Estudiante","Empresa Andina S.A. (convenio 15%)","Clínica Valle (convenio 10%)","Otra empresa…"],w="260px",col=False))+kv(("Niveles","2 (4 módulos)"),("Precio lista","$1,000"),("Libros","B1 + B2 · $80"),("Inicio","3 nov 2026"))),
     card("Descuento", filters(sel("Descuento %",["0%","5%","10%","15%","20%"],w="120px"),sel("Motivo (obligatorio)",["Referido","Promoción","Convenio empresa","Otro"],w="220px"))+note("Hasta 10% lo aplica el asesor. Más de 10% pasa a aprobación del Director Comercial y la venta queda en espera.","warn")+row(btn("Solicitar aprobación","SolicitudDescuento.html")))),
 card("Resultado", table(["Concepto","Cant.","Precio","Descuento","Total"],[["Matrícula (tuition fee)","1","$0","—","$0"],["Nivel B1 (módulos 7–8)","1","$500","10% · referido","$450"],["Nivel B2 (módulos 9–10)","1","$500","10% · referido","$450"],["Libros / materiales B1 + B2","2","$40","—","$80"]])+filters(sel("Método de pago",["Transferencia","Efectivo","Tarjeta","Crédito directo"],w="180px"),actions=kv(("Subtotal","$1,080"),("Descuento","-$100"),("Total","$980")))+note("Una sola matrícula y una factura consolidada por el paquete (en TeamDesk hoy son 4 enrollments y 4 facturas por módulo). Al confirmar: el estudiante queda en el curso elegido, se comprometen 2 libros y se registra la comisión del asesor en estado pendiente.")+row(btn("Atrás"),btn("Confirmar matrícula y emitir factura","DetalleMatricula.html",True))),
 subtitle="Reemplaza la facturación 1:1 por módulo")
page("NuevaVenta.html","Nueva matrícula",venta,"Nueva matrícula (venta por niveles)")

# 5b Detalle de matrícula (equivalente al Enrollment de TeamDesk, pero por paquete de niveles)
page("DetalleMatricula.html","Detalle matrícula",shell("Matrícula 001-202602794","Estudiantes",
 row(kv(("Estudiante",'<a href="Ficha360.html">María Andrade</a>'),("Curso",'<a href="DetalleCurso.html">0001-2026-0767 · English for Adults B1 Virtual</a>'),("Horario","Lu-Ma-Mi-Ju 19:00–21:00"),("Inicio","3 nov 2026"),("Fin","20 feb 2027"),("Asesor (vendor)","Carla M."),("Plan de pago","Contado"),("Estado",badge("En curso","ok"))),'<div style="margin-left:auto"></div>',btn("Cambio de curso"),btn("Enviar enlace de clase"),btn("Hoja de asistencia"),btn("Anular matrícula")),
 two(card("Resumen", kv(("Subtotal","$1,080"),("Descuento","-$100 (10% referido)"),("Total","$980"),("Pagado","$980"),("Saldo","$0"))+progress(50,"Paquete · módulo 7 de 10 comprados (B1–B2)")),
     card("Cargos y descuentos", table(["Concepto","Monto","Descuento","Subtotal","Observación"],[["Matrícula (tuition fee)","$0","—","$0","—"],["Nivel B1 (módulos 7–8)","$500","10%","$450","Beneficio referido · aprobado Dir. Comercial"],["Nivel B2 (módulos 9–10)","$500","10%","$450","—"],["Libros / materiales","$80","—","$80","Empower B1+ SB + WB"]]))),
 tabs(["Facturas y pagos","Códigos de libros","Asistencia","Certificados","Comisión"],"Facturas y pagos",{
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
 filters(search("Buscar","Código, nombre o profesor",w="240px"),sel("Vista",["Todos los cursos","Cursos abiertos por horario","Disponibilidad (cupos libres)","Cursos con saldos de estudiantes","Terminados sin calificar","Próximos a iniciar","Cerrados"],w="230px",col=False),sel("Programa",["Todos","Adults","Teens","Kids","Tailored"],w="130px"),sel("Nivel",["Todos","A1","A2","B1","B2","Kids 1","Kids 2"],w="110px"),sel("Modalidad",["Todas","Virtual","Presencial"],w="130px"),sel("Profesor",["Todos","P. Gómez","L. Vega","M. Castro","(sin asignar)"],w="150px"),sel("Estado",["Todos","En curso","Por abrir","Terminado sin calificar","Cerrado"],w="200px"),actions=btn("Nuevo curso",None,True)),
 kpis([("Cursos en curso",sv(41,22,12,7),"esta semana"),("Por abrir",sv(6,2,3,1),"inician en 30 días"),("Con saldos de estudiantes",sv(9,4,3,2),sv("$2,840 pendientes","$1,320","$980","$540")),("Terminados sin calificar",sv(2,1,1,0),"bloquean certificados")]),
 table(["Código","Curso","Sede","Programa","Nivel","Modalidad","Horario","Aula","Profesor","Cupo","Avance","Estado","Acción"],[
  ["0001-2026-0767","English for Adults B1 Virtual","Quito","Adults","B1","Virtual","Lu-Ma-Mi-Ju 19:00–21:00","Zoom 2","P. Gómez","12/15","60%",badge("En curso","ok"),V],
  ["0001-2026-0328","English for Kids 2 Tarde","Valle","Kids","Kids 2","Presencial","Sa 09:00–13:00","C-3","L. Vega","8/10","55%",badge("En curso","ok"),V],
  ["0001-2026-0192","English for Teens A2","Ambato","Teens","A2","Presencial","Vi 15:00–19:00","A-1","(sin asignar)","5/10","0%",badge("Por abrir","warn"),V],
  ["0001-2026-0620","English for Adults A2","Valle","Adults","A2","Presencial","Lu-Mi 18:00–20:00","C-5","P. Gómez","9/12","59%",badge("En curso","ok"),V],
  ["0001-2026-0518","English for Kids 1 Mañana","Ambato","Kids","Kids 1","Presencial","Lu-Mi 16:00–18:00","A-2","M. Castro","7/10","28%",badge("En curso","ok"),V],
  ["0001-2026-0538","English for Adults B2 Intensivo","Quito","Adults","B2","Presencial","Sa 09:00–13:00","Q-4","L. Vega","11/12","46%",badge("En curso","ok"),V],
  ["0001-2026-0430","English for Adults A1 Sábados","Quito","Adults","A1","Presencial","Sa 09:00–13:00","Q-1","L. Vega","14/15","100%",badge("Terminado sin calificar","bad"),V],
  ["0001-2026-0772","English for Teens B1 Virtual","Valle","Teens","B1","Virtual","Lu-Ma-Mi-Ju 19:00–21:00","Teams 1","P. Gómez","6/12","0%",badge("Por abrir","warn"),V],
  ["0001-2026-0599","English for Kids 2 Mañana","Quito","Kids","Kids 2","Presencial","Sa 09:00–13:00","Q-2","M. Castro","10/10","53%",badge("En curso","ok"),V],
  ["0001-2026-0608","Tailored · Inglés corporativo","Ambato","Tailored","B1","Virtual","Ma-Ju 07:00–08:30","Zoom 1","(sin asignar)","3/12","0%",badge("Por abrir","warn"),V],
  ["0001-2025-0330","English for Teens A2","Valle","Teens","A2","Presencial","Vi 15:00–19:00","C-2","L. Vega","9/10","100%",badge("Cerrado"),V]],sede=2),
 pager(sv(58,29,18,11)),
 note("El código de curso conserva el formato de TeamDesk (0001-AAAA-NNNN) para la migración y la reconciliación. Avance = % de horas dictadas sobre el total."),
 subtitle="Programa, nivel, modalidad, horario y aula por sede")
page("Cursos.html","Cursos",cursos,"Listado de cursos")

# 8 Detalle curso
det=shell("0001-2026-0767 · English for Adults B1 Virtual · Quito","Cursos",
 row(kv(("Programa","English for Adults"),("Nivel","B1 · módulos 7–8"),("Horario","Lu-Ma-Mi-Ju 19:00–21:00"),("Inicio","1 sep 2026"),("Fin","20 nov 2026"),("Aula","Zoom 2"),("Cupo","12/15"),("Libro","Empower B1+ Intermediate Combo B")),'<div style="margin-left:auto"></div>',btn("Registrar sesión",None,True),btn("Enviar enlace de clase"),btn("Hoja de asistencia"),btn("Editar curso")),
 progress(60,"Avance del curso · 22 de 36 horas dictadas · termina en 7 semanas"),
 two(card("Profesor asignado", kv(("Profesor",'<a href="FichaProfesor.html">P. Gómez</a>'),("Contrato",badge("Activo hasta dic 2026","ok")),("Tarifa","$7.00/h"),("Horas en este curso","22 h · $154"))+filters(sel("Cambiar profesor",["P. Gómez","L. Vega","M. Castro","R. Salas (contrato vencido)"],w="260px"),actions=btn("Cambiar",None,False,"Si el nuevo profesor no tiene contrato activo, el cambio queda pendiente de aprobación de Coordinación."))+note("Cambiar profesor valida contrato activo. Si no lo tiene, la asignación va a la bandeja de aprobaciones.")),
     card("Sesiones", table(["Fecha","Horas","Registro"],[["01 oct","2","Automático"],["03 oct","2","Manual"],["06 oct","2","Pendiente"]]))),
 card("Estudiantes matriculados", filters(sel("Mostrar",["Todos","Con saldo pendiente","En riesgo (asistencia < 75%)"],w="220px",col=False),actions=btn("Calificar curso",None,True)+btn("Exportar"))+table(["Matrícula","Estudiante","Asistencia","Total","Pagado","Saldo","Teléfono contacto","Nota","Estado","Acción"],[
  ["001-202602794",'<a href="Ficha360.html">María Andrade</a>',"90%","$230","$230","$0","099 000 0001","—",badge("En curso","ok"),'<a href="DetalleMatricula.html">Ver</a>'],
  ["001-202602846",'<a href="Ficha360.html">Pedro Mora</a>',"85%","$230","$122","$108","099 000 0002","—",badge("Saldo pendiente","warn"),'<a href="DetalleMatricula.html">Ver</a>'],
  ["001-202602860",'<a href="Ficha360.html">Valeria Cedeño</a>',"70%","$230","$230","$0","099 000 0003","—",badge("Riesgo asistencia","bad"),'<a href="DetalleMatricula.html">Ver</a>'],
  ["001-202602863",'<a href="Ficha360.html">Gabriela Núñez</a>',"40%","$195","$0","$195","099 000 0004","—",badge("Sin pago · riesgo","bad"),'<a href="DetalleMatricula.html">Ver</a>']])+kv(("Matriculados","12/15"),("Saldo pendiente del curso","$303"),("Asistencia promedio","84%"))+note("Al terminar las 36 horas el curso queda 'Terminado sin calificar' hasta que el profesor registre pass/fail. Reemplaza las vistas 'Matrículas con saldos' y 'Finished courses with ungraded students' de TeamDesk.")),
 subtitle="Las sesiones registradas aquí alimentan la payment sheet del profesor y el progreso del estudiante")
page("DetalleCurso.html","Detalle curso",det,"Detalle de curso y sesiones")

# 9 Profesores
prof=shell("Profesores","Profesores",
 filters(search("Buscar","Nombre o cédula",w="260px"),sel("Estado",["Todos","Activo","Pendiente de aprobación","Inactivo"],w="200px"),sel("Contrato",["Todos","Por horas","Nómina","Vencido"],w="140px"),actions=btn("Alta de profesor","AltaProfesor.html",True)+btn("Payment sheet","PaymentSheet.html")),
 table(["Profesor","Sede","Contrato","Tarifa/h","Cursos activos","Estado","Acción"],[
  ["P. Gómez","Quito","Por horas · vigente","$7.00","3",badge("Activo","ok"),'<a href="FichaProfesor.html">Ver ficha</a>'],
  ["L. Vega","Valle","Por horas · vigente","$6.50","2",badge("Activo","ok"),'<a href="FichaProfesor.html">Ver ficha</a>'],
  ["R. Salas","Ambato","Vencido","$5.70","0",badge("Inactivo","bad"),'<a href="FichaProfesor.html">Ver ficha</a>'],
  ["M. Castro","Ambato","Por horas · vigente","$6.50","2",badge("Activo","ok"),'<a href="FichaProfesor.html">Ver ficha</a>'],
  ["S. Jiménez","Quito","Nómina","—","4",badge("Activo","ok"),'<a href="FichaProfesor.html">Ver ficha</a>'],
  ["D. Paredes","Valle","Por horas · pendiente","$6.00","0",badge("Pendiente de aprobación","warn"),'<a href="FichaProfesor.html">Ver ficha</a>']],sede=1),
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
page("Usuarios.html","Usuarios",shell("Usuarios y roles","Configuración",
 filters(search("Buscar","Nombre o email",w="260px"),sel("Rol",["Todos","Administrador General","Gerente General","Director Comercial","Administrador de Sucursal","Coordinador Académico","Asesor Comercial","Secretaría","Profesor (consulta)"],w="220px"),sel("Estado",["Todos","Activo","Inactivo"],w="130px"),actions=btn("Nuevo usuario",None,True)),
 table(["Usuario","Rol","Sedes visibles","Estado","Acción"],[["Estefanía","Administrador General","Todas","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Carla M.","Asesor Comercial","Quito","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Coord. Académica","Coordinador Académico","Valle","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["P. Gómez","Profesor (consulta)","Quito","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Diego R.","Asesor Comercial","Valle","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Sofía L.","Asesor Comercial","Ambato","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Dir. Comercial","Director Comercial","Todas","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Secretaría Ambato","Secretaría","Ambato","Inactivo",'<a href="NuevoUsuario.html">Editar</a>'],["Admin. Sucursal Valle","Administrador de Sucursal","Valle","Activo",'<a href="NuevoUsuario.html">Editar</a>'],["Gerencia","Gerente General","Todas","Activo",'<a href="NuevoUsuario.html">Editar</a>']],sede=2),
 note("Los empleados de TeamDesk (tabla Employees: p. ej. 'Administrador de Sucursal') se migran como usuarios con rol; los datos personales del empleado (cédula, teléfono, cumpleaños) quedan en su ficha de usuario, no en una tabla aparte."),
 card("Matriz de permisos por rol", table(["Acción","Admin General","Gerente","Dir. Comercial","Admin. Sucursal","Coord. Académica","Asesor","Secretaría"],[["Crear estudiante / matrícula","✓","—","✓","✓","—","✓","✓"],["Aplicar descuento >10%","✓","—","✓","—","—","—","—"],["Aprobar profesor","✓","✓","✓","—","—","—","—"],["Calificar curso (pass/fail)","✓","—","—","—","✓","—","—"],["Aprobar payment sheet","✓","✓","—","✓","—","—","—"],["Exportar base completa","✓","—","—","—","—","—","—"],["Ver otras sedes","✓","✓","✓","—","—","—","—"],["Dashboard ejecutivo","✓","✓","✓","—","—","—","—"]])),
 subtitle="RBAC: roles, permisos por acción y visibilidad multi-sede"),"Usuarios y roles")

# 14 Audit log
page("AuditLog.html","Audit log",shell("Audit log","Configuración",
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
cal="".join(f'<div style="border:1px solid {LINE};min-height:90px;padding:6px;font-size:12px"><b>{d}</b><br>{c}</div>' for d,c in [("Lun 5","B1 Virtual 18:00<br>Kids 2 15:00"),("Mar 6","Teens A2 16:00"),("Mié 7","B1 Virtual 18:00<br>Kids 2 15:00"),("Jue 8","Teens A2 16:00"),("Vie 9","B1 Virtual 18:00"),("Sáb 10","Intensivo A1 09:00"),("Dom 11","")])
page("Sesiones.html","Sesiones",shell("Registro de sesiones","Cursos",
 filters(sel("Semana",["5–11 oct 2026","28 sep–4 oct 2026","12–18 oct 2026"],w="190px",col=False),sel("Profesor",["Todos","P. Gómez","L. Vega","M. Castro"],w="160px"),sel("Origen",["Todos","Automática (Moodle)","Manual"],w="170px"),sel("Estado",["Todas","Confirmada","Pendiente","No dictada"],w="140px"),actions=kv(("Confirmadas","4"),("Pendientes","3"),("No dictadas","1"))+btn("Registrar sesión manual",None,True)),
 table(["Fecha","Curso","Sede","Profesor","Horas","Origen","Estado"],[["Lun 5 · 18:00","B1 Virtual","Quito","P. Gómez","2","Automática (Moodle)",badge("Pendiente","warn")],["Lun 5 · 15:00","Kids 2 Tarde","Valle","L. Vega","2","Manual",badge("Confirmada","ok")],["Mar 6 · 16:00","Teens A2","Ambato","M. Castro","2","Manual",badge("Confirmada","ok")],["Mié 7 · 18:00","B1 Virtual","Quito","P. Gómez","2","Automática (Moodle)",badge("Confirmada","ok")],["Mié 7 · 15:00","Kids 2 Tarde","Valle","L. Vega","2","Manual",badge("No dictada","bad")],["Jue 8 · 16:00","Teens A2","Ambato","M. Castro","2","Manual",badge("Pendiente","warn")],["Vie 9 · 18:00","B1 Virtual","Quito","P. Gómez","2","Automática (Moodle)",badge("Pendiente","warn")],["Sáb 10 · 09:00","Intensivo A1","Quito","L. Vega","4","Manual",badge("Confirmada","ok")]],sede=2),
 card("Calendario de la semana", f'<div style="display:grid;grid-template-columns:repeat(7, minmax(0, 1fr));gap:4px">{cal}</div>'),
 two(card("Sesión seleccionada", kv(("Curso","B1 Virtual · Quito"),("Fecha","Lun 5 oct · 18:00–20:00"),("Profesor","P. Gómez"),("Horas","2"),("Origen","Automática (Moodle)"),("Asistencia","12/15"),("Estado",badge("Pendiente","warn")))+row(btn("Confirmar sesión",None,True),btn("Marcar no dictada"))),
     card("Alertas", li(["Sesión fuera del horario programado","Profesor con contrato vencido","Curso sin sesiones registradas esta semana"]))),
 subtitle="Las sesiones confirmadas alimentan progreso y payment sheet"),"Registro de sesiones")

# 20 Ficha profesor
page("FichaProfesor.html","Ficha profesor",shell("P. Gómez","Profesores",
 row(kv(("Cédula","1709876543"),("Contrato",badge("Por horas · vigente hasta dic 2026","ok")),("Tarifa","$7.00/h"),("Sedes","Quito y Valle"),("Cursos activos","3"),("Horas del mes","48")),'<div style="margin-left:auto"></div>',btn("Editar","AltaProfesor.html"),btn("Ver payment sheet","PaymentSheet.html")),
 tabs(["Datos","Contrato y tarifa","Cursos","Sesiones","Historial de pagos"],"Contrato y tarifa",{
  "Datos": form(["Nombres y apellidos","Cédula / ID","Fecha de nacimiento","Email","Teléfono","Sede(s)","Especialidad / certificaciones","Estado"])+row(btn("Guardar cambios",None,True)),
  "Contrato y tarifa": two(card("Contrato", kv(("Tipo","Por horas"),("Tarifa","$7.00/h"),("Vigencia","1 ene – 31 dic 2026"),("Aprobado por","Dirección · 10 ene 2026"),("Modalidades","Virtual y presencial"))+table(["Documento","Subido por","Fecha"],[["contrato_pgomez_2026.pdf","Coord. Académica","8 ene 2026"],["cedula_pgomez.pdf","Coord. Académica","8 ene 2026"]])),
     card("Historial de contratos", table(["Vigencia","Tipo","Tarifa","Aprobó"],[["2026","Por horas","$7.00/h","Dirección"],["2025","Por horas","$6.50/h","Dirección"]]))),
  "Cursos": table(["Curso","Sede","Nivel","Modalidad","Horario","Estudiantes","Estado"],[["Adults B1 Virtual","Quito","B1","Virtual","L-M-V 19:00","12","En curso"],["Adults A2","Valle","A2","Presencial","M-J 17:00","9","En curso"],["Adults A1","Quito","A1","Presencial","S 09:00","14","Cerrado"]])+row(btn("Ver cursos","Cursos.html")),
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
page("SolicitudDescuento.html","Solicitud de descuento",shell("Solicitud de descuento","Facturación",
 f'<div style="max-width:640px;border:2px solid {INK};padding:24px;display:flex;flex-direction:column;gap:16px">'+kv(("Venta","María Andrade · B1 + B2"),("Precio lista","$1,000"),("Asesor","Carla M."))+form(["Descuento solicitado (%)","Monto resultante"])+form(["Motivo (obligatorio, lista cerrada: referido, promoción, convenio, otro)"],1)+form(["Justificación"],1)+note("Más de 10% requiere aprobación del Director Comercial. El asesor ve el estado de su solicitud en Notificaciones.","warn")+row(btn("Cancelar","NuevaVenta.html"),btn("Enviar solicitud","Aprobaciones.html",True))+'</div>',
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
 table(["Código","ISBN","Producto","Programa","Nivel","Quito","Valle","Ambato","Comprometido","Códigos pendientes","Estado","Acción"],[
  ["1141","9781108961523","Empower B1+ Intermediate Combo B (digital pack)","Adults","B1+","4","-2","1","5","1",badge("Negativo","bad"),'<a href="NuevoPedido.html">Pedir 6</a>'],
  ["1293","9781108909303","Super Minds 2Ed Level 3 WB with Digital Pack","Kids","Kids 2","0","3","-1","4","0",badge("Negativo","bad"),'<a href="NuevoPedido.html">Pedir 4</a>'],
  ["1115","9781009029780","Prepare 3 SB with eBook 2E","Teens","A2","8","2","5","3","0",badge("OK","ok"),"—"],
  ["1132","9781108961691","Empower A1 Starter SB with digital pack","Adults","A1","2","1","0","6","2",badge("Bajo mínimo","warn"),'<a href="NuevoPedido.html">Pedir 5</a>'],
  ["1271","9781009293891","Four Corners 2ED L4 ESB with DP","Adults","B2","6","4","2","2","0",badge("OK","ok"),"—"],
  ["1292","9781108812276","Super Minds 2Ed Level 3 SB with eBook","Kids","Kids 2","3","0","-2","4","0",badge("Negativo","bad"),'<a href="NuevoPedido.html">Pedir 6</a>'],
  ["1116","9781009030502","Prepare 3 WB with Digital Pack 2E","Teens","A2","1","1","1","6","10",badge("Bajo mínimo","warn"),'<a href="NuevoPedido.html">Pedir 4</a>'],
  ["1999","—","Libreta Superpower","—","—","25","10","8","0","—",badge("OK","ok"),"—"]]),
 note("Equivale a Inventory Management + Products/Services de TeamDesk. 'Códigos pendientes' = códigos de activación de material digital comprados y aún no asignados a un estudiante (hoy 'Pending codes')."),
 subtitle="Reemplaza el email diario de notify@teamdesk con alertas inteligentes"),"Inventario de libros")

# 28 Movimientos
page("Movimientos.html","Movimientos",shell("Movimientos y pedidos","Inventario",
 tabs(["Ingresos de proveedor","Movimientos","Pedidos a proveedor","Códigos de activación","Notas de crédito"],"Ingresos de proveedor",{
  "Ingresos de proveedor": filters(search("Buscar","Nº de factura del proveedor",w="220px"),sel("Proveedor",["Todos","Books & Bits","Otro"],w="150px"),sel("Estado",["Todos","Recibido","Con pendientes"],w="150px"),dates(),actions=btn("Registrar ingreso de proveedor",None,True))+table(["Fecha","Ingreso","Factura proveedor","Proveedor","Sede","Ítems","Total","Libros pendientes","Códigos pendientes","Comprobante","Estado"],[
     ["04 oct","IM202610-02","000815787","Books & Bits","Valle","4","$145.30","0","0","comprobante_books_and_bits_2026-10-04.pdf",badge("Recibido","ok")],
     ["01 oct","IM202610-01","000814675","Books & Bits","Valle","14","$456.71","0","0","comprobante_books_and_bits_2026-10-01.pdf",badge("Recibido","ok")],
     ["30 sep","IM202609-12","000813312","Books & Bits","Quito","22","$772.29","0","0","comprobante_2026-09-30.pdf",badge("Recibido","ok")],
     ["30 sep","IM202609-11","Anulación 002-002-000020971","Books & Bits","Quito","1","$85.00","1","0","—",badge("Con pendientes","warn")],
     ["25 sep","IM202609-10","Libretas Superpower","Otro","Ambato","10","$79.92","10","0","—",badge("Con pendientes","warn")],
     ["24 sep","IM202609-09","000809715","Books & Bits","Ambato","9","$333.03","0","0","comprobante_2026-09-24.pdf",badge("Recibido","ok")]],sede=4)
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
page("DashboardEjecutivo.html","Dashboard ejecutivo",shell("Dashboard ejecutivo","Reportes",
 rep_tabs("Dashboard ejecutivo"),
 filters(sel("Período",["2026 (ene–oct)","2025","Último trimestre"],w="170px"),sel("Comparar con",["2025","Sin comparación"],w="160px"),sel("Programa",["Todos","Adults","Teens","Kids"],w="130px")),
 kpis([("Ingresos YTD",sv("$386,400","$204,800","$116,900","$64,700"),"+12% vs 2025"),("Estudiantes activos",sv(812,420,230,162),"+3% vs 2025"),("Ticket promedio por paquete",sv("$915","$940","$890","$880"),"2.1 niveles por venta"),("Margen por sede",sv("34%","38%","31%","27%"),"después de profesores y libros")]),
 two(card("Ingresos por mes (miles de $)", linechart(["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct"],{"Quito":[18,19,21,20,22,21,19,20,23,24],"Valle":[10,11,12,11,13,12,11,12,13,14],"Ambato":[6,6,7,6,7,7,6,6,7,8]})), card("Mix por programa y modalidad", stacked([("Adults",58),("Teens",24),("Kids",18)])+stacked([("Presencial",63),("Virtual",37)]))),
 two(card("Funnel comercial (2026)", funnel([("Leads Kommo",2840),("Cotizaciones",1120),("Ventas",640),("Matriculados",598)])), card("Retención y avance de niveles", hbars([("Continúan al siguiente nivel",71),("Pausan (vuelven en 6 meses)",14),("Abandonan",15)],"")+progress(71,"Retención objetivo 2026: 75%"))),
 subtitle="Vista gerencial, distinta de la reportería operativa"),"Dashboard ejecutivo")

# 31 Chatbot
chat=f'<div style="max-width:760px;border:2px solid {INK};display:flex;flex-direction:column;height:520px"><div style="flex:1;padding:16px;display:flex;flex-direction:column;gap:12px;overflow:auto">'+ \
 f'<div style="align-self:flex-end;max-width:70%;padding:10px 14px;background:{INK};color:#fff;font-size:14px">¿Cuántos estudiantes activos tiene Valle en nivel B1?</div>'+ \
 f'<div style="align-self:flex-start;max-width:70%;padding:10px 14px;background:{FILL};font-size:14px">Valle tiene 23 estudiantes activos en B1, repartidos en 2 cursos (P. Gómez y L. Vega). ¿Quieres ver el listado?</div>'+ \
 f'<div style="align-self:flex-end;max-width:70%;padding:10px 14px;background:{INK};color:#fff;font-size:14px">¿Qué pagos a profesores están pendientes de aprobar?</div>'+ \
 f'<div style="align-self:flex-start;max-width:70%;padding:10px 14px;background:{FILL};font-size:14px">La payment sheet de octubre está en borrador con 2 alertas. Solo puedes ver pagos de las sedes que tu rol permite.</div>'+ \
 f'</div><div style="display:flex;gap:8px;padding:12px;border-top:2px solid {LINE}"><label for="msg" style="position:absolute;left:-9999px">Mensaje</label><input id="msg" placeholder="Pregunta sobre estudiantes, cursos, pagos o reportes" style="flex:1;min-height:44px;padding:0 12px;border:2px solid {LINE};font-size:14px">{btn("Enviar",None,True)}</div></div>'
page("Chatbot.html","Asistente interno",shell("Asistente interno","Inicio",chat,
 two(card("Qué puede responder", li(["Consultas sobre estudiantes, cursos, profesores, facturas y stock","Estado de aprobaciones y payment sheet","Resúmenes: '¿cuántos estudiantes activos tiene Valle en B1?'"])), card("Límites", li(["Responde solo con datos de la plataforma","Respeta el rol y las sedes del usuario (RBAC)","No modifica datos: para eso enlaza a la pantalla correspondiente"]))),
 subtitle="Consulta ágil para el equipo, sin armar un reporte"),"Asistente interno")

# 32 Integraciones
page("Integraciones.html","Integraciones",shell("Integraciones","Configuración",
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
rec=f'''<div style="min-height:{H}px;display:flex;align-items:center;justify-content:center;font-family:'IBM Plex Sans',sans-serif;color:{INK};background:{FILL2}">
<form style="width:100%;max-width:420px;background:#fff;border:2px solid {INK};padding:40px;display:flex;flex-direction:column;gap:18px;box-sizing:border-box">
  {logo()}
  <h1 style="margin:0;font-size:22px">Recuperar contraseña</h1>
  <p style="margin:0;font-size:14px;color:{MUTE}">Te enviamos un enlace temporal al correo registrado. Caduca en 30 minutos.</p>
  <label for="email" style="font-size:13px;font-weight:600">Correo</label>
  <input id="email" type="email" placeholder="nombre@cambridge.edu.ec" style="min-height:44px;padding:0 12px;border:2px solid {LINE};font-size:14px">
  {btn("Enviar enlace",None,True,"Si el correo existe se envía el enlace de recuperación. El intento queda en el audit log.","Main.html")}
  <a href="Main.html" style="font-size:13px;text-align:center">Volver al login</a>
</form>
</div>'''
page("RecuperarContrasena.html","Recuperar contraseña",rec,"Recuperar contraseña")

# 35 Registrar sesión manual
page("RegistrarSesion.html","Registrar sesión",shell("Registrar sesión manual","Cursos",
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
page("RegistrarMovimiento.html","Registrar movimiento",shell("Registrar movimiento de inventario","Inventario",
 form(["Tipo (ingreso / salida / traslado / devolución)","Libro","Cantidad","Sede origen","Sede destino (solo traslado)","Vinculado a (factura / curso / pedido / nota de crédito)","Observación"]),
 note("Una salida sin factura o curso vinculado pide justificación y se marca para revisión.","warn"),
 row(btn("Cancelar","Movimientos.html"),btn("Registrar movimiento",None,True,"Se actualiza el stock de la sede y el movimiento queda en el historial con tu usuario.","Movimientos.html")),
 subtitle="Reemplaza los ajustes a mano en TeamDesk"),"Registrar movimiento")

# 39 Nuevo pedido a proveedor
page("NuevoPedido.html","Nuevo pedido",shell("Nuevo pedido a proveedor","Inventario",
 form(["Proveedor (Books & Bits)","Sede destino","Fecha estimada de entrega"]),
 card("Ítems", table(["Libro","Stock actual","Comprometido","Sugerido","Cantidad a pedir"],[["Adults B1 Student Book","-2","5","6","6"],["Kids 2 Workbook","-1","4","4","4"],["Teens A2","5","3","—","0"]])+note("Sugerido = comprometido por cursos que abren − stock disponible.")),
 row(btn("Cancelar","Movimientos.html"),btn("Enviar pedido",None,True,"El pedido queda En camino y se notifica a Secretaría de la sede para registrar el ingreso cuando llegue.","Movimientos.html")),
 subtitle="Pedido con cantidades sugeridas por el forecast de cursos"),"Nuevo pedido a proveedor")

# 40 Nuevo usuario
page("NuevoUsuario.html","Nuevo usuario",shell("Nuevo usuario","Configuración",
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
 ("Acceso y navegación",[("Main.html","Login"),("RecuperarContrasena.html","Recuperar contraseña"),("Home.html","Inicio por rol"),("Notificaciones.html","Notificaciones"),("Chatbot.html","Asistente interno")],"Login → Inicio por rol. Las notificaciones y el asistente son transversales y acompañan todos los flujos."),
 ("Estudiantes",[("Estudiantes.html","Listado"),("NuevoEstudiante.html","Nuevo estudiante"),("Ficha360.html","Ficha 360°"),("DetalleMatricula.html","Detalle de matrícula"),("ImportExport.html","Importar / exportar")],"Buscar o crear estudiante → ficha 360° con matrículas, niveles, facturas y archivos. Importación con validación de duplicados, exportación auditada."),
 ("Flujo comercial",[("NuevaVenta.html","Nueva matrícula (venta por niveles)"),("SolicitudDescuento.html","Solicitud de descuento"),("Aprobaciones.html","Bandeja de aprobaciones"),("Facturas.html","Facturas"),("DetalleFactura.html","Detalle de factura"),("RegistrarPago.html","Registrar pago"),("NotaCredito.html","Nota de crédito")],"Venta por paquete de niveles → descuento fuera de regla pasa por aprobación." if HIDDEN else "Venta por paquete de niveles → descuento fuera de regla pasa por aprobación → una factura consolidada con su estado de cobro, pagos y notas de crédito."),
 ("Flujo académico",[("Cursos.html","Cursos"),("NuevoCurso.html","Nuevo curso"),("DetalleCurso.html","Detalle de curso"),("Sesiones.html","Registro de sesiones"),("RegistrarSesion.html","Sesión manual")],"Curso con profesor validado → sesiones registradas (automáticas o manuales) → alimentan progreso del estudiante y payment sheet."),
 ("Flujo profesores",[("Profesores.html","Profesores"),("AltaProfesor.html","Alta con aprobación"),("FichaProfesor.html","Ficha del profesor"),("PaymentSheet.html","Payment sheet")],"Alta pasa por aprobación antes de poder cobrar. Payment sheet = sesiones × tarifa, comparada contra la factura del profesor."),
 ("Comisiones",[("Comisiones.html","Período de comisiones"),("DetalleComision.html","Detalle por asesor"),("ReglasComision.html","Reglas de comisión")],"Cierre de mes: cálculo automático por reglas configurables (draft → revisión → aprobado), con detalle por asesor."),
 ("Inventario",[("Inventario.html","Stock por sede"),("Movimientos.html","Movimientos y pedidos"),("NuevoPedido.html","Nuevo pedido"),("RegistrarMovimiento.html","Registrar movimiento")],"Stock por sede, pedidos a Books & Bits, ingresos, movimientos y notas de crédito vinculadas a cursos y facturas."),
 ("Reportes y dashboards",[("Reportes.html","Dashboard por rol"),("ConstructorReportes.html","Constructor de reportes"),("DashboardEjecutivo.html","Dashboard ejecutivo")],"Reportería operativa self-service y vista gerencial separada."),
 ("Administración y gobierno",[("Usuarios.html","Usuarios y roles"),("NuevoUsuario.html","Nuevo usuario"),("Configuracion.html","Configuración"),("NuevaSede.html","Nueva sede"),("NuevoNivel.html","Nuevo nivel"),("NuevaRegla.html","Nueva regla"),("AuditLog.html","Audit log"),("Integraciones.html","Integraciones")],"RBAC, catálogos y reglas configurables, trazabilidad completa e integraciones con Kommo, Moodle y Dora."),
]
sec=""
N=0
rows=[(t,[(f,n) for f,n in files if f not in HIDDEN],d) for t,files,d in rows]
rows=[r for r in rows if r[1]]
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
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap">
<link rel="stylesheet" href="style.css">
</head>
<body class="hub">
<header class="hub-head">
<h1>Plataforma Cambridge · Wireframes</h1>
<p>Versión de alto nivel para validar el flujo, no el diseño. Cada pantalla es navegable: los botones y enlaces llevan a la siguiente pantalla del flujo. {TOTAL} pantallas que cubren los 11 módulos del contrato. Los botones de acción (guardar, aprobar, exportar…) muestran qué pasaría al confirmar. El selector de sede de la barra superior filtra cifras y tablas.</p>
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
open(os.path.join(ROOT,"README.md"),"w").write("# Wireframes Plataforma Cambridge\n\nWireframes estáticos de alto nivel (HTML/CSS, sin build) publicados con GitHub Pages.\n\n- `index.html`: mapa de pantallas por flujo\n- Una página por pantalla (`Main.html` = login)\n\nPublicación: GitHub Pages desde `main` / root (Settings → Pages → Deploy from a branch) o con el workflow `.github/workflows/pages.yml` (Source: GitHub Actions). URL: https://crpozo.github.io/cambridge-wireframes/\n")
