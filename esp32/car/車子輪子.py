from machine import Pin, PWM
from time import sleep
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
        sleep(1)


# 腳位設定
pin_AIA = Pin(21, Pin.OUT)
pin_AIB = Pin(47, Pin.OUT)

pin_BIA = Pin(4, Pin.OUT)
pin_BIB = Pin(14, Pin.OUT)


# 初始化 PWM
pwm_AIA = PWM(pin_AIA)
pwm_AIB = PWM(pin_AIB)

pwm_BIA = PWM(pin_BIA)
pwm_BIB = PWM(pin_BIB)

pwm_AIA.freq(1000)
pwm_AIB.freq(1000)

pwm_BIA.freq(1000)
pwm_BIB.freq(1000)


def set_speed(pwm, percent):
    """將 0~100% 轉換為 PWM duty (0~65535)"""
    duty = int((max(0, min(percent, 100)) / 100) * 65535)
    pwm.duty_u16(duty)

def forward(speed_percent):
    """正轉，speed_percent 範圍 0~100"""
    set_speed(pwm_AIA, speed_percent)
    set_speed(pwm_AIB, 0)
    set_speed(pwm_BIA, speed_percent)
    set_speed(pwm_BIB, 0)
    print(f"Forward {speed_percent}%")

def backward(speed_percent):
    """反轉，speed_percent 範圍 0~100"""
    set_speed(pwm_AIA, 0)
    set_speed(pwm_AIB, speed_percent)
    set_speed(pwm_BIA, 0)
    set_speed(pwm_BIB, speed_percent)
    print(f"Backward {speed_percent}%")

while True:
    
    res_road = urequests.get("http://172.20.10.3:5000/road/test?id=uc")
    if res_road.text == "True":
        forward(80)
        sleep(1)
        forward(40)
        sleep(1)
        forward(0)
        sleep(4)
    else:
        forward(100)
   
    


