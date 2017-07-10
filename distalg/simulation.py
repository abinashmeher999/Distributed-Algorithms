import networkx as nx
from process import Process
from channel import Channel


class Simulation:
    def __init__(self, embedding_graph=None, process_type=Process, channel_type=Channel):

        self.graph = nx.freeze(embedding_graph)

        self.process_map = {}
        self.node_map = {}
        self.channel_map = {}

        for n, neighbors_dict in self.graph.adjacency_iter():
            if n not in self.process_map:
                self.process_map[n] = process_type()
                self.node_map[self.process_map[n].id] = n

            for neighbor, edge_attr in neighbors_dict.items():
                if neighbor not in self.process_map:
                    self.process_map[neighbor] = process_type()
                    self.node_map[self.process_map[neighbor].id] = neighbor

                channel = channel_type()
                self.channel_map[(n, neighbor)] = channel
                self.process_map[n].out_channel.append(channel)
                self.process_map[neighbor].in_channel.append(channel)

    def run(self):
        # starts the simulation
        pass
