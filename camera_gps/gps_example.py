import cv2
from ultralytics import YOLO
import requests
import os
import numpy as np
# print(os.getcwd())

model = YOLO("bloss_and_whale.pt")     # 也可改成 yolov8s.pt / m / l / x
cap = cv2.VideoCapture(1)      # 0=預設攝影機；改成 "video.mp4" 可讀影片檔
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) # 寬度
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) # 高度
WIDTH  = 1280
HEIGHT = 720
CENTER_X = WIDTH / 2
CENTER_Y = HEIGHT / 2
SLEEP_MS = 1000 # 每隔多少毫秒傳送一次資料
# SERVER = "http://192.168.1.100:5000"
SERVER = " http://192.168.0.60:5000"
CALIBRATION_MATRIX = np.array([ # 先跑 perspct_calibrate.py 得到這個矩陣，貼在這下面
 [ 8.23328950e-01,  8.15177178e-03, -1.48215514e+02],
 [-1.21458243e-01,  9.41017600e-01,  1.99804485e+01],
 [-3.14207873e-04,  1.03832930e-05,  1.00000000e+00],
], dtype=np.float32) 

def calibrate_point(point, M):
    """
    point: (x, y)
    M: 3x3 透視投影的校正矩陣
    回傳: 投影後 (x', y')
    """
    # 建成 OpenCV 要的形狀 (1,1,2)
    p = np.array(point, dtype=np.float32).reshape(1, 1, 2)
    warped = cv2.perspectiveTransform(p, M)
    return warped[0,0]  # 拆回 (x, y)

def update_car_xy(id, x, y):
    try: # 網路很容易有問題，所以用 try 包起來，除了避免程式當掉，也可以捕捉錯誤訊息
        url = f"{SERVER}/car/update_row?id={id}&x={x}&y={y}"
        response = requests.get(url)
        if response.status_code == 200:
            print("已更新車子位置")
        else:
            print(f"警告：伺服器回應狀態碼 {response.status_code}")
    except Exception as e:
        print(f"無法傳送資料到伺服器，錯誤：\n{e}")

while True:
    ok, frame = cap.read()
    if not ok:
        break
    results = model(
        frame, # 影像
        conf=0.25, # 信心門檻值
        iou=0.45, # IoU 門檻值
        verbose=False)
    
    for box in results[0].boxes:
        coords = box.xyxy[0].cpu().numpy().flatten()  # 取得外框座標
        x1, y1, x2, y2 = coords
        cls = int(box.cls[0])         # 取得類別
        conf = box.conf[0]            # 取得信心分數
        label = model.names[cls]      # 取得類別名稱

        # 校正透視投影的變形
        x1, y1 = calibrate_point((x1, y1), CALIBRATION_MATRIX)
        x2, y2 = calibrate_point((x2, y2), CALIBRATION_MATRIX)
        print(f"Detected {label} with confidence {conf:.2f} at ({x1}, {y1}), ({x2}, {y2})")
        
        # 假設我們只對特定類別感興趣，例如 "cell phone"
        if label == "bloss" and conf > 0.5:
            # 計算中心點座標
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            update_car_xy(1, cx, cy)
        elif label == "whale" and conf > 0.5:
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            update_car_xy(2, cx, cy)
        elif label == "fc" and conf > 0.5:
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            update_car_xy(3, cx, cy)
        elif label == "uc2" and conf > 0.5:
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            update_car_xy(4, cx, cy)
    tagged_frame = results[0].plot()       # YOLO 幫你畫好框、類別、信心分數
    cv2.imshow("YOLOv8", tagged_frame)


    # 暫停 SLEEP_MS 並檢查是否按下 ESC 鍵
    if cv2.waitKey(SLEEP_MS) & 0xFF == 27:     # 按 ESC 離開
        break

cap.release()
cv2.destroyAllWindows()
