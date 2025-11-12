import cv2
import numpy as np

# ==== 滑鼠事件處理 ====
points = []  # 儲存使用者點選的座標

def mouse_callback(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        print(f"Point {len(points)}: ({x}, {y})")

# ==== 初始化相機 ====
camera = cv2.VideoCapture(0)  # 改成自己的攝影機編號
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    ok, img = camera.read()
    if not ok:
        print("無法讀取影像，請檢查攝影機")
        exit()
    cv2.imshow("Select Points", img)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):  # 按 Esc 離開
        print("開始選取透視投影點")
        break


# 顯示畫面讓使用者點四個點
clone = img.copy()
cv2.namedWindow("Select Points")
cv2.setMouseCallback("Select Points", mouse_callback)

print("請用滑鼠左鍵依序點選 4 個點：左上、右上、右下、左下")

while True:
    temp = clone.copy()
    # 畫出使用者已經點的點與線段
    for i, p in enumerate(points):
        cv2.circle(temp, p, 5, (0, 0, 255), -1)
        cv2.putText(temp, str(i + 1), (p[0] + 10, p[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    if len(points) == 4:
        cv2.polylines(temp, [np.int32(points)], True, (255, 0, 0), 2)
    cv2.imshow("Select Points", temp)
    key = cv2.waitKey(1) & 0xFF

    if key == 27:  # 按 Esc 離開
        print("中止操作")
        cv2.destroyAllWindows()
        exit()
    if len(points) == 4:
        break

cv2.destroyWindow("Select Points")

# ==== 開始透視轉換 ====
pts_src = np.float32(points)

# 設定輸出影像的大小
width, height = 400, 300
pts_dst = np.float32([
    [0, 0],
    [width - 1, 0],
    [width - 1, height - 1],
    [0, height - 1]
])

# 計算透視變換矩陣
M = cv2.getPerspectiveTransform(pts_src, pts_dst)
print(f"成功取得透視變換矩陣:")
print(M)

# 執行透視變換
warped = cv2.warpPerspective(img, M, (width, height))

# 顯示結果
cv2.imshow("Original", img)
cv2.imshow("Warped", warped)
cv2.waitKey(0)
cv2.destroyAllWindows()
