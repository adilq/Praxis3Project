from machine import UART, Pin

uart_nano = UART(1,baudrate=9600,tx=Pin(4),rx=Pin(5))

colors = {
    'RED' : 0.00000232,
    'BLUE': 0.2343,
    'GREEN': 093.33423
    }

colors = str(colors)

uart_nano.write(colors)
print("written")
