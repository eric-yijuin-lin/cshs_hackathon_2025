import time
from servo import Servo

# 建立伺服馬達物件，使用 GPIO 21（可改）
servo = Servo(pin_id=21)

# 移動到 30 度
print("轉到 30°")
servo.write(30)
time.sleep(2)

# 移動到 120 度
print("轉到 120°")
servo.write(120)
time.sleep(2)

# 回到 90 度
print("轉回 90°")
servo.write(90)
time.sleep(2)

print("完成。")
