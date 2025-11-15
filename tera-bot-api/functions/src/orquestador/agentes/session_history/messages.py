
from dataclasses import dataclass
import logging
from agents import SQLiteSession

@dataclass
class Message:
    """
    Mensaje en la conversación con SQLiteSession de OpenAI.
    Estructura básica para almacenar mensajes.
    """

    def create_and_get_session_id(self, user_id: str):
        """
        Crea un session_id único por usuario.
        Usa SQLiteSession para manejar el historial.
        Args:
            user_id: ID único del usuario
        """
        logging.warn(f"Creando sesión de historial para usuario: {user_id}")
        session_id = f"session_{user_id}"
        return SQLiteSession(session_id, "conversations.db")