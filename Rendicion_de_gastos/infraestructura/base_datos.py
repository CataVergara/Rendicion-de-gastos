import streamlit as st

class RepositorioRendicionMemory:
    def __init__(self):
        if 'db_usuarios' not in st.session_state:
            st.session_state.db_usuarios = [
                {"id": 1, "username": "francisco", "password": "123", "nombre": "Francisco Benavides", "rol": "Rendidor"},
                {"id": 2, "username": "catalina", "password": "123", "nombre": "Catalina Vergara", "rol": "Bandeja Auditoria"},
                {"id": 3, "username": "tesorero", "password": "123", "nombre": "Encargado de Pagos", "rol": "Cierre Tesoreria"}
            ]
        
        if 'db_rendiciones' not in st.session_state:
            st.session_state.db_rendiciones = [
                {"id": 1, "usuario_id": 1, "usuario": "Francisco Benavides", "rut": "76.452.128-K", "folio": "1045", "monto": 620000, "estado": "Pendiente", "justificacion": "Compra de insumos y routers ISP.", "requiere_gerencia": True},
                {"id": 2, "usuario_id": 1, "usuario": "Francisco Benavides", "rut": "19.234.567-8", "folio": "892", "monto": 45000, "estado": "Autorizado", "justificacion": "Suscripción mensual AWS.", "requiere_gerencia": False}
            ]

    def validar_credenciales(self, username, password):
        for u in st.session_state.db_usuarios:
            if u["username"] == username.lower() and u["password"] == password:
                return u
        return None

    def obtener_por_usuario(self, usuario_id):
        return [r for r in st.session_state.db_rendiciones if r['usuario_id'] == usuario_id]

    def obtener_todas(self):
        return st.session_state.db_rendiciones

    def obtener_siguiente_id(self) -> int:
        if not st.session_state.db_rendiciones:
            return 1
        return max(r['id'] for r in st.session_state.db_rendiciones) + 1

    def verificar_duplicado(self, rut: str, folio: str) -> bool:
        return any(r['rut'] == rut and r['folio'] == folio for r in st.session_state.db_rendiciones)

    def guardar(self, rendicion: dict):
        st.session_state.db_rendiciones.append(rendicion)

    def actualizar_estado(self, gasto_id: int, nuevo_estado: str):
        for r in st.session_state.db_rendiciones:
            if r['id'] == gasto_id:
                r['estado'] = nuevo_estado
                break