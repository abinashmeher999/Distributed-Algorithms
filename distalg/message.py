class Message:
    def __init__(self, **kwargs):
        if kwargs is not None:
            for key, value in kwargs.items():
                setattr(self, key, value)

if __name__ == "__main__":
    msg = Message(sender="A", receiver="B")
    assert msg.sender is "A"
    assert msg.receiver is "B"
