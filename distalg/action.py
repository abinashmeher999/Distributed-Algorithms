class Action:
    def __init__(self, callback):
        """
        :param callback: The function that will be called when the action is executed.
                        Please note that the action will be executed asynchronously
        """
        if not callable(callback):
            if hasattr(callback, '__name__'):
                message = "Passed callback '{}' is not callable.".format(callback.__name__)
            else:
                message = "Passed callback of type {} is not callable".format(type(callback))
            raise TypeError(message)
        else:
            self.callback = callback

    async def run_in(self, process):
        return self.callback(process)
