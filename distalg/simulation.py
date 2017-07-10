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
                process_n = process_type()
                self.process_map[n] = process_n
                self.node_map[process_n.id] = n
            else:
                process_n = self.process_map[n]

            for neighbor, edge_attr in neighbors_dict.items():
                if neighbor not in self.process_map:
                    process_nbr = process_type()
                    self.process_map[neighbor] = process_nbr
                    self.node_map[process_nbr.id] = neighbor
                else:
                    process_nbr = self.process_map[neighbor]

                channel = channel_type(
                    {process_n},
                    {process_nbr}
                )
                self.channel_map[(n, neighbor)] = channel
                process_n.out_channel.append(channel)
                process_nbr.in_channel.append(channel)

    def run(self):
        # starts the simulation
        pass
