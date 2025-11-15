from datetime import date, datetime
from flask import Request, Response
from firebase_admin import firestore
import logging
import json
from src.modelos.all_info import AllInfo
from src.modelos.ficha_medica import FichaMedica
from src.modelos.sigsa import Sigsa
from src.modelos.paciente import Paciente

class PatientService:
    """Servicio para actualizar información de pacientes en Firestore."""

    def __init__(self):
        self.db = firestore.client()

    def _to_json_safe(self, obj):
        try:
            if isinstance(obj, dict):
                return {k: self._to_json_safe(v) for k, v in obj.items()}
            
            if isinstance(obj, list):
                return [self._to_json_safe(i) for i in obj]

            if isinstance(obj, list):
                return [self._to_json_safe(i) for i in obj]
            
            if isinstance(obj, tuple):
                return tuple(self._to_json_safe(i) for i in obj)
            
            if isinstance(obj, (date, datetime)):
                return obj.isoformat()
            
            if hasattr(obj, "path") and obj.__class__.__name__.endswith("DocumentReference"):
                return obj.path
            
            if hasattr(obj, "latitude") and hasattr(obj, "longitude") and obj.__class__.__name__.endswith("GeoPoint"):
                return {"latitude": obj.latitude, "longitude": obj.longitude}
            
            if isinstance(obj, (bytes, bytearray)):
                return obj.decode("utf-8", errors="ignore")
            return obj
        except Exception as e:
            logging.error(f'Error converting to JSON safe: {e}')
            return str(obj)

    def handle_request(self, request: Request) -> Response:
        request_json = request.get_json(silent=True)

        if not request_json:
            body = json.dumps({
                "success": False,
                "error": "No JSON body found"
            })
            return Response(
                body,
                status=400,
                headers={"Content-Type": "application/json"}
            )

        patient_id = request_json.get('uid')
        new_info = request_json.get('new_info')
        sigsa_info = request_json.get('sigsa_info')
        ficha_medica_info = request_json.get('ficha_medica_info')

        if not patient_id:
            body = json.dumps({
                "success": False,
                "error": "Invalid request: Missing required field 'ref_patient'"
            })
            return Response(
                body,
                status=400,
                headers={"Content-Type": "application/json"}
            )

        try:
            sigsa_ref = self.update_sigsa_info_in_firestore(patient_id, sigsa_info)
            ficha_medica_ref = self.update_medical_record_in_firestore(patient_id, ficha_medica_info)
            self.update_patient_info_in_firestore(patient_id, new_info, sigsa_ref, ficha_medica_ref)
            body = json.dumps({"success": True})
            return Response(
                body,
                status=200,
                headers={"Content-Type": "application/json"}
            )
        except Exception as e:
            logging.error(f'Unhandled error in handle_request: {e}')
            body = json.dumps({
                "success": False,
                "error": str(e)
            })
            return Response(
                body,
                status=500,
                headers={"Content-Type": "application/json"}
            )
        finally:
            # Cerrar cliente si tiene método close
            try:
                if hasattr(self.db, 'close'):
                    self.db.close()
            except Exception:
                pass

    def update_patient_info_in_firestore(
            self,
            patient_id: str,
            new_info: dict,
            sigsa_ref: firestore.firestore.DocumentReference,
            ficha_medica_ref: firestore.firestore.DocumentReference
        ) -> None:
        """Actualiza los datos del paciente en la colección 'info_paciente'."""
        try:
            logging.info(f'Updating patient information for {patient_id} with {new_info}')
            info_patient = Paciente(
                uid=patient_id,
                nombre=new_info.get("nombre"),
                apellido=new_info.get("apellido"),
                fecha_consulta=new_info.get("fecha_consulta"),
                estado_paciente=new_info.get("estado_paciente"),
                ref_sigsa=sigsa_ref,
                ref_ficha_medica=ficha_medica_ref
            )
            logging.info(f'New patient info: {json.dumps(info_patient, default=str)}')
            patient_ref = self.db.collection('pacientes').document(patient_id)
            # Guardar únicamente new_info pero también se podría guardar info_patient dependiendo del diseño
            patient_ref.set(info_patient.__dict__, merge=True)
            logging.info(f'Patient information updated for {patient_ref.id}')
        except Exception as e:
            logging.error(f'Error updating patient information: {e}')
            raise

    def update_sigsa_info_in_firestore(
            self,
            patient_id: str,
            sigsa_info: dict,
        ) -> firestore.firestore.DocumentReference:
        """Actualiza o crea el documento SIGSA del paciente en 'sigsa'."""
        try:
            documents = self.db.collection('sigsa').get()
            doc = self.db.collection('sigsa').document(patient_id)

            if not doc.get().exists:
                documents_len = len(documents)
                new_id = documents_len + 1
                logging.info(f'Creating new SIGSA document for {patient_id}')
                doc.set({
                    "created": firestore.firestore.SERVER_TIMESTAMP,
                    "no_historia_clinica": new_id
                })

            logging.info(f'Updating SIGSA information for {patient_id} with {sigsa_info}')
            sigsa_data = Sigsa(
                uid=patient_id,
                fecha_consulta=sigsa_info.get("fecha_consulta"),
                nombre=sigsa_info.get("nombre"),
                apellido=sigsa_info.get("apellido"),
                cui=sigsa_info.get("cui"),
                fecha_nacimiento=sigsa_info.get("fecha_nacimiento"),
                edad=sigsa_info.get("edad"),
                ninio_menor_15=sigsa_info.get("ninio_menor_15"),
                adulto=sigsa_info.get("adulto"),
                genero=sigsa_info.get("genero"),
                municipio=sigsa_info.get("municipio"),
                aldea=sigsa_info.get("aldea"),
                embarazo=sigsa_info.get("embarazo"),
                consulta=sigsa_info.get("consulta"),
                diagnostico=sigsa_info.get("diagnostico"),
                cie_10=sigsa_info.get("cie_10"),
                terapia=sigsa_info.get("terapia"),
            )
            logging.info(f'New SIGSA info: {json.dumps(sigsa_data, default=str)}')
            sigsa_ref = self.db.collection('sigsa').document(patient_id)
            sigsa_ref.set(sigsa_data.__dict__, merge=True)
            logging.info(f'SIGSA information updated for {sigsa_ref.id}')
            return sigsa_ref
        except Exception as e:
            logging.error(f'Error updating SIGSA information: {e}')
            raise

    def update_medical_record_in_firestore(
            self,
            patient_id: str,
            medical_record: dict,
        ) -> firestore.firestore.DocumentReference:
        """Actualiza la ficha médica del paciente en 'fichas_medicas'."""
        try:
            logging.info(f'Updating medical record for {patient_id} with {medical_record}')
            medical_record_data = FichaMedica(
                uid=patient_id,
                patologia=medical_record.get("patologia"),
                cui=medical_record.get("cui"),
                escolaridad=medical_record.get("escolaridad"),
                edad=medical_record.get("edad"),
                ocupacion=medical_record.get("ocupacion"),
                aldea=medical_record.get("aldea"),
                estado_civil=medical_record.get("estado_civil"),
                paciente_referido=medical_record.get("paciente_referido"),
                genero=medical_record.get("genero"),
                municipio=medical_record.get("municipio"),
                cei10=medical_record.get("cei10"),
                tipo_consulta=medical_record.get("tipo_consulta"),
                tipo_terapia=medical_record.get("tipo_terapia"),
                embarazo=medical_record.get("embarazo"),
            )
            logging.info(f'New medical record: {json.dumps(medical_record_data, default=str)}')
            ficha_medica_ref = self.db.collection('fichas_medicas').document(patient_id)
            ficha_medica_ref.set(medical_record_data.__dict__, merge=True)
            logging.info(f'Medical record updated for {ficha_medica_ref.id}')
            return ficha_medica_ref
        except Exception as e:
            logging.error(f'Error updating medical record: {e}')
            raise
    
    def get_patient_info(self, request: Request) -> Response:
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

        request_json = request.get_json(silent=True)
        if not request_json:
            body = json.dumps({
                "success": False,
                "error": "No JSON body found"
            })
            logging.error("No JSON body found in request")
            return Response(
                body,
                status=400,
                headers={"Content-Type": "application/json"}
            )

        uid = request_json.get('uid')

        try:
            if not uid:
                body = json.dumps({
                    "success": False,
                    "error": "Petición inválida: Falta el campo requerido 'uid'"
                })
                logging.error("Falta el campo requerido 'uid'")
                return Response(
                    body,
                    status=400,
                    headers={"Content-Type": "application/json"}
                )

            paciente_ref = self.db.collection('pacientes').document(uid)
            paciente_doc = paciente_ref.get()
            if paciente_doc.exists:
                raw = paciente_doc.to_dict()
                safe = self._to_json_safe(raw)
                paciente_obj = Paciente(**safe)
                logging.info(f"Los datos encontrasdos son: {safe}")
                body = json.dumps({
                    "success": True,
                    "data": paciente_obj.__dict__
                })
            else:
                body = json.dumps({
                    "success": False,
                    "error": "No se encontraron datos para el UID proporcionado"
                })
            return Response(
                body,
                status=200 if paciente_doc.exists else 404,
                headers={"Content-Type": "application/json"}
            )
        except Exception as e:
            logging.error(f"Error fetching patient info for UID {uid}: {e}")
            raise

    def get_sigsa_info(self, request: Request) -> Response:
        if request.method != 'GET':
            body = json.dumps({
                "success": False,
                "error": "Método HTTP inválido. Solo se permiten solicitudes GET."
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
                "error": "No JSON body found"
            })
            logging.error("No JSON body found in request")
            return Response(
                body,
                status=400,
                headers={"Content-Type": "application/json"}
            )

        uid = request_json.get('uid')
        
        try:
            if not uid:
                body = json.dumps({
                    "success": False,
                    "error": "Petición inválida: Falta el campo requerido 'uid'"
                })
                logging.error("Falta el campo requerido 'uid'")
                return Response(
                    body,
                    status=400,
                    headers={"Content-Type": "application/json"}
                )
            
            sigsa_ref = self.db.collection('sigsa').document(uid)
            sigsa_doc = sigsa_ref.get()
            if sigsa_doc.exists:
                raw = sigsa_doc.to_dict()
                safe = self._to_json_safe(raw)
                sigsa_obj = Sigsa(**safe)
                logging.info(f"Los datos encontrasdos son: {safe}")
                body = json.dumps({
                    "success": True,
                    "data": sigsa_obj.__dict__
                })
            else:
                body = json.dumps({
                    "success": False,
                    "error": "No se encontraron datos para el UID proporcionado"
                })
            return Response(
                body,
                status=200 if sigsa_doc.exists else 404,
                headers={"Content-Type": "application/json"}
            )
        except Exception as e:
            logging.error(f"Error fetching SIGSA info for UID {uid}: {e}")
            raise

    def get_medical_record(self, request: Request) -> Response:
        if request.method != 'GET':
            body = json.dumps({
                "success": False,
                "error": "Método HTTP inválido. Solo se permiten solicitudes GET."
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
                "error": "No JSON body found"
            })
            logging.error("No JSON body found in request")
            return Response(
                body,
                status=400,
                headers={"Content-Type": "application/json"}
            )

        uid = request_json.get('uid')

        try:
            if not uid:
                body = json.dumps({
                    "success": False,
                    "error": "Petición inválida: Falta el campo requerido 'uid'"
                })
                logging.error("Falta el campo requerido 'uid'")
                return Response(
                    body,
                    status=400,
                    headers={"Content-Type": "application/json"}
                )

            ficha_medica_ref = self.db.collection('fichas_medicas').document(uid)
            ficha_medica_doc = ficha_medica_ref.get()
            if ficha_medica_doc.exists:
                raw = ficha_medica_doc.to_dict()
                safe = self._to_json_safe(raw)
                ficha_medica_obj = FichaMedica(**safe)
                logging.info(f"Los datos encontrasdos son: {safe}")
                body = json.dumps({
                    "success": True,
                    "data": ficha_medica_obj.__dict__
                })
            else:
                body = json.dumps({
                    "success": False,
                    "error": "No se encontraron datos para el UID proporcionado"
                })
            return Response(
                body,
                status=200 if ficha_medica_doc.exists else 404,
                headers={"Content-Type": "application/json"}
            )
        except Exception as e:
            logging.error(f"Error fetching medical record for UID {uid}: {e}")
            raise

    def get_all_patients(self) -> list[AllInfo]:
        try:
            patients = self.db.collection('pacientes').stream()
            sigsa = self.db.collection('sigsa').stream()
            ficha_medica = self.db.collection('fichas_medicas').stream()
            # Obtener todas las colecciones
            patients_docs = list(patients)
            sigsa_docs = list(sigsa)
            ficha_medica_docs = list(ficha_medica)

            # Crear diccionarios indexados por UID
            sigsa_dict = {doc.id: self._to_json_safe(doc.to_dict()) for doc in sigsa_docs}
            ficha_medica_dict = {doc.id: self._to_json_safe(doc.to_dict()) for doc in ficha_medica_docs}
            
            all_info = []
            
            for patient_doc in patients_docs:
                patient_uid = patient_doc.id
                patient_data = self._to_json_safe(patient_doc.to_dict())
                patient_data['uid'] = patient_uid
                
                # Obtener datos relacionados
                sigsa_data = sigsa_dict.get(patient_uid, {'uid': patient_uid})
                ficha_medica_data = ficha_medica_dict.get(patient_uid, {'uid': patient_uid})
                
                # Asegurar que los datos tengan UID
                if 'uid' not in sigsa_data:
                    sigsa_data['uid'] = patient_uid
                if 'uid' not in ficha_medica_data:
                    ficha_medica_data['uid'] = patient_uid
                
                try:
                    # Crear instancias de los modelos
                    paciente_obj = Paciente(**patient_data)
                    sigsa_obj = Sigsa(**sigsa_data)
                    ficha_medica_obj = FichaMedica(**ficha_medica_data)
                    logging.warn(f"Paciente: {paciente_obj.__dict__}")
                    logging.warn(f"SIGSA: {sigsa_obj.__dict__}")
                    logging.warn(f"Ficha Médica: {ficha_medica_obj.__dict__}")
                    
                    # Crear objeto AllInfo
                    info = AllInfo(
                        paciente=paciente_obj,
                        sigsa=sigsa_obj,
                        ficha_medica=ficha_medica_obj
                    )
                    logging.warn(f"AllInfo: {info}")
                    all_info.append(info)
                    logging.warn(f"Added AllInfo for patient UID {patient_uid}")
                    logging.warn(f"Current total patients: {len(all_info)}")
                    logging.warn(f"Patient data: {all_info}")

                except Exception as e:
                    logging.error(f"Error creating models for patient {patient_uid}: {e}")
                    logging.error(f"Patient data: {patient_data}")
                    logging.error(f"SIGSA data: {sigsa_data}")
                    logging.error(f"Ficha médica data: {ficha_medica_data}")
                    continue
            
    
            logging.info(f"Total patients fetched: {all_info}")
            return all_info
        except Exception as e:
            logging.error(f"Error fetching all patients: {e}")
            raise
    
    def close(self):
        try:
            if hasattr(self.db, 'close'):
                self.db.close()
        except Exception as e:
            logging.error(f'Error closing Firestore client: {e}')

