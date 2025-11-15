import datetime
import logging
from typing import Any, Dict, List, Optional
import json
from firebase_admin import firestore
from flask import Request, Response

from src.services.appointment.google_calendar import AdministradorCalendarioGoogle

def _json_response(payload: Dict[str, Any], status: int = 200) -> Response:
    """
    Respuesta HTTP con JSON serializable.
    Maneja automáticamente tipos de Firestore como DatetimeWithNanoseconds.
    """
    try:
        # Usar default=str para manejar tipos no serializables
        json_str = json.dumps(payload, default=str, ensure_ascii=False)
        logging.info(f"Response: {json_str}")
        
        return Response(
            json_str,
            status=status,
            headers={
                "Content-Type": "application/json; charset=utf-8"
            },
        )
    except Exception as e:
        logging.error(f"Error serializing JSON response: {e}")
        # Fallback response
        error_response = {
            "success": False, 
            "error": "Error interno del servidor al serializar respuesta"
        }
        return Response(
            json.dumps(error_response),
            status=500,
            headers={"Content-Type": "application/json; charset=utf-8"},
        )

def _bad_request(msg: str) -> Response:
    return _json_response({"success": False, "error": msg}, status=400)


def _method_not_allowed() -> Response:
    return _json_response(
        {"success": False, "error": "Invalid HTTP method. Only POST requests are allowed."},
        status=405,
    )

# Clase para manejar las operaciones con Firestore
# Utilizada para almacenar y gestionar las citas localmente
# Usamos el patrón Singleton para la conexión a Firestore
class FirestoreCitasRepository:
    def __init__(self, collection_name: str = "citas"):
        self._col = firestore.client().collection(collection_name)
        self._collection_name = collection_name

    def guardar_evento(self, id_evento: str, data: dict) -> dict:
        logging.info(f"[Firestore] Guardando evento id={id_evento} en {self._collection_name}")
        data = {
            **data,
            "actualizado_en": firestore.firestore.SERVER_TIMESTAMP,
        }
        logging.info(f"[Firestore] Datos a guardar: {data}")
        # Creamos el doc con id_evento (mantenemos mismo id que Google Calendar)
        self._col.document(id_evento).set(
            {
                **data,
                "fecha_creacion": firestore.firestore.SERVER_TIMESTAMP,
            },
            merge=True,
        )
        doc = self._col.document(id_evento).get()
        return {"id": doc.id, **(doc.to_dict() or {})}

    def actualizar_evento(self, id_evento: str, data: dict) -> dict:
        logging.info(f"[Firestore] Actualizando evento id={id_evento} en {self._collection_name}")
        data = {
            **data,
            "actualizado_en": firestore.firestore.SERVER_TIMESTAMP,
        }
        self._col.document(id_evento).set(data, merge=True)
        doc = self._col.document(id_evento).get()
        if not doc.exists:
            raise ValueError("El evento no existe en Firestore.")
        return {"id": doc.id, **(doc.to_dict() or {})}

    def eliminar_evento(self, id_evento: str) -> None:
        logging.info(f"[Firestore] Eliminando evento id={id_evento} en {self._collection_name}")
        self._col.document(id_evento).delete()

    def obtener_evento(self, id_evento: str) -> Optional[dict]:
        doc = self._col.document(id_evento).get()
        if not doc.exists:
            return None
        return {"id": doc.id, **(doc.to_dict() or {})}

    def listar_eventos(self, limit: int = 100, id_paciente: Optional[str] = None) -> List[dict]:
        logging.info(f"[Firestore] Listando eventos (limit={limit}, id_paciente={id_paciente})")
        query = self._col.order_by("fecha_inicio").limit(limit)
        if id_paciente:
            query = self._col.where("id_paciente", "==", id_paciente).order_by("fecha_inicio").limit(limit)

        docs = query.stream()
        return [{"id": d.id, **(d.to_dict() or {})} for d in docs]

