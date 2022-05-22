import busio
import board
import digitalio
import time
import mqtt_publish
import DataPacket
import json

#set up LEDs
onboard_led = digitalio.DigitalInOut(board.LED)
onboard_led.direction = digitalio.Direction.OUTPUT
green_led = digitalio.DigitalInOut(board.D2)
green_led.direction = digitalio.Direction.OUTPUT

#set up button
button = digitalio.DigitalInOut(board.D3)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

def check_button_state(state):
    '''#check the state of the button
    '''
    was_pressed = False
    if (not state):
        #the button has been pressed
        for i in range(0, 10):
            green_led.value = not green_led.value
            time.sleep(0.15)
        while not button.value:
            pass
        was_pressed = True

    return was_pressed

#flash both rapidly unitl button is pressed
def flash_leds():
    for i in range(20):
        green_led.value = not green_led.value
        onboard_led.value = not onboard_led.value
        time.sleep(0.05)
    return

def convert_2_bin(string):
    return bytes(string, 'utf-8')

def stop_comm(uart):
    uart.reset_input_buffer()
    uart.write(convert_2_bin('STOP'))  #tell pico to turn off uart
    time.sleep(1)
    while uart.read() != b'STOPPING':  #wait until you get confirmation
        time.sleep(0.5)
    uart.deinit()  #deinitialize uart

def start_comm():
    uart = busio.UART(board.D8, board.D9)  #re establish uart
    uart.write(convert_2_bin('START'))
    return uart

def reset_to_send():
    TO_SEND = {TRACKER_ID: { 'status' : [],'time' : [],'lon' : [],'lat' : []}}

def send_to_drone(connection, msg):
    try:
        connection.mqtt_client.publish(connection.mqtt_topic, msg)
        return 1
    except:
        connection.esp.reset()
        connection.reinit()
        connection.mqtt_client.publish(connection.mqtt_topic, msg)
        return 0

#list of data packet objects
push = []
connection = False
TRACKER_ID = 1
TO_SEND = {TRACKER_ID: {'status' : [], 'time' : [], 'lon' : [], 'lat' : []}}

uart = start_comm()

#main loop
while True:
    ready = True
    data = uart.read()  #read data from Pico
    #data = "{'Hello' : 13012321, 'Status' : 0}" #dummy test code
    button_state = button.value
    button_state = button.value
    was_pressed = check_button_state(button_state)
    print(83, was_pressed)

    if data != b'\x00' and data is not None:
        onboard_led.value = True
        #make a new DataPacket object and convert back to dictionary
        pack = DataPacket.Packet(data)
        pack.convert()
        pack.data["time"] = time.time()
        # if there is a position, append data to list.
        # If its the first time, flash both LEDs so that we can see
        if (pack.data["status"] == 1) and (len(push) == 0):
            flash_leds()
            TRACKER_ID = pack.data['id'] # save tracker id as global
            push.append(pack)
        elif (pack.data["status"] == 1):
            push.append(pack)

        print(pack.data)
        onboard_led.value = False
    else:
        green_led.value = not green_led.value

    #sending data over wifi
    if was_pressed:
        #establish connection with mqtt broker
        stop_comm(uart)

        if not connection:
            connection = mqtt_publish.Connection()  #this is an object (see mqtt_publish.py)
        elif not connection.esp.is_connected:
            connection.try_connect()

        #go through each sample
        for packet in push:
            if not packet.sent:
                onboard_led.value = not onboard_led.value  #flash the led
                # add data from that sample to the dictionary to be sent
                # doing this here makes sure we don't send the same data twice
                print(packet.data['status'])
                TO_SEND[TRACKER_ID]['status'].append(packet.data['status'])
                TO_SEND[TRACKER_ID]['time'].append(packet.data['time'])
                TO_SEND[TRACKER_ID]['lat'].append(packet.data['lat'])
                TO_SEND[TRACKER_ID]['lon'].append(packet.data['lon'])
                packet.update_sent()

        if len(push) == 0:
            msg = 'Nothing to push'
            send_to_drone(connection, msg)
        else:
            #flash led so that we know its about to push
            for i in range(3):
                onboard_led.value = not onboard_led.value
                time.sleep(0.1)

            msg = json.dumps(TO_SEND)
            send_to_drone(connection, msg)


            #flash slowly so that we know it has been pushed
            for i in range(3):
                onboard_led.value = not onboard_led.value
                time.sleep(0.5)

            push.clear()
            reset_to_send()
        uart = start_comm()
        onboard_led.value = False
