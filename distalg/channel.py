import asyncio
import random
from distalg.message import Message
from multipledispatch import dispatch


class UnreliableDelayedChannel:
    class TerminateToken(Message):
        """
        A special kind of message which when sent into a channel
        breaks/terminates the channel
        """
        def __init__(self):
            super(UnreliableDelayedChannel.TerminateToken, self).__init__()

    class PoppedMsgsAsyncIterable:
        def __init__(self, outer_instance):
            self.outer = outer_instance

        def __aiter__(self):
            return self

        async def __anext__(self):
            return await self.outer.started.get()

    def obtain_msgs(self):
        return UnreliableDelayedChannel.PoppedMsgsAsyncIterable(self)

    def __init__(self,
                 delay_mean=100,
                 delay_std_dev=10,
                 min_delay=1,
                 max_delay=500,
                 reliability=0.9):
        """
        Every message sent into the channel is sent individually to all the receiving processes.
        All units are in milliseconds
        :param delay_mean: mean delay for a message to reach from in end to out end
        :param delay_std_dev: variation in delay for a message to reach from in end to out end
        :param min_delay: guarantee that the delay won't be less than this value
        :param max_delay: guarantee that the delay won't be more than this value
        :param reliability: The reliability with which a message is delivered. [0.0, 1.0]
        """
        self._in_end = None  # The process sending messages into the channel
        self._out_end = None  # The process receiving messages from the channel
        self.delay_mean = delay_mean
        self.delay_std_dev = delay_std_dev
        self.started = asyncio.Queue()
        self.in_transit = set()
        self.reached = set()
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.reliability = reliability
        self._back = None  # The channel that is the opposite direction of this channel

    @property
    def in_end(self):
        """
        :return: The Process that is sending messages into the channel
        """
        return self._in_end

    @property
    def out_end(self):
        """
        :return: The Process that is receiving messages from the channel
        """
        return self._out_end

    @property
    def back(self):
        """
        :return: The channel that connects the participating processes in the reverse direction
        """
        return self._back

    async def __deliver(self, message):
        """
        :param message: The Message object to be delivered
        :return: None
        """
        sample = random.random()  # generates [0.0, 1.0)
        if sample >= self.reliability:
            return
        self.in_transit.add(message)

        # delay time in milliseconds
        delay_time = random.gauss(self.delay_mean, self.delay_std_dev)
        clamped_delay_time = min(self.max_delay, max(self.min_delay, delay_time))
        await asyncio.sleep(clamped_delay_time / 1000)  # asyncio.sleep expects in seconds

        self.in_transit.remove(message)
        await self._out_end.incoming_msgs.put(message)

    async def start(self):
        """
        The function needs to be called in the event loop for the channel to function.
        This function directs the channel to start conducting messages from the in_end to out_end.
        :return: None
        """
        async for msg in self.obtain_msgs():
            if isinstance(msg, UnreliableDelayedChannel.TerminateToken):
                return
            await self.__deliver(msg)

    async def send(self, message):
        """
        Submits the message to the channel to be delivered at the
        receiving end. May not be received at the other end if
        channel is unreliable.
        :param message: The message to be sent across the channel
        :return: None
        """
        message._channel = self
        await self.started.put(message)

    async def close(self):
        """
        The function closes the channel. All the pending messages before issuing this
        function will be delivered and then the channel will stop.
        This also means that all the messages submitted after issuing this
        command will not be delivered unless the channel is started again.
        :return: None
        """
        await self.started.put(UnreliableDelayedChannel.TerminateToken())


class DelayedChannel(UnreliableDelayedChannel):
    def __init__(self, delay_mean=100, delay_std_dev=10, min_delay=1, max_delay=500):
        """
        A kind of channel that is reliable but has a delay between when send is
        called and when the message reaches at the receiving end.
        :param delay_mean: (default 100 ms) The average delay in receiving a message
        :param delay_std_dev: (default 10 ms) The standard deviation in the
            normal distribution from which the actual delay is sampled
        :param min_delay: (default 1 ms) The minimum time message is going
            to take to reach the receiving end.
        :param max_delay: (default 500 ms) The maximum delay. Any message won't take
            longer than this to reach the receiving end.
        """
        super(DelayedChannel, self).__init__(
            delay_mean=delay_mean,
            delay_std_dev=delay_std_dev,
            min_delay=min_delay,
            max_delay=max_delay,
            reliability=1.0
        )


class UnreliableChannel(UnreliableDelayedChannel):
    def __init__(self, reliability=0.9):
        """
        A kind of channel that is instant with no delay but is unreliable.
        :param reliability: The probability with which the message will
            reach the receiving end and won't get lost midway
        """
        super(UnreliableChannel, self).__init__(
            delay_mean=0,
            delay_std_dev=0,
            min_delay=0,
            max_delay=0,
            reliability=reliability
        )


class Channel(DelayedChannel):
    def __init__(self):
        """
        A normal reliable channel with no transit delays.
        """
        super(Channel, self).__init__(0, 0, 0, 0)

    async def __deliver(self, message):
        await self._out_end.incoming_msgs.put(message)


class UnreliableDelayedFIFOChannel(UnreliableDelayedChannel):
    def __init__(self, *args, **kwargs):
        super(UnreliableDelayedFIFOChannel, self).__init__(*args, **kwargs)

    def __deliver(self, message):
        raise NotImplementedError
