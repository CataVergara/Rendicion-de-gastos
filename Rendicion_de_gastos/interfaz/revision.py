import streamlit as st

def renderizar_vista(repositorio, caso_uso):
    st.markdown("""
        <style>
        .auditoria-container { max-width: 1000px; margin: 0 auto; }
        .btn-aprobar button {
            background-color: #10b981 !important; color: white !important;
            border-radius: 6px !important; border: none !important;
        }
        .btn-aprobar button:hover { background-color: #059669 !important; }
        .btn-observar button {
            background-color: #ef4444 !important; color: white !important;
            border-radius: 6px !important; border: none !important;
        }
        .btn-observar button:hover { background-color: #dc2626 !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="auditoria-container">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #0f172a; font-size: 24px; font-weight: 800; margin: 0;'>Bandeja de Auditoría - Analista</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 14px; margin-top: 4px; margin-bottom: 25px;'>Validación, control de integridad y auditoría de evidencias digitales.</p>", unsafe_allow_html=True)

    todas_rendiciones = repositorio.obtener_todas()
    gastos_pendientes = [r for r in todas_rendiciones if r['estado'] == 'Pendiente']

    if not gastos_pendientes:
        st.success("🎉 ¡Bandeja limpia! No registran rendiciones de gastos pendientes de auditoría.")
    else:
        for g in gastos_pendientes:
            color_borde = "#f59e0b" if g.get("requiere_gerencia", False) else "#2563eb"
            
            st.markdown(f"""
                <div style='background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; border-left: 5px solid {color_borde}; margin-bottom: 5px;'>
                    <strong style='color: #0f172a; font-size: 16px;'>Folio: {g['folio']} | Solicitante: {g['usuario']}</strong><br/>
                    <span style='color: #475569; font-size: 14px;'>Monto Operación: <strong>${g['monto']:,}</strong> | RUT Emisor: {g['rut']}</span><br/>
                    <span style='color: #64748b; font-size: 13px; font-style: italic;'>Justificación: {g['justificacion']}</span>
                </div>
            """, unsafe_allow_html=True)

            # Desplegable de Evidencia
            with st.expander(f"🔍 Ver Evidencia Digital Adjunta (Folio {g['folio']})"):
                st.markdown(f"""
                    <div style="border: 1px dashed #cbd5e1; padding: 12px; border-radius: 6px; background-color: #f8fafc; font-family: monospace; font-size: 12px;">
                        RUT EMISOR: {g['rut']} | FOLIO: {g['folio']} | TOTAL: ${g['monto']:,}
                    </div>
                """, unsafe_allow_html=True)

            # Bloque de comentarios para Observaciones
            comentario_obs = st.text_input("Comentario / Motivo del Reparo (Obligatorio para observar)", key=f"txt_obs_{g['id']}", placeholder="Ej: El RUT del emisor no es legible o el monto no coincide.")

            # Acciones
            col_b1, col_b2, _ = st.columns([2, 2, 6])
            with col_b1:
                st.markdown('<div class="btn-aprobar">', unsafe_allow_html=True)
                if st.button(f"Aprobar Documento", key=f"ap_btn_{g['id']}", use_container_width=True):
                    nuevo_estado = "Autorizado" if not g.get("requiere_gerencia", False) else "Aprobado Analista"
                    repositorio.actualizar_estado(g['id'], nuevo_estado)
                    st.success("Aprobado con éxito.")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col_b2:
                st.markdown('<div class="btn-observar">', unsafe_allow_html=True)
                if st.button(f"Observar Gasto", key=f"obs_btn_{g['id']}", use_container_width=True):
                    if not comentario_obs.strip():
                        st.error("Debe ingresar un comentario para poder observar la rendición.")
                    else:
                        # Guardamos el estado como 'Observado' y añadimos el comentario al registro
                        repositorio.actualizar_estado(g['id'], "Observado")
                        # Simulamos guardar el comentario en el diccionario del repositorio
                        g["comentario_auditoria"] = comentario_obs.strip()
                        st.warning(f"Folio {g['folio']} devuelto al rendidor.")
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)