import networkx as nx
import pandas as pd

# Load CSV data into DataFrames
routes_df = pd.read_csv("./datas/data_sncf/routes.txt")
trips_df = pd.read_csv("./datas/data_sncf/trips.txt")
stop_times_df = pd.read_csv("./datas/data_sncf/stop_times.txt")
stops_df = pd.read_csv("./datas/data_sncf/stops.txt")

# Create a directed graph
G = nx.DiGraph()

# Add stops as nodes to the graph
for index, row in stops_df.iterrows():
    print(index)
    G.add_node(row["stop_id"], stop_name=row["stop_name"])

# Add connections between stops as directed edges with travel times as weights
for index, row in stop_times_df.iterrows():
    print(index)
    from_stop = row["stop_id"]
    to_stop = stop_times_df.iloc[index + 1]["stop_id"] if index + 1 < len(stop_times_df) else None
    if to_stop:
        try:
            travel_time = (pd.to_datetime(row["departure_time"]) - pd.to_datetime(row["arrival_time"])).total_seconds()
            G.add_edge(from_stop, to_stop, weight=travel_time)
        except:
            continue

# Find the fastest path using Dijkstra's algorithm
start_stop = "StopArea:OCE87411017"
end_stop = "StopPoint:OCETrain TER-87295667"

try:
    shortest_path = nx.shortest_path(G, source=start_stop, target=end_stop, weight="weight")
    print("Fastest Path:", shortest_path)
except nx.NetworkXNoPath:
    print("No path found between the start and end stops.")