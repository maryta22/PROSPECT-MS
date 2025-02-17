import logging
from flask import request, jsonify
from swagger_server.models.prospect_request import  ProspectRequest # noqa: E501
from ..models import ProspectUpdate
from ..repositories.admin_prospect_repository import AdminProspectRepository  # Import repository

prospect_repository = AdminProspectRepository()

def admin_prospects_get():  # noqa: E501
    """
    Returns:
        tuple: (data, status_code)
        200: Lista de prospectos
        500: Error del servidor
    """
    return prospect_repository.get_all_prospects()

def admin_prospects_id_delete(id_):  # noqa: E501
    return prospect_repository.delete_prospect_by_id(id_)

def admin_prospects_id_get(id_):  # noqa: E501
    return prospect_repository.get_prospect_by_id(id_)

def admin_prospects_id_patch(body, id_):  # noqa: E501
    if request.is_json:
        try:
            raw_data = request.get_json()
            logging.info(f"Data received to update prospect: {raw_data}")
            body = ProspectUpdate.from_dict(raw_data)  # noqa: E501
            print(body)
            return prospect_repository.update_prospect(id_, body)
        except ValueError as ve:
            logging.error(f"Error de validacion: {ve}")
            return {"message": str(ve)}, 400
        except Exception as e:
            logging.error(f"Error al procesar los datos: {e}")
            return {"message": f"Error al procesar los datos: {str(e)}"}, 500

def admin_prospects_post():  # noqa: E501
    """
    Returns:
        tuple: (data, status_code)
        201: Prospecto creado exitosamente
        400: Datos inválidos
    """
    if request.is_json:
        try:
            data = request.get_json()
            user_data = data.get("user")
            prospect_data = data.get("prospect")

            if not user_data or not prospect_data:
                return {"message": "El usuario y el prospecto es requerido"}, 400

            response, status = prospect_repository.create_prospect(user_data, prospect_data)
            return jsonify(response), status

        except Exception as e:
            logging.error(f"Error processing request: {e}")
            return {"message": f"Error al procesar la respuesta: {str(e)}"}, 500
    else:
        return {"message": "El formato de la solicitud debe estar en formato JSON."}, 400

def admin_prospects_sales_advisor_advisor_id_get(advisor_id):  # noqa: E501
    return prospect_repository.get_prospects_by_sales_advisor_id(advisor_id)

def admin_prospects_id_prospections_get(id_):  # noqa: E501
    return prospect_repository.get_prospections_by_prospect_id(id_)

