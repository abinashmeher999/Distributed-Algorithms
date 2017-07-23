import asyncio
from collections import OrderedDict

import shortuuid
from multipledispatch import dispatch
from distalg.message import Message

import wrapt


@wrapt.decorator
async def main(wrapped, instance, args, kwargs):
    await wrapped(*args, **kwargs)
    await asyncio.wait([channel.close() for channel in instance.out_channels])


class Process(object):
    class ReceiverAsyncIterable:
        def __init__(self, outer_instance):
            self.outer = outer_instance

        def __aiter__(self):
            return self

        async def __anext__(self):
            return await self.outer.incoming_msgs.get()

    def _receive_msgs_creator(self):
        def _receive_msgs():
            return Process.ReceiverAsyncIterable(self)

        return _receive_msgs

    def __init__(self, pid=None):
        self._id = pid or shortuuid.uuid()
        self.in_channels = []
        self.out_channels = []
        self.incoming_msgs = asyncio.Queue()
        self.receive_msgs = self._receive_msgs_creator()
        self.state = {}
        self._parent_state = None
        self.subroutines = OrderedDict()

    async def process_messages(self):
        async for msg in self.receive_msgs():
            await self.on_receive(msg)

    async def run(self):
        raise NotImplementedError

    @dispatch(Message)
    async def on_receive(self, msg):
        pass

    @property
    def id(self):
        return str(self._id)

    @property
    def parent_state(self):
        return self._parent_state

    def add_subroutine(self, name, process_instance):
        """
        :param name: The name of the subroutine eg: "echo1", "echo2",...
        :param process_instance: An instance of the Process class or its subclass with method `run`
        :return: None
        """
        process_instance.in_channels = self.in_channels
        process_instance.out_channels = self.out_channels
        process_instance._parent_state = self.state
        self.subroutines[name] = process_instance

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
