import logging
from flask import request, jsonify
from ..repositories.alert_repository import AlertRepository

alert_repository = AlertRepository()

def get_alert_days(id_):
    """
    Retrieve the `days` value of an alert by its ID.
    """
    try:
        response, status = alert_repository.get_alert_days(id_)
        return jsonify(response), status
    except Exception as e:
        logging.error(f"Error al obtener los días de la alerta con ID {id_}: {e}")
        return {"message": f"Error al procesar la solicitud: {str(e)}"}, 500

def update_alert_days(id_):
    """
    Update the `days` value of an alert by its ID.
    """
    if request.is_json:
        try:
            data = request.get_json()
            response, status = alert_repository.update_alert_days(id_, data)
            return jsonify(response), status
        except Exception as e:
            logging.error(f"Error al actualizar los días de la alerta con ID {id_}: {e}")
            return {"message": f"Error al procesar la solicitud: {str(e)}"}, 500
    else:
        return {"message": "El cuerpo de la solicitud debe estar en formato JSON."}, 400
