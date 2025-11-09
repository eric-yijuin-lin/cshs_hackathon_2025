import cv2
import requests
import numpy as np
import threading
import time
from queue import Queue
from ultralytics import YOLO

# ======== 設定區 ========

CAMERA_URLS = [
    "http://192.168.0.52/capture",
    # "http://192.168.0.45/capture",
    # 加更多相機就繼續貼
]

MODEL_PATH = "yolov8s.pt"  # 換成你的模型
queue_max = 10          # queue 緩衝，避免塞爆
frame_queue = Queue(maxsize=queue_max)

model = YOLO(MODEL_PATH)

# ======== 攝影機 Thread：抓影像 Producer ========

def camera_worker(url):
    while True:
        try:
            print("getting", url)
            r = requests.get(url, timeout=10)
            img = cv2.imdecode(np.frombuffer(r.content, np.uint8), cv2.IMREAD_COLOR)
            if img is not None:
                if not frame_queue.full():
                    frame_queue.put((url, img))
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ {url} error: {e}")

# ======== YOLO Thread：消費者 Consumer ========

def yolo_worker():
    while True:
        url, frame = frame_queue.get()
        results = model.predict(
            frame, # 影像
            conf=0.5, # 信心門檻值
            iou=0.45, # IoU 門檻值
        )
        output = results[0].plot()

        cv2.imshow(url, frame)
        cv2.imshow(url, output)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

# ======== 啟動 Threads ========

# Camera threads
for url in CAMERA_URLS:
    t = threading.Thread(target=camera_worker, args=(url,), daemon=True)
    t.start()

# YOLO thread
yt = threading.Thread(target=yolo_worker, daemon=True)
yt.start()

yt.join()
