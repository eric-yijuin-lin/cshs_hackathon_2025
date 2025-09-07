from machine import Pin, PWM
from time import sleep

# 腳位設定
PIN_A1 = 21  # L9110 A-1A
PIN_B1 = 47   # L9110 A-1B
PWM_FREQ = 20000  # 20kHz

pwm_a = PWM(Pin(PIN_A1), freq=PWM_FREQ, duty=0)
pwm_b = PWM(Pin(PIN_B1), freq=PWM_FREQ, duty=0)

def _pct_to_duty(pct):
    return int(1023 * (pct / 100))  # duty 範圍 0~1023

def set_speed(percent):
    """percent: -100 ~ 100，正負表示方向"""
    if percent > 0:   # 正轉
        pwm_a.duty(_pct_to_duty(percent))
        pwm_b.duty(0)
    elif percent < 0: # 反轉
        pwm_a.duty(0)
        pwm_b.duty(_pct_to_duty(-percent))
    else:             # 停止（coast）
        pwm_a.duty(0)
        pwm_b.duty(0)

# 測試
set_speed(100)   # 正轉 50%
sleep(10)

set_speed(0)    # 停止
