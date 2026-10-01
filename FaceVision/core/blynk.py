"""Small, non-blocking client for Blynk's device HTTPS API."""

from concurrent.futures import ThreadPoolExecutor
import threading
from time import monotonic
from urllib.parse import urlencode
from urllib.request import urlopen


class BlynkClient:
    def __init__(self, token, server="https://blynk.cloud", timeout=3.0):
        self.token = token.strip()
        self.server = server.rstrip("/")
        self.timeout = timeout
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="blynk")
        self._last_error = None

    @property
    def enabled(self):
        return bool(self.token)

    def update(self, values):
        """Update virtual-pin values without slowing recognition."""
        if not self.enabled:
            return
        payload = {"token": self.token, **values}
        self._submit("/external/api/batch/update", payload)

    def trigger_event(self, code, description):
        if not self.enabled or not code:
            return
        self._submit(
            "/external/api/logEvent",
            {"token": self.token, "code": code, "description": description},
        )

    def _submit(self, path, payload):
        self._executor.submit(self._request, path, payload)

    def _request(self, path, payload):
        try:
            with urlopen(f"{self.server}{path}?{urlencode(payload)}", timeout=self.timeout) as response:
                response.read()
            self._last_error = None
        except Exception as error:  # Blynk must never stop the camera pipeline.
            self._last_error = str(error)

    def close(self):
        self._executor.shutdown(wait=False, cancel_futures=True)


class BlynkPinListener:
    """Watch a Blynk datastream for a low-to-high trigger transition."""

    def __init__(
        self,
        token,
        pin,
        on_trigger,
        server="https://blynk.cloud",
        poll_interval=1.0,
        timeout=5.0,
    ):
        self.token = token.strip()
        self.pin = pin.strip().lower()
        self.on_trigger = on_trigger
        self.server = server.rstrip("/")
        self.poll_interval = poll_interval
        self.timeout = timeout
        self._stop_event = threading.Event()
        self._thread = None
        self._last_value = None
        self._last_error = None

        if not self.token:
            raise ValueError("A blind-stick Blynk device token is required.")
        if not self.pin.startswith("v") or not self.pin[1:].isdigit():
            raise ValueError(f"Invalid Blynk virtual pin: {pin}")
        if self.poll_interval <= 0:
            raise ValueError("Blynk pin poll interval must be greater than zero.")

    def start(self):
        if self._thread is not None:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._poll,
            name="blind-stick-blynk-listener",
            daemon=True,
        )
        self._thread.start()

    def _read_pin(self):
        query = urlencode({"token": self.token})
        with urlopen(
            f"{self.server}/external/api/get?{query}&{self.pin}",
            timeout=self.timeout,
        ) as response:
            value = response.read().decode("utf-8").strip()

        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        if value not in ("0", "1"):
            raise ValueError(f"Blynk {self.pin} returned an unexpected value: {value!r}")
        return value == "1"

    def _poll(self):
        while not self._stop_event.is_set():
            try:
                self.poll_once()
                if self._last_error is not None:
                    print("[INFO] Blind-stick Blynk listener reconnected.")
                self._last_error = None
            except Exception as error:
                safe_error = str(error).replace(self.token, "[redacted]")
                if safe_error != self._last_error:
                    print(f"[WARNING] Blind-stick Blynk poll failed: {safe_error}")
                    self._last_error = safe_error
            self._stop_event.wait(self.poll_interval)

    def poll_once(self):
        value = self._read_pin()
        if value and self._last_value is not True:
            self.on_trigger()
        self._last_value = value

    def stop(self):
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=self.timeout + self.poll_interval + 1)
            self._thread = None
