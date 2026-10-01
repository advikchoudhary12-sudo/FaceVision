# ESP32-CAM firmware

The `ESP_32/ESP_32/` sketch is the ESP32 camera web-server firmware configured for the **AI Thinker ESP32-CAM** board.

| File | Responsibility |
| --- | --- |
| `ESP_32.ino` | Wi-Fi connection, camera initialization, and web-server startup. |
| `wifi_secrets.example.h` | Safe Wi-Fi credential template. |
| `wifi_secrets.h` | Your local Wi-Fi credentials; ignored by Git. |
| `board_config.h` | Selects `CAMERA_MODEL_AI_THINKER`. |
| `camera_pins.h` | Pin mappings for supported ESP32 camera boards. |
| `app_httpd.cpp` | HTTP controls and MJPEG `/stream` endpoint on port 81. |
| `camera_index.h` | Web interface assets. |
| `partitions.csv` | Firmware partition layout. |
| `ci.yml` | Continuous-integration configuration for firmware checks. |

## Flashing

1. Copy `wifi_secrets.example.h` to `wifi_secrets.h`.
2. Add your Wi-Fi name and password only to `wifi_secrets.h`.
3. In Arduino IDE, select **AI Thinker ESP32-CAM** and flash `ESP_32.ino`.
4. Read the device IP in Serial Monitor, then set `ESP32_STREAM_URL = "http://<ESP32-IP>:81/stream"` in `FaceVision/local_settings.py`.

## Separate blind-stick controller

`../FaceVision/BlindStick/ESP32/BlindStick.ino` is for the separate ESP32-S3
SuperMini and HC-SR04; it does not change the AI Thinker camera firmware. Set
`TRIG_PIN` and `ECHO_PIN` near the top of the sketch to the pins you wired.
Copy `blind_stick_secrets.example.h` to `blind_stick_secrets.h` in the sketch
folder and configure Wi-Fi plus the existing FaceVision Blynk device token.
Install the Blynk library in Arduino IDE before building.

The controller sets Blynk V10 high once when an obstacle first enters the
configured range, then resets it only after the obstacle stays clear for
`OBSTACLE_CLEAR_TIME_MS` and `TRIGGER_COOLDOWN_MS` has expired. FaceVision
listens to the Blynk datastream using the existing `BLYNK_AUTH_TOKEN` and
`BLIND_STICK_PIN` setting in `FaceVision/local_settings.py`. If using an
HC-SR04 powered at 5 V, level-shift its ECHO output to 3.3 V before connecting
it to an ESP32-S3 GPIO.
