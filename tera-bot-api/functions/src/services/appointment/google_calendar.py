import datetime as dt
import json
import logging
import os.path
import os
from dotenv import load_dotenv
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

_env_path = Path(__file__).resolve().parents[3] / ".env"
if _env_path.exists():
    load_dotenv(dotenv_path=_env_path, override=False)

# Clase para gestionar el calendario de Google
class AdministradorCalendarioGoogle:
    """Clase para gestionar el calendario de Google.
    Proporciona métodos para autenticar, listar, crear, actualizar y eliminar eventos en el calendario.

    Args:
        None

    Returns:
        json: Respuesta de la API de Google Calendar.

    Methods:
        lista_eventos_proximos: Lista los próximos eventos en el calendario.
        crear_evento: Crea un nuevo evento en el calendario.
        actualizar_evento: Actualiza un evento existente en el calendario.
        eliminar_evento: Elimina un evento del calendario.
    Raises:
        HttpError: Si ocurre un error al interactuar con la API de Google Calendar.
        ValueError: Si los parámetros de entrada son inválidos.
    """

    # Inicializa el servicio de Google Calendar
    def __init__(self):
        self.servicio = self._autenticar()

    # Método para autenticar el servicio de Google Calendar
    def _autenticar(self):
        """
        Autentica y devuelve el servicio de Google Calendar.
        Returns:
            servicio: Instancia del servicio de Google Calendar autenticado.
        """
        try:
            credenciales = None
            token_file = "token_calendar.json" # Use a consistent name for user tokens
            client_secret_file = "client-secret.json" # Your application's client secret
            base_dir = Path(__file__).parent
            token_file = os.getenv(
                "GOOGLE_CALENDAR_TOKEN_FILE",
                str(base_dir / token_file)
            )
            logging.info(f"Usando archivo de tokens: {token_file}")

            client_secret_file = os.getenv(
                "GOOGLE_CLIENT_SECRET_FILE",
                str(base_dir / client_secret_file)
            )
            logging.info(f"Usando archivo de secretos del cliente: {client_secret_file}")

            # 1. Try to load existing user credentials (tokens)
            if os.path.exists(token_file):
                logging.info(f"El archivo de tokens '{token_file}' existe.")
                try: 
                    credenciales = Credentials.from_authorized_user_file(token_file, SCOPES)
                    logging.info("Credenciales cargadas desde el archivo de tokens.")
                except Exception as e:
                    logging.error(f"Error al cargar credenciales desde el archivo de tokens: {e}")
                    credenciales = None
            else:
                logging.info(f"El archivo de tokens '{token_file}' no existe.")
                logging.info("No se encontró token, se requiere autenticación.")
            
            logging.info(f"Credenciales antes de la validación: {credenciales}")

            # 2. If no valid credentials, initiate the full OAuth flow
            if not credenciales or not credenciales.valid:
                print("No se encontraron credenciales válidas, iniciando flujo de autenticación.")
                logging.info("No se encontraron credenciales válidas, iniciando flujo de autenticación.")

                # Refresh if expired and refresh_token exists
                if credenciales and credenciales.expired and credenciales.refresh_token:
                    print("Credenciales expiradas, intentando refrescar.")
                    credenciales.refresh(Request())
                else:
                    # Start the flow using the application's client_secret.json
                    # This file should contain client_id and client_secret
                    if not os.path.exists(client_secret_file):
                        raise FileNotFoundError(f"Error: El archivo de secretos del cliente '{client_secret_file}' no se encontró.")

                    flujo = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
                    print("Iniciando el servidor local para la autenticación...")
                    credenciales = flujo.run_local_server()

                # Save the obtained credentials (including refresh_token) for future use
                with open(token_file, "w") as token:
                    token.write(credenciales.to_json())
                print(f"Credenciales guardadas en '{token_file}'.")

            print("Autenticación exitosa.")
            return build("calendar", "v3", credentials=credenciales)
        except Exception as e:
            logging.error(f"Error al autenticar con Google Calendar: {e}")
            raise



    # Listar los próximos eventos en el calendario
    def lista_eventos_proximos(
            self,
            max_resultados: int = 50,
            ) -> list:
        """
        Lista los próximos eventos en el calendario.
        Args:
            max_resultados (int): Número máximo de eventos a listar.
        Returns:
            eventos (list): Lista de eventos próximos.
        """
        ahora = dt.datetime.now(dt.timezone.utc).isoformat()
        manana = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=30)).replace(hour=23, minute=59, second=0, microsecond=0).isoformat()

        resultados_eventos = self.servicio.events().list(
            calendarId='primary',
            timeMin=ahora, timeMax=manana,
            maxResults=max_resultados,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        eventos = resultados_eventos.get('items', [])

        if not eventos:
            print('No se encontraron eventos próximos.')
        else:
            for evento in eventos:
                inicio = evento['start'].get('dateTime', evento['start'].get('date'))
                print(inicio, evento.get('summary'), evento.get('id'))
        
        return eventos

    # Método para crear un nuevo evento en el calendario
    def crear_evento(
            self,
            nombre_evento: str,
            descripcion_evento: str,
            inicio: str,
            fin: str,
            zona_horaria: str,
            asistentes: list | None,
            ) -> dict:
        """
        Crea un nuevo evento en el calendario.
        Args:
            nombre_evento (str): Nombre o resumen del evento.
            inicio (str): Fecha y hora de inicio del evento en formato ISO 8601.
            fin (str): Fecha y hora de fin del evento en formato ISO 8601.
            zona_horaria (str): Zona horaria del evento (por ejemplo, 'Europe/Madrid').
            asistentes (list, optional): Lista de correos electrónicos de los asistentes al evento. Defaults to None.
        Returns:
            evento (dict): Detalles del evento creado.
        """

        # Crear el cuerpo del evento
        evento: dict = {
            'summary': nombre_evento,
            'description': descripcion_evento,
            'start': {
                'dateTime': inicio,
                'timeZone': zona_horaria,
            },
            'end': {
                'dateTime': fin,
                'timeZone': zona_horaria,
            },
            # Recordatorios predeterminados
            'reminders': {

                # Usar recordatorios predeterminados
                'useDefault': False,

                # O definir recordatorios personalizados
                'overrides': [
                    # Recordatorio por correo electrónico
                    {'method': 'email', 'minutes': 24 * 60},

                    # Recordatorio emergente
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        }

        # Agregar asistentes si se proporcionan
        if asistentes:
            # Se usa una COMPRENSIÓN DE LISTAS para crear la lista de asistentes
            evento["attendees"] = [{"email": email} for email in asistentes]

        try:
            # Llamar a la API de Google Calendar para crear el evento
            evento = self.servicio.events().insert(calendarId="primary", body=evento).execute()
            print(f"Evento creado: {evento.get('htmlLink')}")
            print("El evento es:", json.dumps(evento))
            return evento
        except HttpError as error:
            print(f"Ocurrió un error: {error}")
            return {"error": str(error)}

    # Método para actualizar un evento existente
    def actualizar_evento(
            self,
            evento_id: str,
            resumen: str | None = None,
            description: str | None = None,
            inicio: dt.datetime | None = None,
            fin: dt.datetime | None = None,
            asistentes: list | None = None,
    ) -> dict:
        """
        Actualiza un evento existente en el calendario.
        Args:
            evento_id (str): ID del evento a actualizar.
            resumen (str, optional): Nuevo resumen del evento. Defaults to None.
            inicio (datetime, optional): Nueva fecha y hora de inicio del evento. Defaults to None.
            fin (datetime, optional): Nueva fecha y hora de fin del evento. Defaults to None
        Returns:
            evento_actualizado (dict): Detalles del evento actualizado.
        Raises:
            ValueError: Si no se proporciona ningún campo para actualizar.
        """
        try:
            # Obtener el evento existente
            evento: dict = self.servicio.events().get(calendarId='primary', eventId=evento_id).execute()

            # Actualizar los campos proporcionados
            if resumen:
                evento['summary'] = resumen

            if description:
                evento['description'] = description

            # Actualizar la fecha y hora de inicio
            if inicio:
                # Si inicio es datetime, formatear; si es string dejarlo tal cual
                if hasattr(inicio, "strftime"):
                    evento['start']['dateTime'] = inicio.strftime('%Y-%m-%dT%H:%M:%S')
                else:
                    evento['start']['dateTime'] = inicio

            if fin:
                if hasattr(fin, "strftime"):
                    evento['end']['dateTime'] = fin.strftime('%Y-%m-%dT%H:%M:%S')
                else:
                    evento['end']['dateTime'] = fin
            
            if asistentes is not None:
                evento['attendees'] = [{"email": email} for email in asistentes]

            evento_actualizado = self.servicio.events().update(
                calendarId='primary', eventId=evento_id, body=evento).execute()
            print(f"Evento actualizado: {json.dumps(evento_actualizado)}")
            return evento_actualizado
        except HttpError as error:
            print(f"Ocurrió un error al actualizar el evento: {error}")
            return {"error": str(error)}

    def eliminar_evento(
            self,
            evento_id: str,
            ) -> bool:
        """
        Método para eliminar un evento del calendario.
        Args:
            evento_id (str): ID del evento a eliminar.
        Returns:
            bool: True si el evento fue eliminado exitosamente, False en caso contrario.
        Raises:
            HttpError: Si ocurre un error al intentar eliminar el evento.
        """
        try:
            # Llamar a la API de Google Calendar para eliminar el evento
            self.servicio.events().delete(calendarId='primary', eventId=evento_id).execute()
            print(f"Evento con ID {evento_id} eliminado.")
            return True
        except HttpError as error:
            print(f"Ocurrió un error al eliminar el evento: {error}")
            return False
    
