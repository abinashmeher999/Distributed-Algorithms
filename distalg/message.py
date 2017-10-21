class Message:
    def __init__(self, from_channel=None, **kwargs):
        """
        A message object is the one that is used to carry information across processes.

        :param from_channel (Channel, optional): The channel on which this will be sent on.
            Because at the receiving end we can find out which channel it came from after receiving it.
        :param kwargs : all the keywords are set as attributes of the resulting object with the argument
            as their values
        """
        self._channel = from_channel
        if kwargs is not None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    @property
    def carrier(self):
        """
        At the receiving end it returns the channel is came through

        :return: (Channel) The channel it came through
        """
        return self._channel

if __name__ == "__main__":
    msg = Message(sender="A", receiver="B")
    assert msg.sender is "A"
    assert msg.receiver is "B"
