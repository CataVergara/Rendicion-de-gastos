import streamlit as st
from datetime import date
import re
import base64

# --- FUNCIONES DE FORMATEO EN TIEMPO REAL ---
def formatear_rut(rut_raw):
    if not rut_raw: return ""
    rut_limpio = re.sub(r'[^0-9kK]', '', str(rut_raw))
    if len(rut_limpio) < 2: return rut_limpio.upper()
    cuerpo = rut_limpio[:-1]
    dv = rut_limpio[-1].upper()
    try:
        cuerpo_formateado = f"{int(cuerpo):,}".replace(",", ".")
        return f"{cuerpo_formateado}-{dv}"
    except ValueError:
        return rut_raw

def formatear_monto(monto_raw):
    if monto_raw == "" or monto_raw is None: return "0"
    monto_limpio = re.sub(r'[^0-9]', '', str(monto_raw))
    if not monto_limpio: return "0"
    return f"{int(monto_limpio):,}".replace(",", ".")

def limpiar_monto_a_int(monto_str):
    monto_limpio = re.sub(r'[^0-9]', '', str(monto_str))
    return int(monto_limpio) if monto_limpio else 0


def renderizar_vista(repositorio, caso_uso, usuario_activo):
    # Inicialización estructurada de variables en el contenedor de estados
    if "val_rut" not in st.session_state:
        st.session_state.val_rut = ""
    if "val_folio" not in st.session_state:
        st.session_state.val_folio = ""
    if "val_monto_str" not in st.session_state:
        st.session_state.val_monto_str = "0"
    if "val_just" not in st.session_state:
        st.session_state.val_just = ""
    if "gasto_editar_id" not in st.session_state:
        st.session_state.gasto_editar_id = None

    st.markdown("""
        <style>
        [data-testid="stSidebar"] { background-color: #1e3a8a !important; }
        [data-testid="stSidebar"] * { color: white !important; }
        .ft-max-width-container { max-width: 900px; margin: 0 auto; }
        [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stVerticalBlockBorderWrapper"] > div {
            background: linear-gradient(135deg, #ffffff 30%, #cbd5e1 100%) !important;
            border-radius: 14px !important;
        }
        .ft-max-width-container div[data-baseweb="input"],
        .ft-max-width-container div[data-baseweb="select"],
        .ft-max-width-container .stNumberInput div,
        .ft-max-width-container [data-baseweb="datepicker"] {
            background-color: #ffffff !important;
            border: 1px solid #94a3b8 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            min-height: 44px !important;
            padding: 0 14px !important;
            margin: 0 !important;
            display: flex !important;
            align-items: center !important;
        }
        .ft-max-width-container div[data-baseweb="input"] > div,
        .ft-max-width-container div[data-baseweb="select"] > div,
        .ft-max-width-container .stNumberInput div > div,
        .ft-max-width-container [data-baseweb="datepicker"] > div {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        .ft-max-width-container input,
        .ft-max-width-container select,
        .ft-max-width-container textarea {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
            color: #0f172a !important;
            height: auto !important;
            padding: 10px 0 !important;
            margin: 0 !important;
        }
        .ft-max-width-container div[role="combobox"] button {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #94a3b8 !important;
            border-radius: 8px !important;
            height: 44px !important;
            padding: 0 14px !important;
            box-shadow: none !important;
            margin: 0 !important;
        }
        .ft-max-width-container [data-testid="stFileUploader"] {
            background-color: #ffffff !important;
            border: 1px solid #94a3b8 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            padding: 10px !important;
            width: 100% !important;
            max-width: 100% !important;
            margin: 0 0 16px 0 !important;
        }
        .ft-max-width-container [data-testid="stFileUploader"] > div:first-child,
        .ft-max-width-container [data-testid="stFileUploader"] > div:first-child > div,
        .ft-max-width-container [data-testid="stFileUploader"] [data-baseweb="input"],
        .ft-max-width-container [data-testid="stFileUploader"] [data-baseweb="file-uploader"],
        .ft-max-width-container [data-testid="stFileUploader"] .css-1v3fvcr {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        .ft-max-width-container [data-testid="stFileUploader"] div[role="button"],
        .ft-max-width-container [data-testid="stFileUploader"] button {
            min-height: 40px !important;
            border-radius: 6px !important;
            background-color: #1e3a8a !important;
            color: #ffffff !important;
            border: none !important;
        }
        .ft-max-width-container [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] {
            margin: 0 !important;
            padding: 0 !important;
        }
        [data-testid="stWidgetLabel"] p, label { color: #0f172a !important; font-weight: 700 !important; }
        .header-card { background-color: #ffffff; padding: 22px 30px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px; }
        .btn-enviar button { background-color: #1e3a8a !important; color: #ffffff !important; font-weight: 700 !important; }
        .btn-borrador button { background-color: #ffffff !important; color: #475569 !important; border: 1px solid #cbd5e1 !important; font-weight: 700 !important; }
        .btn-borrador button:hover { background-color: #f1f5f9 !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="ft-max-width-container">', unsafe_allow_html=True)

    st.markdown("""
        <div class="header-card">
            <h2 style="color: #1e3a8a; font-size: 22px; font-weight: 800; margin: 0;">Módulo de Rendición de Gastos</h2>
            <p style="color: #64748b; font-size: 13px; margin: 4px 0 0 0;">Ingreso técnico de metadatos con persistencia y matriz de trazabilidad.</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.gasto_editar_id:
        st.info(f"📝 Editando activamente la rendición ID/Folio: {st.session_state.val_folio}.")
    
    # SE AGREGA FORMULARIO AUTOMÁTICO CON ENTRADAS DE CONTROL CONJUNTAS
    with st.form("contenedor_rendicion", clear_on_submit=False):
        st.markdown('<p style="font-size: 13px; font-weight: 800; color: #475569;">DATOS SOLICITADOS DEL COMPROBANTE</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            raw_rut = st.text_input("RUT Emisor", value=st.session_state.val_rut, placeholder="Ej: 76123456K")
            input_rut = formatear_rut(raw_rut)
            if input_rut != raw_rut:
                st.session_state.val_rut = input_rut
                st.rerun()

            input_folio = st.text_input("Número de Folio / Boleta", value=st.session_state.val_folio, placeholder="Ej: 00412")
            input_fecha = st.date_input("Fecha de Emisión del Documento", value=date.today())
        with col2:
            raw_monto = st.text_input("Monto Total Documento ($)", value=st.session_state.val_monto_str, placeholder="Ej: 150000")
            monto_formateado = formatear_monto(raw_monto)
            if monto_formateado != raw_monto:
                st.session_state.val_monto_str = monto_formateado
                st.rerun()
            
            input_monto = limpiar_monto_a_int(monto_formateado)
            input_just = st.text_area("Justificación Comercial / Motivo", value=st.session_state.val_just, placeholder="Ej: Insumos TI", height=44)
            categoria = st.selectbox("Categoría de Clasificación", ["Seleccione una categoría...", "Logística y Transportes", "Alimentación y Viáticos", "Materiales e Insumos TI", "Licencias y Servicios Cloud"])
            
        st.markdown("<p style='font-weight: 700; font-size: 14px; margin-bottom: 4px; color: #0f172a;'>Evidencia Digital Adjunta</p>", unsafe_allow_html=True)
        archivo_cargado = st.file_uploader("Subir comprobante", type=["pdf", "png", "jpg", "jpeg"], label_visibility="collapsed")
            
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.markdown('<div class="btn-enviar">', unsafe_allow_html=True)
            btn_enviar = st.form_submit_button("Enviar a Flujo de Aprobación", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col_btn2:
            st.markdown('<div class="btn-borrador">', unsafe_allow_html=True)
            btn_borrador = st.form_submit_button("Guardar como Borrador", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # --- PLANIFICADOR DE CONTROL ANTIFRAUDE Y EXCEPCIONES ---
    if btn_enviar or btn_borrador:
        dias_antiguedad = (date.today() - input_fecha).days
        
        if st.session_state.gasto_editar_id:
            es_duplicado = repositorio.verificar_duplicado(input_rut, input_folio, usuario_activo["id"], exclude_id=st.session_state.gasto_editar_id)
        else:
            es_duplicado = repositorio.verificar_duplicado(input_rut, input_folio, usuario_activo["id"])
        
        if not str(input_rut).strip() or not str(input_folio).strip() or not str(input_just).strip() or input_monto <= 0:
            st.error("⚠️ Error de Completitud: Por favor complete todos los campos mandatorios solicitados y asegure un monto total superior a $0.")
        
        elif categoria == "Seleccione una categoría...":
            st.error("⚠️ Validación técnica: Debe clasificar la rendición dentro de una categoría contable válida.")
            
        elif btn_enviar and archivo_cargado is None:
            st.error("⚠️ BR-04 (Evidencia Obligatoria): Es mandatorio adjuntar el archivo digitalizado de la boleta para enviar a revisión fiscal.")
            
        elif es_duplicado:
            st.error(f"❌ Excepción E4 (Control de Fraude): El Número de Folio '{input_folio}' ya se encuentra registrado en tus rendiciones vigentes.")
            
        else:
            justificacion_completa = f"[{categoria}] {input_just}"
            requiere_g = True if input_monto > 500000 else False
            
            if btn_borrador:
                estado_inicial = "Borrador"
            else:
                if dias_antiguedad > 30:
                    estado_inicial = "Borrador"
                    st.warning(f"⏳ Excepción E5: Documento con {dias_antiguedad} días de antigüedad detectado. El registro se mantendrá bloqueado en 'Borrador' hasta autorización de Gerencia de Finanzas.")
                else:
                    estado_inicial = "Pendiente"

            archivo_b64 = ""
            mime_type = ""
            if archivo_cargado is not None:
                archivo_b64 = base64.b64encode(archivo_cargado.getvalue()).decode("utf-8")
                mime_type = archivo_cargado.type

            if st.session_state.gasto_editar_id:
                g_id = st.session_state.gasto_editar_id
                for r in repositorio.obtener_todas():
                    if r["id"] == g_id:
                        origen = r["estado"]
                        update_data = {
                            "rut": input_rut, "folio": input_folio, "monto": input_monto, 
                            "justificacion": justificacion_completa, "estado": estado_inicial, 
                            "requiere_gerencia": requiere_g, "fecha_documento": str(input_fecha)
                        }
                        if archivo_b64:
                            update_data["archivo_base64"] = archivo_b64
                            update_data["archivo_mime"] = mime_type
                        r.update(update_data)
                        repositorio.registrar_log(g_id, usuario_activo["nombre"], origen, estado_inicial)
                
                # REINICIO ABSOLUTO DE VARIABLES SIN COLISIONES DE BUFFER
                st.session_state.gasto_editar_id = None
                st.session_state.val_rut = ""
                st.session_state.val_folio = ""
                st.session_state.val_monto_str = "0"
                st.session_state.val_just = ""
                st.rerun()
                
            else:
                nuevo_id = repositorio.obtener_siguiente_id_rendicion()
                nueva_rendicion = {
                    "id": nuevo_id, "usuario_id": usuario_activo["id"], "usuario": usuario_activo["nombre"],
                    "rut": input_rut, "folio": input_folio, "monto": input_monto,
                    "justificacion": justificacion_completa, "estado": estado_inicial,
                    "requiere_gerencia": requiere_g, "fecha_documento": str(input_fecha),
                    "archivo_base64": archivo_b64, "archivo_mime": mime_type
                }
                repositorio.obtener_todas().append(nueva_rendicion)
                repositorio.registrar_log(nuevo_id, usuario_activo["nombre"], "Ninguno", estado_inicial)
                
                # REINICIO ABSOLUTO DE VARIABLES SIN COLISIONES DE BUFFER
                st.session_state.val_rut = ""
                st.session_state.val_folio = ""
                st.session_state.val_monto_str = "0"
                st.session_state.val_just = ""
                st.rerun()

    st.markdown("<br><h3 style='color:#1e3a8a; font-weight:800; font-size:18px;'>Mis Rendiciones Recientes</h3>", unsafe_allow_html=True)
    mis_gastos = [g for g in repositorio.obtener_todas() if g.get('usuario_id') == usuario_activo['id']]
    
    for g in mis_gastos:
        estado_g = g['estado']
        if estado_g == 'Observado': bg_b, ft_b = '#fef3c7', '#d97706'
        elif estado_g in ['Autorizado', 'Pagado', 'Aprobado Analista', 'Autorizado - Pendiente de Fondos']: bg_b, ft_b = '#d1fae5', '#065f46'
        elif estado_g == 'Borrador': bg_b, ft_b = '#f1f5f9', '#475569'
        else: bg_b, ft_b = "#e0f2fe", '#0369a1'

        st.markdown(f"""
            <div style='background-color: #ffffff; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 10px;'>
                <span style='float: right; background-color: {bg_b}; color: {ft_b}; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;'>{estado_g}</span>
                <strong>RUT Emisor: {g['rut']}</strong> | <strong>Folio: {g['folio']}</strong> | Monto: ${g['monto']:,} | Emisión: {g['fecha_documento']}<br/>
                <span style='color:#334155; font-size:14px;'>{g['justificacion']}</span>
        """, unsafe_allow_html=True)
        
        if estado_g == 'Borrador':
            st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
            if st.button(f"Editar Borrador Folio {g['folio']}", key=f"edit_borr_{g['id']}", type="secondary"):
                st.session_state.gasto_editar_id = g['id']
                st.session_state.val_rut = g['rut']
                st.session_state.val_folio = g['folio']
                st.session_state.val_monto_str = formatear_monto(g['monto'])
                st.session_state.val_just = g['justificacion'].split(']')[-1].strip()
                st.rerun()
        
        if estado_g == 'Observado' and g.get("comentario_auditoria"):
            st.markdown(f'<div style="background-color: #fffbeb; padding: 10px; border-radius: 6px; margin: 8px 0; color: #b45309; font-size: 13px;">⚠️ <strong>Reparo Analista:</strong> {g["comentario_auditoria"]}</div>', unsafe_allow_html=True)
            if st.button(f"Corregir Folio {g['folio']}", key=f"corr_{g['id']}"):
                st.session_state.gasto_editar_id = g['id']
                st.session_state.val_rut = g['rut']
                st.session_state.val_folio = g['folio']
                st.session_state.val_monto_str = formatear_monto(g['monto'])
                st.session_state.val_just = g['justificacion'].split(']')[-1].strip()
                st.rerun()

        logs_g = repositorio.obtener_logs_por_rendicion(g['id'])
        if logs_g:
            st.markdown("<p style='margin: 8px 0 2px 0; font-size: 11px; color: #94a3b8; font-weight:800;'>HISTORIAL DE TRAZABILIDAD (LOGS):</p>", unsafe_allow_html=True)
            for log in logs_g:
               st.markdown(f"<p style='margin:0; font-size:11px; color:#64748b; font-family:monospace;'>• [{log['timestamp']}] Usuario '{log['autor']}' cambió estado de <strong>{log['estado_origen']}</strong> a <strong>{log['estado_destino']}</strong></p>", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)