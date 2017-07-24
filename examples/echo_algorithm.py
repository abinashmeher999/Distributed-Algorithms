from distalg import Process, DelayedChannel, Message, Simulation, dispatch, main
import networkx as nx
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)


class EchoToken(Message):
    def __init__(self, value):
        super(EchoToken, self).__init__(value=value)


class EchoProcess(Process):
    def __init__(self, pid=None):
        super(EchoProcess, self).__init__(pid=pid)
        self.father = None
        self.rec_p = 0
        self.is_initiator = False
        self.log = logging.getLogger('echo')

    async def run(self):
        self.log.debug(self.id + " started.")
        if self.is_initiator:
            await asyncio.wait([channel.send(EchoToken(self.id)) for channel in self.out_channels])
        await self.process_messages()

    @dispatch(EchoToken)
    async def on_receive(self, msg):
        channel = msg.carrier
        self.rec_p += 1
        if self.is_initiator:
            if self.rec_p == len(self.in_channels):
                self.log.debug('Process: ' + self.id + ' : ' + msg.value)
        else:
            if self.father is None:
                self.father = channel.back
                await asyncio.wait([ch.send(EchoToken(msg.value)) for ch in self.out_channels if ch is not self.father])
            if self.rec_p == len(self.in_channels):
                self.log.debug('Process: ' + self.id + ' : ' + msg.value)
                await self.father.send(EchoToken(msg.value))


class TerminatingEchoProcess(Process):
    def __init__(self, pid=None):
        super(TerminatingEchoProcess, self).__init__(pid=pid)
        self.father = None
        self.rec_p = 0
        self.is_initiator = False
        self.log = logging.getLogger('echo')

    @main
    async def run(self):
        self.log.debug(self.id + " started.")
        if self.is_initiator:
            await asyncio.wait([channel.send(EchoToken(self.id)) for channel in self.out_channels])
            last_val = None
            while self.rec_p < len(self.in_channels):
                msg = await self.receive_a_msg()
                self.rec_p += 1
                last_val = msg.value
            self.log.debug('Process: ' + self.id + ' : ' + last_val)  # Decide Operation
        else:
            last_val = None
            while self.rec_p < len(self.in_channels):
                msg = await self.receive_a_msg()
                channel = msg.carrier
                self.rec_p += 1
                if self.father is None:
                    self.father = channel.back
                    await asyncio.wait(
                        [ch.send(EchoToken(msg.value)) for ch in self.out_channels if ch is not self.father])
                last_val = msg.value
            self.log.debug('Process: ' + self.id + ' : ' + last_val)  # Decide Operation
            await self.father.send(EchoToken(last_val))
        return


def test_echo():
    graph = nx.hypercube_graph(4)  # 4 dimensional
    sm = Simulation(embedding_graph=graph, process_type=TerminatingEchoProcess, channel_type=DelayedChannel)
    for a in sm.node_map:
        a.is_initiator = True
        break

    sm.run(quit_after=4.0)

if __name__ == '__main__':
    test_echo()
