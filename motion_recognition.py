import cv2
import time

# 動画の読み込み
movie = cv2.VideoCapture('movie.mp4')

# 枠線の色を赤に設定
red = (0, 0, 255)
# 前回の画像を保存する変数
before = None
# 動画のFPSを取得
fps = int(movie.get(cv2.CAP_PROP_FPS))

# 最後に動体が検知された時間を記録
last_motion_time = time.time()
# 動体が検知されているかどうかのフラグ
motion_detected = False

while True:
    # 画像を取得
    ret, frame = movie.read()
    # 再生が終了したらループを抜ける
    if ret == False: break
    # 画像を白黒に変換
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 初回フレームの場合は前回の画像として保存して次へ
    if before is None:
        before = gray.astype("float")
        continue

    # 現在のフレームと前回のフレームの移動平均との差を計算
    cv2.accumulateWeighted(gray, before, 0.5)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(before))
    # frameDeltaの画像を2値化
    thresh = cv2.threshold(frameDelta, 3, 255, cv2.THRESH_BINARY)[1]
    # 輪郭のデータを取得
    contours = cv2.findContours(thresh,
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE)[0]

    # フレーム内に動体があるかどうかのフラグ
    motion_in_frame = False

    # 差分があった点を画面に描く
    for target in contours:
        x, y, w, h = cv2.boundingRect(target)
        if w < 30: continue # 小さな変更点は無視
        cv2.rectangle(frame, (x, y), (x+w, h), red, 2)
        motion_in_frame = True

    # 動体が検知された場合
    if motion_in_frame:
        last_motion_time = time.time()
        if not motion_detected:
            print("検知されました")
            motion_detected = True
    else:
        # 5分間動体が検知されなかった場合
        if time.time() - last_motion_time > 300:
            if motion_detected:
                print("5分間検知されていません")
                motion_detected = False

    # ウィンドウでの再生速度を元動画と合わせる
    time.sleep(1/fps)
    # ウィンドウで表示
    cv2.imshow('target_frame', frame)
    # Enterキーが押されたらループを抜ける
    if cv2.waitKey(1) == 13: break

# ウィンドウを破棄
cv2.destroyAllWindows()
