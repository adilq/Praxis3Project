import time
import board
import busio
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_requests as requests
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import json

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Set up SPI pins
esp32_cs = DigitalInOut(board.CS1)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

# Connect RP2040 to the WiFi module's ESP32 chip via SPI, then connect to WiFi
spi = busio.SPI(board.SCK1, board.MOSI1, board.MISO1)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets)

# The callback for when the client receives a CONNACK response from the server.
def connected(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    teamid = "1034-H" #TODO: fill in your team ID
    client.subscribe(f"uoft/p3/{teamid}/msg")

def disconnected(client, userdata, rc):
    # This method is called when the client is disconnected
    print("Disconnected from MQTT Broker!")

# The callback for when a PUBLISH message is received from the server.
def message(client, userdata, msg):
    #print(msg.topic+": "+str(msg.payload))
    print("Message received: " + msg)
    publish_msg(msg)

# Format message to JSON dict and publish to UI via requests PATCH
def publish_msg(msg):
    cur_track = {}
    track_dict = json.loads(msg)
    for id in track_dict:
        cur_track = json.loads(msg)[id]
        JSON_PATCH_URL = f"https://d62e-128-100-201-39.ngrok.io/api/trackers/{id}/"
        json_data = {"json_dump" : json.dumps(cur_track)}

        # Publish it to UI
        failure_count = 0
        response = None
        print("PATCHing data to {0}: {1}".format(JSON_PATCH_URL, json_data))
        while not response:
            try:
                response = requests.patch(JSON_PATCH_URL, json=json_data)
                failure_count = 0
            except AssertionError as error:
                print("Request failed, retrying...\n", error)
                failure_count += 1
                if failure_count >= attempts:
                    raise AssertionError("Failed to resolve hostname, please check your router's DNS configuration.")
                continue
        print("Data patched successfully!")
        print('-'*40)

        # Parse out the 'json' key from json_resp dict.
        json_resp = response.json()
        print("JSON Data received from server:", json_resp['json_dump'])
        print('-'*40)
        response.close()

# Connect to WiFi
print("Connecting to WiFi...")
wifi.connect()
print("Connected to WiFi!")

# Initialize MQTT interface with the esp interface
MQTT.set_socket(socket, esp)

# Set up a MiniMQTT Client
mqtt_client = MQTT.MQTT(broker=secrets["broker"],port=secrets["port"])

# Setup the callback methods above
mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected
mqtt_client.on_message = message

# Connect the client to the MQTT broker.
print("Connecting to MQTT broker...")
mqtt_client.connect()

# Set up POST request
socket.set_interface(esp)
requests.set_socket(socket, esp)
attempts = 3  # Number of attempts to retry each request

# Main Loop
prv_refresh_time = 0.0
while True:
    try:
        mqtt_client.loop()
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        mqtt_client.reconnect()
        continue
