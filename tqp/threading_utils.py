from threading import Event, Thread


class Interval(Thread):
    """Run a function periodically.

    The code is a modified version of `threading.Timer` that runs
    periodically until cancelled
    """

    def __init__(self, interval, function, args=None, kwargs=None):
        super().__init__()
        self.interval = interval
        self.function = function
        self.args = args or []
        self.kwargs = kwargs or {}
        self.finished = Event()

    def cancel(self):
        """Stop the timer if it hasn't finished yet"""
        self.finished.set()

    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.cancel()
