import sys
import os
import signal


class SignalHandler:
    """
    The object that will handle signals and stop the worker threads.
    """

    #: The stop event that's shared by this handler and threads.
    stopper = None

    #: The pool of worker threads
    workers = None

    def __init__(self, stopper, workers):
        self.stopper = stopper
        self.workers = workers

    def __call__(self, signum, frame):
        """
        This will be called by the python signal module

        https://docs.python.org/3/library/signal.html#signal.signal
        """
        self.stopper.set()
        for worker in self.workers:
            worker.join()
        os.kill(os.getpid(),
                signal.SIGKILL)  # force kill for now when receving sigint (thread is stopped gracefully anyway)
        sys.exit(0)
