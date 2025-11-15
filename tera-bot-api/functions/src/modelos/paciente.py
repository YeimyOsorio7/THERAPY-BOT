from datetime import datetime
from firebase_admin import firestore
from typing import Optional


class Paciente:
    """"
    Modelo de datos para un paciente.
    """
    def __init__(
            self,
            uid: Optional[str] = None,
            nombre: Optional[str] = None,
            apellido: Optional[str] = None,
            fecha_consulta: Optional[datetime] = None,
            estado_paciente: Optional[str] = None,
            motivo_consulta: Optional[str] = None,
            thread: Optional[firestore.firestore.DocumentReference] = None,
            ref_sigsa: Optional[firestore.firestore.DocumentReference] = None,
            ref_ficha_medica: Optional[firestore.firestore.DocumentReference] = None
            ):
        self.uid = uid
        self.nombre = nombre
        self.apellido = apellido
        self.fecha_consulta = fecha_consulta
        self.estado_paciente = estado_paciente
        self.motivo_consulta = motivo_consulta
        self.thread = thread
        self.ref_sigsa = ref_sigsa
        self.ref_ficha_medica = ref_ficha_medica