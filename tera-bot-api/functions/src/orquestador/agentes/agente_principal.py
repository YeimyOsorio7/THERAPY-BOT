"""
Agente de IA para Clínica Psicológica con RAG y gestión de historial.
"""
from typing import Any
from agents import Agent, handoff
from src.orquestador.agentes.agents.agente_examenes_salud_mental import agente_de_examenes_salud_mental
from src.orquestador.agentes.agents.agente_de_respuestas_salud_mental import agente_de_respuestas_salud_mental
from src.orquestador.agentes.agents.agente_salud_mental_coloquial import agente_de_salud_mental_coloquial
from src.orquestador.agentes.agents.agente_transtornos_salud_mental import agente_de_transtornos_salud_mental
from src.orquestador.agentes.prompt_system.prompt_agente_principal import PromptAgentePrincipal
from src.orquestador.chroma_data_base.chroma import get_chroma_service
import logging

logger = logging.getLogger("openai.agents")
# Para debug detallado
logger.setLevel(logging.DEBUG)
# Para mostrar info y niveles superiores
logger.setLevel(logging.INFO)
# Para mostrar advertencias y niveles superiores
logger.setLevel(logging.WARNING)

class PsychologyClinicAgent:
    """
    Agente de IA especializado para clínica psicológica.
    Integra RAG con ChromaDB y manejo de historial de conversaciones.
    """

    SYSTEM_PROMPT = PromptAgentePrincipal.SYSTEM_PROMPT.value

    def __init__(
        self,
        model: str = "gpt-5-mini",
    ):
        """
        Inicializa el agente de la clínica psicológica.
        
        Args:
            model: Modelo de OpenAI a usar
        """
        self.model = model
        
        # Inicializar RAG con ChromaDB
        self.chroma = get_chroma_service()

    async def agentPsychology(
        self,
        user_id: str,
        user_message: str,
    ) -> Agent[Any]:
        """
        Procesa un mensaje del usuario y genera una respuesta.
        
        Args:
            user_id: ID único del usuario
            user_message: Mensaje del usuario
            temperature: Temperatura para la generación
            max_tokens: Límite de tokens en la respuesta
            
        Returns:
            Respuesta del asistente
        """
        try:
            logging.info(f"Procesando mensaje para usuario: {user_id}")
            logging.debug(f"Mensaje del usuario: {user_message}")
            # Obtenemos el prompt del agente principal
            prompt = self.SYSTEM_PROMPT

            agente_examenes = agente_de_examenes_salud_mental()
            agente_transtornos = agente_de_transtornos_salud_mental()
            agente_coloquial = agente_de_salud_mental_coloquial()
            agente_respuestas_salud_mental = agente_de_respuestas_salud_mental()
            # Generar respuesta con OpenAI
            agent = Agent(
                name="TerapyBot",
                model=self.model,
                instructions=prompt,
                handoffs=[agente_respuestas_salud_mental, handoff(agente_coloquial), handoff(agente_transtornos), handoff(agente_examenes)],
            )

            logger.info(f"User ({user_id}): {user_message}")
            return agent

        except Exception as e:
            error_msg = f"Error al procesar mensaje: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

