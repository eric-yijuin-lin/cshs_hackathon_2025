import cv2
from ultralytics import YOLO
import requests

model = YOLO("yolov8s.pt")     # 也可改成 yolov8s.pt / m / l / x
cap = cv2.VideoCapture(0)      # 0=預設攝影機；改成 "video.mp4" 可讀影片檔
WIDTH  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
HEIGHT = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
CENTER_X = WIDTH / 2
CENTER_Y = HEIGHT / 2
SLEEP_MS = 1000 # 每隔多少毫秒傳送一次資料
# SERVER = "http://192.168.1.100:5000"
SERVER = "http://localhost:5000"

def update_car_xy(id, x, y):
    try: # 網路很容易有問題，所以用 try 包起來，除了避免程式當掉，也可以捕捉錯誤訊息
        url = f"{SERVER}/car/update_xy?id={id}&x={x}&y={y}"
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
        x1, y1, x2, y2 = box.xyxy[0]  # 取得外框座標
        cls = int(box.cls[0])         # 取得類別
        conf = box.conf[0]            # 取得信心分數
        label = model.names[cls]      # 取得類別名稱
        print(f"Detected {label} with confidence {conf:.2f} at ({x1}, {y1}), ({x2}, {y2})")
        
        # 假設我們只對特定類別感興趣，例如 "cell phone"
        if label == "cell phone" and conf > 0.5:
            # 計算中心點座標
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            update_car_xy(0, cx, cy)
    tagged_frame = results[0].plot()       # YOLO 幫你畫好框、類別、信心分數
    cv2.imshow("YOLOv8", tagged_frame)


    # 暫停 SLEEP_MS 並檢查是否按下 ESC 鍵
    if cv2.waitKey(SLEEP_MS) & 0xFF == 27:     # 按 ESC 離開
        break

cap.release()
cv2.destroyAllWindows()
