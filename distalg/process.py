import asyncio
import shortuuid
from multipledispatch import dispatch
from distalg.message import Message
from distalg.channel import UnreliableDelayedChannel
from functools import wraps


class job(object):
    def __init__(self, func):
        self.event = asyncio.Event()
        self.func = func

    async def __call__(self, *args, **kwargs):
        await self.func(*args, **kwargs)
        self.event.set()

@dispatch(job)
def only_after(job_obj):
    def wrap(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            await job_obj.event.wait()
            return await func(*args, **kwargs)
        return wrapper
    return wrap

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
