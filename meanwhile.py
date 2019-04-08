import time


futures = {}


class Future:
    """A trivial future, that is immediately finished."""
    def done(self):
        return True


class SleepFuture(Future):
    """A future that is finished after set time."""
    def __init__(self, when):
        self.when = when

    def done(self):
        return self.when <= time.monotonic()


class PinChangeFuture(Future):
    """A future that is finished when a pin value changes."""
    def __init__(self, pin):
        self.pin = pin
        self.last_value = pin.value

    def done(self):
        return self.last_value != self.pin.value


def watch_pin(pin):
    """Asynchronously wait until a pin changes value."""
    yield PinChangeFuture(pin)


def sleep(seconds):
    """Asynchronously wait until given time passes."""
    yield SleepFuture(time.monotonic() + seconds)


def start_soon(*awaitables):
    """Schedule awaitables to be executed."""
    for awaitable in awaitables:
        futures[awaitable] = Future()


def run(*awaitables):
    """Run all scheduled and specified awaitables until they all finish."""
    start_soon(*awaitables)
    while futures:
        # Find an awaitable that is not blocked on a future.
        for awaitable, future in futures.items():
            if future.done():
                break
        else:
            continue
        # Remove that future from the list.
        del futures[awaitable]
        # Run the awaitable until it hits another future or finishes.
        try:
            future = next(awaitable)
        except StopIteration:
            pass
        else:
            # Add the new future to the list.
            futures[awaitable] = future
