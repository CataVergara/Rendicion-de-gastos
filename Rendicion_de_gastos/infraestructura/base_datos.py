import streamlit as st
from datetime import datetime
import hashlib  # Librería nativa para aplicar hashing criptográfico
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path
import os
import base64

# =====================================================================
# INTERCEPTORES DE CAMBIOS AUTOMÁTICOS PARA FIRESTORE
# =====================================================================

class TrackedDict(dict):
    """Diccionario inteligente que detecta cambios internos y los sincroniza en tiempo real con Firestore."""
    def __init__(self, data, db, doc_id):
        super().__init__(data)
        self.db = db
        self.doc_id = str(doc_id)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.db.collection("rendiciones").document(self.doc_id).set({key: value}, merge=True)

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.db.collection("rendiciones").document(self.doc_id).set(dict(self), merge=True)


class TrackedList(list):
    """Lista inteligente que detecta operaciones .append() y registra el nuevo documento en Firestore."""
    def __init__(self, data, db):
        super().__init__(data)
        self.db = db

    def append(self, item):
        doc_id = str(item.get("id"))
        tracked_item = TrackedDict(item, self.db, doc_id)
        super().append(tracked_item)
        self.db.collection("rendiciones").document(doc_id).set(item)


# =====================================================================
# REPOSITORIO DE PRODUCCIÓN CON CLOUD FIRESTORE (AUTO-MIGRABLE)
# =====================================================================

