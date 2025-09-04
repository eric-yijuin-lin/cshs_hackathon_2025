# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.3
#   kernelspec:
#     display_name: .venv
#     language: python
#     name: python3
# ---

# %% [markdown]
# ### 安裝所需 package (一大堆模組包起來的 "套件包")
#

# %%
# !pip install ultralytics==8.0.196
# !pip install roboflow

# %% [markdown]
# ### 設定「HOME」變數
# - home 變數通常代表程式運行起點的資料夾
# - 程式會從這個資料夾，根據指定的路徑找到需要的檔案，例如訓練 AI 的圖片、AI 模型

# %%
import os
HOME = os.getcwd()
print(HOME)

# %% [markdown]
# ### 引用相關模組
# - IPython
#     - 圖片與進階 UI 顯示畫面的模組
#     - Jupyter (現在這個分區塊寫程式跟筆記的介面) 以及 Colab 用來顯示圖片或其他進階介面的模組
# - YOLO
#     - AI 框架 (framework)
#     - 大幅簡化 AI 訓練的流程，並降低程式操作的難度
# - Roboflow
#     - 圖片標記平台
#     - 可以讓我們在平台上方便的標記圖片來訓練 AI
#     - 也能透過程式碼下載我們標記的圖片，融入 Python 程式

# %%
import json
from IPython import display
display.clear_output()

import ultralytics
from ultralytics import YOLO
from IPython.display import display, Image
from roboflow import Roboflow

ultralytics.checks()

# %% [markdown]
# ### 透過命令列測試 YOLO 是否能運作
# - 如果運作成功，會跑出一隻狗狗的辨識圖

# %%
# %cd {HOME}
# !yolo task=detect mode=predict model=yolov8n.pt conf=0.25 source='https://media.roboflow.com/notebooks/examples/dog.jpeg' save=True
Image(filename='runs/detect/predict/dog.jpeg', height=600)

# %% [markdown]
# ### 換透過 Python 程式碼測試 YOLO 是否正常運作
# - 如果正常運作，會在第二行最後面看到「640x384 1 person, 1 car, 1 dog, 64.0ms」

# %%
model = YOLO(f'{HOME}/yolov8n.pt')
results = model.predict(source='https://media.roboflow.com/notebooks/examples/dog.jpeg', conf=0.25)

# %% [markdown]
# ### 建立 "dataset" 資料夾存放訓練圖片

# %%
if not os.path.exists(f"{HOME}/datasets"):
    os.mkdir(f"{HOME}/datasets")

# %% [markdown]
# ### 從 user_secret.json 讀取機密資訊

# %%
# %cd {HOME}
rf_secret = {}
with open("user_secret.json", "r") as f:
    user_secret = json.load(f)
    rf_secret = user_secret["roboflow"]
# print(user_secret)

# %% [markdown]
# ### 使用 roboflow 下載訓練資料集

# %%
# %cd {HOME}/datasets
rf = Roboflow(api_key=rf_secret["api_key"])
workspace = rf.workspace(rf_secret["workspace"])
project = workspace.project(rf_secret["project"])
version = project.version(rf_secret["version"])
dataset = version.download("yolov8")

# %% [markdown]
# ### 訓練 AI 模型

# %%
# %cd {HOME}
model = YOLO("yolov8s.pt") # 載入預訓練模型
model.train(
    data=f"{dataset.location}/data.yaml",  # 資料集設定
    epochs=25,                             # 訓練輪數
    imgsz=800,                             # 輸入影像大小
    plots=True,                            # 是否輸出訓練過程圖表
    workers=0,                             # 關閉多程序
)

# 訓練資料集比較大或 epoch 輪數較多時，可以試試看以下指令是否能加速
# 但是這個指令必須在 VS Code 的 Terminal 或 CMD 命令列執行
# 直接在 Jupyter Notebook 跑會因為 Windows 的系統跟 Jupyter 互動的限制而失敗
# yolo task=detect mode=train model=yolov8s.pt data={dataset.location}/data.yaml epochs=25 imgsz=800 plots=True

