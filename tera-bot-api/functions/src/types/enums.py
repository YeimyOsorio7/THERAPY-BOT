from enum import Enum

class ChromaCollections(Enum):
    """
    Enum para los nombres de las colecciones en ChromaDB.
    """
    SIGSA = "sigsa"
    TRANSTORNOS_DE_SALUD_MENTAL = "mental_health_disorders"
    EXAMENES_DE_SALUD_MENTAL = "mental_health_screenings"
    RESPUESTAS_DE_SALUD_MENTAL = "mental_health_responses"
    SALUD_MENTAL_COLLOQUIAL = "mental_health_colloquial"