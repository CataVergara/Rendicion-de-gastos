from dominio.reglas import ReglasNegocioFinancieras

class CasoUsoRendicion:
    def __init__(self, repositorio):
        self.repo = repositorio

    def registrar_gasto(self, usuario: str, rut: str, folio: str, monto: float, justificacion: str):
        if not ReglasNegocioFinancieras.validar_campos_obligatorios(rut, folio, monto):
            return {"success": False, "msg": "Error: Campos obligatorios vacíos o monto inválido."}
        
        if self.repo.verificar_duplicado(rut, folio):
            return {"success": False, "msg": "Excepción E4: Este documento tributario ya ha sido registrado."}
            
        requiere_g = ReglasNegocioFinancieras.requiere_aprobacion_gerencia(monto)
        
        nueva_rendicion = {
            "id": self.repo.obtener_siguiente_id(),
            "usuario": usuario,
            "rut": rut,
            "folio": folio,
            "monto": monto,
            "justificacion": justificacion,
            "estado": "Pendiente",
            "requiere_gerencia": requiere_g
        }
        
        self.repo.guardar(nueva_rendicion)
        
        if requiere_g:
            return {"success": True, "msg": "Rendición ingresada. BR-05: Requiere flag de aprobación por Gerencia."}
        return {"success": True, "msg": "Rendición ingresada y enviada a revisión con éxito."}

    def actualizar_estado_gasto(self, gasto_id: int, nuevo_estado: str):
        self.repo.actualizar_estado(gasto_id, nuevo_estado)