from src.modelos.ficha_medica import FichaMedica
from src.modelos.paciente import Paciente
from src.modelos.sigsa import Sigsa
from typing import Optional


class AllInfo:
    """
    Clase que representa toda la información de un paciente.
    """
    def __init__(
            self,
            paciente: Optional[Paciente],
            ficha_medica: Optional[FichaMedica],
            sigsa: Optional[Sigsa]
    ):
        self.paciente = paciente
        self.ficha_medica = ficha_medica
        self.sigsa = sigsa