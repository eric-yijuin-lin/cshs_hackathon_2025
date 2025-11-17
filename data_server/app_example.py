# python ./data_server/app_example.py
from flask import Flask, request, render_template
app = Flask("hackathon server")
import random
import cv2
from time import sleep
# from ultralytics import YOLO
import numpy as np
from ultralytics import YOLO
from shapely.geometry import Point, Polygon
from pathlib import Path
from datetime import datetime

print("載入模型...")
model = YOLO("yolov8n.pt")
names = model.names
print("OK")
print("偵測類別:", names)

app.no_object_count = 0
app.road_area = [
    ["road_kill_1", Polygon([(182,0),(278,8),(90,341),(4,321)])],
    ["road_kill_2", Polygon([(4,321),(90,341),(338,687),(232,694)])],
    ["emergency", Polygon([[265,538],[693,623],[625,698],[302,635]])],
    ["car_distance", Polygon([[854,235],[917,325],[748,700],[693,623]])],
    ["small_1", Polygon([[378,219],[413,267],[296,336],[245,305]])],
    ["small_2", Polygon([[296,336],[520,494],[490,539],[236,372]])],
    #["intersection", Polygon([[245,305],[296,336],[236,372],[192,338]])],
    ["people_1", Polygon([[662,85],[710,0],[854,235],[800,340]])],
    ["people_2", Polygon([[331,49],[619,10],[662,85],[389,125]])],
]

app.cars = [
    # [id, x, y, slow, alarm,safemode,路段,people_servo,small_servo] 0:whale 1:bloss 
    [0, 0, 0, False, False, True,0,False,False], # id 通常要大於 0，這裡我把 id==0 拿來 debug 用
    ["1", 0, 0, False , 'no',True, "unknown",False,False], 
    ["0", 0, 0, False , 'no' ,True, "unknown",False,False],
]
#資料庫基本完善↑
#路段要改↓  
app.roads = [
    # [id, [x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    ["road_kill_1",[182,0],[278,8],[90,341],[4,321]],           #路殺1段
    ["road_kill_2",[4,321],[90,341],[338,687],[232,694]],       #路殺2段
    ["emergency",[265,538],[693,623],[625,698],[302,635]],      #救護車路
    ["car_distance",[854,235],[917,325],[748,700],[693,623]],   #車距路
    ["small_1",[378,219],[413,267],[147,447],[113,413]],        #小巷1段
    ["small_2",[154,232],[520,494],[490,539],[113,288]],        #小巷2段
    # ["intersection",[245,305],[296,336],[236,372],[192,338]], #十字路口
    ["people_1",[662,85],[710,0],[854,235],[800,340]],          #行人1段
    ["people_2",[331,49],[619,10],[662,85],[389,125]],          #行人2段
]

def update_all_car_status():
    car_number = len(app.cars)
    for i in range(car_number - 1):
        car1 = app.cars[i]
        car2 = app.cars[i + 1]
        if car1[6] == car2[6] and car1[6] != "unknown":
            distance = ((car1[1] - car2[1])**2 + (car1[2] - car2[2])**2)**0.5
            if distance < 100:  # 假設安全距離是 100 單位
                car1[3] = True  # 設定慢速
                car2[3] = True  # 設定慢速
                car1[4] = "car_too_close"
                car2[4] = "car_too_close"
@app.route("/safe_mode")#設定自動模式(True)(預設是on)
def safe_mode():
    safemode = request.args.get("safe_mode")
    car_id = request.args.get("id")
    for car in app.cars:
        if str(car[0]) == car_id:
            if safemode == "True":
                safemode = True
            else:
                safemode = False
            car[5] = safemode
@app.route("/car/update_row") #更新車子所有資訊
def car_update():
    car_id = request.args.get("id")
    x = request.args.get("x")
    y = request.args.get("y")
    
    for car in app.cars:
        if str(car[0]) == car_id:
            x = float(x)
            y = float(y)
            for road_area in app.road_area:
                point = Point(x, y)
                if point.within(road_area[1]):
                    car[6] = road_area[0]
            car[1] = x
            car[2] = y
            update_all_car_status()
            print(f"Updated car {car_id} to position ({x}, {y})in {car[6]}")
            return "ok"
    print("car not found")
    return "car not found"
@app.route("/button/get")#行人按鈕被按下 會用到
def button_get():
    button_status = request.args.get("button")
    for car in app.cars:
        if button_status == "turn_on" and (car[6]=="people_1" or car[6]=="people_2"):
            car[3] = True
            car[4] = "people"
            car[7] = True
            print("🚶 按鈕被按下，通知車端停車")
        else:
            car[3] = False
            car[4] = "no"
            car[7] = False
    return "請稍後..."
@app.route("/traffic/state")
def get_state():
    car_id = request.args.get("id")
    for car in app.cars:
        if str(car[0]) == car_id:
            return car
    return "查無此車"
@app.route("/gps/app_inventor")#app inventor gps更新位置
def gps_app_inventer():
    car_id = request.args.get("id")
    for car in app.cars:
        if str(car[0]) == car_id:
            return car
    return "not found"
@app.route("/esp32/capture")
def esp32_capture():
    object = request.args.get("object")
    if object == "st" :
        for car in app.cars:
            if car[6]=="road_kill_1" or car[6]=="road_kill_2":
                car[3]=True
                car[4]="road_kill"
    # elif object == "km" or object == "cs":
    #     for car in app.cars:
    #         if car[6]=="people_1" or car[6]=="people_2":
    #             car[3]=True
    #             car[4]="people"
    #             car[7]=True
    elif object == "whale" or object == "bloss" :
        for car in app.cars:
            if car[6]=="small_1" or car[6]=="small_2":
                car[3]=True
                car[4]="small_streetl"
                car[8]=True
    else:
        app.no_object_count += 1
        if app.no_object_count > 3:
            for car in app.cars:
                car[3] = False
                car[4] = "no"
                car[8] = False
    return "ok"
@app.route("/esp32-upload", methods=["GET", "POST"])
def test_upload():
    if request.method == "GET":
        return render_template("test_upload.html")
    elif request.method == "POST":
        if "file" not in request.files:
            print("[debug] /esp32-upload: No file part")
            return 400, "No file part"
        file = request.files["file"]
        if file.filename == "":
            print("[debug] /esp32-upload: No selected file")
            return 400, "No selected file"
        
        file_prefix = Path(file.filename).stem
        file_surffix = Path(file.filename).suffix
        time_str = datetime.now().strftime("%Y-%m-%d %H%M%S")
        file_name = f"{file_prefix} {time_str}{file_surffix}"
        full_name = f"C:/Users/user/Documents/temp/{file_name}"
        file.save(full_name)

        return "image saved"
  


app.run(host="0.0.0.0", port=5000)