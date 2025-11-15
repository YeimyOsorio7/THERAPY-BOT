import logging
from typing import Dict
from agents import Runner, SQLiteSession, TResponseInputItem
from src.orquestador.agentes.agente_principal import PsychologyClinicAgent
from src.orquestador.agentes.session_history.messages import Message


class Orquestador:
    """
    Orquestador principal que maneja la interacción entre el usuario y los agentes.
    Integra RAG con ChromaDB y manejo de historial de conversaciones.
    
    Usa SQLiteSession para manejar el historial.
    
        Args:
            user_id: ID único del usuario
            message: Mensaje del usuario
        Returns:
            Respuesta del asistente
        """
    def __init__(
            self,
            user_id: str,
            message: str,
        ) -> None:
        self.user_id = user_id
        self.message = message
        self.history = None

    async def generate_response(self) -> Dict[str, str | list[TResponseInputItem]]:
        """
        Procesa la interacción del usuario y genera una respuesta.
        """
        try:
            if self.history is None:
                logging.info(f"No hay historial previo para usuario: {self.user_id}. Creando nuevo historial.")
                self.history = self._create_history_session(self.user_id)

            history = self.history
            logging.warn(f"Sesión de historial creada para usuario: {self.user_id}")

            psychologyClinicAgent = PsychologyClinicAgent()
            agent = await psychologyClinicAgent.agentPsychology(
                user_id=self.user_id,
                user_message=self.message,
            )
            logging.info(f"Agente creado para usuario: {self.user_id}")

            result = await Runner.run(
                agent,
                self.message,
                session=self.history,
            )
            logging.warn(f"TerapyBot: {result}")
            logging.warn(f"Result Session: {self.history}")
            history = await self._get_all_history(self.user_id)
            logging.warn(f"Historial de mensajes para usuario {self.user_id}: {history}")

            return {
                "respuesta": result.final_output,
                "historial": history,
            }

        except Exception as e:
            logging.error(f"Orquestador: Error procesando interacción para {self.user_id}: {e}")
            return {"error": f"Error procesando la solicitud: {e}"}

    def _create_history_session(self, user_id: str) -> SQLiteSession:
        """
        Crea un session_id único por usuario.
        Usa SQLiteSession para manejar el historial.
        Args:
            user_id: ID único del usuario
        """
        try:
            logging.info(f"Creando sesión de historial para usuario: {user_id}")
            message = Message()
            session = message.create_and_get_session_id(user_id=user_id)
            return session
        except Exception as e:
            logging.error(f"Error creando sesión de historial para {user_id}: {e}")
            raise

    async def _get_all_history(self, user_id: str) -> list[TResponseInputItem]:
        """
        Obtiene todo el historial de mensajes para un usuario.
        Args:
            user_id: ID único del usuario
        """
        logging.info(f"Obteniendo historial de mensajes para usuario: {user_id}")
        if self.history is None:
            logging.info(f"No hay historial previo para usuario: {user_id}. Creando nuevo historial.")
            return []

        conversations = await self.history.get_items()
        logging.warn(f"Historial obtenido para usuario {user_id}: {conversations}")
        return conversations