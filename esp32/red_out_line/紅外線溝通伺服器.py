from machine import Pin
import time
import network
import urequests

WIFI_SSID = "iPhone-YJL"
WIFI_PASS = "12345678"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)

while True:
    if wifi .isconnected():
        print("connected")
        break
    else:
        print("...")


IR_SENSOR_PIN = 21
sensor = Pin(IR_SENSOR_PIN, Pin.IN)



while True:

    if sensor.value() == 0:
        response = urequests.get("http://34.81.204.58:5000/ir_sensed")
        print(response.text)
    else:
        print("safe")
    time.sleep(0.5)