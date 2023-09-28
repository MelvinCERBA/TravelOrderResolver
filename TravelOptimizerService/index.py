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


@app.route('/fastest_route', methods=['GET'])
def fastest_route():
    # source_station_name = request.args.get('source')
    # destination_station_name = request.args.get('destination')
    #
    # source_station = ai.get_station_id_by_name(source_station_name)
    # destination_station = ai.get_station_id_by_name(destination_station_name)

    print("fastest_route")
    result = ai.find_fastest_route("StopPoint:OCETrain TER-87317115", "StopPoint:OCETrain TER-87575480")
    print(result)
    return jsonify({"fastest_route": result})


if __name__ == "__main__":
    serve(app, port=8081)
