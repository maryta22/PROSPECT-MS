import datetime
import logging
from datetime import datetime

from flask import jsonify
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine
from swagger_server.database_models.models import Prospection, Prospect, AcademicProgram, SalesAdvisor, StateProspection, StateProspectionProspection, ProspectionSalesAdvisor, User, Note
from dotenv import load_dotenv
import os

from ..services.automatic_reasig import AutomaticReasig

from sqlalchemy.orm import aliased

load_dotenv()

class ProspectionRepository:
    def __init__(self):
        db_password = os.getenv('DB_PASSWORD')
        self.engine = create_engine(f'mysql+pymysql://root:{db_password}@localhost:3306/espae_prospections')
        self.Session = sessionmaker(bind=self.engine)

    def get_all_prospections(self):
        session = self.Session()
        try:
            # Crea alias para la tabla User
            prospect_user_alias = aliased(User)  # Para los prospectos
            sales_advisor_user_alias = aliased(User)  # Para los asesores
    
            prospections = session.query(
                Prospection.id.label("id"),
                Prospect.id.label("prospect_id"),
                Prospect.id_number.label("cedula"),
                Prospect.company.label("company"),
                Prospection.state.label("state"),
                Prospection.date.label("date"),
                AcademicProgram.name.label("program"),
                Prospection.channel.label("channel"),
                StateProspection.description.label("prospection_state"),  # Estado de gestión actual
                # Prospect user info
                prospect_user_alias.first_name.label("prospect_first_name"),
                prospect_user_alias.last_name.label("prospect_last_name"),
                # Sales advisor user info
                SalesAdvisor.id.label("sales_advisor_id"),
                sales_advisor_user_alias.first_name.label("sales_advisor_first_name"),
                sales_advisor_user_alias.last_name.label("sales_advisor_last_name")
            ).join(
                Prospect, Prospection.id_prospect == Prospect.id
            ).join(
                AcademicProgram, Prospection.id_academic_program == AcademicProgram.id
            ).outerjoin(
                StateProspectionProspection,
                StateProspectionProspection.id_prospection == Prospection.id
            ).outerjoin(
                StateProspection,
                StateProspectionProspection.id_state_prospection == StateProspection.id
            ).outerjoin(
                ProspectionSalesAdvisor,
                ProspectionSalesAdvisor.id_prospection == Prospection.id
            ).outerjoin(
                SalesAdvisor,
                SalesAdvisor.id == ProspectionSalesAdvisor.id_sales_advisor
            ).outerjoin(
                prospect_user_alias, Prospect.id_user == prospect_user_alias.id  # Prospect -> User
            ).outerjoin(
                sales_advisor_user_alias, SalesAdvisor.id_user == sales_advisor_user_alias.id  # Sales Advisor -> User
            ).filter(
                StateProspectionProspection.state == 1
            ).all()
    
            result = [
                {
                    "id": row.id,
                    "prospect_id": row.prospect_id,
                    "cedula": row.cedula,
                    "company": row.company,
                    "state": row.state,
                    "date": row.date.strftime('%Y-%m-%d') if row.date else None,
                    "program": row.program,
                    "channel": row.channel,
                    "prospection_state": row.prospection_state,
                    # Prospect user name
                    "prospect_name": f"{row.prospect_first_name} {row.prospect_last_name}" if row.prospect_first_name and row.prospect_last_name else None,
                    # Sales advisor user name
                    "sales_advisor": f"{row.sales_advisor_first_name} {row.sales_advisor_last_name}" if row.sales_advisor_first_name and row.sales_advisor_last_name else None
                }
                for row in prospections
            ]
            print(result)
            print("antes de la prueba")
            prueba = AutomaticReasig().get_sales_advisor_with_least_prospections(1)
            print(prueba)
            return result, 200
        except Exception as e:
            logging.error(f"Error retrieving prospections for admin: {e}")
            return {"message": f"Error retrieving prospections: {str(e)}"}, 500
        finally:
            session.close()

    def create_prospection(self, prospection_data):
        session = self.Session()
        try:
            new_prospection = Prospection(
                id_prospect=prospection_data["prospect_id"],
                id_academic_program=prospection_data.get("academic_program_id"),
                date=prospection_data.get("date", datetime.now()),
                state=prospection_data.get("state", 1),
                channel=prospection_data.get("channel", "web prospecciones")
            )
            session.add(new_prospection)
            session.flush()

            initial_state = StateProspectionProspection(
                id_prospection=new_prospection.id,
                id_state_prospection=1,
                date=datetime.now(),
                state=1
            )
            session.add(initial_state)

            session.commit()

            return {
                "message": "Prospection created successfully.",
                "id": new_prospection.id
            }, 201
        except Exception as e:
            session.rollback()
            logging.error(f"Error creating prospection: {e}")
            return {"message": f"Error creating prospection: {str(e)}"}, 400
        finally:
            session.close()

    def create_prospection_sales_advisor(self, prospection_id, sales_advisor_id):
        session = self.Session()
        try:
            new_association = ProspectionSalesAdvisor(
                id_prospection=prospection_id,
                id_sales_advisor=sales_advisor_id,
                state=1,  # Estado activo
                date=datetime.now()
            )
            session.add(new_association)
            session.commit()

            return new_association.to_dict(), 201
        except Exception as e:
            session.rollback()
            logging.error(f"Error creating prospection-sales advisor association: {e}")
            return {"message": f"Error creating association: {str(e)}"}, 500
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

    def save_note(self, body):
        session = self.Session()
        try:
            new_note = Note(
                id_prospection=body["prospection_id"],
                message=body["message"],
                date= datetime.now()
            )

            session.add(new_note)
            session.commit()

            return new_note.to_dict(), 201
        except Exception as e:
            logging.error(f"Error saving note: {e}")
            session.rollback()
            return {"message": f"Error saving note: {str(e)}"}, 500
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