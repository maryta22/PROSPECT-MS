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
        #db_password = os.getenv('DB_PASSWORD')
        #self.engine = create_engine(f'mysql+pymysql://root:{db_password}@localhost:3306/espae_prospections')
        self.engine = create_engine('mysql+pymysql://root:root@localhost:3306/espae_prospections')
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
            new_user = User(**user_data)
            session.add(new_user)
            session.flush()

            prospect_data["id_user"] = new_user.id
            prospect_data["creation_date"] = datetime.now()  # Agregar la fecha y hora actual
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

    def update_prospection(self, id_, prospection_data):
        session = self.Session()
        try:
            prospection = session.query(Prospection).filter_by(id=id_).first()
            if not prospection:
                return {"message": "Prospection not found"}, 404

            for key, value in prospection_data.items():
                if hasattr(prospection, key):
                    setattr(prospection, key, value)

            session.commit()
            return {"message": "Prospection updated successfully."}, 200
        except Exception as e:
            session.rollback()
            logging.error(f"Error updating prospection: {e}")
            return {"message": f"Error updating prospection: {str(e)}"}, 400
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
                StateProspection.description.label("prospection_state")  # Estado de gestión actual
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
                    "date": row.date.strftime('%Y-%m-%d') if row.date else None,
                    "program": row.program,
                    "channel": row.channel,
                    "prospection_state": row.prospection_state
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
            # Realizar la consulta para obtener las prospecciones y el estado del prospecto
            prospections = session.query(
                Prospection.id.label("id"),
                Prospection.date.label("date"),
                Prospection.state.label("state"),
                Prospection.channel.label("channel"),
                AcademicProgram.name.label("program"),
                Prospect.id.label("prospect_id"),
                Prospect.company.label("company"),
                Prospect.id_number.label("cedula"),
                StateProspection.description.label("prospection_state")  # Estado del prospecto
            ).join(
                Prospect, Prospection.id_prospect == Prospect.id
            ).outerjoin(
                AcademicProgram, Prospection.id_academic_program == AcademicProgram.id
            ).outerjoin(
                StateProspectionProspection, StateProspectionProspection.id_prospection == Prospection.id
            ).outerjoin(
                StateProspection, StateProspectionProspection.id_state_prospection == StateProspection.id
            ).filter(
                Prospection.id_prospect == prospect_id,
                StateProspectionProspection.state == 1  # Asegurarse de obtener el estado activo
            ).all()

            # Si no se encuentran resultados
            if not prospections:
                return {"message": "No prospections found for this prospect."}, 404

            # Formatear la respuesta con los datos necesarios
            result = [
                {
                    "id": row.id,
                    "date": row.date.strftime('%Y-%m-%d') if row.date else None,
                    "state": row.state,
                    "channel": row.channel,
                    "program": row.program,
                    "prospect_id": row.prospect_id,
                    "company": row.company,
                    "cedula": row.cedula,
                    "prospection_state": row.prospection_state  # Añadir el estado del prospecto
                }
                for row in prospections
            ]
            return result, 200
        except Exception as e:
            logging.error(f"Error retrieving prospections for prospect {prospect_id}: {e}")
            return {"message": f"Error retrieving prospections: {str(e)}"}, 500
        finally:
            session.close()

    def get_prospection_history_with_logs(self, prospection_id):
        session = self.Session()
        try:
            # Obtener historial de vendedores
            vendedor_historial = session.query(
                ProspectionSalesAdvisor.date.label("date"),
                SalesAdvisor.id.label("vendedor_id"),
                User.first_name.label("vendedor_first_name"),
                User.last_name.label("vendedor_last_name"),
                ProspectionSalesAdvisor.state.label("state")
            ).join(SalesAdvisor, ProspectionSalesAdvisor.id_sales_advisor == SalesAdvisor.id
                   ).join(User, SalesAdvisor.id_user == User.id
                          ).filter(ProspectionSalesAdvisor.id_prospection == prospection_id).all()

            # Obtener historial de estados
            estado_historial = session.query(
                StateProspectionProspection.date.label("date"),
                StateProspection.description.label("state_description"),
                StateProspectionProspection.state.label("state")
            ).join(StateProspection, StateProspectionProspection.id_state_prospection == StateProspection.id
                   ).filter(StateProspectionProspection.id_prospection == prospection_id).all()

            # Obtener notas
            notas = session.query(
                Note.date.label("date"),
                Note.message.label("message"),
                Note.id.label("note_id")
            ).filter(Note.id_prospection == prospection_id).all()

            # Construir el historial
            historial = []

            for vendedor in vendedor_historial:
                log = (
                    f"Vendedor asignado a {vendedor.vendedor_first_name} {vendedor.vendedor_last_name} "
                    f"con estado {'activo' if vendedor.state else 'inactivo'}."
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
                    f"Estado de prospección cambiado a '{estado.state_description}'."
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
                log = f"Nota añadida: '{nota.message}'."
                historial.append({
                    "type": "nota",
                    "date": nota.date.strftime('%Y-%m-%d %H:%M:%S') if nota.date else None,
                    "log": log,
                    "details": {
                        "note_id": nota.note_id,
                        "message": nota.message
                    }
                })

            # Ordenar el historial por fecha, de más reciente a más antiguo
            historial.sort(key=lambda x: x["date"], reverse=True)

            return historial, 200
        except Exception as e:
            logging.error(f"Error retrieving history for prospection {prospection_id}: {e}")
            return {"message": f"Error retrieving history: {str(e)}"}, 500
        finally:
            session.close()

    def get_state_prospections(self):
        session = self.Session()
        try:
            states = session.query(StateProspection).all()
            return [state.to_dict() for state in states], 200
        except Exception as e:
            logging.error(f"Error retrieving state prospections: {e}")
            return {"message": f"Error retrieving state prospections: {str(e)}"}, 500
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

            return {"message": "Gestion state updated successfully."}, 200
        except Exception as e:
            session.rollback()
            logging.error(f"Error updating gestion state: {e}")
            return {"message": f"Error updating gestion state: {str(e)}"}, 500
        finally:
            session.close()

    def create_prospection(self, prospection_data):
        session = self.Session()
        try:
            # Validar si ya existe una prospección para el prospecto y programa académico específico
            existing_prospection = session.query(Prospection).join(StateProspectionProspection).filter(
                Prospection.id_prospect == prospection_data["prospect_id"],
                Prospection.id_academic_program == prospection_data["academic_program_id"],
                StateProspectionProspection.id_state_prospection != 4,
                StateProspectionProspection.id_state_prospection != 5,
                StateProspectionProspection.state == 1,
            ).first()

            if existing_prospection:
                return {
                    "message": "Ya existe una prospección activa con este programa académico."
                }, 400

            # Crear nueva prospección
            new_prospection = Prospection(
                id_prospect=prospection_data["prospect_id"],
                id_academic_program=prospection_data.get("academic_program_id"),
                date=prospection_data.get("date", datetime.now()),
                state=prospection_data.get("state", 1),
                channel=prospection_data.get("channel", "web prospecciones")
            )
            session.add(new_prospection)
            session.flush()

            # Agregar estado inicial
            initial_state = StateProspectionProspection(
                id_prospection=new_prospection.id,
                id_state_prospection=1,
                date=datetime.now(),
                state=1
            )
            session.add(initial_state)

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

    def get_all_cities(self):
        session = self.Session()
        try:
            # Consulta todas las ciudades
            cities = session.query(City).all()
            # Convierte las ciudades a diccionarios
            return [city.to_dict() for city in cities], 200
        except Exception as e:
            # Manejo de errores
            logging.error(f"Error retrieving cities: {e}")
            return {"message": f"Error retrieving cities: {str(e)}"}, 500
        finally:
            # Cierra la sesión
            session.close()