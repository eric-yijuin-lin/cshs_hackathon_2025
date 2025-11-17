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
    if wifi.isconnected():
        print("connected")
        time.sleep(1)
        print(wifi.ifconfig())
        break
    else:
        print("...")
        time.sleep(1)


# 建立伺服馬達物件，使用 GPIO 21（可改）
servo = Servo(pin_id=21)
while True:
    print("getting http://192.168.0.60:5000/traffic/state?id=1")
    responce = urequests.get("http://192.168.0.60:5000/traffic/state?id=1")
    if responce.status_code != 200:
        print(responce.status_code)
        continue
    else:
        data_row = responce.json()
        if data_row[8] == True:
            print("轉到 20°")
            servo.write(20)
        else:
            # 回到 90 度
            print("轉回 115°")
            servo.write(115)

            print("完成。")
    time.sleep(1)


