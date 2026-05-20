import streamlit as st

def renderizar_vista(repositorio, caso_uso):
    st.markdown('<div class="card"><p class="title">Tesorería y Dispersión de Fondos</p><p class="subtitle">Ejecución del pago bancario final sobre cuentas técnicas autorizadas.</p></div>', unsafe_allow_html=True)
    
    rendiciones_autorizadas = [r for r in repositorio.obtener_todas() if r['estado'] == "Autorizado"]
    
    if not rendiciones_autorizadas:
        st.info("No se registran documentos visados listos para liberación de liquidez.")
    else:
        for r in rendiciones_autorizadas:
            st.markdown(f"""
                <div style='background-color: #f0fdf4; padding: 15px; border-radius: 8px; border: 1px solid #bbf7d0; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <strong>Beneficiario de Pago:</strong> {r['usuario']} <br/>
                        <small style='color: #16a34a;'>Documento Tributario: Folio {r['folio']}</small>
                    </div>
                    <span style='color: #16a34a; font-size: 18px; font-weight: bold;'>Liquidez a Transferir: ${r['monto']:,}</span>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("Ejecutar Dispersión de Fondos", key=f"btn_pago_{r['id']}"):
                caso_uso.actualizar_estado_gasto(r['id'], "Pagado")
                st.success("Transacción bancaria simulada con éxito. Liquidación completada.")
                st.rerun()