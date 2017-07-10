import asyncio
import random


class UnreliableDelayedChannel:
    def __init__(self,
                 in_end=None,
                 out_end=None,
                 delay_mean=100,
                 delay_std_dev=10,
                 min_delay=1,
                 max_delay=500,
                 reliability=0.9):
        """
        :param in_end: The set of processes that are sending into the channel
        :param out_end: The set of processes that are receiving the messages from the channel
        Every message sent into the channel is sent individually to all the receiving processes.
        All units are in milliseconds
        :param delay_mean: mean delay for a message to reach from in end to out end
        :param delay_std_dev: variation in delay for a message to reach fro in end to out end
        :param min_delay: guarantee that the delay won't be less than this value
        :param max_delay: guarantee that the delay won't be more than this value
        :param reliability: The reliability with which a message is delivered. [0.0, 1.0]
        """
        self.in_end = in_end or set()
        self.out_end = out_end or set()
        self.delay_mean = delay_mean
        self.delay_std_dev = delay_std_dev
        self.in_transit = set()
        self.reached = set()
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.reliability = reliability

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
        process.on_receive(message)

    async def send(self, message):
        async for process in self.out_end:
            self.__deliver(message, process)


class DelayedChannel(UnreliableDelayedChannel):
    def __init__(self, in_end=None, out_end=None, delay_mean=100, delay_std_dev=10, min_delay=1, max_delay=500):
        super(DelayedChannel, self).__init__(
            in_end=in_end,
            out_end=out_end,
            delay_mean=delay_mean,
            delay_std_dev=delay_std_dev,
            min_delay=min_delay,
            max_delay=max_delay,
            reliability=1.0
        )


class UnreliableChannel(UnreliableDelayedChannel):
    def __init__(self, in_end=None, out_end=None, reliability=0.9):
        super(UnreliableChannel, self).__init__(
            in_end=in_end,
            out_end=out_end,
            delay_mean=0,
            delay_std_dev=0,
            min_delay=0,
            max_delay=0,
            reliability=reliability
        )


class Channel(UnreliableDelayedChannel):
    def __init__(self, in_end=None, out_end=None):
        super(Channel, self).__init__(in_end, out_end, 0, 0, 0, 0, reliability=1.0)

    async def __deliver(self, message, process):
        process.on_receive(message)


class UnreliableDelayedFIFOChannel(UnreliableDelayedChannel):
    def __init__(self, *args, **kwargs):
        super(UnreliableDelayedFIFOChannel, self).__init__(*args, **kwargs)

    def __deliver(self, message, process):
        raise NotImplementedError
