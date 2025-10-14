from flask import Flask, request
app = Flask("hackathon server")

app.cars = [
    # [id, x, y, speed, alarm]
    [0, 0, 0, 0, False], # id 通常要大於 0，這裡我把 id==0 拿來 debug 用
    [1, 0, 0, 0, False],
    [2, 0, 0, 0, False],
    [3, 0, 0, 0, False],
]

app.roads = [
    # [id, x1, y1, x2, y2, width, height]
    [1,-500,350,500,200,1000,150],
    [2,-300,500,300,-500,600,1000],
    [3,-500,200,500,150,1000,50],
]

app.intersections = [
    # [id, [connected_road_ids]]
    [1, [1, 2]],
    [2, [1, 3]],
    [3, [2, 3]],
]

@app.route("/car/update_xy") #更新車子的xy
def car_update_xy():
    car_id = request.args.get("id")
    x = request.args.get("x")
    y = request.args.get("y")
    
    for car in app.cars:
        if str(car[0]) == car_id:
            car[1] = float(x)
            car[2] = float(y)
            return "ok"
    return "car not found"

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


app.run(host="0.0.0.0", port=5000)