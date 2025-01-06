from swagger_server.models.city import City  # noqa: E501
from swagger_server.repositories.prospect_repository import ProspectRepository

prospect_repository = ProspectRepository()

def get_all_cities():  # noqa: E501
    return prospect_repository.get_all_cities()
