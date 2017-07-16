import asyncio
import shortuuid
from multipledispatch import dispatch
from distalg.message import Message


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

    async def process_messages(self):
        async for msg in self.receive_msgs():
            await self.on_receive(msg)

    async def run(self):
        raise NotImplementedError

    @dispatch(Message)
    async def on_receive(self, msg):
        raise NotImplementedError

    @property
    def id(self):
        return str(self._id)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
