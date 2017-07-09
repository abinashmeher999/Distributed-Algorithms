import asyncio
from random import random


class Channel:
    def __init__(self, delay_mean=100, delay_std_dev=10, min_delay=1, max_delay=500):
        """
        :param delay_mean: mean delay for a message to reach from in end to out end
        :param delay_std_dev: variation in delay for a message to reach fro in end to out end
        :param min_delay: guarantee that the delay won't be less than this value
        :param max_delay: guarantee that the delay won't be more than this value
        """
        self.delay_mean = delay_mean
        self.delay_std_dev = delay_std_dev
        self.in_transit = set()
        self.reached = set()
        self.min_delay = min_delay
        self.max_delay = max_delay

    async def __deliver(self, message):
        """
        :param message: The Message object to be delivered
        :return:
        """
        self.in_transit.add(message)
        delay_time = random.gauss(self.delay_mean, self.delay_std_dev)
        clamped_delay_time = min(self.max_delay, max(self.min_delay, delay_time))
        asyncio.sleep(clamped_delay_time)
        self.in_transit.remove(message)
        self.reached.add(message)

