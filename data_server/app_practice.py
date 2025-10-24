from flask import Flask, request
app = Flask("carrrrrrrrrrr")
table = []
app.map = [
    [1,-500,350,500,200,1000,150],
    [2,-300,500,300,-500,600,1000],
    [3,-500,200,500,150,1000,50],
]

#測試
@app.route("/hello")
def hello():
    return"hello"
@app.route("/car/capital") #取資料存在table
def car_capital():
    car_id = request.args.get("id")
    x = request.args.get("x")
    y = request.args.get("y")
    speed = request.args.get("speed")
    alarm = request.args.get("alarm")
    if alarm == "True":
        alarm = True
    else:
        alarm = False
    
    car_row = [car_id, float(x), float(y), speed, alarm]
    table.append(car_row)
    return "ok"
@app.route("/car/search") #查詢車自己的狀況
def car_search():
    search_id = request.args.get("id")
    index = 0
    car_row = []
    while index < 5:
        car_row = table[index]
        if car_row[0] == search_id:
            break
        index += 1
    return car_row
    # return car_row
@app.route("/car/updata")
def car_updata():
    search_id = request.args.get("id")
    x = request.args.get("x")
    y = request.args.get("y")
    speed = request.args.get("speed")
    alarm = request.args.get("alarm")
    if alarm == "True":
        alarm = True
    else:
        alarm = False
    index = 0
    car_row = []
    while index < 5:
        car_row = table[index]
        if car_row[0] == search_id:
            break
        index += 1
    car_row[1] = float(x)
    car_row[2] = float(y)
    car_row[3] = speed
    car_row[4] = alarm
    return "ok"
@app.route("/car/distance")
def car_distance():

    search_id = request.args.get("id")
    search_id2 = request.args.get("id2")
    index = 0
    car_row = []
    car_row2 = []
    while index < 5:
        car_row = table[index]
        if car_row[0] == search_id:
            break
        index += 1
    index = 0
    while index < 5:
        car_row2 = table[index]
        if car_row2[0] == search_id2:
            break
        index += 1

    x3 =  float(car_row2[1])**2 - float(car_row[1])**2
    y3 =  float(car_row[2])**2 - float(car_row2[2])**2
    distance = (x3 + y3)**0.5
    return f"{distance:.2f}"
@app.route("/esp32/name")
def name():
    esp32 = request.args.get("esp32")
    action = request.args.get("action")
    if action == "warn2":
        print(f"{esp32}那邊有行人")
        return "1"
@app.route("/button/get")
@app.route("/getmap")
def getmap():
    x = request.args.get("x")
    y = request.args.get("y")
    x = float(x)
    y = float(y)
    if -300 <=x <= 300 and 200 <= y <= 350:
        print("in area 1&2")
        return  "you are in area 1&2"
    elif -300 <=x <= 300 and 150 <= y <= 200:
        print("in area 2&3")
        return  "you are in area 2&3"
    elif -500 <=x <= 500 and 200 <= y <= 350:
        print("in area 1")
        return  "you are in area 1"
    elif -300 <=x <= 300 and -500 <= y <= 500:
        print("in area 2")
        return  "you are in area 2"
    elif -500 <=x <= 500 and 150 <= y <= 200:
        print("in area 3")
        return  "you are in area 3"
    else:
        print("out of area")
        return "you are out of area"
        
    return app.map
    
 











app.run(host="0.0.0.0")