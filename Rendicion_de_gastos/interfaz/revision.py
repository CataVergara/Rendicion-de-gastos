import streamlit as st

def renderizar_vista(repositorio, caso_uso):
    st.markdown("""
        <style>
        .auditoria-container { max-width: 900px; margin: 0 auto; }
        .btn-aprobar button { background-color: #10b981 !important; color: white !important; font-weight: 700 !important; border-radius: 6px !important; }
        .btn-aprobar button:hover { background-color: #059669 !important; }
        .btn-observar button { background-color: #f59e0b !important; color: white !important; font-weight: 700 !important; border-radius: 6px !important; }
        .btn-observar button:hover { background-color: #d97706 !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="auditoria-container">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #0f172a; font-size: 24px; font-weight: 800; margin: 0;'>Bandeja de Auditoría - Analista</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 14px; margin-bottom: 25px;'>Revisión técnica de legalidad y visualización de adjuntos reales.</p>", unsafe_allow_html=True)

    gastos = [r for r in repositorio.obtener_todas() if r['estado'] == 'Pending' or (r['estado'] == 'Pendiente' and not r.get('requiere_gerencia', False))]

    if not gastos:
        st.info("No se registran documentos pendientes de auditoría técnica estándar.")
    else:
        for g in gastos:
            viene_de_gerencia = g['monto'] > 500000
            borde_tarjeta = "#4f46e5" if viene_de_gerencia else "#2563eb"
            
            st.markdown(f"""
                <div style='background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; border-left: 5px solid {borde_tarjeta}; margin-bottom: 10px;'>
                    <strong style='color: #0f172a;'>Folio: {g['folio']} | Solicitante: {g['usuario']}</strong><br/>
                    <span style='color: #475569;'>Monto: ${g['monto']:,} | RUT: {g['rut']} | Emisión: {g['fecha_documento']}</span><br/>
                    <span style='color: #64748b; font-size: 13px; font-style: italic;'>Justificación: {g['justificacion']}</span>
                </div>
            """, unsafe_allow_html=True)

            if viene_de_gerencia:
                st.warning("ℹ️ **Control Jerárquico:** Este documento ya posee la firma digital de aprobación de la Gerencia de Finanzas por Alta Cuantía. Proceda con la auditoría técnica de la evidencia.")

            # --- RENDERIZADO DESDE BASE64 DE FIRESTORE ---
            with st.expander(f"🔍 Ver Evidencia Digital Adjunta Real (Folio {g['folio']})"):
                b64_data = g.get("archivo_base64", "")
                mime_type = g.get("archivo_mime", "image/png")
                
                if b64_data:
                    if "image" in mime_type:
                        # Insertar el string Base64 directamente como fuente de la imagen en HTML
                        st.markdown(f"""
                            <div style="text-align: center; background-color: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 15px;">
                                <img src="data:{mime_type};base64,{b64_data}" style="max-width: 100%; max-height: 400px; border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);"/>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Si es un PDF, creamos un botón de descarga decodificado en tiempo real
                        bytes_decorados = base64.b64decode(b64_data)
                        st.info("La evidencia se guardó como un Documento PDF institucional.")
                        st.download_button(
                            label="📥 Descargar y Visualizar PDF Adjunto",
                            data=bytes_decorados,
                            file_name=f"boleta_folio_{g['folio']}.pdf",
                            mime=mime_type,
                            use_container_width=True
                        )
                else:
                    st.markdown("""
                        <div style="background-color: #f1f5f9; padding: 15px; border-radius: 6px; font-family: monospace; font-size: 12px; color: #475569;">
                            [OCR ADAPTATIVE FALLBACK] Sin archivo binario físico en base de datos.<br>
                            RUT EMISOR DETECTADO: {}<br>
                            FOLIO CORRESPONDIENTE: {}<br>
                            TOTAL TRANSACCIÓN: ${:,}
                        </div>
                    """.format(g['rut'], g['folio'], g['monto']), unsafe_allow_html=True)

            comentario_obs = st.text_input("Motivo del Reparo Técnico (Obligatorio para observar)", key=f"txt_obs_{g['id']}", placeholder="Ej: Imagen borrosa o datos dispares.")

            col_b1, col_b2, _ = st.columns([3, 3, 4])
            with col_b1:
                st.markdown('<div class="btn-aprobar">', unsafe_allow_html=True)
                if st.button("Aprobar Documento", key=f"ap_btn_{g['id']}", use_container_width=True):
                    repositorio.actualizar_estado(g['id'], "Autorizado", "Catalina Vergara")
                    st.success(f"Folio {g['folio']} autorizado con éxito.")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with col_b2:
                st.markdown('<div class="btn-observar">', unsafe_allow_html=True)
                if st.button("Observar Gasto (E1)", key=f"obs_btn_{g['id']}", use_container_width=True):
                    if not comentario_obs.strip():
                        st.error("Ingrese un comentario explicativo para poder observar la rendición.")
                    else:
                        g["comentario_auditoria"] = comentario_obs.strip()
                        repositorio.actualizar_estado(g['id'], "Observado", "Catalina Vergara")
                        st.warning(f"Folio {g['folio']} devuelto al colaborador para corrección.")
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)