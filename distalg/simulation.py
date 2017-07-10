import networkx as nx
from copy import deepcopy
from process import Process
from channel import Channel
from action import Action


class Simulation:
    def __init__(self, embedding_graph=nx.Graph):
        if isinstance(embedding_graph, type):
            embedding_graph = embedding_graph()  # readable and dry alternative for object as default arg

        self.graph = nx.Graph()
        process_map ={}
        for node in embedding_graph.nodes_iter():
            if node not in process_map:
                process_map[node] = Process()
                self.graph.add_node(process_map[node])

        for edge in embedding_graph.edges_iter():
            u, v = edge
            self.graph.add_edge(process_map[u], process_map[v], object=Channel())

    def run(self):
        # starts the simulation
        pass
