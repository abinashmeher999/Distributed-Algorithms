#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from distalg.skeleton import fib
import networkx as nx
from distalg.process import Process
from distalg.channel import Channel
from distalg.simulation import Simulation

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
