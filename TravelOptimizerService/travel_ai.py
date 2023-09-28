import networkx as nx
import pandas as pd
import pickle


class TrainTravelAI:
    def __init__(self):
        self.routes_df = pd.DataFrame()
        self.trips_df = pd.DataFrame()
        self.stop_times_df = pd.DataFrame()
        self.stops_df = pd.DataFrame()
        self.graph = nx.Graph()

    def read_data_from_files(self):
        self.routes_df = pd.read_csv("./datas/data_sncf/routes.txt")
        self.trips_df = pd.read_csv("./datas/data_sncf/trips.txt")
        self.stop_times_df = pd.read_csv("./datas/data_sncf/stop_times.txt")
        self.stops_df = pd.read_csv("./datas/data_sncf/stops.txt")

    def build_graph(self):
        print("build_graph")
        for index, row in self.stops_df.iterrows():
            self.graph.add_node(row["stop_id"], stop_name=row["stop_name"])

        for index, row in self.stop_times_df.iterrows():
            from_stop = row["stop_id"]
            to_stop = self.stop_times_df.iloc[index + 1]["stop_id"] if index + 1 < len(self.stop_times_df) else None
            if to_stop:
                try:
                    travel_time = (pd.to_datetime(row["departure_time"]) - pd.to_datetime(row["arrival_time"])).total_seconds()
                    self.graph.add_edge(from_stop, to_stop, weight=travel_time)
                except:
                    continue

    def find_fastest_route(self, start_stop, end_stop):
        print("find_fastest_route")
        best_path = None
        best_travel_time = float('inf')

        try:
            for path in nx.all_simple_paths(self.graph, source=start_stop, target=end_stop):
                print(path)
                travel_time = self.calculate_travel_time(self.graph, path)

                if travel_time < best_travel_time:
                    best_path = path
                    best_travel_time = travel_time

            return best_path
        except:
            print("No path found between the start and end stops.")

    def calculate_travel_time(graph, path):
        travel_time = 0
        for i in range(len(path) - 1):
            from_stop = path[i]
            to_stop = path[i + 1]
            edge_data = graph[from_stop][to_stop]
            travel_time += edge_data['weight']

        return travel_time

    def save_graph(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.graph, file)

    def load_graph(self, filename):
        with open(filename, 'rb') as file:
            self.graph = pickle.load(file)
