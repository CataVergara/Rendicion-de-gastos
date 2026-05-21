import streamlit as st

def renderizar_vista(repositorio, caso_uso):
    st.markdown("""
        <style>
        .tesoreria-container { max-width: 900px; margin: 0 auto; }
        .btn-pagar button { background-color: #1e3a8a !important; color: white !important; font-weight:700; border-radius: 6px !important; }
        .btn-pagar button:hover { background-color: #0f172a !important; }
        .btn-encolar button { background-color: #64748b !important; color: white !important; font-weight:700; border-radius: 6px !important; }
        .btn-encolar button:hover { background-color: #475569 !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="tesoreria-container">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #0f172a; font-size: 24px; font-weight: 800; margin: 0;'>Bandeja de Cierre - Tesorería</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 14px; margin-bottom: 25px;'>Gestión de liquidez y dispersión bancaria final.</p>", unsafe_allow_html=True)

    todas = repositorio.obtener_todas()
    # Captura documentos autorizados listos para pago, o retenidos por liquidez
    gastos_pago = [r for r in todas if r['estado'] in ['Autorizado', 'Autorizado - Pendiente de Fondos']]

    if not gastos_pago:
        st.info("No se registran órdenes de pago liberadas por Finanzas.")
    else:
        for g in gastos_pago:
            badge_liq = "⚠️ RETENIDO POR FONDOS" if g['estado'] == 'Autorizado - Pendiente de Fondos' else "✅ DISPONIBLE PARA EGRESO"
            color_liq = "#d97706" if g['estado'] == 'Autorizado - Pendiente de Fondos' else "#10b981"
            
            st.markdown(f"""
                <div style='background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 10px;'>
                    <span style='float: right; color: {color_liq}; font-weight:800; font-size:12px;'>{badge_liq}</span>
                    <strong style='color:#0f172a;'>Folio: {g['folio']} | Beneficiario: {g['usuario']}</strong><br/>
                    <span style='color:#334155; font-weight:700;'>Monto a Reembolsar: ${g['monto']:,}</span><br/>
                    <span style='color:#64748b; font-size:13px;'>Gasto: {g['justificacion']}</span>
                </div>
            """, unsafe_allow_html=True)

            col_t1, col_t2, _ = st.columns([3, 3, 4])
            with col_t1:
                st.markdown('<div class="btn-pagar">', unsafe_allow_html=True)
                # SE CORRIGE: Se pasa "Tesorero Liquidador" como tercer parámetro para registrar el log de pago con éxito
                if st.button(f"Registrar Egreso Bancario", key=f"pag_{g['id']}", use_container_width=True):
                    repositorio.actualizar_estado(g['id'], "Pagado", "Tesorero Liquidador")
                    st.success(f"Folio {g['folio']} pagado con éxito.")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with col_t2:
                # Si el sistema no tiene liquidez, el tesorero lo encola (Manejo de Excepción E6 del informe)
                if g['estado'] != 'Autorizado - Pendiente de Fondos':
                    st.markdown('<div class="btn-encolar">', unsafe_allow_html=True)
                    # SE CORRIGE: Se pasa "Tesorero Liquidador" al mover el folio a la cola de espera de fondos
                    if st.button(f"Retener por Liquidez (E6)", key=f"enc_{g['id']}", use_container_width=True):
                        repositorio.actualizar_estado(g['id'], "Autorizado - Pendiente de Fondos", "Tesorero Liquidador")
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)