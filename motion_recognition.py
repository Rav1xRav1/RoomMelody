import cv2
import time
import os

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from ENV import ENV

# Lofi Girl - beats to relax/study to のプレイリストID
PLAYLIST_ID = "0vvXsWCC9xrXsKd4FyS8kM"

CLIENT_ID = ENV.CLIENT_ID
CLIENT_SECRET = ENV.CLIENT_SECRET
REDIRECT_URI = ENV.REDIRECT_URI  # リダイレクトURIを設定

SCOPE = "user-modify-playback-state,user-read-playback-state"

auth_manager = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
)

sp = spotipy.Spotify(auth_manager=auth_manager)

tracks = sp.playlist_items(PLAYLIST_ID)

# アクティブなデバイスを取得
devices = sp.devices()

# デバイス名がDESKTOP-OG9460IであるデバイスのIDを取得
device_id = None
for device in devices['devices']:
    if device['name'] == ENV.DEVICE_NAME:
        device_id = device['id']
        break

# 取得したプレイリストからランダムに一つ再生する
track = tracks['items'][0]['track']['uri']

sp.start_playback(device_id=device_id, uris=[track])

# 動画の読み込み
movie = cv2.VideoCapture(0)

# 枠線の色を赤に設定
red = (0, 0, 255)
# 前回の画像を保存する変数
before = None
# 動画のFPSを取得
# fps = int(movie.get(cv2.CAP_PROP_FPS))

# 最後に動体が検知された時間を記録
last_motion_time = time.time()
# 動体が検知されているかどうかのフラグ
motion_detected = False
# 動体が検知された回数をカウントする変数
motion_detected_count = 0
# 動体が検知された回数の閾値
MOTION_DETECTION_THRESHOLD = 5

# 保存先ディレクトリを設定
SAVE_DIR = "detected_frames"
os.makedirs(SAVE_DIR, exist_ok=True)

def fade_out_volume(sp, device_id, duration=5):
    current_volume = sp.current_playback()['device']['volume_percent']
    steps = 10
    step_duration = duration / steps
    volume_step = current_volume / steps

    for i in range(steps):
        new_volume = max(0, current_volume - volume_step * (i + 1))
        sp.volume(int(new_volume), device_id)
        time.sleep(step_duration)

def fade_in_volume(sp, device_id, target_volume=100, duration=5):
    steps = 10
    step_duration = duration / steps
    volume_step = target_volume / steps

    for i in range(steps):
        new_volume = min(target_volume, volume_step * (i + 1))
        sp.volume(int(new_volume), device_id)
        time.sleep(step_duration)

while True:
    # 画像を取得
    ret, frame = movie.read()
    # 再生が終了したらループを抜ける
    if ret == False: break
    # 画像を上下逆にする
    frame = cv2.flip(frame, 0)
    # 画像を白黒に変換
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 初回フレームの場合は前回の画像として保存して次へ
    if before is None:
        before = gray.astype("float")
        continue

    # 差計算の重み
    weight = 0.8
    # 現在のフレームと前回のフレームの移動平均との差を計算
    cv2.accumulateWeighted(gray, before, 0.8)
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
        motion_detected_count += 1
        if not motion_detected and motion_detected_count >= MOTION_DETECTION_THRESHOLD:
            motion_detected = True
            # 検知されたフレームを保存
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            cv2.imwrite(os.path.join(SAVE_DIR, f"detected_{timestamp}.jpg"), frame)
            # Spotifyの再生状態を取得
            playback_state = sp.current_playback()
            # Spotifyが再生中でない場合のみ再生を開始
            if playback_state and not playback_state['is_playing']:
                sp.start_playback(device_id=device_id)
                fade_in_volume(sp, device_id)
            else:
                sp.start_playback(device_id=device_id, uris=[track])
                fade_in_volume(sp, device_id)
    else:
        motion_detected_count = 0
        # 5分間動体が検知されなかった場合
        if time.time() - last_motion_time > 10:
            if motion_detected:
                print("5分間検知されていません")
                motion_detected = False
                # 音楽をフェードアウトして停止
                fade_out_volume(sp, device_id)
                sp.pause_playback(device_id=device_id)

    # ウィンドウでの再生速度を元動画と合わせる
    # time.sleep(1/fps)
    # ウィンドウで表示
    # cv2.imshow('target_frame', frame)
    # Enterキーが押されたらループを抜ける
    # if cv2.waitKey(1) == 13: break

# ウィンドウを破棄
cv2.destroyAllWindows()
