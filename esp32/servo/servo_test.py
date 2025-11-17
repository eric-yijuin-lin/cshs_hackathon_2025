import time
from servo import Servo
from machine import Pin
import network
import urequests


WIFI_SSID = "DLINK_6021"
WIFI_PASS = "cshs1234"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)

while True:
    if wifi .isconnected():
        print("connected")
        break
    else:
        print("...")
        sleep(1)


# 建立伺服馬達物件，使用 GPIO 21（可改）
servo = Servo(pin_id=21)
while True:

    responce = urequests.get("http://192.168.0.60:5000/traffic/state?id=1")
    if responce[7] == "true":
            
# 移動到 120 度
            print("轉到 120°")
            servo.write(120)
            time.sleep(2)

            # 回到 90 度
            print("轉回 90°")
            servo.write(90)
            time.sleep(2)

            print("完成。")
