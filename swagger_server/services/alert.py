import logging
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import requests  # Para hacer solicitudes HTTP
from swagger_server.database_models.models import Alert, AlertStateProspection, SalesAdvisor, \
    StateProspectionProspection

load_dotenv()


def process_and_send_alerts():
    """
    Procesa las prospecciones de los vendedores activos y envía alertas si cumplen las condiciones.
    """
    db_password = os.getenv('DB_PASSWORD')
    engine = create_engine(f'mysql+pymysql://root:{db_password}@localhost:3306/espae_prospections')
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print("Procesando alertas...")
        alerts = session.query(Alert).filter_by(state=1).all()
        alert_state_prospections = session.query(AlertStateProspection).filter_by(state=1).all()

        alert_state_map = {
            alert_state.id_state_prospection: alert.days
            for alert_state in alert_state_prospections
            for alert in alerts if alert.id == alert_state.id_alert
        }

        sellers = session.query(SalesAdvisor).filter_by(state=1).all()

        for seller in sellers:
            pending_prospections = []

            for relation in seller.prospections:
                if relation.state != 1:
                    continue

                prospection = relation.prospection

                if prospection.state != 1:
                    continue

                state_prospections = session.query(StateProspectionProspection).filter_by(
                    id_prospection=prospection.id, state=1
                ).all()

                for state_prospection in state_prospections:
                    if state_prospection.id_state_prospection in alert_state_map:
                        alert_days = alert_state_map[state_prospection.id_state_prospection]

                        date_compare = datetime.now() - timedelta(days=alert_days)
                        if prospection.date.date() == date_compare.date():
                            prospect_name = f"{prospection.prospect.user.first_name} {prospection.prospect.user.last_name}"
                            pending_prospections.append(prospect_name)

            if pending_prospections:
                seller_email = seller.user.email
                prospect_list = ", ".join(pending_prospections)  # Convertir nombres a un string
                endpoint_url = "http://127.0.0.1:2043/send/individual"  # Endpoint del servicio
                payload = {
                    "to_email": seller_email,
                    "to_name": seller.user.first_name,
                    "message": f"Hola {seller.user.first_name}, tienes las siguientes prospecciones pendientes: {prospect_list}",
                    "sender_email": "maria.mariaog.rivera@gmail.com",
                    "sender_name": "Sistema de Prospecciones",
                    "subject": "Alertas de Prospecciones Pendientes"
                }

                try:
                    response = requests.post(endpoint_url, json=payload)
                    if response.status_code == 200:
                        print(f"Correo enviado exitosamente a {seller_email}")
                    else:
                        print(f"Error al enviar correo a {seller_email}: {response.text}")
                except Exception as e:
                    print(f"Error al realizar la solicitud HTTP: {e}")
    except Exception as e:
        logging.error(f"Error al procesar alertas: {e}")
    finally:
        session.close()
