from firebase_admin import firestore, credentials, auth
import logging
import json

from flask import Request, Response

def login_user_http(request: Request) -> Response:
    """
    Funcion para autenticar a un usuario mediante una solicitud HTTP.
    Esta funcion autentica a un usuario con el nombre de usuario y la contrasenia proporcionados.
    Args:
        request (Request): La solicitud HTTP que contiene los datos de autenticacion.
    Returns:
        Response: Una respuesta HTTP que indica el resultado de la operacion.
    """
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

    usuario = request_json.get('usuario')
    contrasenia = request_json.get('contrasenia')

    if not usuario or not contrasenia:
        body = json.dumps({
            "success": False,
            "error": "Invalid request: Missing required fields"
        })
        logging.error("Missing required fields: 'usuario' or 'contrasenia'")
        return Response(
            body,
            status=400,
            headers={"Content-Type": "application/json"}
        )

    try:
        # Llamar a la funcion de autenticacion
        user_id = login_with_data_base(usuario, contrasenia)
        if user_id:
            body = json.dumps({
                "success": True,
                "uid": user_id['uid'],
                "admin": user_id['admin']
            })
            return Response(
                body,
                status=200,
                headers={"Content-Type": "application/json"},
            )
        else:
            body = json.dumps({
                "success": False,
                "error": "Authentication failed"
            })
            logging.error("Authentication failed for user")
            return Response(
                body,
                status=401,
                headers={"Content-Type": "application/json"},
            )
    except Exception as e:
        body = json.dumps({
            "success": False,
            "error": str(e)
        })
        logging.error(f'Error logging in user: {str(e)}')
        return Response(
            body,
            status=500,
            headers={"Content-Type": "application/json"},
        )


def login_with_data_base(usuario: str, contrasenia: str) -> dict[str, bool]:
    """
    Authenticate a user with the given username and password.
    Args:
        usuario (str): The username of the user.
        contrasenia (str): The password of the user.
    Returns:
        dict: A dictionary containing the user's UID and a thread ID if authentication is successful.
    """
    try:
        # Inicializar instancia de Firestore
        db = firestore.client()
        users_ref = db.collection('users')

        # Realizamos una consulta para encontrar el usuario con las credenciales proporcionadas
        query = users_ref.where('usuario', '==', usuario).where('contrasenia', '==', contrasenia).limit(1)

        # Ejecutamos la consulta
        results = query.stream()
        
        # Si encontramos un usuario que coincide, devolvemos su UID y thread ID
        for user_doc in results:
            # Obtenemos los datos del usuario
            user_data = user_doc.to_dict()
            return {
                "uid": user_doc.id,
                "admin": user_data.get('admin', False)
            }
    except Exception as e:
        logging.error(f"Error de autenticación {usuario}: {e}")
    return {}

def login_with_firecrebase_auth(usuario: str, contrasenia: str) -> dict[str, bool]:
    """
    Authenticate a user with Firebase Authentication.
    Args:
        usuario (str): The username of the user.
        contrasenia (str): The password of the user.
    Returns:
        dict: A dictionary containing the user's UID and a thread ID if authentication is successful.
    """
    try:
        # Intentar autenticar al usuario con Firebase Auth
        user = auth.get_user_by_email(usuario)
        # Aquí deberías verificar la contraseña, pero Firebase Admin SDK no permite verificar contraseñas directamente.
        # Normalmente, esto se hace en el cliente o mediante un servicio de autenticación personalizado.

        # Si el usuario es encontrado, devolvemos su UID
        return {
            "uid": user.uid,
            "admin": user.custom_claims.get('admin', False) if user.custom_claims else False
        }
    except auth.UserNotFoundError:
        logging.error(f"Usuario no encontrado: {usuario}")
    except Exception as e:
        logging.error(f"Error de autenticación con Firebase Auth {usuario}: {e}")
    return {}