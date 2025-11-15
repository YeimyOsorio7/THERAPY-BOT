import logging
from agents import Agent, function_tool

from src.orquestador.chroma_data_base.chroma import get_chroma_service
from src.types.enums import ChromaCollections

chroma_service = get_chroma_service()

@function_tool(name_override="buscar_conocimiento_con_RAG", description_override="Busca información relevante en la base de conocimientos.")
def buscar_conocimiento_con_RAG(
        query: str,
    ) -> str:
    """
    Busca información relevante en la base de conocimientos
    Args:
        query: Consulta a buscar
    Returns:
        Información relevante encontrada
    """
    
    # Busca en el vector store
    results = chroma_service.query(
        name_collection=ChromaCollections.EXAMENES_DE_SALUD_MENTAL.value,
        query_texts=[query],
        n_results=3,
    )

    logging.info(f"RAG results: {results}")
    
    # Retorna el contexto encontrado
    if results['documents']:
        context = "\n\n".join(results['documents'][0])
        return f"Información encontrada:\n{context}"
    return "No se encontró información relevante."

def agente_de_examenes_salud_mental() -> Agent:
    """
    Crea un agente que utiliza RAG para obtener contexto relevante de la base de conocimientos.
    
    Args:
        model: Modelo de lenguaje a utilizar
        uid_user: ID del usuario para el historial de conversaciones
        
    Returns:
        Agente configurado con RAG
    """
    logging.warn("Creando agente de exámenes de salud mental con RAG")
    return Agent(
        name="AgenteDeExamenesDeSaludMental",
        instructions="""Eres un agente que proporciona respuestas sobre exámenes de salud mental.
    Usa buscar_conocimiento_con_RAG.
    Siempre basa tus respuestas en la información recuperada. Si no hay información relevante, indícalo.
    Responde de manera clara y concisa.""",
        tools=[buscar_conocimiento_con_RAG]
    )
