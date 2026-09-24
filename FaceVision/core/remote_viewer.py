"""Tiny, dependency-free viewer for FaceVision's finished overlay frames."""

from __future__ import annotations

import json
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import cv2


class RemoteViewer:
    """Serve the newest annotated frame as a phone-friendly MJPEG stream."""

    def __init__(
        self,
        host="0.0.0.0",
        port=8080,
        max_width=800,
        quality=80,
        max_fps=12,
        capture_enabled=True,
    ):
        self.host = host
        self.port = port
        self.max_width = max_width
        self.quality = quality
        self.max_fps = max_fps
        self.capture_enabled = capture_enabled
        self._condition = threading.Condition()
        self._jpeg = None
        self._latest_frame = None
        self._sequence = 0
        self._server = None
        self._thread = None
        self._last_publish = 0.0

    @property
    def url(self):
        return f"http://{self.host}:{self.port}/"

    def start(self):
        """Start serving in the background; return the bound port."""
        if self._server is not None:
            return self._server.server_address[1]

        viewer = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path in ("/", "/index.html"):
                    self._send_page()
                elif self.path == "/stream":
                    self._send_stream()
                elif self.path == "/health":
                    self._send_health()
                elif self.path == "/capture.jpg" and viewer.capture_enabled:
                    self._send_capture()
                else:
                    self.send_error(HTTPStatus.NOT_FOUND)

            def log_message(self, format, *args):
                # A browser requests a steady stream of frames; do not flood the console.
                return

            def _send_page(self):
                capture = (
                    '<p><a href="/capture.jpg"><button type="button">Capture still</button></a></p>'
                    if viewer.capture_enabled
                    else ""
                )
                content = (
                    '<!doctype html><html><head><meta name="viewport" '
                    'content="width=device-width, initial-scale=1"><title>FaceVision Live</title>'
                    '<style>body{margin:0;background:#111;color:#eee;font:16px system-ui;text-align:center}'
                    'header{padding:14px}img{width:100%;max-width:960px;display:block;margin:auto}'
                    'button{padding:10px 18px;font-size:16px}small{color:#aaa}</style></head><body>'
                    '<header><strong>FaceVision Live</strong><br><small>Final processed view</small></header>'
                    '<img src="/stream" alt="Waiting for FaceVision frames">'
                    + capture
                    + "</body></html>"
                ).encode()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(content)

            def _send_health(self):
                with viewer._condition:
                    body = json.dumps({"running": True, "has_frame": viewer._jpeg is not None}).encode()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _send_stream(self):
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
                self.send_header("Pragma", "no-cache")
                self.end_headers()
                sequence = -1
                try:
                    while True:
                        jpeg, sequence = viewer._next_frame(sequence)
                        if jpeg is None:
                            continue
                        self.wfile.write(b"--frame\r\nContent-Type: image/jpeg\r\n")
                        self.wfile.write(f"Content-Length: {len(jpeg)}\r\n\r\n".encode())
                        self.wfile.write(jpeg)
                        self.wfile.write(b"\r\n")
                except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                    pass

            def _send_capture(self):
                with viewer._condition:
                    frame = (
                        None
                        if viewer._latest_frame is None
                        else viewer._latest_frame.copy()
                    )
                if frame is None:
                    self.send_error(HTTPStatus.SERVICE_UNAVAILABLE, "No frame available")
                    return
                encoded, jpeg = cv2.imencode(
                    ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 95]
                )
                if not encoded:
                    self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, "Still capture failed")
                    return
                content = jpeg.tobytes()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Disposition", 'attachment; filename="facevision-still.jpg"')
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)

        class Server(ThreadingHTTPServer):
            daemon_threads = True
            allow_reuse_address = True

        self._server = Server((self.host, self.port), Handler)
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="facevision-remote-viewer",
            daemon=True,
        )
        self._thread.start()
        return self._server.server_address[1]

    def publish(self, frame, now):
        """JPEG-encode a copy of an already-annotated frame at a capped rate."""
        if self._server is None or now - self._last_publish < 1.0 / self.max_fps:
            return
        self._last_publish = now

        with self._condition:
            self._latest_frame = frame.copy()

        height, width = frame.shape[:2]
        if width > self.max_width:
            scale = self.max_width / width
            frame = cv2.resize(frame, (self.max_width, int(height * scale)), interpolation=cv2.INTER_AREA)

        encoded, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, self.quality])
        if not encoded:
            return
        with self._condition:
            self._jpeg = jpeg.tobytes()
            self._sequence += 1
            self._condition.notify_all()

    def _next_frame(self, previous_sequence):
        with self._condition:
            if self._sequence == previous_sequence:
                self._condition.wait(timeout=5.0)
            return self._jpeg, self._sequence

    def stop(self):
        if self._server is None:
            return
        self._server.shutdown()
        self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        self._server = None
        self._thread = None