# %% [markdown]
# ### 查看 Confusion Matrix
# - 直翻是「混淆矩陣」
# - 用來視覺化預測以及實際之間的差異或比例
#     - 縱軸: Predicted (YOLO 的預測)
#     - 橫軸: True (真實的類別)
#     - 預測與真實相符的比例越高 (顏色越深) 越好

# %%
# %cd {HOME}
Image(filename=f'{HOME}/runs/detect/train/confusion_matrix.png', width=600)

# %% [markdown]
# ### 查看訓練過程圖表

# %%
# %cd {HOME}
Image(filename=f'{HOME}/runs/detect/train/results.png', width=600)

# %% [markdown]
# ### 查看預測的圖片
# - 每個預測都會包含三個東西
#     - 外框：YOLO 認為在這個範圍內有我們要他偵測的物件
#     - 類別：YOLO 偵測到的物件所屬的類別名稱
#     - 信心：0.1~1.0 的小數，代表 YOLO 認為他是這個類別的機率

# %%
# %cd {HOME}
Image(filename=f'{HOME}/runs/detect/train/val_batch0_pred.jpg', width=600)

# %% [markdown]
# ### 驗證模型效果
# - model.val() 函式可以幫我們用量化數據計算模型的效果好壞
# - 各種不同的效果有各種不同的意義 (我也還在啃書努力找研究所回憶 (遮臉))
# - 可以先看 PR-Curve 最直觀
#     - R -> Recall: 抓「出」東西的能力
#     - P -> Precision: 抓「準」東西的能力
#     - 曲線越靠近右上方模型效果越好

# %%
# %cd {HOME}
model = YOLO(f"{HOME}/runs/detect/train/weights/best.pt")
metrics = model.val(data=f"{dataset.location}/data.yaml")

# # !yolo task=detect mode=val model={HOME}/runs/detect/train/weights/best.pt data={dataset.location}/data.yaml

Image(filename=f'{HOME}/runs/detect/train/PR_curve.png', width=600)

# %% [markdown]
# ### 實際把模型拿來推理
# - model.predict() 可以把目前最好的模型 (best.pt) 拿來偵測物件
# - conf = 0.5 設定只顯示信心 0.5 以上的預測
# - iou = 0.1 設定重疊閾值，越低越不允許重疊
# - save = True 會把偵測的結果儲存到檔案

# %%
# %cd {HOME}
model = YOLO(f"{HOME}/runs/detect/train/weights/best.pt")

# 推論
results = model.predict(
    source=f"{dataset.location}/test/images",  # 測試集影像
    conf=0.6,  # 信心閾值
    iou=0.1,  # 重疊閾值
    save=True   # 儲存推論結果到 runs/detect/predict
)

# # !yolo task=detect mode=predict model={HOME}/runs/detect/train/weights/best.pt conf=0.25 source={dataset.location}/test/images save=True

# %% [markdown]
# ### 查看預測結果照片
# - glob 模組可以大幅簡化從指定資料夾尋找 jpg 檔案的寫法
# - [:1] 代表抽取第一張，如果要抽取三張顯示，把 1 改成 3 即可

# %%
import glob

for image_path in glob.glob(f'{HOME}/runs/detect/predict/*.jpg')[:1]:
      display(Image(filename=image_path, width=600))
      print("\n")

# %% [markdown]
# ### 查看預測結果數據

# %%
names = model.names
r = results[0]  # 第一張影像的結果
# 每個偵測到的框
for box in r.boxes:
    xyxy = box.xyxy[0].tolist()   # [x1, y1, x2, y2]
    conf = box.conf[0].item()     # 信心分數
    index = int(box.cls[0].item())
    label = names[index]

    print(f"類別: {label}, 信心: {conf}, 框: {xyxy}")
