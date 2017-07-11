import asyncio
import networkx as nx
from distalg.process import Process
from distalg.channel import Channel


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
                self.node_map[process_n] = n
            else:
                process_n = self.process_map[n]

            for neighbor, edge_attr in neighbors_dict.items():
                if neighbor not in self.process_map:
                    process_nbr = process_type()
                    self.process_map[neighbor] = process_nbr
                    self.node_map[process_nbr] = neighbor
                else:
                    process_nbr = self.process_map[neighbor]

                channel = channel_type()
                channel.__in_end = process_n
                channel.__out_end = process_nbr
                self.channel_map[(n, neighbor)] = channel
                if (neighbor, n) in self.channel_map:
                    rev_channel = self.channel_map[(neighbor, n)]
                    channel.__back = rev_channel
                    rev_channel.__back = channel

                process_n.out_channels.append(channel)
                process_nbr.in_channels.append(channel)

    async def start_all(self):
        await asyncio.wait([process.start() for process in self.node_map])

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start_all())
        pass
