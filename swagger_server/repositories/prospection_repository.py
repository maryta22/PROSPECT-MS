import logging
from datetime import datetime

from flask import jsonify
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine
from swagger_server.database_models.models import Prospection, Prospect, AcademicProgram, StateProspection, \
    StateProspectionProspection, Note, ProspectionSalesAdvisor, Email, SalesAdvisor, User
from dotenv import load_dotenv
import os

load_dotenv()

class ProspectionRepository:
    def __init__(self):
        db_password = os.getenv('DB_PASSWORD')
        self.engine = create_engine(f'mysql+pymysql://root:{db_password}@localhost:3306/espae_prospections')
        self.Session = sessionmaker(bind=self.engine)

    def get_notes_by_prospection_id(self, prospection_id):
        session = self.Session()
        try:
            notes = session.query(Note).filter_by(id_prospection=prospection_id).all()
            if not notes:
                return {"message": "No se encontraron notas para esta prospección"}, 404

            return [note.to_dict() for note in notes], 200
        except Exception as e:
            logging.error(f"Error al recuperar las notas: {e}")
            return {"message": f"Error al recuperar las notas: {str(e)}"}, 500
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
            return {"message": f"Error al guardar la nota: {str(e)}"}, 500
        finally:
            session.close()

    def create_prospection(self, prospection_data):
        session = self.Session()
        try:
            # Validar si ya existe una prospección activa para el prospecto y programa académico específico
            existing_prospection = session.query(Prospection).join(StateProspectionProspection).filter(
                Prospection.id_prospect == prospection_data["prospect_id"],
                Prospection.id_academic_program == prospection_data["academic_program_id"],
                StateProspectionProspection.id_state_prospection.notin_([4, 7]),  # Excluir estados específicos
                StateProspectionProspection.state == 1,  # Estado activo
            ).first()
            if existing_prospection:
                return {
                    "message": "Ya existe una prospección activa con este programa académico."
                }, 400

            # Crear la nueva prospección
            new_prospection = Prospection(
                id_prospect=prospection_data["prospect_id"],
                id_academic_program=prospection_data.get("academic_program_id"),
                date=prospection_data.get("date", datetime.now()),
                state=prospection_data.get("state", 1),
                channel=prospection_data.get("channel", "web prospecciones")
            )
            session.add(new_prospection)
            session.flush()

            # Crear el estado inicial de la prospección
            initial_state = StateProspectionProspection(
                id_prospection=new_prospection.id,
                id_state_prospection=1,  # Estado inicial
                date=datetime.now(),
                state=1
            )
            session.add(initial_state)
            print("prospeccion creada")


            # Si se proporciona un ID de vendedor, asociarlo a la prospección
            sales_advisor_id = prospection_data.get("sales_advisor_id")
            if sales_advisor_id:
                prospection_sales_advisor = ProspectionSalesAdvisor(
                    id_prospection=new_prospection.id,
                    id_sales_advisor=sales_advisor_id,
                    state=1,  # Estado activo
                    date=datetime.now()
                )
                session.add(prospection_sales_advisor)

            # Confirmar los cambios
            session.commit()

            return {
                "message": "Prospección creada exitosamente.",
                "id": new_prospection.id
            }, 201
        except Exception as e:
            session.rollback()
            logging.error(f"Error creando la prospección: {e}")
            return {"message": f"Error creando la prospección: {str(e)}"}, 400
        finally:
            session.close()

    def get_all_prospections(self):
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
                StateProspection.id.label("prospection_state_id"),
            ).join(Prospect, Prospection.id_prospect == Prospect.id
                   ).join(AcademicProgram, Prospection.id_academic_program == AcademicProgram.id
                          ).outerjoin(
                StateProspectionProspection,
                StateProspectionProspection.id_prospection == Prospection.id
            ).outerjoin(
                StateProspection,
                StateProspectionProspection.id_state_prospection == StateProspection.id
            ).filter(StateProspectionProspection.state == 1
                     ).all()

            result = [
                {
                    "id": row.id,
                    "prospect_id": row.prospect_id,
                    "cedula": row.cedula,
                    "company": row.company,
                    "state": row.state,
                    "date": row.date.strftime('%Y-%m-%d %H:%M:%S') if row.date else None,
                    "program": row.program,
                    "channel": row.channel,
                    "prospection_state": row.prospection_state,
                    "prospection_state_id": row.prospection_state_id,
                }
                for row in prospections
            ]
            return result, 200
        except Exception as e:
            logging.error(f"Error retrieving prospections for table: {e}")
            return {"message": f"Error retrieving data: {str(e)}"}, 500
        finally:
            session.close()

    def get_prospections_by_prospect_id(self, prospect_id):
        session = self.Session()
        try:
            prospections = session.query(
                Prospection.id.label("id"),
                Prospection.date.label("date"),
                Prospection.state.label("state"),
                Prospection.channel.label("channel"),
                AcademicProgram.name.label("program"),
                Prospect.id.label("prospect_id"),
                Prospect.company.label("company"),
                Prospect.id_number.label("cedula"),
                StateProspection.description.label("prospection_state"),  # Estado del prospecto
                StateProspection.id.label("prospection_state_id"),
                SalesAdvisor.id.label("sales_advisor_id"),
            ).join(
                Prospect, Prospection.id_prospect == Prospect.id
            ).outerjoin(
                AcademicProgram, Prospection.id_academic_program == AcademicProgram.id
            ).outerjoin(
                StateProspectionProspection, StateProspectionProspection.id_prospection == Prospection.id
            ).outerjoin(
                StateProspection, StateProspectionProspection.id_state_prospection == StateProspection.id
            ).outerjoin(
                ProspectionSalesAdvisor, Prospection.id == ProspectionSalesAdvisor.id_prospection
            ).outerjoin(
                SalesAdvisor, ProspectionSalesAdvisor.id_sales_advisor == SalesAdvisor.id
            ).filter(
                Prospection.id_prospect == prospect_id,
                StateProspectionProspection.state == 1,
                ProspectionSalesAdvisor.state == 1
            ).distinct(
                Prospection.id
            ).all()

            if not prospections:
                return {"message": "No se encontraron prospecciones para este prospecto"}, 404

            result = [
                {
                    "id": row.id,
                    "date": row.date.strftime('%Y-%m-%d %H:%M:%S') if row.date else None,
                    "state": row.state,
                    "channel": row.channel,
                    "program": row.program,
                    "prospect_id": row.prospect_id,
                    "company": row.company,
                    "cedula": row.cedula,
                    "prospection_state": row.prospection_state,  # Añadir el estado del prospecto
                    "sales_advisor_id": row.sales_advisor_id,  # Añadir el ID del vendedor
                    "prospection_state_id": row.prospection_state_id,
                }
                for row in prospections
            ]
            return result, 200
        except Exception as e:
            logging.error(f"Error al recuperar las prospecciones para el prospecto {prospect_id}: {e}")
            return {"message": f"Error al recuperar las prospecciones: {str(e)}"}, 500
        finally:
            session.close()

    def get_prospection_history_with_logs(self, prospection_id):
        session = self.Session()
        try:
            vendedor_historial = session.query(
                ProspectionSalesAdvisor.date.label("date"),
                SalesAdvisor.id.label("vendedor_id"),
                User.first_name.label("vendedor_first_name"),
                User.last_name.label("vendedor_last_name"),
                ProspectionSalesAdvisor.state.label("state")
            ).join(SalesAdvisor, ProspectionSalesAdvisor.id_sales_advisor == SalesAdvisor.id
                   ).join(User, SalesAdvisor.id_user == User.id
                          ).filter(ProspectionSalesAdvisor.id_prospection == prospection_id).all()

            estado_historial = session.query(
                StateProspectionProspection.date.label("date"),
                StateProspection.description.label("state_description"),
                StateProspectionProspection.state.label("state")
            ).join(StateProspection, StateProspectionProspection.id_state_prospection == StateProspection.id
                   ).filter(StateProspectionProspection.id_prospection == prospection_id).all()

            notas = session.query(
                Note.date.label("date"),
                Note.message.label("message"),
                Note.id.label("note_id")
            ).filter(Note.id_prospection == prospection_id).all()

            historial = []

            for vendedor in vendedor_historial:
                log = (
                    f"Asignado a {vendedor.vendedor_first_name} {vendedor.vendedor_last_name} "
                )
                historial.append({
                    "type": "vendedor",
                    "date": vendedor.date.strftime('%Y-%m-%d %H:%M:%S') if vendedor.date else None,
                    "log": log,
                    "details": {
                        "vendedor_id": vendedor.vendedor_id,
                        "vendedor_name": f"{vendedor.vendedor_first_name} {vendedor.vendedor_last_name}",
                        "state": vendedor.state
                    }
                })

            for estado in estado_historial:
                log = (
                    f"Estado cambiado a '{estado.state_description}'."
                )
                historial.append({
                    "type": "estado",
                    "date": estado.date.strftime('%Y-%m-%d %H:%M:%S') if estado.date else None,
                    "log": log,
                    "details": {
                        "state_description": estado.state_description,
                        "state": estado.state
                    }
                })

            for nota in notas:
                log = f"{nota.message}"
                historial.append({
                    "type": "nota",
                    "date": nota.date.strftime('%Y-%m-%d %H:%M:%S') if nota.date else None,
                    "log": log,
                    "details": {
                        "note_id": nota.note_id,
                        "message": nota.message
                    }
                })

            historial.sort(key=lambda x: x["date"] or "", reverse=True)

            return historial, 200
        except Exception as e:
            logging.error(f"Error al recuperar el historial de la prospección {prospection_id}: {e}")
            return {"message": f"Error al recuperar el historial: {str(e)}"}, 500
        finally:
            session.close()


    def get_state_prospections(self):
        session = self.Session()
        try:
            states = session.query(StateProspection).all()
            return [state.to_dict() for state in states], 200
        except Exception as e:
            logging.error(f"Error al recuperar el estado de las prospecciones: {e}")
            return {"message": f"Error al recuperar el estado de las prospecciones: {str(e)}"}, 500
        finally:
            session.close()

    def update_prospection_state(self, prospection_id, data):
        session = self.Session()
        try:
            new_state_id = data["new_state_id"]
            session.query(StateProspectionProspection).filter_by(
                id_prospection=prospection_id, state=1
            ).update({"state": 0})

            new_state = StateProspectionProspection(
                id_prospection=prospection_id,
                id_state_prospection=new_state_id,
                date=datetime.now(),
                state=1
            )
            session.add(new_state)
            session.commit()

            return {"message": "Estado de gestión actualizado exitosamente."}, 200
        except Exception as e:
            session.rollback()
            logging.error(f"Error al actualizar el estado de gestión: {e}")
            return {"message": f"Error al actualizar el estado de gestión: {str(e)}"}, 500
        finally:
            session.close()

    def update_prospection(self, id_, prospection_data):
        session = self.Session()
        try:
            prospection = session.query(Prospection).filter_by(id=id_).first()
            if not prospection:
                return {"message": "Prospección no encontrada"}, 404

            for key, value in prospection_data.items():
                if hasattr(prospection, key):
                    setattr(prospection, key, value)

            session.commit()
            return {"message": "Prospección actualizada exitosamente."}, 200
        except Exception as e:
            session.rollback()
            logging.error(f"Error al actualizar la prospección: {e}")
            return {"message": f"Error al actualizar la prospección: {str(e)}"}, 400
        finally:
            session.close()

    def get_emails_by_prospection_id(self, prospection_id):
        session = self.Session()
        try:
            emails = session.query(Email).filter_by(id_prospection=prospection_id).all()
            if not emails:
                return {"message": "No se encontraron correos para esta prospección"}, 404

            return [email.to_dict() for email in emails], 200
        except Exception as e:
            logging.error(f"Error al recuperar los correos: {e}")
            return {"message": f"Error al recuperar los correos: {str(e)}"}, 500
        finally:
            session.close()

    def get_sales_advisor_by_prospection_id(self, prospection_id):
        session = self.Session()
        try:
            prospection = session.query(ProspectionSalesAdvisor).filter_by(id_prospection=prospection_id).first()
            if not prospection:
                return {"message": "No se encontró un asesor de ventas para esta prospección"}, 404

            return prospection.sales_advisor.to_dict(), 200
        except Exception as e:
            logging.error(f"Error al recuperar el asesor de ventas: {e}")
            return {"message": f"Error al recuperar el asesor de ventas: {str(e)}"}, 500
        finally:
            session.close()

    def get_prospections_by_sales_advisor(self, sales_advisor_id):
        session = self.Session()
        try:
            # Consultar las prospecciones asociadas al asesor de ventas
            prospections = session.query(
                Prospection.id.label("id"),
                Prospect.id.label("prospect_id"),
                Prospect.id_number.label("cedula"),
                Prospect.company.label("company"),
                Prospection.state.label("state"),
                Prospection.date.label("date"),
                AcademicProgram.name.label("program"),
                Prospection.channel.label("channel"),
                SalesAdvisor.id.label("sales_advisor_id"),
                StateProspection.description.label("prospection_state"),
                StateProspection.id.label("prospection_state_id"),
                User.first_name.label("first_name"),
                User.last_name.label("last_name"),
            ).distinct().join(
                ProspectionSalesAdvisor, Prospection.id == ProspectionSalesAdvisor.id_prospection
            ).join(
                SalesAdvisor, ProspectionSalesAdvisor.id_sales_advisor == SalesAdvisor.id
            ).join(
                Prospect, Prospection.id_prospect == Prospect.id
            ).join(
                User, Prospect.id_user == User.id
            ).join(
                AcademicProgram, Prospection.id_academic_program == AcademicProgram.id
            ).outerjoin(
                StateProspectionProspection, StateProspectionProspection.id_prospection == Prospection.id
            ).outerjoin(
                StateProspection, StateProspectionProspection.id_state_prospection == StateProspection.id
            ).filter(
                SalesAdvisor.id == sales_advisor_id,
                ProspectionSalesAdvisor.state == 1,
                StateProspectionProspection.state == 1
            ).all()

            if not prospections:
                return {"message": "No se encontraron prospecciones para este asesor de ventas."}, 404

            # Formatear los resultados
            result = [
                {
                    "id": row.id,
                    "prospect_id": row.prospect_id,
                    "cedula": row.cedula,
                    "company": row.company,
                    "state": row.state,
                    "date": row.date.strftime('%Y-%m-%d %H:%M:%S') if row.date else None,
                    "program": row.program,
                    "channel": row.channel,
                    "prospection_state": row.prospection_state,
                    "prospection_state_id": row.prospection_state_id,
                    "prospect_name": f"{row.first_name} {row.last_name}"  # Nombre completo
                }
                for row in prospections
            ]

            return result, 200
        except Exception as e:
            logging.error(f"Error al recuperar las prospecciones para el asesor de ventas {sales_advisor_id}: {e}")
            return {"message": f"Error al recuperar los datos: {str(e)}"}, 500
        finally:
            session.close()

