# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

import json
from firebase_functions import https_fn
from flask import Request, Response
from firebase_functions.options import set_global_options
from firebase_admin import initialize_app

# Importar las funciones para los servicios de login y creación de usuarios
from src.services.agents.agent_chat_http import chat_agent_http
from src.services.login.login_user import login_user_http
from src.services.login.create_user import create_user_http

# Importar las funciones para los servicios de citas
from src.services.appointment.citas_consultorio import crear_cita
from src.services.appointment.citas_consultorio import actualizar_cita
from src.services.appointment.citas_consultorio import listar_citas
from src.services.appointment.citas_consultorio import eliminar_cita

# Importar las funciones para los servicios para pacientes
from src.services.patient.patient_service import get_all_patients
from src.services.patient.patient_service import update_patient_information
from src.services.patient.patient_service import get_patient_information
from src.services.patient.patient_service import get_sigsa_information
from src.services.patient.patient_service import get_medical_record_information


# For cost control, you can set the maximum number of containers that can be
# running at the same time. This helps mitigate the impact of unexpected
# traffic spikes by instead downgrading performance. This limit is a per-function
# limit. You can override the limit for each function using the max_instances
# parameter in the decorator, e.g. @https_fn.on_request(max_instances=5).
set_global_options(max_instances=10)

initialize_app()

@https_fn.on_request()
def create_user(request: Request) -> Response:
    """Create a new user via HTTP request.
    This function creates a new user in Firebase Authentication using the
    provided email, password, and display name from the HTTP request.
    Args:
        request: The HTTP request object in JSON format.

    Returns:
        A HTTP response indicating the result of the operation.
    """

    if request.method != 'POST':
        body = json.dumps({
            "success": False,
            "error": "Invalid HTTP method. Only POST requests are allowed."
        })
        return Response(
            body,
            status=405,
            headers={"Content-Type": "application/json"}
        )
    return create_user_http(request)
    
@https_fn.on_request()
def login_user(request: Request) -> Response:
    """Authenticate a user via HTTP request.
    This function authenticates a user with the given username and password.
    Args:
        request: The HTTP request object in JSON format.

    Returns:
        A HTTP response indicating the result of the operation.
    """
    if request.method != 'POST':
        body = json.dumps({
            "success": False,
            "error": "Invalid HTTP method. Only POST requests are allowed."
        })
        return Response(
            body,
            status=405,
            headers={"Content-Type": "application/json"}
        )

    return login_user_http(request)

@https_fn.on_request()
def listar_todos_pacientes(request: Request) -> Response:
    """List all patients in the Firestore database.
    This function retrieves all patient records from the Firestore database.
    Args:
        request: The HTTP request object in JSON format.
    Returns:
        A HTTP response containing the list of all patients.
    """
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
        patients = get_all_patients()
        body = json.dumps({
            "success": True,
            "patients": patients,
            "total": len(patients)
        })
        return Response(
            body,
            status=200,
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        body = json.dumps({
            "success": False,
            "error": str(e)
        })
        return Response(
            body,
            status=500,
            headers={"Content-Type": "application/json"}
        )

@https_fn.on_request()
def update_patient(request: Request) -> Response:
    """Update patient information.
    This function updates patient information in the Firestore database.
    Args:
        request: The HTTP request object in JSON format.
    Returns:
        A HTTP response indicating the result of the operation.
    """
    if request.method != 'POST':
        body = json.dumps({
            "success": False,
            "error": "Invalid HTTP method. Only POST requests are allowed."
        })
        return Response(
            body,
            status=405,
            headers={"Content-Type": "application/json"}
        )
    return update_patient_information(request)

@https_fn.on_request()
def paciente_info(request: Request) -> Response:
    """Obtener información del paciente.
    Esta función obtiene la información del paciente desde Firestore.
    Args:
        request: The HTTP request object in JSON format.

    Returns:
        A HTTP response indicating the result of the operation.
    """
    return get_patient_information(request)

@https_fn.on_request()
def ficha_medica_info(request: Request) -> Response:
    """Obtener información de la ficha médica.
    Esta función obtiene la información de la ficha médica desde Firestore.
    Args:
        request: The HTTP request object in JSON format.

    Returns:
        A HTTP response indicating the result of the operation.
    """
    return get_medical_record_information(request)

@https_fn.on_request()
def sigsa_info(request: Request) -> Response:
    """Obtener información de SIGSA.
    Esta función obtiene la información de SIGSA desde Firestore.
    Args:
        request: The HTTP request object in JSON format.

    Returns:
        A HTTP response indicating the result of the operation.
    """
    return get_sigsa_information(request)

@https_fn.on_request()
def crear_cita_consultorio(request: Request) -> Response:
    """Crear una nueva cita en el consultorio.
    Esta función crea una nueva cita en el calendario de Google y almacena
    la información de la cita en Firestore.
    Args:
        request: The HTTP request object in JSON format.

    Returns:
        A HTTP response indicating the result of the operation.
    """
    
    return crear_cita(request)

@https_fn.on_request()
def actualizar_cita_consultorio(request: Request) -> Response:
    """Actualizar una cita en el consultorio.
    Esta función actualiza una cita existente en el calendario de Google y
    actualiza la información de la cita en Firestore.
    Args:
        request: The HTTP request object in JSON format.

    Returns:
        A HTTP response indicating the result of the operation.
    """
    return actualizar_cita(request)

@https_fn.on_request()
def eliminar_cita_consultorio(request: Request) -> Response:
    """Eliminar una cita en el consultorio.
    Esta función elimina una cita existente en el calendario de Google y
    elimina la información de la cita en Firestore.
    Args:
        request: The HTTP request object in JSON format.

    Returns:
        A HTTP response indicating the result of the operation.
    """
    return eliminar_cita(request)

@https_fn.on_request()
def listar_citas_consultorio(request: Request) -> Response:
    """Listar citas en el consultorio.
    Esta función lista todas las citas almacenadas en Firestore.
    Args:
        request: The HTTP request object in JSON format.

    Returns:
        A HTTP response indicating the result of the operation.
    """
    return listar_citas(request)

@https_fn.on_request()
def chat_agent(request: Request) -> Response:
    """
    Maneja las interacciones con el agente de la clínica psicológica.
    """
    return chat_agent_http(request)