# Función de entrada compatible con Cloud Functions que delega en la clase
def update_patient_information(request: Request) -> Response:
    service = PatientService()
    response = service.handle_request(request)
    service.close()
    return response

# Función para obtener información del paciente
def get_patient_information(request: Request) -> Response:
    service = PatientService()
    response = service.get_patient_info(request)
    service.close()
    return response

# Función para obtener información de SIGSA
def get_sigsa_information(request: Request) -> Response:
    service = PatientService()
    response = service.get_sigsa_info(request)
    service.close()
    return response

# Función para obtener información de la ficha médica
def get_medical_record_information(request: Request) -> Response:
    service = PatientService()
    response = service.get_medical_record(request)
    service.close()
    return response


def get_all_patients() -> list[AllInfo]:
    service = PatientService()
    patients = service.get_all_patients()
    logging.info(f"Patients retrieved: {patients}")
    patient_data = []
    for patient in patients:
        try:
            patient_data.append({
                "uid": patient.paciente.uid if patient.paciente else None,
                "paciente": patient.paciente.__dict__ if patient.paciente else None,
                "sigsa": patient.sigsa.__dict__ if patient.sigsa else None,
                "ficha_medica": patient.ficha_medica.__dict__ if patient.ficha_medica else None,
            })
        except Exception as e:
            logging.error(f"Error converting patient to dict: {e}")
            continue
    service.close()
    return patient_data