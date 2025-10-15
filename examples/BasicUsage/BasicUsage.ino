#include <WiFi.h>
#include <WiFiClientSecure.h>

#include "esp32_cert_bundle.h"

// -----------------------------------------------------------------------------
// User Settings
// -----------------------------------------------------------------------------
#pragma region UserSettings
// === User Settings ===
// Please review and update the settings below as needed,
// or define them separately in "arduino_secrets.h" (if available).
// Do not share sensitive information (e.g. passwords, API keys) publicly.
// === ユーザー設定 ===
// 必要に応じて下記の設定値を確認・変更してください
// または、"arduino_secrets.h" に定義しても構いません（存在する場合は自動的に使用されます）
// パスワードやAPIキーなどの機密情報は公開しないよう注意してください
#if __has_include("arduino_secrets.h")
#include "arduino_secrets.h"
#else
#define WIFI_SSID "YourSSID"         // Enter your Wi-Fi SSID here / Wi-FiのSSIDを入力
#define WIFI_PASS "YourPassword"     // Enter your Wi-Fi password here / Wi-Fiのパスワードを入力
#define WIFI_TEST_HOST "example.com" // Hostname for testing Wi-Fi connection / Wi-Fi接続確認用のホスト名
#define WIFI_TEST_PORT 443           // Port for testing Wi-Fi connection / Wi-Fi接続確認用のポート番号
#endif
#pragma endregion UserSettings

WiFiClientSecure client;

void setup()
{
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(250);
  }

  client.setCACertBundle(x509_crt_bundle, x509_crt_bundle_len);
  if (!client.connect(WIFI_TEST_HOST, WIFI_TEST_PORT))
  {
    Serial.println("TLS connection failed");
    return;
  }

  client.println("GET / HTTP/1.1\r\nHost: " WIFI_TEST_HOST "\r\nConnection: close\r\n\r\n");
}

void loop()
{
  while (client.connected() || client.available())
  {
    while (client.available())
    {
      Serial.write(client.read());
    }
  }
  client.stop();
  delay(10000);
}
