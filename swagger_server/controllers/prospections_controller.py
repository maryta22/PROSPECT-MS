import logging
from flask import request, jsonify
from swagger_server.models.prospect_request import ProspectRequest  # noqa: E501
from ..models import IdStateprospectionsBody
from ..repositories.prospect_repository import ProspectRepository  # Import repository

prospect_repository = ProspectRepository()

def prospections_get():  # noqa: E501
    return prospect_repository.get_all_prospections()

def prospections_id_get(id_):  # noqa: E501
    return prospect_repository.get_prospection_by_id(id_)

def prospections_id_delete(id_):  # noqa: E501
    return prospect_repository.delete_prospection_by_id(id_)

def prospections_id_emails_get(id_):  # noqa: E501
    return prospect_repository.get_emails_by_prospection_id(id_)

def prospections_id_sales_advisor_get(id_):  # noqa: E501
    return prospect_repository.get_sales_advisor_by_prospection_id(id_)

def prospections_post():  # noqa: E501
    if request.is_json:
        try:
            data = request.get_json()

            response, status = prospect_repository.create_prospection(data)
            return jsonify(response), status

        except Exception as e:
            logging.error(f"Error processing prospection creation: {e}")
            return {"message": f"Error processing request: {str(e)}"}, 500
    else:
        return {"message": "Request body must be JSON."}, 400

def prospections_id_patch(id_):  # noqa: E501
    """
    Partially update a prospection.
    This function handles PATCH requests to update an existing prospection's data.
    """
    if request.is_json:
        try:
            data = request.get_json()
            response, status = prospect_repository.update_prospection(id_, data)
            return jsonify(response), status

        except Exception as e:
            logging.error(f"Error updating prospection: {e}")
            return {"message": f"Error processing request: {str(e)}"}, 500
    else:
        return {"message": "Request body must be JSON."}, 400

def prospects_id_prospections_get(id_):  # noqa: E501
    return prospect_repository.get_prospections_by_prospect_id(id_)

def prospections_id_history_get(id_):
    return prospect_repository.get_prospection_history_with_logs(id_)

def get_state_prospection():  # noqa: E501
    return prospect_repository.get_state_prospections()

def prospections_id_state_patch(id_):  # noqa: E501
    if request.is_json:
        try:
            data = request.get_json()  # noqa: E501
            response, status = prospect_repository.update_prospection_state(id_, data)
            return jsonify(response), status

        except Exception as e:
            logging.error(f"Error updating prospection: {e}")
            return {"message": f"Error processing request: {str(e)}"}, 500
    else:
        return {"message": "Request body must be JSON."}, 400