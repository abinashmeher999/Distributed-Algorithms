#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import time

from distalg.skeleton import fib
import networkx as nx
from distalg import Process, Channel, Simulation, Message, dispatch
import logging

logging.basicConfig(level=logging.DEBUG)

__author__ = "Abinash Meher"
__copyright__ = "Abinash Meher"
__license__ = "mit"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)


def test_simulation():
    graph = nx.path_graph(5)
    sm = Simulation(embedding_graph=graph, process_type=Process, channel_type=Channel)
    sm.run()


class EchoToken(Message):
    def __init__(self, value):
        super(EchoToken, self).__init__(value=value)


class EchoProcess(Process):
    def __init__(self):
        super(EchoProcess, self).__init__()
        self.father = None
        self.rec_p = 0
        self.is_initiator = False
        self.log = logging.getLogger('echo')

    def start(self):
        self.log.debug(self.id, 'started')
        if self.is_initiator:
            for channel in self.out_channels:
                channel.send(EchoToken(self.id))

    @dispatch(EchoToken, Channel)
    def on_receive(self, msg, channel):
        if self.is_initiator:
            if self.rec_p == len(self.in_channels):
                self.log.debug('Process:', self.id, ':', msg.value)
            else:
                self.rec_p += 1
        else:
            if self.father is None:
                self.father = channel.back
                for ch in [ch for ch in self.out_channels if not self.father]:
                    ch.send(EchoToken(msg.value))
            if self.rec_p == len(self.out_channels):
                self.log.debug('Process:', self.id, ':', msg.value)
                self.father.send(EchoToken(msg.value))
            else:
                self.rec_p += 1


def test_echo():
    graph = nx.hypercube_graph(4)  # 4 dimensional
    sm = Simulation(embedding_graph=graph, process_type=Process, channel_type=Channel)
    for a in sm.node_map:
        a.is_initiator = True
        break
    sm.run()
    time.sleep(10)
