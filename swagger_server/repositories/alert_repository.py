import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from swagger_server.database_models.models import Alert
from dotenv import load_dotenv
import os

load_dotenv()

class AlertRepository:
    def __init__(self):
        db_password = os.getenv('DB_PASSWORD')
        self.engine = create_engine(f'mysql+pymysql://root:{db_password}@localhost:3306/espae_prospections')
        self.Session = sessionmaker(bind=self.engine)

    def get_alert_days(self, alert_id):
        """
        Get the `days` value for a specific alert.
        """
        session = self.Session()
        try:
            alert = session.query(Alert).filter_by(id=alert_id).first()
            if not alert:
                return {"message": "Alerta no encontrada."}, 404

            return {"days": alert.days}, 200
        except Exception as e:
            logging.error(f"Error al obtener los días de la alerta: {e}")
            return {"message": f"Error al obtener los datos: {str(e)}"}, 500
        finally:
            session.close()

    def update_alert_days(self, alert_id, data):
        """
        Update the `days` value for a specific alert.
        """
        session = self.Session()
        try:
            new_days = data.get("days")
            if new_days is None or not isinstance(new_days, int):
                return {"message": "El valor de 'days' debe ser un entero."}, 400

            alert = session.query(Alert).filter_by(id=alert_id).first()
            if not alert:
                return {"message": "Alerta no encontrada."}, 404

            alert.days = new_days
            session.commit()

            return {"message": "El campo 'days' fue actualizado exitosamente."}, 200
        except Exception as e:
            logging.error(f"Error al actualizar los días de la alerta: {e}")
            session.rollback()
            return {"message": f"Error al actualizar los datos: {str(e)}"}, 500
        finally:
            session.close()
