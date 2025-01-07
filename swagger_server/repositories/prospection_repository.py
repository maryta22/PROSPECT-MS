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
            return result, 200
        except Exception as e:
            logging.error(f"Error retrieving prospections for admin: {e}")
            return {"message": f"Error retrieving prospections: {str(e)}"}, 500
        finally:
            session.close()

    def create_prospection(self, prospection_data):
        session = self.Session()
        try:
            # Obtener el vendedor con el menor número de prospecciones para el programa seleccionado
            program_id = prospection_data.get("program")
            if not program_id or program_id=="None":
                return {"message": "Academic program ID is required."}, 400

            sales_advisor_id = AutomaticReasig().get_sales_advisor_with_least_prospections(program_id)
            print(sales_advisor_id)
            if not sales_advisor_id:
                return {"message": "No sales advisor found for the selected program."}, 404

            # Crear la nueva prospección
            print("creando nuevo prospeccion con id: ",prospection_data.get("prospect"))
            if not prospection_data.get("prospect"):
                return {"message": "Prospect ID is required."}, 400

            if not program_id or program_id=="None":
                return {"message": "Academic program ID is required."}, 400

            new_prospection = Prospection(
                id_prospect=prospection_data.get("prospect"),  # Asegúrate de que el prospect_id se esté utilizando correctamente
                id_academic_program=program_id,
                date=prospection_data.get("date", datetime.now()),
                state=prospection_data.get("state", 1),
                channel=prospection_data.get("channel", "web prospecciones")
            )
            session.add(new_prospection)
            session.flush()

            print("New prospection ID: ", new_prospection.id)
            print("Sales advisor ID: ", sales_advisor_id)
            print("pondré en la tabla de prospeciton sales advisor..")
            # Asignar la prospección al vendedor obtenido
            new_prospection_sales_advisor = ProspectionSalesAdvisor(
                id_prospection=new_prospection.id,
                id_sales_advisor=sales_advisor_id,
                state=1,  # Estado activo
                date=datetime.now()
            )
            session.add(new_prospection_sales_advisor)
            print("prospection sales advisor añadido!")

            print("Ahora veré initial state...")
            # Crear el estado inicial de la prospección
            initial_state = StateProspectionProspection(
                id_prospection=new_prospection.id,
                id_state_prospection=1,
                date=datetime.now(),
                state=1
            )
            session.add(initial_state)
            print("initial state añadido!")
            session.commit()
            print("commiteado!")

            print(
                "query ---- obtener datos completos de la prospeccion recien creada!"
            )
            # Obtener los datos completos de la prospección recién creada
            complete_prospection = session.query(
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
                SalesAdvisor.id.label("sales_advisor_id"),
                User.first_name.label("sales_advisor_first_name"),
                User.last_name.label("sales_advisor_last_name")
            ).join(Prospect, Prospection.id_prospect == Prospect.id
                   ).join(AcademicProgram, Prospection.id_academic_program == AcademicProgram.id
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
                User,
                User.id == SalesAdvisor.id_user
            ).filter(Prospection.id == new_prospection.id).first()
            print("fin de la query: ", complete_prospection)

            result = {
                "id": complete_prospection.id,
                "prospect_id": complete_prospection.prospect_id,
                "cedula": complete_prospection.cedula,
                "company": complete_prospection.company,
                "state": complete_prospection.state,
                "date": complete_prospection.date.strftime('%Y-%m-%d') if complete_prospection.date else None,
                "program": complete_prospection.program,
                "channel": complete_prospection.channel,
                "prospection_state": complete_prospection.prospection_state,
                "prospect_name": f"{complete_prospection.prospect_first_name} {complete_prospection.prospect_last_name}" if complete_prospection.prospect_first_name and complete_prospection.prospect_last_name else None,
                "sales_advisor": f"{complete_prospection.sales_advisor_first_name} {complete_prospection.sales_advisor_last_name}" if complete_prospection.sales_advisor_first_name and complete_prospection.sales_advisor_last_name else None
            }
            return result, 201
        except Exception as e:
            session.rollback()
            logging.error(f"Error creating prospection: {e} holap")
            return {"message": f"Error creating prospection: {str(e)}"}, 500
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