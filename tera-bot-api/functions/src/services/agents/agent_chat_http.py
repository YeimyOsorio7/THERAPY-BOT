import asyncio
import logging
import json

from flask import Request, Response
from src.orquestador.orquestador import Orquestador

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def chat_agent_http(request: Request) -> Response:
    """
    Endpoint HTTP para manejar interacciones con el agente de la clínica psicológica.
    Espera solicitudes POST con un cuerpo JSON que contenga 'messages' y 'user_id'.
    Devuelve respuestas generadas por el agente y el historial de la conversación.
    """

    if request.method != 'POST':
        body = json.dumps({
            "success": False,
            "error": "Método no permitido. Solo se permiten solicitudes POST."
        })
        return Response(
            body,
            status=405,
            headers={"Content-Type": "application/json"}
        )
     
    request_json = request.get_json(silent=True)

    if not request_json:
        body = json.dumps({
            "success": False,
            "error": "Petición inválida: No se encontró el cuerpo JSON"
        })
        logging.error("Petición inválida: No se encontró el cuerpo JSON")
        return Response(
            body,
            status=400,
            headers={"Content-Type": "application/json"}
        )

    messages = request_json.get('messages')
    user_id = request_json.get('user_id')

    if not messages or not user_id:
        body = json.dumps({
            "success": False,
            "error": "Petición inválida: Faltan campos requeridos 'messages' o 'user_id'"
        })
        logging.error("Petición inválida: Faltan campos requeridos 'messages' o 'user_id'")
        return Response(
            body,
            status=400,
            headers={"Content-Type": "application/json"}
        )

    try:
        orquestador = Orquestador(
            user_id=user_id,
            message=messages,
        )
        
        result = asyncio.run(orquestador.generate_response())
        body = json.dumps({
            "success": True,
            "respuesta_asistente": result["respuesta"],
            "historial": result["historial"]
        })
        return Response(
            body,
            status=200,
            headers={"Content-Type": "application/json"},
        )
    except Exception as e:
        body = json.dumps({
            "success": False,
            "error": str(e)
        })
        logging.error(f'Error en generar la respuesta: {str(e)}')
        return Response(
            body,
            status=500,
            headers={"Content-Type": "application/json"},
        )
