import logging
from datetime import datetime
import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine
from swagger_server.database_models.models import *

load_dotenv()
class ProspectRepository:

    def __init__(self):
        db_password = os.getenv('DB_PASSWORD')
        self.engine = create_engine(f'mysql+pymysql://root:{db_password}@localhost:3306/espae_prospections')
        self.Session = sessionmaker(bind=self.engine)

    def get_all_prospects(self):
        session = self.Session()
        try:
            prospects = session.query(Prospect).options(
                joinedload(Prospect.user),
                joinedload(Prospect.city)
            ).all()
            return [prospect.to_dict() for prospect in prospects], 200
        except Exception as e:
            logging.error(f"Error retrieving prospects: {e}")
            return {"message": f"Error retrieving prospects: {str(e)}"}, 500
        finally:
            session.close()

    def get_prospect_by_id(self, id):
        session = self.Session()
        try:
            prospect = session.query(Prospect).options(
                joinedload(Prospect.user),
                joinedload(Prospect.city)
            ).filter_by(id=id).first()
            if not prospect:
                return {"message": "Prospect not found"}, 404
            return prospect.to_dict(), 200
        except Exception as e:
            logging.error(f"Error retrieving prospect: {e}")
            return {"message": f"Error retrieving prospect: {str(e)}"}, 500
        finally:
            session.close()

    def create_prospect(self, user_data, prospect_data):
        session = self.Session()
        try:
            existing_prospect = session.query(Prospect).filter_by(id_number=prospect_data.get("id_number")).first()
            if existing_prospect:
                return {
                    "message": "Ya existe un prospecto con ese numero de cedula",
                    "id": existing_prospect.id,
                }, 400

            # Crear un nuevo usuario
            new_user = User(**user_data)
            session.add(new_user)
            session.flush()

            # Crear un nuevo prospecto asociado al usuario
            prospect_data["id_user"] = new_user.id
            new_prospect = Prospect(**prospect_data)
            session.add(new_prospect)
            session.flush()
            session.commit()

            return {
                "message": "Prospect and user created successfully.",
                "id": new_prospect.id,
            }, 201
        except Exception as e:
            session.rollback()
            logging.error(f"Error creating prospect: {e}")
            return {"message": f"Error creating prospect: {str(e)}"}, 400
        finally:
            session.close()

    def update_prospect(self, id_, prospect_data):
        session = self.Session()
        try:
            if hasattr(prospect_data, 'attribute_map'):
                clean_data = {
                    field_name: getattr(prospect_data, field_name, None)
                    for field_name in prospect_data.attribute_map.values()
                    if getattr(prospect_data, field_name, None) is not None
                }
            else:
                clean_data = {k: v for k, v in prospect_data.__dict__.items() if v is not None}

            prospect = session.query(Prospect).filter_by(id=id_).first()
            if not prospect:
                return {"message": "Prospect not found"}, 404

            user = session.query(User).filter_by(id=prospect.id_user).first()
            if not user:
                return {"message": "User associated with the prospect not found"}, 404

            if "state" in clean_data:
                prospect.state = clean_data["state"]
            if "id_city" in clean_data:
                prospect.id_city = clean_data["id_city"]
            if "degree" in clean_data:
                prospect.degree = clean_data["degree"]
            if "company" in clean_data:
                prospect.company = clean_data["company"]

            user_fields = ["first_name", "last_name", "email", "phone"]
            for field in user_fields:
                if field in clean_data:
                    setattr(user, field, clean_data[field])

            session.commit()
            return {"message": "Prospect and user updated successfully."}, 200

        except Exception as e:
            session.rollback()
            logging.error(f"Error updating prospect and user: {e}")
            return {"message": f"Error updating prospect and user: {str(e)}"}, 400
        finally:
            session.close()

    def delete_prospect_by_id(self, id_):
        session = self.Session()
        try:
            prospect = session.query(Prospect).filter_by(id=id_).first()
            if not prospect:
                return {"message": "Prospect not found"}, 404

            session.delete(prospect)
            session.commit()
            return {"message": "Prospect deleted successfully."}, 204
        except Exception as e:
            session.rollback()
            logging.error(f"Error deleting prospect: {e}")
            return {"message": f"Error deleting prospect: {str(e)}"}, 400
        finally:
            session.close()


    def get_prospects_by_sales_advisor_id(self, sales_advisor_id):
        session = self.Session()
        try:
            prospections = session.query(Prospection).join(ProspectionSalesAdvisor).filter(
                ProspectionSalesAdvisor.id_sales_advisor == sales_advisor_id
            ).all()
            if not prospections:
                return {"message": "No prospects found for this sales advisor"}, 404

            return [p.prospect.to_dict() for p in prospections], 200
        except Exception as e:
            logging.error(f"Error retrieving prospects for sales advisor: {e}")
            return {"message": f"Error retrieving prospects: {str(e)}"}, 500
        finally:
            session.close()


    def get_all_cities(self):
        session = self.Session()
        try:
            cities = session.query(City).all()
            return [city.to_dict() for city in cities], 200
        except Exception as e:
            logging.error(f"Error retrieving cities: {e}")
            return {"message": f"Error retrieving cities: {str(e)}"}, 500
        finally:
            session.close()