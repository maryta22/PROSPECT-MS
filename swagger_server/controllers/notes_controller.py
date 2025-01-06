import connexion
import six
from flask import request, jsonify

from swagger_server.models.note import Note  # noqa: E501
from swagger_server import util
from swagger_server.repositories.prospect_repository import ProspectRepository
from swagger_server.repositories.prospection_repository import ProspectionRepository

prospection_repository = ProspectionRepository()


def notes_post():
    body = request.get_json()
    return prospection_repository.save_note(body)



def prospections_id_notes_get(id_):  # noqa: E501
    return prospection_repository.get_notes_by_prospection_id(id_)
