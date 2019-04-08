import meanwhile
import board
import digitalio


#async
def blink1(pin):
    io = digitalio.DigitalInOut(pin)
    io.switch_to_output()
    while True:
        print("blink!")
        io.value = not io.value
        #await
        yield from meanwhile.sleep(1)

#async
def blink2(pin):
    #await
    yield from meanwhile.sleep(0.5)
    #await
    yield from blink1(pin)


def pin_change(pin):
    io = digitalio.DigitalInOut(pin)
    while True:
        #await
        yield from meanwhile.watch_pin(io)
        print("pin changed!")


meanwhile.run(blink1(board.D1), blink2(board.D2), pin_change(board.D3))
