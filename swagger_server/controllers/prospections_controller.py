import logging
from flask import request, jsonify
from swagger_server.models.prospect_request import ProspectRequest  # noqa: E501
from ..repositories.prospect_repository import ProspectRepository  # Import repository

prospect_repository = ProspectRepository()

def prospections_get():  # noqa: E501
    return prospect_repository.get_all_prospections()

def prospections_id_get(id_):  # noqa: E501
    return prospect_repository.get_prospection_by_id(id_)

def prospections_id_delete(id_):  # noqa: E501
    return prospect_repository.delete_prospection_by_id(id_)

def prospections_id_notes_get(id_):  # noqa: E501
    return prospect_repository.get_notes_by_prospection_id(id_)

def prospections_id_emails_get(id_):  # noqa: E501
    return prospect_repository.get_emails_by_prospection_id(id_)

def prospections_id_sales_advisor_get(id_):  # noqa: E501
    return prospect_repository.get_sales_advisor_by_prospection_id(id_)

def prospections_post():  # noqa: E501
    if request.is_json:
        try:
            data = request.get_json()
            # Extrae los datos necesarios del cuerpo de la solicitud
            prospection_data = data.get("prospection")

            if not prospection_data:
                return {"message": "Prospection data is required."}, 400

            # Llama al repositorio para crear la prospección
            response, status = prospect_repository.create_prospection(prospection_data)
            return jsonify(response), status

        except Exception as e:
            logging.error(f"Error processing prospection creation: {e}")
            return {"message": f"Error processing request: {str(e)}"}, 500
    else:
        return {"message": "Request body must be JSON."}, 400
