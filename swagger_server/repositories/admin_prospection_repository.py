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

class AdminProspectionRepository:
    def __init__(self):
        db_password = os.getenv('DB_PASSWORD')
        self.engine = create_engine(f'mysql+pymysql://root:{db_password}@localhost:3306/espae_prospections')
        self.Session = sessionmaker(bind=self.engine)

    def get_all_prospections(self):
        session = self.Session()
        try:
            # Crear alias para la tabla User
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
                StateProspectionProspection.state == 1,
                ProspectionSalesAdvisor.state == 1  # Solo considerar ProspectionSalesAdvisor con estado 1
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

            # Asignar la prospección al vendedor obtenido
            new_prospection_sales_advisor = ProspectionSalesAdvisor(
                id_prospection=new_prospection.id,
                id_sales_advisor=sales_advisor_id,
                state=1,  # Estado activo
                date=datetime.now()
            )
            session.add(new_prospection_sales_advisor)

            # Crear el estado inicial de la prospección
            initial_state = StateProspectionProspection(
                id_prospection=new_prospection.id,
                id_state_prospection=1,
                date=datetime.now(),
                state=1
            )
            session.add(initial_state)
            session.commit()

            data, status_code = self.get_prospection_by_id(new_prospection.id)
            return data, status_code
        
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

    def get_prospections_by_prospect_id(self, prospect_id):
        session = self.Session()
        try:
            # Crear alias para la tabla User
            prospect_user_alias = aliased(User)  # Para los prospectos
            sales_advisor_user_alias = aliased(User)  # Para los asesores

            prospections = session.query(
                Prospection.id.label("id"),
                Prospect.id.label("prospect_id"),
                Prospect.id_number.label("cedula"),
                Prospect.company.label("company"),
                Prospection.state.label("state"),
                Prospection.date.label("date"),
                AcademicProgram.id.label("program_id"),
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
                prospect_user_alias,
                prospect_user_alias.id == Prospect.id_user
            ).outerjoin(
                sales_advisor_user_alias,
                sales_advisor_user_alias.id == SalesAdvisor.id_user
            ).filter(
                Prospection.id_prospect == prospect_id,  # Asegúrate de filtrar por el ID del prospecto
                StateProspectionProspection.state == 1  # Asegúrate de obtener el estado activo
            ).distinct().all()  # Utilizar DISTINCT para evitar duplicados

            # Si no se encuentran resultados
            if not prospections:
                return {"message": "No prospections found for this prospect."}, 404

            # Formatear la respuesta con los datos necesarios
            result = [
                {
                    "id": row.id,
                    "prospect_id": row.prospect_id,
                    "cedula": row.cedula,
                    "company": row.company,
                    "state": row.state,
                    "date": row.date.strftime('%Y-%m-%d') if row.date else None,
                    "program_id": row.program_id,
                    "program": row.program,
                    "channel": row.channel,
                    "prospection_state": row.prospection_state,
                    "prospect_name": f"{row.prospect_first_name} {row.prospect_last_name}" if row.prospect_first_name and row.prospect_last_name else None,
                    "sales_advisor": f"{row.sales_advisor_first_name} {row.sales_advisor_last_name}" if row.sales_advisor_first_name and row.sales_advisor_last_name else None
                }
                for row in prospections
            ]
            return result, 200
        except Exception as e:
            logging.error(f"Error retrieving prospections for prospect {prospect_id}: {e}")
            return {"message": f"Error retrieving prospections: {str(e)}"}, 500
        finally:
            session.close()
    
    def get_prospection_by_id(self, prospection_id):
        session = self.Session()
        try:
            # Crear alias para la tabla User
            prospect_user_alias = aliased(User)  # Para los prospectos
            sales_advisor_user_alias = aliased(User)  # Para los asesores

            prospection = session.query(
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
                prospect_user_alias,
                prospect_user_alias.id == Prospect.id_user
            ).outerjoin(
                sales_advisor_user_alias,
                sales_advisor_user_alias.id == SalesAdvisor.id_user
            ).filter(Prospection.id == prospection_id).first()

            if not prospection:
                return {"message": "Prospection not found"}, 404

            result = {
                "id": prospection.id,
                "prospect_id": prospection.prospect_id,
                "cedula": prospection.cedula,
                "company": prospection.company,
                "state": prospection.state,
                "date": prospection.date.strftime('%Y-%m-%d') if prospection.date else None,
                "program": prospection.program,
                "channel": prospection.channel,
                "prospection_state": prospection.prospection_state,
                "prospect_name": f"{prospection.prospect_first_name} {prospection.prospect_last_name}" if prospection.prospect_first_name and prospection.prospect_last_name else None,
                "sales_advisor": f"{prospection.sales_advisor_first_name} {prospection.sales_advisor_last_name}" if prospection.sales_advisor_first_name and prospection.sales_advisor_last_name else None
            }
            return result, 200
        except Exception as e:
            logging.error(f"Error retrieving prospection by id: {e}")
            return {"message": f"Error retrieving prospection: {str(e)}"}, 500
        finally:
            session.close()

    def update_prospection_seller(self, prospection_id, new_sales_advisor_id):
        session = self.Session()
        try:
            # Obtener el registro actual del vendedor asignado a la prospección
            current_assignment = session.query(ProspectionSalesAdvisor).filter_by(
                id_prospection=prospection_id, state=1
            ).first()

            if new_sales_advisor_id == current_assignment.id_sales_advisor:
                return {"message": "The new sales advisor is the same as the current one"}, 400
            if not current_assignment:
                return {"message": "No active sales advisor found for this prospection"}, 404

            # Cambiar el estado del registro actual a 0
            current_assignment.state = 0
            session.add(current_assignment)

            # Agregar un nuevo registro con el nuevo vendedor asignado y el estado 1
            new_assignment = ProspectionSalesAdvisor(
                id_prospection=prospection_id,
                id_sales_advisor=new_sales_advisor_id,
                state=1,  # Estado activo
                date=datetime.now()
            )
            session.add(new_assignment)

            session.commit()
            return {"message": "Sales advisor updated successfully"}, 200
        except Exception as e:
            session.rollback()
            logging.error(f"Error updating sales advisor for prospection {prospection_id}: {e}")
            return {"message": f"Error updating sales advisor: {str(e)}"}, 500
        finally:
            session.close()

    def update_prospection(self, prospection_id, prospection_data):
        session = self.Session()
        try:
            #prospection_id = data.get("prospection_id")
            if not prospection_id:
                return {"message": "Prospection ID is required."}, 400

            #prospection_data = data.get("prospection_data")
            if not prospection_data:
                return {"message": "Prospection data is required."}, 400
            
            # Obtener la prospección existente por su ID
            prospection = session.query(Prospection).filter_by(id=prospection_id).first()
            if not prospection:
                return {"message": "Prospection not found"}, 404

            # Actualizar el programa si se proporciona
            if "program_id" in prospection_data:
                prospection.id_academic_program = prospection_data["program_id"]

            # Actualizar el vendedor asignado si se proporciona
            if "sales_advisor_id" in prospection_data:
                # Obtener el registro actual del vendedor asignado a la prospección
                current_assignment = session.query(ProspectionSalesAdvisor).filter_by(
                    id_prospection=prospection_id, state=1
                ).first()

                if current_assignment:
                    # Cambiar el estado del registro actual a 0
                    current_assignment.state = 0
                    session.add(current_assignment)

                # Agregar un nuevo registro con el nuevo vendedor asignado y el estado 1
                new_assignment = ProspectionSalesAdvisor(
                    id_prospection=prospection_id,
                    id_sales_advisor=prospection_data["sales_advisor_id"],
                    state=1,  # Estado activo
                    date=datetime.now()
                )
                session.add(new_assignment)

            # Guardar los cambios en la prospección
            session.commit()

            # Obtener los datos completos de la prospección actualizada
            updated_prospection = self.get_prospection_by_id(prospection_id)
            return updated_prospection, 200
        except Exception as e:
            session.rollback()
            logging.error(f"Error updating prospection {prospection_id}: {e}")
            return {"message": f"Error updating prospection: {str(e)}"}, 500
        finally:
            session.close()