class RepositorioRendicionFirestore:
    def __init__(self):
        # 1. Inicialización segura de Firebase con rutas dinámicas absolutas
        if not firebase_admin._apps:
            directorio_actual = os.path.dirname(__file__)
            cred_path = os.path.join(directorio_actual, "rendicion-de-gastos-bd.json")
            
            if not os.path.exists(cred_path):
                base_dir = Path(__file__).resolve().parent.parent
                cred_path = base_dir / "rendicion-de-gastos-bd.json"
                
            if not os.path.exists(str(cred_path)):
                raise FileNotFoundError(f"Archivo de credenciales no encontrado.")
                
            cred = credentials.Certificate(str(cred_path))
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
        self._todas_cache = None
        self._verificar_y_cargar_datos_iniciales()
        self._migrar_contrasenas_existenses()

    def _hash_password(self, password: str) -> str:
        """Aplica un algoritmo criptográfico SHA-256 de una sola vía a la contraseña."""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def _verificar_y_cargar_datos_iniciales(self):
        """Puebla Firestore automáticamente con contraseñas de fábrica si está vacío."""
        users_ref = self.db.collection("usuarios")
        if not list(users_ref.limit(1).stream()):
            password_hasheado = self._hash_password("123")
            usuarios_base = [
                {"id": 1, "username": "francisco", "password": password_hasheado, "nombre": "Francisco Benavides", "rol": "Rendidor"},
                {"id": 2, "username": "catalina", "password": password_hasheado, "nombre": "Catalina Vergara", "rol": "Bandeja Auditoria"},
                {"id": 3, "username": "gerente", "password": password_hasheado, "nombre": "Gerente de Finanzas", "rol": "Gerencia Finanzas"},
                {"id": 4, "username": "tesorero", "password": password_hasheado, "nombre": "Tesorero Liquidador", "rol": "Cierre Tesoreria"}
            ]
            for u in usuarios_base:
                users_ref.document(u["username"]).set(u)

        rend_ref = self.db.collection("rendiciones")
        if not list(rend_ref.limit(1).stream()):
            sample_rendicion = {
                "id": 1, "usuario_id": 1, "usuario": "Francisco Benavides", 
                "rut": "76.452.128-K", "folio": "1045", "monto": 620000, 
                "estado": "Pendiente", "justificacion": "[Materiales e Insumos TI] Compra de insumos y routers ISP.", 
                "requiere_gerencia": True, "fecha_documento": "2026-05-10",
                "archivo_base64": "", "archivo_mime": ""
            }
            rend_ref.document("1").set(sample_rendicion)
            self.registrar_log(1, "Francisco Benavides", "Borrador", "Pendiente")

    def _migrar_contrasenas_existenses(self):
        """Escanea los usuarios actuales y encripta las contraseñas de texto plano en segundo plano."""
        usuarios = self.db.collection("usuarios").stream()
        for doc in usuarios:
            datos = doc.to_dict()
            password_actual = datos.get("password", "")
            if len(password_actual) != 64:
                password_encriptada = self._hash_password(password_actual)
                self.db.collection("usuarios").document(doc.id).update({
                    "password": password_encriptada
                })

    def registrar_log(self, rendicion_id: int, autor: str, origen: str, destino: str):
        """Registra la trazabilidad como una subcolección interna del documento de rendición."""
        nuevo_log = {
            "rendicion_id": int(rendicion_id),
            "autor": autor,
            "estado_origen": origen,
            "estado_destino": destino,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.db.collection("rendiciones").document(str(rendicion_id)).collection("logs").add(nuevo_log)

    def obtener_logs_por_rendicion(self, rendicion_id: int):
        """Extrae el historial cronológico desde la subcolección de Firebase."""
        logs_ref = self.db.collection("rendiciones").document(str(rendicion_id)).collection("logs").stream()
        lista_logs = [doc.to_dict() for doc in logs_ref]
        lista_logs.sort(key=lambda x: x.get('timestamp', ''))
        return lista_logs

    def validar_credenciales(self, username, password):
        """Hashea la contraseña ingresada en el Login y la compara con el hash de Firestore."""
        hashed_input = self._hash_password(password)
        query = self.db.collection("usuarios").where("username", "==", username.lower()).where("password", "==", hashed_input).stream()
        for doc in query:
            return doc.to_dict()
        return None

    def obtener_todas(self):
        """Devuelve la lista adaptada y protegida contra mutaciones externas de las vistas."""
        docs = self.db.collection("rendiciones").stream()
        raw_list = []
        for doc in docs:
            data = doc.to_dict()
            raw_list.append(TrackedDict(data, self.db, data.get("id")))
        
        raw_list.sort(key=lambda x: x['id'])
        self._todas_cache = TrackedList(raw_list, self.db)
        return self._todas_cache

    def existe_folio(self, folio: str, exclude_id: int = None) -> bool:
        """Verifica si un número de folio ya existe en otra boleta."""
        query = self.db.collection("rendiciones").where("folio", "==", folio.strip()).stream()
        for doc in query:
            if exclude_id is None or str(doc.to_dict().get("id")) != str(exclude_id):
                return True
        return False

    def rut_asignado_a_otro_usuario(self, rut: str, usuario_id: int, exclude_id: int = None) -> bool:
        """Verifica si el rut ya está asociado a un usuario distinto."""
        query = self.db.collection("rendiciones").where("rut", "==", rut.strip()).stream()
        for doc in query:
            data = doc.to_dict()
            if (exclude_id is None or str(data.get("id")) != str(exclude_id)) and data.get("usuario_id") != usuario_id:
                return True
        return False

    def usuario_tiene_otro_rut(self, usuario_id: int, rut: str, exclude_id: int = None) -> bool:
        """Verifica si el usuario ya usa otro rut en una rendición distinta."""
        query = self.db.collection("rendiciones").where("usuario_id", "==", usuario_id).stream()
        for doc in query:
            data = doc.to_dict()
            if (exclude_id is None or str(data.get("id")) != str(exclude_id)) and data.get("rut") != rut.strip():
                return True
        return False

    def verificar_duplicado(self, rut: str, folio: str, usuario_id: int = None, exclude_id: int = None) -> bool:
        """Verifica si existe conflicto de folio o de rut-usuario antes de crear/modificar."""
        if self.existe_folio(folio, exclude_id=exclude_id):
            return True
        if usuario_id is not None and (
            self.rut_asignado_a_otro_usuario(rut, usuario_id, exclude_id=exclude_id) or
            self.usuario_tiene_otro_rut(usuario_id, rut, exclude_id=exclude_id)
        ):
            return True
        return False

    def actualizar_estado(self, gasto_id: int, nuevo_estado: str, autor: str):
        """Actualiza el estado de flujo del documento y dispara el log de auditoría."""
        doc_ref = self.db.collection("rendiciones").document(str(gasto_id))
        doc = doc_ref.get()
        if doc.exists:
            origen = doc.to_dict().get('estado', 'Ninguno')
            doc_ref.set({'estado': nuevo_estado}, merge=True)
            self.registrar_log(gasto_id, autor, origen, nuevo_estado)