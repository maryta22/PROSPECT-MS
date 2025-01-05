import logging
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine
from swagger_server.database_models.models import Prospection, Prospect, AcademicProgram, SalesAdvisor, StateProspection, StateProspectionProspection, ProspectionSalesAdvisor, User
from dotenv import load_dotenv
import os

load_dotenv()

class ProspectionRepository:
    def __init__(self):
        pass_sam = os.getenv('DB_PASSWORD')
        self.engine = create_engine(f'mysql+pymysql://root:{pass_sam}@localhost:3306/espae_prospections')
        self.Session = sessionmaker(bind=self.engine)

    def get_all_prospections(self):
        session = self.Session()
        try:
            prospections = session.query(
                Prospection.id.label("id"),
                Prospection.prospect_id.label("prospect_id"),
                Prospect.id_number.label("cedula"),
                Prospect.company.label("company"),
                Prospection.state.label("state"),
                Prospection._date.label("date"),
                AcademicProgram.name.label("program"),
                Prospection.channel.label("channel"),
                StateProspection.description.label("prospection_state")
            ).join(Prospect, Prospection.prospect_id == Prospect.id
            ).join(AcademicProgram, Prospection.program == AcademicProgram.id
            ).outerjoin(
                StateProspectionProspection,
                StateProspectionProspection.id_prospection == Prospection.id
            ).outerjoin(
                StateProspection,
                StateProspectionProspection.id_state_prospection == StateProspection.id
            ).filter(StateProspectionProspection.state == 1).all()

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
                    "prospection_state": row.prospection_state
                }
                for row in prospections
            ]
            return result, 200
        except Exception as e:
            logging.error(f"Error retrieving prospections: {e}")
            return {"message": f"Error retrieving prospections: {str(e)}"}, 500
        finally:
            session.close()


    def get_all_prospections_admin(self):
        session = self.Session()
        try:
            prospections = session.query(
                Prospection.id.label("id"),
                Prospect.id.label("prospect_id"),
                Prospect.id_number.label("cedula"),
                Prospect.company.label("company"),
                Prospection.state.label("state"),
                Prospection.date.label("date"),
                AcademicProgram.name.label("program"),
                Prospection.channel.label("channel"),
                StateProspection.description.label("prospection_state"),
                User.first_name.label("prospect_first_name"),
                User.last_name.label("prospect_last_name"),
                User.first_name.label("vendedor_first_name"),
                User.last_name.label("vendedor_last_name")
            ).join(Prospect, Prospection.id_prospect == Prospect.id
                   ).join(AcademicProgram, Prospection.id_academic_program == AcademicProgram.id
                          ).outerjoin(
                StateProspectionProspection,
                StateProspectionProspection.id_prospection == Prospection.id
            ).outerjoin(
                StateProspection,
                StateProspectionProspection.id_state_prospections == StateProspection.id
            ).outerjoin(
                ProspectionSalesAdvisor,
                ProspectionSalesAdvisor.id_prospection == Prospection.id
            ).outerjoin(
                SalesAdvisor,
                SalesAdvisor.id == ProspectionSalesAdvisor.id_sales_advisor
            ).outerjoin(
                User,
                User.id == SalesAdvisor.id_user
            ).filter(StateProspectionProspection.state == 1
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
                    "prospect_name": f"{row.prospect_first_name} {row.prospect_last_name}",
                    "vendedor": f"{row.vendedor_first_name} {row.vendedor_last_name}" if row.vendedor_first_name and row.vendedor_last_name else None
                }
                for row in prospections
            ]
            return result, 200
        except Exception as e:
            logging.error(f"Error retrieving prospections: {e}")
            return {"message": f"Error retrieving prospections: {str(e)}"}, 500
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