from flask import Flask, request
app = Flask("hackathon server")
import random
import cv2
from time import sleep
# from ultralytics import YOLO
import numpy as np

app.cars = [
    # [id, x, y, slow, alarm,direction]
    [0, 0, 0, 0, False], # id 通常要大於 0，這裡我把 id==0 拿來 debug 用
    ["uc", 0, 0, False , False],
    ["uc2", 0, 0, False , False],
    ["nc", 0, 0, False , False],
    ["fc", 0, 0, False , False],
]

def get_intersection_id(x, y):
    if 0<=x<=100 and 100<=y<=500:
        return "meet"
    else:
        return"not find"


app.roads = [
    # [id, x1, y1, x2, y2]
    [1,500,100,1000,200],
    [2,500,300,1000,400],
    [3,600,50,800,450],
]

app.test_lucas = [
    [50,100],
    [50,150],
    [50,200],
    [50,250],
    [50,300],
    [50,350],
    [50,400],
    [50,450],
    [50,500],
    [50,550],
    [200,50],
    [200,100],
    [200,150],
    [200,200],
    [200,250],
]
app.test_index = 0

#測試
@app.route("/hello")
def hello():
    return"hello"

@app.route("/car/update_row") #更新車子所有資訊
def car_update():
    car_id = request.args.get("id")
    x = request.args.get("x")
    y = request.args.get("y")
    speed = request.args.get("speed")
    alarm = request.args.get("alarm")
    if alarm == "True":
        alarm = True
    else:
        alarm = False
    
    for car in app.cars:
        if str(car[0]) == car_id:
            car[1] = float(x)
            car[2] = float(y)
            car[3] = speed
            car[4] = alarm
            return "ok"
    return "car not found"

@app.route("/car/status") #查詢車子的狀況
def car_status():
    search_id = request.args.get("id")
    for car in app.cars:
        if str(car[0]) == search_id:
            return car
    return "找不到車子"

@app.route("/car/update_xy")
def getmap():
    id = request.args.get("id")
    x = request.args.get("x")
    y = request.args.get("y")
    x = float(x)
    y = float(y)
    if 600 <=x <= 800 and 100 <= y <= 200:
        print(f"{id} in area 1&3")
        return  "you are in area 1&3"
    elif 600 <=x <= 800 and 300 <= y <= 400:
        print(f"{id} in area 2&3")
        return  "you are in area 2&3"
    elif 500 <=x <= 1000 and 100 <= y <= 200:
        print(f"{id}in area 1")
        return  "you are in area 1"
    elif 500 <=x <= 1000 and 300 <= y <= 400:
        print(f"{id} in area 2")
        return  "you are in area 2"
    elif 600 <=x <= 800 and 50 <= y <= 450:
        print(f"{id} in area 3")
        return  "you are in area 3"
    else:
        print(f"{id} out of area")
        return "you are out of area"


@app.route("/button/get")
def button_get():
    button_status = request.args.get("button")
    car_id = request.args.get("id")
    for car in app.cars:
        if str(car[0]) == car_id:
            if button_status == "turn_on":
                car[3] = True
                print("🚶 按鈕被按下，通知車端停車")
            else:
                car[3] = False
    return "請稍後..."
@app.route("/traffic/state")
def get_state():
    car_id = request.args.get("id")
    for car in app.cars:
        if str(car[0]) == car_id:
            return str(car[3])
    return "查無此車"   
@app.route("/text/app_inventor")
def text_app_inventer():
    # x = 0
    # y = 0
    # try:
    car_id = request.args.get("id")
    app.test_index += 1
    app.test_index = app.test_index % len(app.test_lucas)
    x = app.test_lucas[app.test_index][0]
    y = app.test_lucas[app.test_index][1]
    # except Exception as e:
    #     print(app.test_lucas)
    #     print(app.test_index)
    #     print(e)
    for car in app.cars:
        if str(car[0]) == car_id:
            car[1] = float(x)
            car[2] = float(y)
            return str(car[1:3])
        
@app.route("/road/test")
def car_lucas_text():
    app.test_index += 1
    app.test_index = app.test_index % len(app.test_lucas) 
    x = app.test_lucas[app.test_index][0]
    y = app.test_lucas[app.test_index][1]
    # x = request.args.get("x")
    # y = request.args.get("y")
    road = get_intersection_id(x, y)
    if road == "meet":
        car_id = request.args.get("id")
        for car in app.cars:
            if str(car[0]) == car_id:
                print(x,y)
                return str(car[3])
    return "查無此車"
@app.route("/photo/app_inventor", methods=["POST"])
def photo_app_inventer():
    data = request.get_data(cache=False, as_text=False)
    if not data:
        return "No data received", 400
    # img = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)


    # if 'file' not in request.files:
    #     return "No file part", 400
    # file = request.files['file']
    # if file.filename == '':
    #     return "No selected file", 400
    # data = file.read()
    image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        return "Invalid image", 400
    h, w = image.shape[:2]
    cv2.rectangle(image, (10, 10), (w-10, h-10), (0, 255, 0), 3)
    cv2.imshow("Received Image", image)
    cv2.imwrite("received_image.jpg", image)
    key = cv2.waitKey(1)
    if key == 27: # 按 Esc 鍵離開
        cv2.destroyAllWindows()
    return "ok"
   


                


app.run(host="0.0.0.0", port=5000)