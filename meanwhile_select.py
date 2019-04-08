import select
import time


class PriorityQueue:
    def __init__(self):
        self.items = []

    def __len__(self):
        return len(self.items)

    def insert(self, priority, item):
        self.items.append((priority, item))
        self.items.sort(key=lambda item:item[0])

    def top_priority(self):
        if not self.items:
            return None
        return self.items[0][0]

    def pop_top(self):
        return self.pop(0)[1]


class Future:
    pass


class SleepFuture(Future):
    def __init__(self, seconds):
        self.seconds = seconds


class ReadFuture(Future):
    def __init__(self, fileno):
        self.fileno = fileno


class WriteFuture(Future):
    def __init__(self, fileno):
        self.fileno = fileno


def sleep(seconds):
    yield SleepFuture(seconds)


def read(file_object, maxlength=None):
    yield ReadFuture(file_object.fileno())
    return file_object.read(maxlength)


def write(file_object, data):
    yield WriteFuture(file_object.fileno())
    return file_object.write(data)


sleeping = PriorityQueue()
reading = {}
writing = {}
running = []


def start_soon(*tasks):
    running.extend(tasks)


def run(*tasks):
    while any(running, sleeping, reading, writing):
        while running:
            # Handle all non-blocked tasks.
            task = running.pop(0)
            # Run the task until it gets blocked or finished.
            try:
                future = next(task)
            except IterationStop:
                continue
            # How is it blocked?
            if isinstance(future, SleepFuture):
                # Sleeping.
                sleeping.insert(time.monotonic() + seconds, task)
            elif isinstance(future, ReadFuture):
                # Reading.
                reading[future.fileno] = reading.get(future.fileno,
                                                     []).append(task)
            elif isinstance(future, WriteFuture):
                # Writing.
                writing[future.fileno] = writing.get(future.fileno,
                                                     []).append(task)
            else:
                # Unhandled.
                raise RuntimeError("future unclear")

        # Now wake up any blocked tasks.
        # How long until the first sleeping task?
        wait = sleeping.top_priority() - time.monotonic()
        # Wait for i/o operations to finish.
        read, write, error = select.select(reading.keys(), writing.keys(),
            reading.keys() + writing.keys(), timeout=wait)
        while time.monotonic() >= sleeping.top_priority():
            # Wake up tasks.
            running.append(sleeping.pop_top())
        for fileno in read:
            # Only wake the first reading task for a given fileno.
            running.append(reading[fileno].pop())
            if not reading[fileno]:
                del reading[fileno]
        for fileno in write:
            # Only wake the first writing task for a given fileno.
            running.append(writing[fileno].pop())
            if not writing[fileno]:
                del writing[fileno]
        for fileno in error:
            # Wake all tasks that have errors, so they can throw exceptions.
            runninge.extend(error[fileno])
