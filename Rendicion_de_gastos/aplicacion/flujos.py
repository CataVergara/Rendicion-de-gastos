# =====================================================================
# CAPA DE APLICACIÓN: CASOS DE USO DE RENDICIÓN
# =====================================================================

class CasoUsoRendicion:
    def __init__(self, repositorio):
        """
        Clase de la capa de Aplicación que coordina las operaciones de negocio
        del sistema de FinTrack Pro, delegando la persistencia de datos 
        en el repositorio inyectado (Firestore).
        """
        self.repositorio = repositorio

    def obtener_flujo_completo(self):
        """Retorna todas las rendiciones vigentes desde la base de datos."""
        return self.repositorio.obtener_todas()

    def procesar_cambio_estado(self, gasto_id: int, nuevo_estado: str, autor: str):
        """Coordina el cambio de estado de una rendición aplicando la trazabilidad."""
        self.repositorio.actualizar_estado(gasto_id, nuevo_estado, autor)