import shortuuid
from multipledispatch import dispatch
from distalg.message import Message
from distalg.channel import UnreliableDelayedChannel


class Process(object):
    def __init__(self, pid=None):
        self._id = pid or shortuuid.uuid()
        self.in_channels = []
        self.out_channels = []

    async def start(self):
        pass

    @dispatch(Message, UnreliableDelayedChannel)
    async def on_receive(self, msg, channel):
        pass

    @property
    def id(self):
        return str(self._id)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
