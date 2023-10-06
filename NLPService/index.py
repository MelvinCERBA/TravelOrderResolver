from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from app.api.interpret_travel_order import InterpretTravelOrder
import os
import logging
from logging.handlers import RotatingFileHandler
from app.middlewares import init_middlewares

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.DefaultConfig')

    # Get env's config
    env = os.environ.get('FLASK_ENV') 
    if env == "production":
        app.config.from_object('config.ProductionConfig')
    elif env == "development":
        app.config.from_object('config.DevelopmentConfig')
    elif env == "testing":
        app.config.from_object('config.TestingConfig')
    else:
        raise Exception(f"Unknown environment '{env}'")
    
    # Logging
    app.logger.setLevel(app.config['LOG_LEVEL'])
    if not app.debug: # For production logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Startup')

    # Routes
    api = Api(app) 
    api.add_resource(InterpretTravelOrder, '/travelOrder')

    # Middlewares
    init_middlewares(app)
        
    return app

app = create_app()