import logging
from flask import request, jsonify
from swagger_server.models.prospection_request import ProspectionRequest  # noqa: E501
from ..models import IdStateprospectionsBody
from ..repositories.admin_prospection_repository import AdminProspectionRepository  # Import repository

prospection_repository = AdminProspectionRepository()

def admin_prospections_get():  # noqa: E501
    """Retrieve all prospections (admin view)

     # noqa: E501


    :rtype: List[Prospection]
    """
    return prospection_repository.get_all_prospections()

def admin_prospections_get_admin():
    return prospection_repository.get_all_prospections_admin()

def admin_prospections_id_get(id_):  # noqa: E501
    return prospection_repository.get_prospection_by_id(id_)

def admin_prospections_id_delete(id_):  # noqa: E501
    return prospection_repository.delete_prospection_by_id(id_)

def admin_prospections_id_emails_get(id_):  # noqa: E501
    return prospection_repository.get_emails_by_prospection_id(id_)

def admin_prospections_id_sales_advisor_get(id_):  # noqa: E501
    return prospection_repository.get_sales_advisor_by_prospection_id(id_)

def admin_prospections_post():  # noqa: E501
    if request.is_json:
        try:
            data = request.get_json()

            response, status = prospection_repository.create_prospection(data)
            return jsonify(response), status

        except Exception as e:
            logging.error(f"Error al procesar la creación de la prospección: {e}")
            return {"message": f"Error al procesar la solicitud: {str(e)}"}, 500
    else:
        return {"message": "El cuerpo de la solicitud debe estar en formato JSON"}, 400

def admin_prospections_id_patch(id_):  # noqa: E501
    """
    Partially update a prospection.
    This function handles PATCH requests to update an existing prospection's data.
    """
    if request.is_json:
        try:
            data = request.get_json()
            response, status = prospection_repository.update_prospection(id_, data)
            return jsonify(response), status

        except Exception as e:
            logging.error(f"Error al actualizar la prospección:{e}")
            return {"message": f"Error al procesar la solicitud: {str(e)}"}, 500
    else:
        return {"message": "El formato de la solicitud debe estar en formato JSON."}, 400

def admin_prospects_id_prospections_get(id_):  # noqa: E501
    return prospection_repository.get_prospections_by_prospect_id(id_)

def admin_prospections_id_history_get(id_):
    return prospection_repository.get_prospection_history_with_logs(id_)

def admin_get_state_prospection():  # noqa: E501
    return prospection_repository.get_state_prospections()

def admin_prospections_id_state_patch(id_):  # noqa: E501
    if request.is_json:
        try:
            data = request.get_json()  # noqa: E501
            response, status = prospection_repository.update_prospection_state(id_, data)
            return jsonify(response), status

        except Exception as e:
            logging.error(f"Error al actualizar la prospección: {e}")
            return {"message": f"Error al procesar la solicitud: {str(e)}"}, 500
    else:
        return {"message": "El formato de la solicitud debe estar en formato JSON."}, 400