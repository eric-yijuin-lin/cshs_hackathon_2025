import cv2
import numpy as np
print("版本：", cv2.__version__)

# 建立一張黑底圖片
img = np.zeros((200, 200, 3), dtype=np.uint8)

# 畫一個白色圓圈
cv2.circle(img, (100, 100), 50, (255, 255, 255), -1)

# 顯示圖片
cv2.imshow("Test", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
