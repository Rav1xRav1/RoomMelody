# RoomMelody
カメラを使用して部屋に人がいるかを感知してSpotifyAPIとRaspotifyを使って [Lofi Girl - beats to relax/study to](https://open.spotify.com/playlist/0vvXsWCC9xrXsKd4FyS8kM?si=3b999b61f6f646cf) のプレイリストを部屋に流すプログラムを作る予定

# 機材
- Raspberry pi 5 スターターキット

https://www.amazon.co.jp/dp/B0CTQRCH8H/ref=sspa_dk_detail_0?psc=1&pd_rd_i=B0CTQRCH8H&pd_rd_w=Lhikm&content-id=amzn1.sym.f293be60-50b7-49bc-95e8-931faf86ed1e&pf_rd_p=f293be60-50b7-49bc-95e8-931faf86ed1e&pf_rd_r=5F8BHHQ89CAJ2H4X29MN&pd_rd_wg=g3GEm&pd_rd_r=13a774ea-d3a9-4858-b8d4-fbf1ac4b1e9d&s=computers&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWw

- ELPドームカメラ

https://www.amazon.co.jp/dp/B08FD44FW6?ref=ppx_yo2ov_dt_b_fed_asin_title

- Edifier D32 ワイヤレススピーカー

https://www.amazon.co.jp/gp/product/B0D5LPT9FB/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1

# 概要

下記のプログラムで `Webカメラ` から画像を取得して差分を計算して認識したら　`Spotify API` を使用して `Spotify Connect` をインストールしている `Raspberry Pi` からスピーカーを通して再生する
