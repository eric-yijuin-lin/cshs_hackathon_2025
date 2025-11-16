# python ./data_server/app_example.py
from flask import Flask, request
app = Flask("hackathon server")
import random
import cv2
from time import sleep
# from ultralytics import YOLO
import numpy as np
from ultralytics import YOLO
from shapely.geometry import Point, Polygon

print("載入模型...")
model = YOLO("yolov8n.pt")
names = model.names
print("OK")
print("偵測類別:", names)
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
    # [id, x, y, slow, alarm,safemode,路段] 0:whale 1:bloss 
    [0, 0, 0, False, False, True,0], # id 通常要大於 0，這裡我把 id==0 拿來 debug 用
    ["1", 0, 0, False , False ,True, "road_kill_1"],
    ["0", 0, 0, False , False ,True, "car_distance"],
]
#資料庫基本完善↑
def get_intersection_id(x, y):
    if 0 <=x <= 100 and 100 <= y <= 500:
        return "meet"
    else:
        return "no_meet"
#路段要改↓  功能好了但要改數值↑
app.roads = [
    # [id, [x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    ["road_kill_1",[182,0],[278,8],[90,341],[4,321]],           #路殺1段
    ["road_kill_2",[4,321],[90,341],[338,687],[232,694]],       #路殺2段
    ["emergency",[265,538],[693,623],[625,698],[302,635]],      #救護車路
    ["car_distance",[854,235],[917,325],[748,700],[693,623]],   #車距路
    ["small_1",[378,219],[413,267],[147,447],[113,413]],        #小巷1段
    ["small_2",[154,232],[520,494],[490,539],[113,288]],        #小巷2段
    ["intersection",[245,305],[296,336],[236,372],[192,338]],   #十字路口
    ["people",[662,85],[710,0],[854,235],[800,340]],            #行人1段
    ["people_2",[331,49],[619,10],[662,85],[389,125]],          #行人2段
]
@app.route("/safe_mode")#設定手動模式(預設是on)
def safe_mode():
    safemode = request.args.get("safe_mode")
    car_id = request.args.get("id")
    for car in app.cars:
        if str(car[0]) == car_id:
            if safemode == "True":
                safemode = True
            else:
                safemode = False
            car[4] = safemode
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
            print(f"Updated car {car_id} to position ({x}, {y})in {car[6]}")
            return "ok"
    print("car not found")
    return "car not found"


@app.route("/car/status") #查詢車子的狀況 可能會用到
def car_status():
    search_id = request.args.get("id")
    for car in app.cars:
        if str(car[0]) == search_id:
            return car
    return "找不到車子"
@app.route("/car/update_xy")#只判斷位置 會用到
def getmap():
    id = request.args.get("id")
    x = request.args.get("x")
    y = request.args.get("y")
    x = float(x)
    y = float(y)
    
    print(f"[debug] bloss at ({cx}, {cy})")
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
@app.route("/button/get")#行人按鈕被按下 會用到
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
@app.route("/gps/app_inventor")#app inventor gps更新位置
def gps_app_inventer():
    car_id = request.args.get("id")
    for car in app.cars:
        if str(car[0]) == car_id:
            print(f"Received GPS for car {car_id}: ({car[1]}, {car[2]})")
            return str(car[1:3])     
@app.route("/road/test")#!!要改
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
   


app.run(host="0.0.0.0", port=5000)