import cv2
import threading


class Camera:

    def __init__(self, index=0, width=640, height=480):

        if isinstance(index, str):
            self.cap = cv2.VideoCapture(index)
        else:
            self.cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap.release()
            raise RuntimeError(f"Unable to open camera {index}.")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self.frame = None
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._consecutive_failures = 0
        self.last_error = None

        # Start capture thread
        self.thread = threading.Thread(target=self.update, name="camera-capture")
        self.thread.start()

    def update(self):

        while not self._stop_event.is_set():
            try:
                ret, frame = self.cap.read()
            except cv2.error as error:
                if not self._stop_event.is_set():
                    self.last_error = f"Camera read failed: {error}"
                break

            if ret:
                with self._lock:
                    self.frame = frame
                self._consecutive_failures = 0
                self.last_error = None
            else:
                self._consecutive_failures += 1
                if self._consecutive_failures >= 30:
                    self.last_error = "Camera stopped returning frames."
                self._stop_event.wait(0.01)

            # Yield briefly so a high-FPS camera does not monopolize a CPU core.
            self._stop_event.wait(0.001)

    def get_frame(self):

        with self._lock:
            return None if self.frame is None else self.frame.copy()

    def has_failed(self):
        return self.last_error is not None

    def release(self):

        self._stop_event.set()
        self.cap.release()
        self.thread.join(timeout=2.0)
