import numpy as np
import os
import cv2
import onnxruntime as ort

from insightface.app import FaceAnalysis

from config import (
    MODEL_NAME,
    DET_SIZE,
    CTX_ID,
    THRESHOLD,
    KNOWN_FACES_PATH,
    PROCESS_EVERY_N_FRAMES
)


class Recognition:

    def __init__(self):

        # -------------------------
        # Init InsightFace
        # -------------------------
        try:
            self._prepare(CTX_ID)
        except Exception as error:
            if CTX_ID == -1:
                raise
            print(f"[WARN] GPU initialization failed ({error}); falling back to CPU.")
            self._prepare(-1)

        self.known_embeddings = None
        self.known_names = []

        self.load_known_faces()

        print(f"[INFO] Loaded {len(self.known_names)} embeddings")

    def _prepare(self, ctx_id):
        # Load CUDA and cuDNN DLLs installed by the onnxruntime-gpu extras.
        # Without this, Windows can advertise CUDA while model sessions fall
        # back to CPU because their dependent DLLs cannot be found.
        if ctx_id >= 0:
            ort.preload_dlls()
        if ctx_id >= 0 and "CUDAExecutionProvider" not in ort.get_available_providers():
            raise RuntimeError(
                "CUDAExecutionProvider is unavailable; install onnxruntime-gpu and its CUDA/cuDNN runtime dependencies."
            )
        self.app = FaceAnalysis(name=MODEL_NAME)
        self.app.prepare(ctx_id=ctx_id, det_size=DET_SIZE)
        if ctx_id >= 0:
            cpu_models = [
                name
                for name, model in self.app.models.items()
                if "CUDAExecutionProvider" not in model.session.get_providers()
            ]
            if cpu_models:
                raise RuntimeError(
                    "CUDA provider could not initialize for: " + ", ".join(cpu_models)
                )

    # -------------------------
    # Load dataset
    # -------------------------
    def load_known_faces(self):

        folder = KNOWN_FACES_PATH
        if not folder.is_dir():
            raise FileNotFoundError(f"Known-faces directory does not exist: {folder}")

        embeddings = []

        for person in sorted(os.listdir(folder)):

            person_folder = os.path.join(folder, person)

            if not os.path.isdir(person_folder):
                continue

            for file in sorted(os.listdir(person_folder)):

                path = os.path.join(person_folder, file)

                image = cv2.imread(path)

                if image is None:
                    continue

                faces = self.app.get(image)

                if len(faces) == 0:
                    continue

                # Reject ambiguous training images by consistently selecting the
                # largest detected face rather than whichever face is returned first.
                face = max(faces, key=lambda candidate: np.prod(candidate.bbox[2:] - candidate.bbox[:2]))
                emb = face.embedding
                norm = np.linalg.norm(emb)
                if norm == 0:
                    continue
                emb = emb / norm

                embeddings.append(emb)
                self.known_names.append(person)

        if embeddings:
            self.known_embeddings = np.vstack(embeddings)

    # -------------------------
    # Process frame
    # -------------------------
    def process(self, frame):

        results = []

        faces = self.app.get(frame)

        for face in faces:

            emb = face.embedding
            norm = np.linalg.norm(emb)
            if norm == 0:
                continue
            emb = emb / norm

            best_score = None
            best_name = "Unknown"

            if self.known_embeddings is not None:
                scores = self.known_embeddings @ emb
                best_index = int(np.argmax(scores))
                best_score = float(scores[best_index])
                best_name = self.known_names[best_index]

            if best_score is None or best_score < THRESHOLD:
                best_name = "Unknown"

            x1, y1, x2, y2 = face.bbox.astype(int)

            results.append({
                "box": (x1, y1, x2, y2),
                "name": best_name,
                "score": best_score
            })

        return results
