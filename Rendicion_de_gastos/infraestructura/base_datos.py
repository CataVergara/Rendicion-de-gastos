import streamlit as st
from datetime import datetime

class RepositorioRendicionMemory:
    def __init__(self):
        if 'db_usuarios' not in st.session_state:
            st.session_state.db_usuarios = [
                {"id": 1, "username": "francisco", "password": "123", "nombre": "Francisco Benavides", "rol": "Rendidor"},
                {"id": 2, "username": "catalina", "password": "123", "nombre": "Catalina Vergara", "rol": "Bandeja Auditoria"},
                {"id": 3, "username": "gerente", "password": "123", "nombre": "Gerente de Finanzas", "rol": "Gerencia Finanzas"},
                {"id": 4, "username": "tesorero", "password": "123", "nombre": "Tesorero Liquidador", "rol": "Cierre Tesoreria"}
            ]
        
        if 'db_rendiciones' not in st.session_state:
            st.session_state.db_rendiciones = [
                {
                    "id": 1, 
                    "usuario_id": 1, 
                    "usuario": "Francisco Benavides", 
                    "rut": "76.452.128-K", 
                    "folio": "1045", 
                    "monto": 620000, 
                    "estado": "Pendiente", 
                    "justificacion": "[Materiales e Insumos TI] Compra de insumos y routers ISP.", 
                    "requiere_gerencia": True,
                    "fecha_documento": "2026-05-10"
                }
            ]

        # SECCIÓN 10: Inicialización de la Entidad Log Evento para trazabilidad académica
        if 'db_logs' not in st.session_state:
            st.session_state.db_logs = [
                {"id": 1, "rendicion_id": 1, "autor": "Francisco Benavides", "estado_origen": "Borrador", "estado_destino": "Pendiente", "timestamp": "2026-05-21 10:30"}
            ]

    def registrar_log(self, rendicion_id: int, autor: str, origen: str, destino: str):
        nuevo_log = {
            "id": len(st.session_state.db_logs) + 1,
            "rendicion_id": rendicion_id,
            "autor": autor,
            "estado_origen": origen,
            "estado_destino": destino,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        st.session_state.db_logs.append(nuevo_log)

    def obtener_logs_por_rendicion(self, rendicion_id: int):
        return [log for log in st.session_state.db_logs if log["rendicion_id"] == rendicion_id]

    def validar_credenciales(self, username, password):
        for u in st.session_state.db_usuarios:
            if u["username"] == username.lower() and u["password"] == password:
                return u
        return None

    def obtener_todas(self):
        return st.session_state.db_rendiciones

    def verificar_duplicado(self, rut: str, folio: str) -> bool:
        return any(r['rut'].strip() == rut.strip() and r['folio'].strip() == folio.strip() for r in st.session_state.db_rendiciones)

    def actualizar_estado(self, gasto_id: int, nuevo_estado: str, autor: str):
        for r in st.session_state.db_rendiciones:
            if r['id'] == gasto_id:
                origen = r['estado']
                r['estado'] = nuevo_estado
                self.registrar_log(gasto_id, autor, origen, nuevo_estado)
                break