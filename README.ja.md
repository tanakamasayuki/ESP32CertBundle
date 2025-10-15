# ESP32 Certificate Bundle

英語版は [README.md](README.md) を参照してください。

## 概要
このリポジトリは、ESP32 向け Arduino 環境でそのまま利用できる最新の X.509 ルート証明書バンドルを提供します。ヘッダファイルはあらかじめ生成済みのため、利用者は追加のツール実行やファイル更新を行う必要はありません。

## 特長
- `esp_crt_bundle_attach()` で即利用できる `x509_crt_bundle` 配列を同梱。
- Arduino-ESP32 v3 系（IDF 5 ベース）および互換フレームワークで動作確認済み。
- メンテナ向けにバンドル再生成用スクリプトを用意。

## Arduino スケッチでの利用
1. ライブラリを Arduino の `libraries` フォルダへ配置するか、PlatformIO 依存として追加します。
2. スケッチ内でヘッダをインクルードします。
   ```cpp
   #include <WiFiClientSecure.h>
   #include "esp32_cert_bundle.h"

   void setup() {
     WiFi.begin(ssid, password);
     // 接続が完了するまで待機 …
     WiFiClientSecure client;
     client.setCACertBundle(x509_crt_bundle, x509_crt_bundle_len);
   }
   ```
3. `WiFiClientSecure` や `HTTPClient`、`PubSubClient` など TLS クライアントを設定する際にバンドルを渡します。
4. `https://example.com` など既知の HTTPS エンドポイントで通信テストを行い、証明書検証が成功することを確認してください。

> **備考:** `setCACertBundle()` は複数のルート CA をまとめたファイルを読み込みます。一般的な公開証明書の大半を検証できますが、その分ヘッダファイルのサイズは大きくなります。

## 同梱物
- `src/esp32_cert_bundle.h`: PROGMEM に配置されたルート証明書バンドル。
- `examples/BasicUsage/BasicUsage.ino`: HTTPS 通信の最小サンプル。
- `tools/update_bundle.py`: バンドルを再生成するための補助スクリプト（メンテナ向け）。

## 証明書バンドルの再生成（上級者向け）
配布済みのヘッダで通常は十分です。バンドルを刷新したい場合のみ、以下の手順を実施してください。

### 前提条件
- Python 3.8 以上（標準ライブラリの `hashlib`、`struct`、`ssl` が利用可能なこと）。
- `wget` や `curl` など CA ストアを取得できる HTTP クライアント。
- ESP-IDF 付属の `gen_crt_bundle.py`（ツールが自動でダウンロードします）。
- 生成されたヘッダを取り込むための ESP32 ツールチェインまたは Arduino IDE 環境。

### 手順
1. Mozilla の CA ストアを Arduino 向けヘッダへ変換します。
   ```bash
   python tools/update_bundle.py
   ```
   スクリプトは Espressif の生成スクリプトと Mozilla CA バンドルをダウンロード（またはキャッシュを再利用）し、`gen_crt_bundle.py` を実行して `src/esp32_cert_bundle.h` を出力します。
2. 生成されたヘッダの内容を確認し、必要に応じてコミットします。

> **補足:** Espressif 公式ドキュメントの手順で `gen_crt_bundle.py` と `cacert.pem` を手動ダウンロードして `python gen_crt_bundle.py -i cacert.pem` を実行し、その後で `python tools/update_bundle.py` を実行してバイナリをヘッダへ変換することもできます。

### 最新状態の維持
- Mozilla の信頼ストアが更新された際は、上記の再生成手順を再実行してください。
- 生成されたヘッダの差分を確認し、証明書データ以外に不要な変更がないことを確かめてください。
- Espressif 側のスクリプトに破壊的変更が入った場合は、[ESP-IDF ドキュメント](https://docs.espressif.com/projects/esp-idf/) を参照し、必要に応じてツールやコードを調整してください。

## 自動化
- GitHub Actions ワークフロー（`.github/workflows/update-bundle.yml`）が毎月 1 日の 00:00 UTC に実行され、更新が検出された場合は自動でリリースを作成します。
- リポジトリの *Run workflow* から手動実行すれば、任意のタイミングで更新できます。
- 手動実行時に `force_release=true`（必要に応じて `version_level`）を指定すると、バンドルに変更がなくてもバージョンを更新してリリースを作成できます。

## コントリビュート
Issue や Pull Request は歓迎します。コントリビュートの際は次の点をご留意ください。
- 変更の動機と再現手順を明記してください（該当する場合）。
- 証明書データの更新に依存する変更では、バンドルを再生成して差分を含めてください。
- 新しいツールやワークフローを追加した際は本ドキュメントも更新してください。

## ライセンス
本プロジェクトは Mozilla Public License 2.0 の下で提供されています。詳細は `LICENSE` を参照してください。
