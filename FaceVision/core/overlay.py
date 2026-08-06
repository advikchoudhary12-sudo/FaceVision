import cv2


class Overlay:

    def __init__(self):

        self.font = cv2.FONT_HERSHEY_SIMPLEX

    # -------------------------
    # Draw everything on frame
    # -------------------------
    def draw(self, frame, results, fps=None):

        height, width = frame.shape[:2]

        # Draw faces
        for r in results:

            x1, y1, x2, y2 = r["box"]
            x1 = max(0, min(x1, width - 1))
            y1 = max(0, min(y1, height - 1))
            x2 = max(0, min(x2, width - 1))
            y2 = max(0, min(y2, height - 1))
            if x2 <= x1 or y2 <= y1:
                continue
            name = r["name"]
            score = r["score"]

            # Color logic
            if name == "Unknown":
                color = (0, 0, 255)  # red
            else:
                color = (0, 255, 0)  # green

            # Box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Label text
            label = name if score is None else f"{name} {score:.2f}"

            cv2.putText(
                frame,
                label,
                (x1, max(20, y1 - 10)),
                self.font,
                0.7,
                color,
                2
            )

        # FPS display
        if fps is not None:

            cv2.putText(
                frame,
                f"FPS: {fps:.1f}",
                (10, 30),
                self.font,
                1,
                (255, 255, 0),
                2
            )
