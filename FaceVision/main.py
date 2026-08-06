import cv2
from time import monotonic

from config import (
    CAMERA_INDEX,
    FRAME_WIDTH,
    FRAME_HEIGHT,
    PROCESS_EVERY_N_FRAMES,
    SHOW_FPS,
    DISPLAY_SCALE,
    WINDOW_NAME,
    BLYNK_AUTH_TOKEN,
    BLYNK_FPS_PIN,
    BLYNK_STATUS_PIN,
    BLYNK_UNKNOWN_EVENT,
    BLYNK_UPDATE_INTERVAL_SECONDS,
    UNKNOWN_DETECTIONS_REQUIRED,
)

from core.camera import Camera
from core.recognition import Recognition
from core.overlay import Overlay
from core.fps import FPSCounter
from core.blynk import BlynkClient
from launcher import run_launcher


def main():

    # -------------------------
    # Init modules
    # -------------------------
    camera = None
    blynk = None
    try:
        camera_source = run_launcher()
        if camera_source is None:
            print("[INFO] Launch cancelled.")
            return

        camera = Camera(
            index=camera_source,
            width=FRAME_WIDTH,
            height=FRAME_HEIGHT
        )
        recognizer = Recognition()
        overlay = Overlay()
        fps = FPSCounter()
        frame_number = 0
        results = []
        process_every = max(1, PROCESS_EVERY_N_FRAMES)
        unknown_detections = 0
        alert_sent = False
        last_blynk_update = 0.0
        blynk = BlynkClient(BLYNK_AUTH_TOKEN)
        if blynk.enabled:
            blynk.update({BLYNK_STATUS_PIN: 1, BLYNK_FPS_PIN: 0})
            print("[INFO] Blynk integration enabled.")
        else:
            print("[INFO] Blynk disabled: set BLYNK_AUTH_TOKEN in local_settings.py to enable it.")

        print("[INFO] FaceVision started. Press Q to quit.")

        while True:
            frame = camera.get_frame()
            if frame is None:
                if camera.has_failed():
                    raise RuntimeError(camera.last_error)
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
                continue

            # Recognition is the expensive operation. Reuse the latest result
            # between inference frames to keep the UI responsive.
            if frame_number % process_every == 0:
                results = recognizer.process(frame)
                unknown_detections = (
                    unknown_detections + 1
                    if any(face["name"] == "Unknown" for face in results)
                    else 0
                )
                if unknown_detections >= UNKNOWN_DETECTIONS_REQUIRED and not alert_sent:
                    blynk.trigger_event(BLYNK_UNKNOWN_EVENT, "Unknown person detected by FaceVision.")
                    alert_sent = True
                elif unknown_detections == 0:
                    alert_sent = False
            frame_number += 1

            fps.update()
            now = monotonic()
            if now - last_blynk_update >= BLYNK_UPDATE_INTERVAL_SECONDS:
                blynk.update({
                    BLYNK_STATUS_PIN: int(alert_sent),
                    BLYNK_FPS_PIN: round(fps.get_fps(), 1),
                })
                last_blynk_update = now
            overlay.draw(frame, results, fps.get_fps() if SHOW_FPS else None)
            display = cv2.resize(
                frame,
                None,
                fx=DISPLAY_SCALE,
                fy=DISPLAY_SCALE,
                interpolation=cv2.INTER_LINEAR,
            )
            cv2.imshow(WINDOW_NAME, display)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        if camera is not None:
            camera.release()
        if blynk is not None:
            blynk.update({BLYNK_STATUS_PIN: 0})
            blynk.close()
        cv2.destroyAllWindows()

    print("[INFO] FaceVision stopped.")


if __name__ == "__main__":
    main()
