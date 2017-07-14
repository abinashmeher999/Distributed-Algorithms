#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import pytest

import networkx as nx
from distalg import Process, Channel, Simulation, Message, dispatch, job, only_after
import logging

logging.basicConfig(level=logging.DEBUG)

__author__ = "Abinash Meher"
__copyright__ = "Abinash Meher"
__license__ = "mit"


def test_simulation():
    graph = nx.path_graph(5)
    sm = Simulation(embedding_graph=graph, process_type=Process, channel_type=Channel)
    sm.run()


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

    @job
    async def start(self):
        self.log.debug(self.id + " started.")
        if self.is_initiator:
            await asyncio.wait([channel.send(EchoToken(self.id)) for channel in self.out_channels])

    @only_after(start)
    @dispatch(EchoToken, Channel)
    async def on_receive(self, msg, channel):
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


def test_echo():
    graph = nx.hypercube_graph(4)  # 4 dimensional
    sm = Simulation(embedding_graph=graph, process_type=EchoProcess, channel_type=Channel)
    for a in sm.node_map:
        a.is_initiator = True
        break

    sm.run()
    assert 0
