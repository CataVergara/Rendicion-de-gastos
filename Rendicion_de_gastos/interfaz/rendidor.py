import streamlit as st

def renderizar_vista(repositorio, caso_uso, usuario_activo):
    # Inicializar llaves de sesión para edición si no existen
    if "gasto_editar_id" not in st.session_state:
        st.session_state.gasto_editar_id = None
        st.session_state.val_rut = ""
        st.session_state.val_folio = ""
        st.session_state.val_monto = 0
        st.session_state.val_just = ""

    st.markdown("""
        <style>
        /* 1. Fondo general claro para la mesa de trabajo */
        .stApp { 
            background-image: none !important; 
            background-color: #f8fafc !important; 
        }
        .stApp::before { display: none !important; }
        
        /* 2. BARRA LATERAL AZUL CÁLIDO PROFESIONAL */
        [data-testid="stSidebar"] {
            background-color: #1e3a8a !important; 
            border-right: 1px solid #172554 !important;
        }
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
            color: #ffffff !important; 
            font-weight: 700 !important;
        }
        [data-testid="stSidebar"] p {
            color: #bfdbfe !important; 
            font-weight: 500 !important;
        }
        [data-testid="stSidebar"] button {
            background-color: #2563eb !important;
            color: #ffffff !important;
            border: 1px solid #3b82f6 !important;
            border-radius: 6px !important;
        }
        [data-testid="stSidebar"] button:hover {
            background-color: #ef4444 !important;
            border-color: #f87171 !important;
        }

        /* 3. ALINEACIÓN GENERAL DEL CONTENIDO CENTRAL */
        .ft-max-width-container {
            max-width: 900px;
            margin: 0 auto;
        }
        
        /* 4. DEGRADADO EN LA TARJETA */
        [data-testid="stVerticalBlockBorderWrapper"], 
        [data-testid="stVerticalBlockBorderWrapper"] > div,
        div[data-linejoin="true"] {
            background: linear-gradient(135deg, #ffffff 30%, #cbd5e1 100%) !important;
            border-radius: 14px !important;
        }
        
        [data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid #cbd5e1 !important;
            box-shadow: 0 10px 20px -3px rgba(15, 23, 42, 0.1) !important;
            padding: 25px !important;
        }
        
        input, select, div[role="combobox"] button, .stNumberInput div {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #94a3b8 !important;
            border-radius: 6px !important;
            height: 40px !important;
        }
        
        input {
            color: #0f172a !important;
            -webkit-text-fill-color: #0f172a !important;
        }
        
        [data-testid="stFileUploadDropzone"] {
            background-color: #ffffff !important;
            border: 2px dashed #94a3b8 !important;
            border-radius: 6px !important;
        }

        [data-testid="stWidgetLabel"] p, label, .stMarkdown p {
            color: #0f172a !important;
            font-weight: 700 !important;
        }
        
        .header-card {
            background-color: #ffffff;
            padding: 22px 30px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            margin-bottom: 20px;
        }
        
        .btn-azul-submit button {
            background-color: #1e3a8a !important;
            color: #ffffff !important;
            border-radius: 6px !important;
            padding: 14px 0px !important;
            font-weight: 700 !important;
            height: auto !important;
            border: none !important;
            margin-top: 15px !important;
            box-shadow: 0 4px 12px rgba(30, 58, 138, 0.2) !important;
        }
        .btn-azul-submit button:hover {
            background-color: #0f172a !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="ft-max-width-container">', unsafe_allow_html=True)

    # Encabezado dinámico
    titulo_acc = "Corregir Rendición de Gastos" if st.session_state.gasto_editar_id else "Módulo de Rendición de Gastos"
    sub_acc = f"Modificando Folio Rechazado: {st.session_state.val_folio}" if st.session_state.gasto_editar_id else "Carga técnica de evidencias, categorización y metadatos financieros."

    st.markdown(f"""
        <div class="header-card">
            <h2 style="color: #1e3a8a; font-size: 22px; font-weight: 800; margin: 0;">{titulo_acc}</h2>
            <p style="color: #64748b; font-size: 13px; margin: 4px 0 0 0;">{sub_acc}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Formulario compacto
    with st.container(border=True):
        st.markdown('<p style="font-size: 13px; letter-spacing: 0.5px; color: #475569 !important; font-weight: 800; margin-top: 5px; margin-bottom: 15px;">DATOS SOLICITADOS DEL COMPROBANTE</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            input_rut = st.text_input("RUT Emisor", value=st.session_state.val_rut, placeholder="76.xxx.xxx-x")
            input_folio = st.text_input("Número de Folio / Boleta", value=st.session_state.val_folio, placeholder="Ej: 00412")
        with col2:
            input_monto = st.number_input("Monto Total Documento ($)", value=st.session_state.val_monto, min_value=0, step=1000)
            input_just = st.text_input("Justificación Comercial / Motivo", value=st.session_state.val_just, placeholder="Ej: Compra de insumos TI")
            
        col3, col4 = st.columns(2)
        with col3:
            categoria = st.selectbox(
                "Categoría de Clasificación",
                ["Seleccione una categoría...", "Logística y Transportes", "Alimentación y Viáticos", "Materiales e Insumos TI", "Licencias y Servicios Cloud"]
            )
        with col4:
            st.markdown("<p style='font-weight: 700; font-size: 14px; margin-bottom: 4px; color: #0f172a;'>Evidencia Digital Adjunta</p>", unsafe_allow_html=True)
            archivo_cargado = st.file_uploader("Subir comprobante", type=["pdf", "png", "jpg", "jpeg"], label_visibility="collapsed")
            
        st.markdown('<div class="btn-azul-submit">', unsafe_allow_html=True)
        texto_boton = "Re-enviar a Auditoría" if st.session_state.gasto_editar_id else "Enviar a Flujo de Aprobación"
        btn_enviar = st.button(texto_boton, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if btn_enviar:
        if archivo_cargado is None:
            st.error("Error obligatorio: Debe adjuntar el archivo o la nueva captura legible.")
        elif categoria == "Seleccione una categoría...":
            st.error("Error: Seleccione la categoría correspondiente.")
        elif not input_rut or not input_folio or input_monto <= 0:
            st.error("Error: Complete los metadatos requeridos.")
        else:
            justificacion_completa = f"[{categoria}] {input_just}"
            
            if st.session_state.gasto_editar_id:
                g_id = st.session_state.gasto_editar_id
                # Buscamos y actualizamos de forma segura asegurando la llave usuario_id
                for r in repositorio.obtener_todas():
                    if r["id"] == g_id:
                        r["rut"] = input_rut
                        r["folio"] = input_folio
                        r["monto"] = input_monto
                        r["justificacion"] = justificacion_completa
                        r["estado"] = "Pendiente"
                        r["usuario_id"] = usuario_activo["id"] # <--- FIJAR ID AQUÍ PARA EVITAR EL KEYERROR
                        if "comentario_auditoria" in r: 
                            del r["comentario_auditoria"]
                
                st.success("¡Rendición corregida y re-enviada con éxito!")
                st.session_state.gasto_editar_id = None
                st.session_state.val_rut = ""; st.session_state.val_folio = ""; st.session_state.val_monto = 0; st.session_state.val_just = ""
                st.rerun()
            else:
                # Flujo normal de creación
                resultado = caso_uso.registrar_gasto(usuario_activo["nombre"], input_rut, input_folio, input_monto, justificacion_completa)
                if resultado["success"]:
                    # Asegurar de forma explícita que el nuevo registro herede el id activo antes de renderizar
                    repositorio.obtener_todas()[-1]["usuario_id"] = usuario_activo["id"]
                    st.success("Rendición cargada con éxito.")
                    st.rerun()

    # Historial de Rendiciones Recientes de forma ultra-segura contra KeyErrors
    st.markdown("<br><h3 style='color:#1e3a8a; font-weight:800; font-size:18px; margin-bottom: 12px;'>Mis Rendiciones Recientes</h3>", unsafe_allow_html=True)
    
    # Filtramos la lista capturando excepciones por si quedó algún registro corrupto flotando en la sesión
    todas_r = repositorio.obtener_todas()
    mis_gastos = [g for g in todas_r if g.get('usuario_id') == usuario_activo['id']]
    
    if not mis_gastos:
        st.markdown("<p style='color:#64748b; font-size:14px; font-style:italic;'>No registra documentos ingresados.</p>", unsafe_allow_html=True)
    else:
        for g in mis_gastos:
            # Seleccionar color de badge según estado
            estado_g = g.get('estado', 'Pendiente')
            if estado_g == 'Observado':
                bg_badge, font_badge = '#fef3c7', '#d97706'
            elif estado_g in ['Autorizado', 'Aprobado Analista', 'Pagado']:
                bg_badge, font_badge = '#d1fae5', '#065f46'
            else:
                bg_badge, font_badge = '#e0f2fe', '#0369a1'

            st.markdown(f"""
                <div style='background-color: #ffffff; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);'>
                    <span style='float: right; background-color: {bg_badge}; color: {font_badge}; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;'>{estado_g}</span>
                    <strong style='color:#0f172a; font-size:15px;'>Folio: {g.get('folio', 'S/F')}</strong> <br/>
                    <span style='color:#334155; font-size:14px; display:inline-block; margin-top:4px;'>{g.get('justificacion', '')}</span><br/>
            """, unsafe_allow_html=True)
            
            if estado_g == 'Observado' and g.get("comentario_auditoria"):
                st.markdown(f"""
                    <div style="background-color: #fffbeb; border: 1px solid #fde68a; padding: 10px; border-radius: 6px; margin: 8px 0; color: #b45309; font-size: 13px;">
                        <strong>⚠️ Comentario de Auditoría:</strong> {g['comentario_auditoria']}
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Corregir Folio {g.get('folio')}", key=f"corr_{g.get('id')}"):
                    st.session_state.gasto_editar_id = g.get('id')
                    st.session_state.val_rut = g.get('rut', '')
                    st.session_state.val_folio = g.get('folio', '')
                    st.session_state.val_monto = g.get('monto', 0)
                    just_raw = g.get('justificacion', '')
                    st.session_state.val_just = just_raw.split(']')[-1].strip() if ']' in just_raw else just_raw
                    st.rerun()

            st.markdown(f"""
                    <hr style='border: 0; border-top: 1px solid #f1f5f9; margin: 10px 0;'>
                    <span style='color: #64748b; font-size: 13px;'>Monto Operación: ${g.get('monto', 0):,} | RUT Emisor: {g.get('rut', '')}</span>
                </div>
            """, unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)