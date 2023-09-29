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
        self.trip_data = {}
        self.stations_links = {}
        self.route_long_names = {}

    def read_data_from_files(self):
        self.routes_df = pd.read_csv("./datas/data_sncf/routes.txt")
        self.trips_df = pd.read_csv("./datas/data_sncf/trips.txt")
        self.stop_times_df = pd.read_csv("./datas/data_sncf/stop_times.txt")
        self.stops_df = pd.read_csv("./datas/data_sncf/stops.txt")

    def build_graph(self):
        print("build_graph")
        for _, row in self.stops_df.iterrows():
            self.graph.add_node(row['stop_id'], name=row['stop_name'], parent_station=(row['parent_station']), trip_id=[])

        for id, row in self.stops_df.iterrows():
            print(id)
            stop_id = row['stop_id']
            if stop_id.startswith('StopPoint:'):
                trips = list(self.stop_times_df.loc[self.stop_times_df['stop_id'] == stop_id]['trip_id'])
                self.stations_links[row['parent_station']] = {
                    'trip_ids': trips
                }

        for _, row in self.trips_df.iterrows():
            self.trip_data[row['trip_id']] = {
                'route_id': row['route_id']
            }

        for id, row in self.stop_times_df.iterrows():
            print(id)
            trip_id = row['trip_id']
            stop_id = row['stop_id']

            self.graph.nodes[stop_id]['trip_id'].append(trip_id)

            if trip_id in self.trip_data:
                route_id = self.trip_data[trip_id]['route_id']
                self.graph.add_edge(row['stop_id'], route_id)

        for _, row in self.routes_df.iterrows():
            self.route_long_names[row['route_id']] = row['route_long_name']

        nx.set_node_attributes(self.graph, self.route_long_names, name='route_long_name')

        print("end_graph")

    def find_fastest_route(self, start_stop, end_stop):
        print("find_fastest_route")
        print(self.graph.nodes[start_stop])
        print(self.graph.nodes[end_stop])
        try:
            if start_stop not in self.graph:
                print(f"Source node '{start_stop}' not found in the graph.")
            elif end_stop not in self.graph:
                print(f"Target node '{end_stop}' not found in the graph.")
            else:
                fastest_path = nx.shortest_path(self.graph, source=start_stop, target=end_stop)
                print("Fastest Path:", fastest_path)
                return fastest_path
        except nx.NetworkXNoPath:
            return None

    def save_graph(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.graph, file)

    def load_graph(self, filename):
        with open(filename, 'rb') as file:
            self.graph = pickle.load(file)
