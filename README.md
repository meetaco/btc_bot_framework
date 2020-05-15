# 暗号通貨高頻度取引bot用websocketベースフレームワーク
## 概要
Pythonによる暗号通貨の高頻度取引bot向けフレームワークです。<br>
このフレームワークの役割は主に以下の３つです。
* websocketを最大限利用することでAPI制限とデータ取得遅延の問題を緩和すること。
* 取引所毎のwebsocketの仕様の差異を吸収すること。
* Bot開発において頻繁に出現する処理を再利用可能な形でモジュール化すること。

簡単な動作確認しかできていないので、バグが多く残っているものと思われます。<br>
コードを参考にする程度に留めるか、実行する際はご自身で十分に検証を行ってください。<br>
プログラムの実行は自己責任です。不具合等によって損失が生じた場合でもこちらでは責任を負えません。<br>

## 主な機能
* websocket経由の約定データ、板情報、注文イベントの取得
* 注文・キャンセル
* 注文イベントの処理: 注文管理、ポジションサイズ計算、(未確定)損益計算
* ポジションの仮想的な分割（複数ロジックの実行）
* リアルタイムシミュレーション
* UDP経由の操作（webインターフェース等との連携用）
* クラス（ロジックファイル）の動的なロード・アンロード

## 取引所対応状況
| 取引所      | API   | 約定情報 | 板情報 | 建玉管理・注文管理 | バグ取り |
|:-----------|:-----:|:-------:|:-----:|:---------------:|:------:|
| bitbank    | ○     | ○       | ○     | ×               | △      |    
| bitflyer   | ○     | ○       | ○     | ○               | ○      |    
| bitmex     | ○     | ○       | ○     | ○               | △      |
| binance    | ○     | ○       | ○     | ○               | △      |
| bybit      | △     | ○       | ○     | △               | △      |
| gmocoin    | ○     | ○       | ○     | ×               | △      |
| liquid     | ○     | ○       | ○     | △(JPYペアのみ)   | △      |

## 動作環境
* UNIX互換環境(Windowsは未検証)
* python>=3.6

## 依存ライブラリ
* ccxt>=1.26.54
* websocket-client>=0.48
* sortedcontainers
* beautifulsoup4 (オプション) – bitflyer web注文

## インストールと使い方
[wiki](https://github.com/penta2019/btc_bot_framework/wiki)をご覧ください。


## このプロジェクトの対象外
* STOP、IFDOCO等の親注文
* ローソク足やインジケータ等のチャート情報
* 実用的な売買ロジック

## 今後の予定
* gmocoin, bitbank 注文周りの実装
