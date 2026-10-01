"""Bridge Blynk Virtual Pin transitions into one-frame FaceVision triggers."""

import threading

from core.blynk import BlynkPinListener


class BlindStickBridge:
    def __init__(
        self,
        token,
        pin,
        server="https://blynk.cloud",
        poll_interval=1.0,
    ):
        self._triggered = threading.Event()
        self._trigger_lock = threading.Lock()
        self._listener = BlynkPinListener(
            token=token,
            pin=pin,
            on_trigger=self._mark_triggered,
            server=server,
            poll_interval=poll_interval,
        )

    def _mark_triggered(self):
        with self._trigger_lock:
            self._triggered.set()

    def start(self):
        self._listener.start()

    def consume_trigger(self) -> bool:
        with self._trigger_lock:
            if not self._triggered.is_set():
                return False
            self._triggered.clear()
            return True

    def stop(self):
        self._listener.stop()