# Servicio principal que integra Google Calendar y Firestore
class CitasConsultorioService:
    def __init__(
        self,
        repo: Optional[FirestoreCitasRepository] = None,
    ):
        self._calendar = AdministradorCalendarioGoogle()
        self._repo = repo or FirestoreCitasRepository()

    # ------------------------- Integración Google + Firestore -----------------
    def crear_cita(self, payload: Dict[str, str | list | None]) -> Dict[str, Any]:
        logging.info("[CitasService] Crear cita - inicio")
        id_paciente = payload.get("uid")
        nombre_evento = payload.get("nombre_evento")
        descripcion_evento = payload.get("descripcion_evento")
        fecha_inicio = payload.get("fecha_y_hora_inicio")
        fecha_fin = payload.get("fecha_y_hora_fin")
        asistentes = payload.get("asistentes", [])
        zona_horaria = payload.get("zona_horaria", "America/Guatemala")

        if not all([id_paciente, nombre_evento, descripcion_evento, fecha_fin]):
            raise ValueError("Faltan campos requeridos.")

        if isinstance(asistentes, str):
            asistentes = [asistentes]

        if not isinstance(nombre_evento, str) or not isinstance(descripcion_evento, str) or not isinstance(fecha_fin, str) or not isinstance(fecha_inicio, str) or not isinstance(zona_horaria, str):
            raise ValueError("nombre_evento, descripcion_evento, fecha_fin, fecha_inicio y zona_horaria deben ser cadenas de texto.")

        logging.info("[CitasService] Creando evento en Google Calendar")
        evento_gc = self._calendar.crear_evento(
            nombre_evento,
            descripcion_evento,
            inicio=fecha_inicio,
            fin=fecha_fin,
            zona_horaria=zona_horaria,
            asistentes=asistentes,
        )

        google_event_id = evento_gc.get("id")
        if not google_event_id:
            raise RuntimeError("No se recibió un id del evento de Google Calendar.")

        # Persistencia en Firestore
        logging.info("[CitasService] Guardando evento en Firestore")
        data_fs = {
            "id_paciente": id_paciente,
            "nombre_evento": nombre_evento,
            "descripcion_evento": descripcion_evento,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "asistentes": asistentes,
            "zona_horaria": zona_horaria,
            "google_event_id": google_event_id,
            "status": "CONFIRMED",
            "created_at": datetime.datetime.now().isoformat() + "Z",
            "updated_at": datetime.datetime.now().isoformat() + "Z",
            "raw_google_event": evento_gc,
        }
        evento_fs = self._repo.guardar_evento(google_event_id, data_fs)

        if evento_fs:
            logging.info("CITA CREADA EXITOSAMENTE")
        return data_fs

    def actualizar_cita(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        logging.info("[CitasService] Actualizar cita - inicio")
        id_evento = payload.get("id_evento")
        nombre_evento = payload.get("nombre_evento")
        descripcion_evento = payload.get("descripcion_evento")
        fecha_inicio = payload.get("fecha_inicio")
        fecha_fin = payload.get("fecha_fin")
        asistentes = payload.get("asistentes", [])

        if not all([id_evento, nombre_evento, descripcion_evento, fecha_inicio, fecha_fin]):
            raise ValueError("Faltan campos requeridos.")
        
        if isinstance(asistentes, str):
            asistentes = [asistentes]

        if not isinstance(id_evento, str):
            raise ValueError("id_evento debe ser una cadena de texto.")

        logging.info("[CitasService] Actualizando evento en Google Calendar")
        evento_gc = self._calendar.actualizar_evento(
            evento_id=id_evento,
            resumen=nombre_evento,
            description=descripcion_evento,
            inicio=fecha_inicio,
            fin=fecha_fin,
            asistentes=asistentes,
        )

        logging.info("[CitasService] Actualizando evento en Firestore")
        data_fs = {
            "nombre_evento": nombre_evento,
            "descripcion_evento": descripcion_evento,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "asistentes": asistentes,
            "status": evento_gc.get("status") or "CONFIRMED",
            "updated_at": datetime.datetime.utcnow().isoformat() + "Z",
            "raw_google_event": evento_gc,
        }
        evento_fs = self._repo.actualizar_evento(id_evento, data_fs)

        if evento_fs:
            logging.info("CITA ACTUALIZADA EXITOSAMENTE")

        logging.info("[CitasService] Actualizar cita - fin")
        return data_fs

    def eliminar_cita(self, id_evento: str) -> None:
        logging.info("[CitasService] Eliminar cita - inicio")
        if not id_evento:
            raise ValueError("Faltan campos requeridos.")

        logging.info("[CitasService] Eliminando evento en Google Calendar")
        self._calendar.eliminar_evento(evento_id=id_evento)

        logging.info("[CitasService] Eliminando evento en Firestore")
        self._repo.eliminar_evento(id_evento)

        logging.info("[CitasService] Eliminar cita - fin")

    def listar_citas_google(self, max_resultados: int = 100) -> List[Dict[str, Any]]:
        logging.info("[CitasService] Listar citas (Google Calendar)")
        citas = self._calendar.lista_eventos_proximos(max_resultados=max_resultados)
        logging.info(f"[CitasService] Citas encontradas: {len(citas)}")
        return citas

    # ------------------------- Solo Firestore ---------------------------------
    def guardar_cita_firestore(self, id_evento: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if not id_evento:
            raise ValueError("id_evento es requerido para guardar en Firestore.")
        return self._repo.guardar_evento(id_evento, data)

    def actualizar_cita_firestore(self, id_evento: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if not id_evento:
            raise ValueError("id_evento es requerido para actualizar en Firestore.")
        return self._repo.actualizar_evento(id_evento, data)

    def eliminar_cita_firestore(self, id_evento: str) -> None:
        if not id_evento:
            raise ValueError("id_evento es requerido para eliminar en Firestore.")
        self._repo.eliminar_evento(id_evento)

    def listar_citas_firestore(self, limit: int = 100, id_paciente: Optional[str] = None) -> List[Dict[str, Any]]:
        return self._repo.listar_eventos(limit=limit, id_paciente=id_paciente)


# Funciones HTTP expuestas
def crear_cita(request: Request) -> Response:
    if request.method != 'POST':
        return _method_not_allowed()

    request_json = request.get_json(silent=True)
    if not request_json:
        return _bad_request("Invalid request format. JSON expected.")

    try:
        service = CitasConsultorioService()
        result = service.crear_cita(request_json)
        logging.info("Cita creada exitosamente")
        return _json_response({"success": True, "data": result, "message": "Cita creada exitosamente"})
    except Exception as e:
        logging.exception("Error al crear cita")
        return _json_response({"success": False, "error": str(e)}, status=500)


def actualizar_cita(request: Request) -> Response:
    if request.method != 'POST':
        return _method_not_allowed()

    request_json = request.get_json(silent=True)
    if not request_json:
        return _bad_request("Invalid request format. JSON expected.")

    try:
        service = CitasConsultorioService()
        result = service.actualizar_cita(request_json)
        return _json_response({"success": True, "data": result, "message": "Cita actualizada exitosamente"})
    except Exception as e:
        logging.exception("Error al actualizar cita")
        return _json_response({"success": False, "error": str(e)}, status=500)


def listar_citas(request: Request) -> Response:
    if request.method != 'GET':
        body = json.dumps({
            "success": False,
            "error": "Invalid HTTP method. Only GET requests are allowed."
        })
        return Response(
            body,
            status=405,
            headers={"Content-Type": "application/json"}
        )

    try:
        max_resultados = int(request.args.get("max_resultados", "100")) if request.args else 100
        service = CitasConsultorioService()
        eventos = service.listar_citas_google(max_resultados=max_resultados)
        logging.info(f"Citas listadas: {len(eventos)}")
        if len(eventos) == 0:
            return _json_response({"success": True, "data": eventos, "message": "No se encontraron citas"})
        return _json_response({"success": True, "data": eventos, "message": "Citas listadas exitosamente"})
    except Exception as e:
        logging.exception("Error al listar citas")
        return _json_response({"success": False, "error": str(e)}, status=500)


def eliminar_cita(request: Request) -> Response:
    if request.method != 'POST':
        return _method_not_allowed()

    request_json = request.get_json(silent=True)
    if not request_json:
        return _bad_request("Invalid request format. JSON expected.")

    id_evento = request_json.get("id_evento")
    if not id_evento:
        return _bad_request("Faltan campos requeridos.")

    try:
        service = CitasConsultorioService()
        service.eliminar_cita(id_evento=id_evento)
        return _json_response({"success": True, "message": "Cita eliminada exitosamente"})
    except Exception as e:
        logging.exception("Error al eliminar cita")
        return _json_response({"success": False, "error": str(e)}, status=500)


# -----------------------------------------------------------------------------
# Endpoints adicionales para operar directamente con Firestore
# -----------------------------------------------------------------------------
def listar_citas_firestore(request: Request) -> Response:
    if request.method != 'GET':
        body = json.dumps({
            "success": False,
            "error": "Invalid HTTP method. Only GET requests are allowed."
        })
        return Response(
            body,
            status=405,
            headers={"Content-Type": "application/json"}
        )
    try:
        args = request.args or {}
        limit = int(args.get("limit", "100"))
        id_paciente = args.get("id_paciente")
        service = CitasConsultorioService()
        eventos = service.listar_citas_firestore(limit=limit, id_paciente=id_paciente)
        return _json_response({"success": True, "data": eventos, "message": "Citas (Firestore) listadas exitosamente"})
    except Exception as e:
        logging.exception("Error al listar citas desde Firestore")
        return _json_response({"success": False, "error": str(e)}, status=500)


def guardar_cita_firestore(request: Request) -> Response:
    if request.method != 'POST':
        return _method_not_allowed()
    request_json = request.get_json(silent=True)
    if not request_json:
        return _bad_request("Invalid request format. JSON expected.")

    id_evento = request_json.get("id_evento")
    data = request_json.get("data", {})
    if not id_evento or not isinstance(data, dict):
        return _bad_request("id_evento y data son requeridos.")

    try:
        service = CitasConsultorioService()
        saved = service.guardar_cita_firestore(id_evento, data)
        return _json_response({"success": True, "data": saved, "message": "Evento guardado en Firestore"})
    except Exception as e:
        logging.exception("Error al guardar evento en Firestore")
        return _json_response({"success": False, "error": str(e)}, status=500)


def actualizar_cita_firestore(request: Request) -> Response:
    if request.method != 'POST':
        return _method_not_allowed()
    request_json = request.get_json(silent=True)
    if not request_json:
        return _bad_request("Invalid request format. JSON expected.")

    id_evento = request_json.get("id_evento")
    data = request_json.get("data", {})
    if not id_evento or not isinstance(data, dict):
        return _bad_request("id_evento y data son requeridos.")

    try:
        service = CitasConsultorioService()
        updated = service.actualizar_cita_firestore(id_evento, data)
        return _json_response({"success": True, "data": updated, "message": "Evento actualizado en Firestore"})
    except Exception as e:
        logging.exception("Error al actualizar evento en Firestore")
        return _json_response({"success": False, "error": str(e)}, status=500)


def eliminar_cita_firestore(request: Request) -> Response:
    if request.method != 'POST':
        return _method_not_allowed()
    request_json = request.get_json(silent=True)
    if not request_json:
        return _bad_request("Invalid request format. JSON expected.")

    id_evento = request_json.get("id_evento")
    if not id_evento:
        return _bad_request("id_evento es requerido.")

    try:
        service = CitasConsultorioService()
        service.eliminar_cita_firestore(id_evento)
        return _json_response({"success": True, "message": "Evento eliminado de Firestore"})
    except Exception as e:
        logging.exception("Error al eliminar evento en Firestore")
        return _json_response({"success": False, "error": str(e)}, status=500)