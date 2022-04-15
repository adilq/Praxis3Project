'''
ESC204 2022W Widget Lab 3IoT, Part 8
Task: Implement an MQTT publisher.
'''
import board
import busio
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_minimqtt.adafruit_minimqtt as MQTT

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

class Connection(object):

    # Set MQTT definitions
    teamid = "1034-H" #TODO: fill in your teamid
    mqtt_topic = f"uoft/p3/{teamid}/msg"
    shhh = secrets

    # Set up SPI pins
    esp32_cs = DigitalInOut(board.CS1)
    esp32_ready = DigitalInOut(board.ESP_BUSY)
    esp32_reset = DigitalInOut(board.ESP_RESET)

    # Connect the RP2040 to the Nina W102 uBlox module's onboard ESP32 chip via SPI connections
    spi = busio.SPI(board.SCK1, board.MOSI1, board.MISO1)
    esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset, debug = 2)

    mqtt_client = None

    def __init__(self):

        # Check if ESP32 chip found and ready to connect and print chip details
        if self.esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
            print("ESP32 found and in idle mode")
        print("Firmware vers.", self.esp.firmware_version)
        print("MAC addr:", [hex(i) for i in self.esp.MAC_address])


        # Print SSIDs for all discovered networks and their signal strengths
        for ap in self.esp.scan_networks():
            print("hello")
            print("\t%s\t\tRSSI: %d" % (str(ap['ssid'], 'utf-8'), ap['rssi']))

        self.try_connect()

        # Set up socket
        socket.set_interface(self.esp)

        # Set up a MiniMQTT Client
        MQTT.set_socket(socket, self.esp)
        self.mqtt_client = MQTT.MQTT(broker=self.shhh["broker"],port=self.shhh["port"])

        # Connect callback handlers to mqtt_client
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_publish = self.on_publish

        # Try to connect to MQTT client
        print("Attempting to connect to %s" % self.mqtt_client.broker)
        self.mqtt_client.connect()

    def try_connect(self):
        # Try to connect to your WiFI network (using the SSID and password from secrets.py)
        print("Connecting to AP...")
        while not self.esp.is_connected:
            try:
                self.esp.connect_AP(self.shhh["ssid"], self.shhh["password"])
            except RuntimeError as e:
                print("could not connect to AP, retrying: ", e)
                continue
            print(".", end="")
        # If successfully connected, print IP
        print("Connected to", str(self.esp.ssid, "utf-8"), "\tRSSI:", self.esp.rssi)
        print("My IP address is", self.esp.pretty_ip(self.esp.ip_address))

    def on_connect(self, mqtt_client, userdata, flags, rc):
        '''
        This function will be called when the mqtt_client is connected successfully to the broker.
        '''
        print("Connected to MQTT Broker!")
        print("Flags: {0}\n RC: {1}".format(flags, rc))

    def on_publish(self, mqtt_client, userdata, topic, pid):
        '''
        This method is called when the mqtt_client publishes data to a feed.
        '''
        print("Published to {0} with PID {1}".format(topic, pid))

# Publish to MQTT topic
'''i = 0
while True:
    led.value = not(led.value)

    msg = "hello world from nano x" + str(i)
    print("got message: %s" % msg)
    if(len(msg) > 0):
        print("Publishing to %s" % self.mqtt_topic)
        self.mqtt_client.publish(self.mqtt_topic, msg)

    i += 1
    time.sleep(1.0)'''

