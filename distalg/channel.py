import asyncio
import random


class UnreliableDelayedChannel:
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
        :param delay_std_dev: variation in delay for a message to reach fro in end to out end
        :param min_delay: guarantee that the delay won't be less than this value
        :param max_delay: guarantee that the delay won't be more than this value
        :param reliability: The reliability with which a message is delivered. [0.0, 1.0]
        """
        self._in_end = None  # The process sending messages into the channel
        self._out_end = None  # The process receiving messages from the channel
        self.delay_mean = delay_mean
        self.delay_std_dev = delay_std_dev
        self.in_transit = set()
        self.reached = set()
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.reliability = reliability
        self._back = None  # The channel that is the opposite direction of this channel

    @property
    def in_end(self):
        return self._in_end

    @property
    def out_end(self):
        return self._out_end

    @property
    def back(self):
        return self._back

    async def __deliver(self, message, process):
        """
        :param message: The Message object to be delivered
        :return:
        """
        sample = random.random()  # generates [0.0, 1.0)
        if sample >= self.reliability:
            return
        self.in_transit.add(message)
        # delay time in milliseconds
        delay_time = random.gauss(self.delay_mean, self.delay_std_dev)
        clamped_delay_time = min(self.max_delay, max(self.min_delay, delay_time))
        asyncio.sleep(clamped_delay_time / 1000)  # asyncio.sleep expects in seconds
        self.in_transit.remove(message)
        await process.on_receive(message, self)

    async def send(self, message):
        await self.__deliver(message, self.out_end)


class DelayedChannel(UnreliableDelayedChannel):
    def __init__(self, delay_mean=100, delay_std_dev=10, min_delay=1, max_delay=500):
        super(DelayedChannel, self).__init__(
            delay_mean=delay_mean,
            delay_std_dev=delay_std_dev,
            min_delay=min_delay,
            max_delay=max_delay,
            reliability=1.0
        )


class UnreliableChannel(UnreliableDelayedChannel):
    def __init__(self, reliability=0.9):
        super(UnreliableChannel, self).__init__(
            delay_mean=0,
            delay_std_dev=0,
            min_delay=0,
            max_delay=0,
            reliability=reliability
        )


class Channel(UnreliableDelayedChannel):
    def __init__(self):
        super(Channel, self).__init__(0, 0, 0, 0, reliability=1.0)

    async def __deliver(self, message, process):
        await process.on_receive(message, self)


class UnreliableDelayedFIFOChannel(UnreliableDelayedChannel):
    def __init__(self, *args, **kwargs):
        super(UnreliableDelayedFIFOChannel, self).__init__(*args, **kwargs)

    def __deliver(self, message, process):
        raise NotImplementedError
