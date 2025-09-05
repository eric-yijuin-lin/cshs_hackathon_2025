import cv2
import numpy as np
import time

# === 相機設定（依需要調整） ===
BACKEND = cv2.CAP_MSMF      # 或 cv2.CAP_DSHOW
CAM_INDEX = 0
WIDTH, HEIGHT = 1280, 720
FPS = 30
FOURCC = "MJPG"

def open_cam():
    cap = cv2.VideoCapture(CAM_INDEX, BACKEND)
    if not cap.isOpened():
        raise RuntimeError("無法開啟攝影機")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*FOURCC))
    time.sleep(0.05)
    ok, _ = cap.read()
    if not ok:
        cap.set(cv2.CAP_PROP_FOURCC, 0)  # 退回預設
        time.sleep(0.05)
        ok, _ = cap.read()
        if not ok:
            raise RuntimeError("攝影機已開啟但無法讀到畫面")
    return cap

def order_points(pts):
    # 將 4 點排序為: 左上、右上、右下、左下
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]      # 左上
    rect[2] = pts[np.argmax(s)]      # 右下
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]   # 右上
    rect[3] = pts[np.argmax(diff)]   # 左下
    return rect

def compute_warp(src_pts):
    rect = order_points(src_pts)
    (tl, tr, br, bl) = rect
    widthA  = np.linalg.norm(br - bl)
    widthB  = np.linalg.norm(tr - tl)
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxW = int(max(widthA, widthB))
    maxH = int(max(heightA, heightB))
    dst = np.array([[0,0],[maxW-1,0],[maxW-1,maxH-1],[0,maxH-1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    return M, (maxW, maxH)

class PointPicker:
    def __init__(self, img):
        self.img = img.copy()
        self.display = img.copy()
        self.points = []
        self.window = "選 4 個角點（左鍵新增、右鍵撤回、Enter 確認）"
        cv2.namedWindow(self.window, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window, self.on_mouse)

    def on_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(self.points) < 4:
            self.points.append((x, y))
        elif event == cv2.EVENT_RBUTTONDOWN and self.points:
            self.points.pop()
        self.display = self.img.copy()
        for i, p in enumerate(self.points):
            cv2.circle(self.display, p, 6, (0, 255, 0), -1)
            cv2.putText(self.display, str(i+1), (p[0]+6, p[1]-6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    def run(self):
        while True:
            cv2.imshow(self.window, self.display)
            key = cv2.waitKey(20) & 0xFF
            if key in (13, 10):  # Enter
                if len(self.points) == 4:
                    break
            elif key in (27, ord('q'), ord('Q')):  # Esc/Q 取消
                self.points = []
                break
        cv2.destroyWindow(self.window)
        return np.array(self.points, dtype=np.float32)

def pick_corners_once(cap):
    # 擷取一張清晰影像供選點
    for _ in range(5):
        ok, frame = cap.read()
        if ok: break
        time.sleep(0.02)
    if not ok:
        raise RuntimeError("擷取影像失敗，無法選點")
    picker = PointPicker(frame)
    pts = picker.run()
    if len(pts) != 4:
        raise RuntimeError("未完成 4 點選取，已取消")
    M, size = compute_warp(pts)
    return M, size

def main():
    cap = open_cam()

    # 一啟動就要求選點並建立透視變換
    M, out_size = pick_corners_once(cap)

    window_in  = "原始畫面（R 重選 / Q 離開）"
    window_out = "校正後畫面"
    cv2.namedWindow(window_in,  cv2.WINDOW_NORMAL)
    cv2.namedWindow(window_out, cv2.WINDOW_NORMAL)

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                continue

            warped = cv2.warpPerspective(frame, M, out_size)

            cv2.putText(frame, "Warp: ON  |  R=重選  Q=離開",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            cv2.imshow(window_in, frame)
            cv2.imshow(window_out, warped)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), ord('Q'), 27):
                break
            elif key in (ord('r'), ord('R')):
                # 重新選 4 點並更新 M
                M, out_size = pick_corners_once(cap)

    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
