# ESP32 Certificate Bundle

[日本語版 README](README.ja.md) も利用できます。

## Overview
This repository hosts an Arduino-compatible library that supplies an ESP32 device with an up-to-date X.509 root certificate bundle. A pre-generated header is included so you can reference the bundle immediately without running any tooling.

## Features
- Ships a pre-generated `x509_crt_bundle` array ready for use with `esp_crt_bundle_attach()`.
- Works out of the box with Arduino-ESP32 v3.x (IDF 5 base) and compatible frameworks.
- Includes regeneration tooling for maintainers who want to refresh the bundle.

## Using in Arduino Sketches
1. Install this library into your Arduino `libraries` folder or include it as a PlatformIO dependency.
2. Include the generated header in your sketch:
   ```cpp
   #include <WiFiClientSecure.h>
   #include "esp32_cert_bundle.h"

   void setup() {
     WiFi.begin(ssid, password);
     // Wait for connection ...
     WiFiClientSecure client;
     client.setCACertBundle(x509_crt_bundle, x509_crt_bundle_len);
   }
   ```
3. Pass the bundle when configuring TLS clients such as `WiFiClientSecure`, `HTTPClient`, or `PubSubClient`.
4. Perform end-to-end testing against a known HTTPS endpoint (e.g., `https://example.com`) to confirm certificate validation succeeds.

> **Note:** `setCACertBundle()` loads a consolidated root-CA file. It enables validation against the full public trust store, but the generated header is comparatively large because it embeds every trusted certificate.

## Library Contents
- `src/esp32_cert_bundle.h`: PROGMEM-stored root certificate bundle.
- `examples/BasicUsage/BasicUsage.ino`: Minimal sketch showing HTTPS connectivity.
- `tools/update_bundle.py`: Optional helper for maintainers to regenerate the bundle.

## Regenerating the Certificate Bundle (Advanced)
The pre-generated header is sufficient for most users. If you need to refresh it:

### Prerequisites
- Python 3.8 or later with standard library `hashlib`, `struct`, and `ssl`.
- Python package `cryptography` (`pip install cryptography`).
- `wget` (or another HTTP client such as `curl`) to download the source CA list.
- ESP-IDF `gen_crt_bundle.py` helper script (downloaded automatically by the tool).
- An ESP32 toolchain or Arduino IDE environment for consuming the regenerated header.

### Steps
1. Run the helper to transform the Mozilla CA store into an Arduino-friendly header:
   ```bash
   python tools/update_bundle.py
   ```
   The script downloads (or reuses cached copies of) the Espressif generator and Mozilla CA bundle, invokes `gen_crt_bundle.py`, and writes `src/esp32_cert_bundle.h`.
2. Verify the generated header and commit the changes.

> **Alternative:** If you prefer to drive the Espressif generator manually, fetch `gen_crt_bundle.py` and `cacert.pem` as shown in the Espressif documentation, run `python gen_crt_bundle.py -i cacert.pem`, and then execute `python tools/update_bundle.py` to convert the resulting binary into a header.

> **Tip:** The helper script can accept multiple `-i` arguments if you need to bundle additional private CAs alongside the public Mozilla store.

### Keeping the Bundle Current
- Repeat the regeneration steps whenever the Mozilla trust store is updated.
- Review the diff of the generated header to ensure only certificate content changed.
- If the Espressif script introduces breaking changes, consult the [ESP-IDF documentation](https://docs.espressif.com/projects/esp-idf/) for updated usage notes.

## Automation
- A scheduled GitHub Actions workflow (`.github/workflows/update-bundle.yml`) runs on the first day of every month to refresh the bundle and publish a release when a change is detected.
- Dispatch the workflow manually via *Run workflow* for an on-demand refresh.
- Provide `force_release=true` (and optionally `version_level`) when dispatching to bump the version and publish a release even if the bundle is unchanged.
- Each automated release attaches an Arduino Library Manager–ready archive (`ESP32CertBundle-<version>.zip`) that mirrors the repository layout.

## Contributing
Issues and pull requests are welcome. When contributing, please:
- Describe the motivation for the change and include reproduction steps where applicable.
- Regenerate the certificate bundle if your change depends on updated certificate data.
- Update this documentation when you add new tooling or workflows.

## License
This project is licensed under the Mozilla Public License 2.0. See `LICENSE` for details.
