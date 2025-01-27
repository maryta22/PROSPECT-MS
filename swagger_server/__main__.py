#!/usr/bin/env python3

from connexion import FlaskApp
from flask_cors import CORS
from swagger_server import encoder

def create_app():
    app = FlaskApp(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    CORS(app.app, resources={r"/*": {"origins": "*"}})
    app.add_api('swagger.yaml', arguments={'title': 'PROSPECTS-MS'}, pythonic_params=True)
    return app

app = create_app().app

def main():
    app.run(port=2034)

if __name__ == '__main__':
    main()
