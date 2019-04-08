import time


futures = {}


class Future:
    def done(self):
        return True


class SleepFuture(Future):
    def __init__(self, when):
        self.when = when

    def done(self):
        return self.when <= time.monotonic()


class PinChangeFuture(Future):
    def __init__(self, pin):
        self.pin = pin
        self.last_value = pin.value

    def done(self):
        return self.last_value != pin.value


def pin_changed(pin):
    yield PinChangeFuture(pin)


def sleep(seconds):
    yield SleepFuture(time.monotonic() + seconds)


def start_soon(*awaitables):
    for awaitable in awaitables:
        futures[awaitable] = Future()


def run(*awaitables):
    start_soon(*awaitables)
    while futures:
        for awaitable, future in futures.iteritems():
            if future.done():
                break
        else:
            continue
        del futures[awaitable]
        try:
            future = next(awaitable)
        except StopIteration:
            pass
        else:
            futures[awaitable] = future
