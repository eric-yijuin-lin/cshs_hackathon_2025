from machine import Pin
import time
import network
import urequests

# 行人紅綠燈
led_red = Pin(41, Pin.OUT)     # 行人紅燈
led_green = Pin(21, Pin.OUT)   # 行人綠燈

# 行人按鈕
button = Pin(42, Pin.IN, Pin.PULL_UP)  # 按下 = LOW

# 狀態控制
cooldown = False
last_press_time = 0

def set_pedestrian(red, green):
    led_red.value(red)
    led_green.value(green)
    
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


# 預設狀態：紅燈亮
set_pedestrian(1, 0)
print("🚦 行人紅綠燈系統啟動 (ESP32-S3)")

while True:
    now = time.time()

    if button.value() == 0 and not cooldown:  # 按下且沒有冷卻
        print("👆 行人按下按鈕，準備通行")
        
        response = urequests.get("http://172.20.10.3:5000/button/get?button=turn_on")
        response = urequests.get("http://172.20.10.3:5000/esp32/name?esp32=1&action=warn2")
    
        # 綠燈 5 秒
        set_pedestrian(0, 1)
        for i in range(5, 0, -1):
            print(f"🚶 行人綠燈 {i} 秒")
            time.sleep(1)

        # 回到紅燈
        set_pedestrian(1, 0)
        print("🚫 紅燈亮，行人停止")

        # 啟動冷卻 15 秒
        cooldown = True
        last_press_time = now

    # 冷卻時間檢查
    if cooldown and now - last_press_time >= 15:
        cooldown = False
        print("✅ 冷卻結束，可以再次按下按鈕")

    time.sleep(0.1)
