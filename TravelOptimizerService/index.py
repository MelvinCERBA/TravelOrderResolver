from flask import Flask, request, jsonify
from waitress import serve

from travel_ai import TrainTravelAI

app = Flask(__name__)

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


@app.route('/fastest_route', methods=['GET', 'POST'])
def fastest_route():
    body = request.get_json(request.data)
    result = ai.find_fastest_route(body['start_stop'], body['end_stop'])
    return jsonify({"fastest_route": result})


if __name__ == "__main__":
    serve(app, port=8081)
