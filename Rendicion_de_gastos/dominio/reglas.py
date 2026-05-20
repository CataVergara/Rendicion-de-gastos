UMBRAL_MONTO_GERENCIA = 500000

class ReglasNegocioFinancieras:
    @staticmethod
    def requiere_aprobacion_gerencia(monto: float) -> bool:
        return monto > UMBRAL_MONTO_GERENCIA

    @staticmethod
    def validar_campos_obligatorios(rut: str, folio: str, monto: float) -> bool:
        return bool(rut and folio and monto > 0)