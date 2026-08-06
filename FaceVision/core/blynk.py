"""Small, non-blocking client for Blynk's device HTTPS API."""

from concurrent.futures import ThreadPoolExecutor
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
