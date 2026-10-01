"""Queue local identity prompts through the computer's default audio output."""

from pathlib import Path
import queue
import sys
import threading
from time import monotonic, sleep


class AudioNarrator:
    def __init__(self, voice_directory: Path, voice_files: dict, replay_cooldown_ms: int):
        if replay_cooldown_ms < 0:
            raise ValueError("Audio replay cooldown cannot be negative.")
        self.voice_directory = Path(voice_directory).resolve()
        self.voice_files = dict(voice_files)
        self.replay_cooldown_seconds = replay_cooldown_ms / 1000.0
        self._last_played: dict[str, float] = {}
        self._pygame = None
        self._audio_error = None
        self._queue: queue.Queue[str | None] = queue.Queue()
        self._thread = threading.Thread(
            target=self._play_queued,
            name="blind-stick-audio",
            daemon=True,
        )
        self._thread.start()

    def enqueue_results(self, names) -> None:
        queued_names = set()
        for name in names:
            audio_key = "unknown" if name == "Unknown" else name
            if not isinstance(audio_key, str) or not audio_key or audio_key in queued_names:
                continue
            queued_names.add(audio_key)
            self._queue.put(audio_key)

    def enqueue_activation(self, names) -> None:
        names = list(names)
        self.enqueue_results(names if names else ["default"])

    def _voice_path(self, name: str) -> Path:
        filename = self.voice_files.get(name)
        if filename is None:
            filename = self.voice_files.get("default", f"{name}.mp3")
        if not isinstance(filename, str) or not filename:
            raise ValueError(f"Invalid voice-file mapping for {name!r}.")
        path = (self.voice_directory / filename).resolve()
        if not path.is_relative_to(self.voice_directory):
            raise ValueError(f"Voice file for {name!r} must be inside the Voice directory.")
        return path

    def _play_queued(self) -> None:
        while True:
            name = self._queue.get()
            try:
                if name is None:
                    return
                self._play(name)
            except Exception as error:
                print(f"[ERROR] Blind-stick audio for {name!r} failed: {error}")
            finally:
                self._queue.task_done()

    def _play(self, name: str) -> None:
        audio_path = self._voice_path(name)
        if not audio_path.is_file():
            print(f"[WARNING] Blind-stick voice prompt not found: {audio_path}")
            return

        now = monotonic()
        previous_play = self._last_played.get(name)
        if previous_play is not None and now - previous_play < self.replay_cooldown_seconds:
            print(f"[INFO] Suppressed repeated blind-stick audio for {name!r}.")
            return

        pygame = self._get_pygame()
        try:
            pygame.mixer.music.load(str(audio_path))
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                sleep(0.05)
        except Exception as error:
            raise RuntimeError(
                f"Could not play MP3 file {audio_path}: {error}"
            ) from error
        self._last_played[name] = monotonic()

    def _get_pygame(self):
        if self._audio_error is not None:
            raise RuntimeError(self._audio_error)
        if self._pygame is None:
            try:
                import pygame
            except ImportError as error:
                self._audio_error = f"Could not import pygame: {error}"
                print(
                    f"[ERROR] Blind-stick audio pygame import failed "
                    f"(Python: {sys.executable}): {error}"
                )
                raise RuntimeError(self._audio_error) from error
            print(
                "[INFO] Blind-stick audio pygame loaded "
                f"(Python: {sys.executable}, "
                f"pygame version: {pygame.version.ver}, "
                f"module: {pygame.__file__})."
            )
            try:
                mixer_status = pygame.mixer.get_init()
                print(
                    "[INFO] Blind-stick audio mixer initialization status: "
                    f"{mixer_status!r}."
                )
                if not mixer_status:
                    pygame.mixer.init()
                mixer_status = pygame.mixer.get_init()
                print(
                    "[INFO] Blind-stick audio mixer initialization status: "
                    f"{mixer_status!r}."
                )
            except Exception as error:
                self._audio_error = f"Could not initialize MP3 playback: {error}"
                print(
                    "[ERROR] Blind-stick audio mixer initialization failed "
                    f"(Python: {sys.executable}, pygame version: "
                    f"{pygame.version.ver}, module: {pygame.__file__}): {error}"
                )
                raise RuntimeError(self._audio_error) from error
            self._pygame = pygame
        return self._pygame

    def close(self) -> None:
        self._queue.put(None)
        self._thread.join()
        if self._pygame is not None and self._pygame.mixer.get_init():
            self._pygame.mixer.quit()
