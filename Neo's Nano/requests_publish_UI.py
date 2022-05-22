# SPDX-FileCopyrightText: Brent Rubell for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import busio
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_requests as requests
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

# Connect to WiFi
print("Connecting to WiFi...")
wifi.connect()
print("Connected!")
# If successfully connected, print IP and try a couple of web tests
print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)
print("My IP address is", esp.pretty_ip(esp.ip_address))
print("IP lookup adafruit.com: %s" %
esp.pretty_ip(esp.get_host_by_name("adafruit.com")))
print("Ping google.com: %d ms" % esp.ping("google.com"))

# Set up POST request
socket.set_interface(esp)
requests.set_socket(socket, esp)
JSON_PATCH_URL = "https://d62e-128-100-201-39.ngrok.io/api/trackers/1/"
#JSON_PATCH_URL = "http://0022-138-51-92-15.ngrok.io/api/trackers/2/"
attempts = 3  # Number of attempts to retry each request

# Main block
prv_refresh_time = 0.0
while True:
    # Send a new GPS reading to UI every 3 seconds
    if (time.monotonic() - prv_refresh_time) > 3:
        # Receive and format GPS data
        lat = -162.24
        long = 79.52
        #json_data = {"cur_loc" : f"SRID=4326;POINT ({lat} {long})"}
        json_data = {"json_dump" : {"status": [True, True, True], "time": ["17:36", "17:36", "17:36"], "lon": [49.11, 49.12, 49.13], "lat" : [69.21, 69.22, 69.23] }}
        # Publish it to UI
        failure_count = 0
        response = None
        print("PATCHing data to {0}: {1}".format(JSON_PATCH_URL, json_data))
        while not response:
            resp = requests.get("https://google.ca")
            print(resp)
            print("------")
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
        print("JSON Data received from server:", json_resp)
        print('-'*40)
        response.close()

        prv_refresh_time = time.monotonic()
