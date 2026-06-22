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
        """Puebla Firestore automáticamente con usuarios de fábrica si está vacío."""
        users_ref = self.db.collection("usuarios")
        if not list(users_ref.limit(1).stream()):
            password_hasheado = self._hash_password("123")
            usuarios_base = [
                {"id": 1, "username": "francisco", "password": password_hasheado, "nombre": "Francisco Benavides", "rol": "Rendidor", "rut": "21.345.245-7"},
                {"id": 2, "username": "catalina", "password": password_hasheado, "nombre": "Catalina Vergara", "rol": "Bandeja Auditoria", "rut": "22.222.222-2"},
                {"id": 3, "username": "gerente", "password": password_hasheado, "nombre": "Gerente de Finanzas", "rol": "Gerencia Finanzas", "rut": "33.333.333-3"},
                {"id": 4, "username": "tesorero", "password": password_hasheado, "nombre": "Tesorero Liquidador", "rol": "Cierre Tesoreria", "rut": "44.444.444-4"}
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

    def obtener_siguiente_id_usuario(self) -> int:
        """Calcula el siguiente identificador numérico incremental para nuevos usuarios."""
        usuarios = self.db.collection("usuarios").stream()
        max_id = 0
        for doc in usuarios:
            datos = doc.to_dict()
            u_id = datos.get("id", 0)
            if u_id > max_id:
                max_id = u_id
        return max_id + 1

    def obtener_siguiente_id_rendicion(self) -> int:
        """Calcula el correlativo numérico incremental real analizando los IDs de la colección en la nube."""
        rendiciones = self.db.collection("rendiciones").stream()
        max_id = 0
        for doc in rendiciones:
            data = doc.to_dict()
            r_id = data.get("id", 0)
            try:
                r_id_int = int(r_id)
                if r_id_int > max_id:
                    max_id = r_id_int
            except (ValueError, TypeError):
                continue
        return max_id + 1

    def registrar_usuario(self, username, password_plana, nombre, rol, rut) -> bool:
        """Encripta la clave y añade de forma estructurada un nuevo colaborador con su RUT institucional."""
        password_encriptada = self._hash_password(password_plana)
        nuevo_usuario = {
            "id": self.obtener_siguiente_id_usuario(),
            "username": username.lower().strip(),
            "password": password_encriptada,
            "nombre": nombre.strip(),
            "rol": rol,
            "rut": rut.strip()
        }
        self.db.collection("usuarios").document(nuevo_usuario["username"]).set(nuevo_usuario)
        return True

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

    def verificar_duplicado(self, rut: str, folio: str, usuario_id: int, exclude_id: int = None) -> bool:
        """
        BR-06 / Excepción E4: Control de Integridad Multivariable y Folio Único.
        Bloquea el ingreso si el Folio ya existe globalmente para el usuario, o si se repite la relación RUT + Folio.
        """
        query_folio = self.db.collection("rendiciones") \
            .where("usuario_id", "==", int(usuario_id)) \
            .where("folio", "==", folio.strip()).stream()
            
        for doc in query_folio:
            data = doc.to_dict()
            if exclude_id is not None and str(data.get("id")) == str(exclude_id):
                continue
            return True

        query_relacional = self.db.collection("rendiciones") \
            .where("usuario_id", "==", int(usuario_id)) \
            .where("rut", "==", rut.strip()) \
            .where("folio", "==", folio.strip()).stream()
            
        for doc in query_relacional:
            data = doc.to_dict()
            if exclude_id is not None and str(data.get("id")) == str(exclude_id):
                continue
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

    # =====================================================================
    # NUEVO MÉTODO: ELIMINACIÓN ESTRICTA Y SINCRONIZACIÓN DE CACHÉ
    # =====================================================================
    def eliminar_rendicion(self, gasto_id, folio_documento) -> bool:
        """
        Elimina de forma segura un borrador específico tanto de Cloud Firestore 
        (incluyendo subcolecciones de logs) como del caché TrackedList local.
        """
        try:
            doc_str_id = str(gasto_id)
            doc_ref = self.db.collection("rendiciones").document(doc_str_id)
            
            # 1. Eliminar subcolección 'logs' interna para mantener limpia la BD
            logs_docs = doc_ref.collection("logs").stream()
            for log_doc in logs_docs:
                log_doc.reference.delete()
                
            # 2. Eliminar el documento base de la rendición
            doc_ref.delete()
            
            # 3. Doble verificación de seguridad en la nube filtrando por folio
            extra_docs = self.db.collection("rendiciones").where("folio", "==", str(folio_documento)).stream()
            for extra_doc in extra_docs:
                data_extra = extra_doc.to_dict()
                # Solo borra si coincide con el ID correlativo para evitar colisiones cruzadas
                if str(data_extra.get("id")) == doc_str_id:
                    extra_doc.reference.delete()

            # 4. Sincronizar de inmediato el caché interno que alimenta a la vista de Streamlit
            if self._todas_cache is not None:
                # Filtramos la lista interna removiendo el elemento exacto que coincida con ID y folio
                elementos_filtrados = [
                    r for r in self._todas_cache 
                    if str(r.get('id')) != doc_str_id and str(r.get('folio')) != str(folio_documento)
                ]
                # Re-instanciamos la lista inteligente sobre los datos limpios
                self._todas_cache = TrackedList(elementos_filtrados, self.db)
                
            return True
        except Exception as e:
            print(f"Error crítico al intentar eliminar la rendición de Firebase: {e}")
            return False