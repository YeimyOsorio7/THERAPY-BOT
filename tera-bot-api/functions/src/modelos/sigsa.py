from datetime import datetime
from typing import Optional

class Sigsa:
    """
    Modelo de datos para un registro SIGSA para el sistema de salud.
    """
    def __init__(
            self,
            uid: Optional[str] = None,
            fecha_consulta: Optional[datetime] = None,
            nombre: Optional[str] = None,
            apellido: Optional[str] = None,
            cui: Optional[str] = None,
            fecha_nacimiento: Optional[datetime] = None,
            edad: Optional[int] = None,
            ninio_menor_15: Optional[bool] = None,
            adulto: Optional[bool] = None,
            genero: Optional[str] = None,
            municipio: Optional[str] = None,
            aldea: Optional[str] = None,
            embarazo: Optional[str] = None,
            consulta: Optional[str] = None,
            diagnostico: Optional[str] = None,
            cie_10: Optional[str] = None,
            created: Optional[datetime] = None,
            tratamiento: Optional[str] = None,
            estado_paciente: Optional[str] = None,
            no_historia_clinica: Optional[int] = None,
            terapia: Optional[str] = None,
            ):
        self.uid = uid
        self.fecha_consulta = fecha_consulta
        self.nombre = nombre
        self.apellido = apellido
        self.cui = cui
        self.fecha_nacimiento = fecha_nacimiento
        self.edad = edad
        self.ninio_menor_15 = ninio_menor_15
        self.adulto = adulto
        self.genero = genero
        self.municipio = municipio
        self.aldea = aldea
        self.embarazo = embarazo
        self.consulta = consulta
        self.diagnostico = diagnostico
        self.cie_10 = cie_10
        self.tratamiento = tratamiento
        self.estado_paciente = estado_paciente
        self.no_historia_clinica = no_historia_clinica
        self.terapia = terapia
        self.created = created