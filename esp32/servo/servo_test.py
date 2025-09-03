import time
from servo import Servo
my_servo = Servo(pin_id=21)
print("30")
my_servo.write(30)
time.sleep(2.0)

print("120")
my_servo.write(120)
time.sleep(2.0)

print("90")
my_servo.write(90)
