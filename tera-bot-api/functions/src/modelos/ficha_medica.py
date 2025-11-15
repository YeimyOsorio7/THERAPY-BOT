from typing import Optional

class FichaMedica:
    """
    Clase que representa una ficha médica de un paciente.
    """
    def __init__(
            self,
            uid: Optional[str] = None,
            cui: Optional[str] = None,
            edad: Optional[str] = None,
            ocupacion: Optional[str] = None,
            escolaridad: Optional[str] = None,
            municipio: Optional[str] = None,
            aldea: Optional[str] = None,
            estado_civil: Optional[str] = None,
            paciente_referido: Optional[bool] = None,
            genero: Optional[str] = None,
            patologia: Optional[str] = None,
            cei10: Optional[str] = None,
            tipo_consulta: Optional[str] = None,
            tipo_terapia: Optional[str] = None,
            embarazo: Optional[str] = None,
            ):
        self.uid = uid
        self.cui = cui
        self.edad = edad
        self.ocupacion = ocupacion
        self.escolaridad = escolaridad
        self.municipio = municipio
        self.aldea = aldea
        self.estado_civil = estado_civil
        self.paciente_referido = paciente_referido
        self.genero = genero
        self.patologia = patologia
        self.cei10 = cei10
        self.tipo_consulta = tipo_consulta
        self.tipo_terapia = tipo_terapia
        self.embarazo = embarazo