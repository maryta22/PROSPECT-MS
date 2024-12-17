import logging
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine
from swagger_server.database_models.models import *

class ProspectRepository:

    def __init__(self):
        self.engine = create_engine('mysql+pymysql://root:root@localhost:3306/espae_prospections')
        self.Session = sessionmaker(bind=self.engine)

    def get_all_prospects(self):
        session = self.Session()
        try:
            prospects = session.query(Prospect).options(
                joinedload(Prospect.user)
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
                joinedload(Prospect.user)
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
            new_user = User(**user_data)
            session.add(new_user)
            session.flush()

            prospect_data["id_user"] = new_user.id
            new_prospect = Prospect(**prospect_data)
            session.add(new_prospect)
            session.commit()

            return {"message": "Prospect and user created successfully."}, 201
        except Exception as e:
            session.rollback()
            logging.error(f"Error creating prospect: {e}")
            return {"message": f"Error creating prospect: {str(e)}"}, 400
        finally:
            session.close()

    def update_prospect(self, id, prospect_data):
        session = self.Session()
        try:
            prospect = session.query(Prospect).filter_by(id=id).first()
            if not prospect:
                return {"message": "Prospect not found"}, 404

            for key, value in prospect_data.items():
                setattr(prospect, key, value)

            session.commit()
            return {"message": "Prospect updated successfully."}, 200
        except Exception as e:
            session.rollback()
            logging.error(f"Error updating prospect: {e}")
            return {"message": f"Error updating prospect: {str(e)}"}, 400
        finally:
            session.close()

    def delete_prospect_by_id(self, id):
        session = self.Session()
        try:
            prospect = session.query(Prospect).filter_by(id=id).first()
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

    def get_notes_by_prospection_id(self, prospection_id):
        session = self.Session()
        try:
            notes = session.query(Note).filter_by(id_prospection=prospection_id).all()
            if not notes:
                return {"message": "No notes found for this prospection"}, 404

            return [note.to_dict() for note in notes], 200
        except Exception as e:
            logging.error(f"Error retrieving notes: {e}")
            return {"message": f"Error retrieving notes: {str(e)}"}, 500
        finally:
            session.close()

    def get_emails_by_prospection_id(self, prospection_id):
        session = self.Session()
        try:
            emails = session.query(Email).filter_by(id_prospection=prospection_id).all()
            if not emails:
                return {"message": "No emails found for this prospection"}, 404

            return [email.to_dict() for email in emails], 200
        except Exception as e:
            logging.error(f"Error retrieving emails: {e}")
            return {"message": f"Error retrieving emails: {str(e)}"}, 500
        finally:
            session.close()

    def get_sales_advisor_by_prospection_id(self, prospection_id):
        session = self.Session()
        try:
            prospection = session.query(ProspectionSalesAdvisor).filter_by(id_prospection=prospection_id).first()
            if not prospection:
                return {"message": "No sales advisor found for this prospection"}, 404

            return prospection.sales_advisor.to_dict(), 200
        except Exception as e:
            logging.error(f"Error retrieving sales advisor: {e}")
            return {"message": f"Error retrieving sales advisor: {str(e)}"}, 500
        finally:
            session.close()
