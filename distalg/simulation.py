import asyncio
import networkx as nx
from distalg.process import Process
from distalg.channel import Channel


class Simulation:
    def __init__(self, embedding_graph=None, process_type=Process, channel_type=Channel, timeout=10.0):

        self.graph = nx.Graph(embedding_graph)
        self.timeout = timeout
        self.process_map = {}
        self.node_map = {}
        self.channel_map = {}
        self.edge_map = {}
        self.tasks = []

        for n, neighbors_dict in self.graph.adjacency_iter():
            if n not in self.process_map:
                process_n = process_type(n)
                self.process_map[n] = process_n
                self.graph.node[n]['process'] = process_n
                self.node_map[process_n] = n
            else:
                process_n = self.process_map[n]

            for neighbor, edge_attr in neighbors_dict.items():
                if neighbor not in self.process_map:
                    process_nbr = process_type(neighbor)
                    self.process_map[neighbor] = process_nbr
                    self.graph.node[neighbor]['process'] = process_nbr
                    self.node_map[process_nbr] = neighbor
                else:
                    process_nbr = self.process_map[neighbor]

                channel = channel_type()
                channel._in_end = process_n
                channel._out_end = process_nbr

                self.channel_map[(n, neighbor)] = channel
                self.edge_map[channel] = (n, neighbor)
                if (neighbor, n) in self.channel_map:
                    rev_channel = self.channel_map[(neighbor, n)]
                    channel._back = rev_channel
                    rev_channel._back = channel

                process_n.out_channels.append(channel)
                process_nbr.in_channels.append(channel)

    async def start_all(self):
        self.tasks += [asyncio.ensure_future(process.run()) for process in self.node_map] \
                      + [asyncio.ensure_future(channel.start()) for channel in self.edge_map]
        await asyncio.wait(self.tasks)

    def stop_all(self):
        for task in self.tasks:
            task.cancel()

    def processes_iter(self):
        yield from self.node_map  # node map is a dict process: node, this iterates over all the keys i.e. processes

    def run(self):
        try:
            loop = asyncio.get_event_loop()
            loop.call_later(self.timeout, self.stop_all)
            loop.run_until_complete(self.start_all())
        except RuntimeError:
            pass
