import cv2
from time import sleep
from ultralytics import YOLO

# 建立攝影機物件並設定參數
camera = cv2.VideoCapture(1) # 0 或 1 要自己試試看
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) # 寬度
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) # 高度


while True:
    # 擷取影像
    ok, frame = camera.read()
    if not ok:
        print("擷取影像失敗")
        sleep(0.5)
        continue

    key = cv2.waitKey(1)
    if key == 27: # 按 Esc 鍵離開
        break
    elif key == ord('c'): # 按 c 儲存影像
        cv2.imwrite("web_cam.jpg", frame)
        print("已儲存 web_cam.jpg")

    cv2.imshow("Web Cam", frame)
camera.release()
cv2.destroyAllWindows()