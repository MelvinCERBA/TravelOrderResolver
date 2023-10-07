from flask import Flask, request, jsonify
import logging, os
from logging.handlers import RotatingFileHandler
from travel_ai import TrainTravelAI

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

    return app

app = create_app()

ai = TrainTravelAI()

graph_filename = 'travel_graph.pkl'
try:
    ai.load_graph(graph_filename)
except FileNotFoundError:
    ai.read_data_from_files()
    ai.build_graph()
    ai.save_graph(graph_filename)


@app.route("/")
def hello_world():
    return "<p>Hello from TravelOptimizerService !</p>"

@app.route('/fastest_route_mock', methods=['GET', 'POST'])
def fastest_route_mock():
    body = request.get_json(request.data)
    
    app.logger.info(f'body : {str(body)}')

    result  = [
        f"{body['origin']} --> Paris",
        f"Paris --> {body['destination']}"
    ]

    app.logger.info(f'Computed mock travel plan : {str(result)}')

    return jsonify({"fastest_route": result}), 200

@app.route('/fastest_route', methods=['GET', 'POST'])
def fastest_route():
    body = request.get_json(request.data)

    app.logger.info(f'body : {str(body)}')

    result  = ai.find_fastest_route(body['start_stop'], body['end_stop'])

    app.logger.info(f'Computed travel plan : {str(result)}')

    return jsonify({"fastest_route": result}), 200


# if __name__ == "__main__": # We serve the application using gunicorn
#     serve(app, port=8081)
