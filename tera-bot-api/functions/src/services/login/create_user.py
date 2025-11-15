from firebase_admin import firestore
import logging
import json

from flask import Request, Response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_user_http(request: Request) -> Response:
    request_json = request.get_json(silent=True)
    if not request_json:
        body = json.dumps({
            "success": False,
            "error": "No JSON body found"
        })
        logging.error("No JSON body found in the request")
        return Response(
            body,
            status=400,
            headers={"Content-Type": "application/json"}
        )

    contrasenia = request_json.get('contrasenia')
    usuario = request_json.get('usuario')
    admin = request_json.get('admin', False)

    if not contrasenia or not usuario:
        body = json.dumps({
            "success": False,
            "error": "Invalid request: Missing required fields"
        })
        logging.error("Missing required fields: 'contrasenia' or 'usuario'")
        return Response(
            body,
            status=400,
            headers={"Content-Type": "application/json"}
        )

    try:
        user_id = create_user(usuario, contrasenia, admin)
        logging.info(f'usuario creado con el UID: {user_id}')
        body = json.dumps({
            "success": True,
            "uid": user_id['uid'],
            "admin": user_id['admin']
        })
        return Response(
            body,
            status=201,
            headers={"Content-Type": "application/json"},
        )
    except Exception as e:
        body = json.dumps({
            "success": False,
            "error": str(e)
        })
        logging.error(f'Error creating user: {str(e)}')
        return Response(
            body,
            status=500,
            headers={"Content-Type": "application/json"},
        )

def create_user(
        usuario: str,
        contrasenia: str,
        admin: bool = False,
    ) -> dict[str, str | bool]:
    """
    Guarda la información del usuario en Firestore.
    Args:
        user_id (str): El ID del usuario.
        display_name (str): El nombre para mostrar del usuario.
    """
    db = firestore.client()
    try:
        # Verificar si el usuario ya existe
        users_ref = db.collection('users')
        # Realizamos una consulta para encontrar el usuario
        query = users_ref.where('usuario', '==', usuario).limit(1)
        results = query.stream()
        for user_doc in results:
            logging.error(f'Fallo la creacion del usuario: El usuario {usuario} ya existe.')
            raise ValueError("Usuario ya existe")

        # Referencias a los documentos de Firestore para la colección 'users', 'pacientes' y 'threads'
        ref_usuario = db.collection('users').document()
        ref_paciente = db.collection('pacientes').document(ref_usuario.id)
        ref_thread = db.collection('threads').document(ref_usuario.id)

        # Crear un batch para realizar múltiples escrituras atómicas
        batch = db.batch()
        batch.set(ref_usuario, {
            'usuario': usuario,
            'contrasenia': contrasenia,
            'admin': admin,
            'fecha_creacion': firestore.firestore.SERVER_TIMESTAMP,
            'ref_paciente': ref_paciente
        })

        batch.set(ref_paciente, {
            'fecha_creacion': firestore.firestore.SERVER_TIMESTAMP,
            'user_name': usuario,
            'estado_paciente': 'pendiente',
            'thread': ref_thread
        })

        batch.set(ref_thread, {
            'fecha_creacion': firestore.firestore.SERVER_TIMESTAMP,
            'ref_paciente': ref_paciente,
            'thread_id': ref_thread.id
        })

        # Commit del batch
        batch.commit()
        logger.info(f'User {ref_usuario.id} saved to Firestore with display name {usuario}')
        return {
            "uid": ref_paciente.id,
            "admin": admin,
        }
    except Exception as e:
        logger.error(f'Error saving user to Firestore: {e}')
        raise
    finally:
        db.close()
    
