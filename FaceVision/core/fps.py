import time


class FPSCounter:

    def __init__(self):

        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0

    # -------------------------
    # Call every frame
    # -------------------------
    def update(self):

        self.frame_count += 1

        current_time = time.time()
        elapsed = current_time - self.last_time

        # Update FPS every second
        if elapsed >= 1.0:

            self.fps = self.frame_count / elapsed

            self.frame_count = 0
            self.last_time = current_time

    # -------------------------
    # Get current FPS
    # -------------------------
    def get_fps(self):

        return self.fps