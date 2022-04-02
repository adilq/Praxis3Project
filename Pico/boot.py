from machine import Pin
import time

led = Pin(25, Pin.OUT)

for i in range (0, 10):
    led.low()
    time.sleep(0.1)
    led.high()
    time.sleep(0.1)

led.low()