#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import pytest

import networkx as nx
from distalg import Process, Simulation, Channel, Message, dispatch

__author__ = "Abinash Meher"
__copyright__ = "Abinash Meher"
__license__ = "mit"


def test_simulation():
    graph = nx.path_graph(5)
    sm = Simulation(embedding_graph=graph, process_type=Process, channel_type=Channel)
    sm.run()
