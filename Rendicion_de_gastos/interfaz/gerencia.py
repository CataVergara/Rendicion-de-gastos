import streamlit as st

def renderizar_vista(repositorio, caso_uso):
    # CSS personalizado adaptado al estilo corporativo
    st.markdown("""
        <style>
        .gerencia-container { max-width: 1000px; margin: 0 auto; }
        .card-excepcion { 
            background-color: #ffffff; 
            color: #0f172a;
            padding: 24px; 
            border-radius: 12px; 
            border: 1px solid #cbd5e1; 
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        }
        .card-excepcion h4 {
            color: #0f172a !important;
            margin: 0 0 8px 0;
            font-size: 16px;
        }
        .card-excepcion p {
            color: #334155 !important;
            margin: 0;
            font-size: 14px;
        }
        .card-excepcion strong {
            color: #0f172a !important;
        }
        .btn-visar button { 
            background-color: #4f46e5 !important; 
            color: white !important; 
            font-weight: 700 !important; 
            border-radius: 8px !important;
        }
        .btn-visar button:hover { 
            background-color: #4338ca !important; 
        }
        .btn-rechazar button { 
            background-color: #ef4444 !important; 
            color: white !important; 
            font-weight: 700 !important; 
            border-radius: 8px !important;
        }
        .btn-rechazar button:hover { 
            background-color: #dc2626 !important; 
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="gerencia-container">', unsafe_allow_html=True)
    
    # Encabezado del módulo
    st.markdown("""
        <div style="background-color: #ffffff; padding: 22px 30px; border-radius: 12px; border: 1px solid #cbd5e1; margin-bottom: 25px;">
            <h2 style='color: #1e3a8a; font-size: 24px; font-weight: 800; margin: 0;'>Bandeja de Control Excepcional - Gerencia</h2>
            <p style='color: #64748b; font-size: 14px; margin: 4px 0 0 0;'>
                Visación jerárquica de rendiciones que superan umbrales financieros o plazos de caducidad (Fase 2).
            </p>
        </div>
    """, unsafe_allow_html=True)

    todas_rendiciones = repositorio.obtener_todas()
    
    # Captura documentos en 'Borrador' (por tiempo vencido) o 'Pendiente' que requieran validación de monto alto
    gastos_excepcionales = [
        r for r in todas_rendiciones 
        if r['estado'] == 'Borrador' or (r['estado'] == 'Pendiente' and r.get('requiere_gerencia', False))
    ]

    if not gastos_excepcionales:
        st.success("🎉 No se registran casos excepcionales pendientes de aprobación gerencial.")
    else:
        for g in gastos_excepcionales:
            # Identificación dinámica del tipo de infracción según las Reglas de Negocio (BR)
            es_monto_alto = g['monto'] > 500000
            
            if es_monto_alto and g['estado'] == 'Borrador':
                tipo_alerta = "🚨 CRÍTICO: ALTO MONTO Y FECHA VENCIDA"
                color_alerta = "#e11d48"  # Rojo intenso
            elif es_monto_alto:
                tipo_alerta = "💰 ALTA CUANTÍA (>500K) - BR-05"
                color_alerta = "#4f46e5"  # Indigo
            else:
                tipo_alerta = "⏳ CADUCIDAD FISCAL (>30 DÍAS) - BR-02"
                color_alerta = "#d97706"  # Ámbar

            st.markdown(f"""
                <div class="card-excepcion" style="border-left: 6px solid {color_alerta};">
                    <span style='float: right; color: {color_alerta}; font-weight: 800; font-size: 12px; background-color: {color_alerta}15; padding: 4px 10px; border-radius: 12px;'>
                        {tipo_alerta}
                    </span>
                    <h4>Folio: {g['folio']} | Colaborador: {g['usuario']}</h4>
                    <p>
                        <strong>Monto Documentado:</strong> ${g['monto']:,} CLP <br/>
                        <strong>RUT Emisor:</strong> {g['rut']} | <strong>Fecha Emisión:</strong> {g['fecha_documento']} <br/>
                        <span style='color: #64748b; font-style: italic;'><strong>Justificación:</strong> {g['justificacion']}</span>
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # Botones de Acción para el Gerente
            col_btn1, col_btn2, _ = st.columns([3, 3, 4])
            
            with col_btn1:
                st.markdown('<div class="btn-visar">', unsafe_allow_html=True)
                if st.button(f"Otorgar Flag de Visación", key=f"vis_ger_{g['id']}", use_container_width=True):
                    # Al visar, removemos el bloqueo jerárquico y lo pasamos al Analista de Finanzas
                    repositorio.actualizar_estado(g['id'], "Pendiente", "Gerente de Finanzas")
                    
                    # Buscamos el registro modificado para apagar el flag y que baje a auditoría técnica
                    for r in todas_rendiciones:
                        if r['id'] == g['id']:
                            r['requiere_gerencia'] = False
                            
                    st.success(f" Folio {g['folio']} visado con éxito. Derivado a Auditoría Técnica.")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col_btn2:
                st.markdown('<div class="btn-rechazar">', unsafe_allow_html=True)
                if st.button(f"Rechazo Definitivo", key=f"rech_ger_{g['id']}", use_container_width=True):
                    repositorio.actualizar_estado(g['id'], "Rechazado", "Gerente de Finanzas")
                    st.error(f" Folio {g['folio']} ha sido rechazado de forma definitiva.")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                
            st.markdown("<hr style='border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;'>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)