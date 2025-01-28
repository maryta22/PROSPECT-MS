#!/usr/bin/env python3
import connexion
from connexion import FlaskApp
from connexion.resolver import MethodViewResolver
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from swagger_server import encoder
from swagger_server.services.alert import process_and_send_alerts


def create_app():
    app = FlaskApp(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    CORS(app.app, resources={r"/*": {"origins": "*"}})
    app.add_api('swagger.yaml',
                arguments={'title': 'PROSPECTS-MS'},
                pythonic_params=True,
                resolver=MethodViewResolver('swagger_server.controllers'))
    return app


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(process_and_send_alerts, 'cron', hour=15, minute=13)
    scheduler.start()
    print("Programador de tareas iniciado. La tarea se ejecutará todos los días a las 8:00 AM.")


# Main
if __name__ == '__main__':
    app = create_app()
    start_scheduler()
    app.run(port=2034)
else:
    app = create_app().app