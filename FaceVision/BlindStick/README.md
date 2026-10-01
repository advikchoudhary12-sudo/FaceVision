# FaceVision blind-stick bridge

The blind-stick ESP32-S3 has only the HC-SR04 sensor. It publishes a latched
0/1 value to Blynk V10; it does not contact the camera or play audio. FaceVision
reads that Blynk datastream once per configured poll interval and recognizes one
frame from the already-running `Camera` pipeline on each low-to-high transition.
It does not poll the ultrasonic sensor or start a second camera.

## Configure Blynk

1. Add an integer datastream on virtual pin **V10**, with minimum 0 and maximum
   1, to the existing Blynk template/device used by FaceVision. It must be on
   the device associated with the existing FaceVision Blynk auth token.
2. Copy `ESP32/blind_stick_secrets.example.h` to
   `ESP32/blind_stick_secrets.h`. Set the Wi-Fi credentials, template ID/name,
   and set `BLYNK_AUTH_TOKEN` to the same device auth token already configured
   as `BLYNK_AUTH_TOKEN` in `FaceVision/local_settings.py`.
3. Set `BLIND_STICK_PIN = "V10"` in `FaceVision/local_settings.py`. FaceVision
   reuses its existing `BLYNK_AUTH_TOKEN` to listen to that pin; no separate
   blind-stick token setting is needed.
4. Install the Blynk Arduino library, select an ESP32-S3 board, and flash
   `ESP32/BlindStick.ino`.

The sketch sets V10 high only on a new obstacle detection. It sets V10 low only
after the sensor reports clear continuously for `OBSTACLE_CLEAR_TIME_MS` and
`TRIGGER_COOLDOWN_MS` has expired. A continuously present obstacle therefore
cannot issue repeated triggers.

## Configure voice prompts

Put the MP3 files you provide in `Voice/`, named for the recognition label, for
example `Voice/Ayan.mp3` and `Voice/unknown.mp3`. FaceVision uses the computer's
default audio device; pair headphones through the operating system and select
them as the default output.

`VOICE_FILES` in `FaceVision/local_settings.py` can override the default
`<identity>.mp3` names. Mapping paths are relative to `Voice/`, for example:

```python
VOICE_FILES = {
    "Ayan": "Ayan.mp3",
    "Alice": "Alice.mp3",
    "unknown": "unknown.mp3",
}
```

Each triggered frame is recognized once. No detected faces produce no audio;
all detected identities are queued once in detector order, with `Unknown`
mapped to the lowercase `unknown` prompt. Replays of an identity are suppressed
for `AUDIO_REPLAY_COOLDOWN_MS` from when that audio begins playing.
