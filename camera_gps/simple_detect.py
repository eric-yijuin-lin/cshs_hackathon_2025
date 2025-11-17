import cv2
from time import sleep

print("載入 ultralytics 模組...")
from ultralytics import YOLO
print("OK")

# !!!!! ===================================== !!!! #
# 注意: 要先把 ai/yolo_test/runs/train/weights/best.pt 
#       複製到 camera_gps/web_cam/yolo/ 目錄下
# !!!!! ===================================== !!!! #

# 載入 YOLO 模型
print("載入模型...")
model = YOLO("bloss_and_whale.pt")
names = model.names
print("OK")
print("偵測類別:", names)

# 建立攝影機物件並設定參數
print("開啟攝影機...")
camera = cv2.VideoCapture(1)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) # 寬度
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) # 高度
print("OK")


while True:
    # 擷取影像
    ok, frame = camera.read()
    if not ok:
        print("擷取影像失敗")
        sleep(0.5)
        continue

    cv2.imshow("simple_detect", frame)
    results = model.predict(
        source=frame,
        conf=0.5,
        iou=0.1,
        imgsz=800
    )
    # 輸出偵測結果
    r = results[0]
    detected_frame = r.plot()
    cv2.imshow("simple_detect", detected_frame)

    key = cv2.waitKey(500)
    if key == 27: # 按 Esc 鍵離開
        break
    elif key == ord('c'): # 按 c 儲存影像
        cv2.imwrite("web_cam.jpg", frame)
        print("已儲存 web_cam.jpg")
        
        
camera.release()
cv2.destroyAllWindows()