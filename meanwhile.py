import time


futures = {}


class Future:
    """A trivial future, that is immediately finished."""
    def done(self):
        return True

    def __iter__(self):
        # Makes it possible to await on the future itself.
        yield self


class SleepFuture(Future):
    """A future that is finished after set time."""
    def __init__(self, when):
        self.when = when

    def done(self):
        return self.when <= time.monotonic()


class PinChangeFuture(Future):
    """A future that is finished when a pin value changes."""
    def __init__(self, pins):
        self.pins = tuple((pin, pin.value) for pin in pins)

    def done(self):
        return any(pin.value != value for pin, value in self.pins)


def watch_pin(*pins):
    """Asynchronously wait until a pin changes value."""
    yield PinChangeFuture(pins)


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
