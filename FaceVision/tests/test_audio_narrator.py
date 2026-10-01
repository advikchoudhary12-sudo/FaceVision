import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from core.audio_narrator import AudioNarrator


class AudioNarratorTests(unittest.TestCase):
    def test_voice_mapping_and_path_traversal_guard(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            narrator = AudioNarrator(
                root,
                {"Ayan": "Ayan.mp3", "unknown": "unknown.mp3"},
                replay_cooldown_ms=5000,
            )
            try:
                self.assertEqual(narrator._voice_path("Ayan"), root / "Ayan.mp3")
                self.assertEqual(narrator._voice_path("unknown"), root / "unknown.mp3")
                with self.assertRaises(ValueError):
                    narrator._voice_path("../outside")
            finally:
                narrator.close()

    def test_default_voice_is_used_when_identity_prompt_is_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            narrator = AudioNarrator(
                root,
                {"default": "activation.mp3"},
                replay_cooldown_ms=5000,
            )
            try:
                self.assertEqual(
                    narrator._voice_path("Advik"),
                    root / "activation.mp3",
                )
                self.assertEqual(
                    narrator._voice_path("default"),
                    root / "activation.mp3",
                )
            finally:
                narrator.close()

    def test_activation_without_detected_faces_queues_default_prompt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            narrator = AudioNarrator(
                Path(temp_dir),
                {"default": "activation.mp3"},
                replay_cooldown_ms=5000,
            )
            try:
                narrator.enqueue_activation([])
                self.assertEqual(narrator._queue.get_nowait(), "default")
                narrator._queue.task_done()
            finally:
                narrator.close()

    def test_same_identity_is_suppressed_until_cooldown_expires(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = Path(temp_dir) / "Ayan.mp3"
            audio_path.touch()
            narrator = AudioNarrator(Path(temp_dir), {}, replay_cooldown_ms=5000)
            play_count = []
            music = SimpleNamespace(
                load=lambda _path: None,
                play=lambda: play_count.append("played"),
                get_busy=lambda: False,
            )
            narrator._get_pygame = lambda: SimpleNamespace(
                mixer=SimpleNamespace(music=music)
            )
            try:
                with patch(
                    "core.audio_narrator.monotonic",
                    side_effect=[10, 10, 12, 15, 15],
                ):
                    narrator._play("Ayan")
                    narrator._play("Ayan")
                    narrator._play("Ayan")
                self.assertEqual(play_count, ["played", "played"])
            finally:
                narrator.close()

    def test_mixer_initialization_failure_reports_actual_exception(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            narrator = AudioNarrator(Path(temp_dir), {}, replay_cooldown_ms=5000)
            pygame = SimpleNamespace(
                version=SimpleNamespace(ver="test"),
                __file__="pygame.py",
                mixer=SimpleNamespace(
                    get_init=lambda: None,
                    init=lambda: (_ for _ in ()).throw(RuntimeError("no audio device")),
                ),
            )
            try:
                with patch.dict("sys.modules", {"pygame": pygame}):
                    with self.assertRaisesRegex(
                        RuntimeError, "Could not initialize MP3 playback: no audio device"
                    ):
                        narrator._get_pygame()
            finally:
                narrator.close()

    def test_playback_failure_reports_filename_and_actual_exception(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = Path(temp_dir) / "Ayan.mp3"
            audio_path.touch()
            narrator = AudioNarrator(Path(temp_dir), {}, replay_cooldown_ms=5000)
            music = SimpleNamespace(
                load=lambda _path: (_ for _ in ()).throw(OSError("unsupported MP3")),
                play=lambda: None,
                get_busy=lambda: False,
            )
            narrator._get_pygame = lambda: SimpleNamespace(
                mixer=SimpleNamespace(music=music)
            )
            try:
                with self.assertRaises(RuntimeError) as context:
                    narrator._play("Ayan")
                self.assertIn(str(audio_path), str(context.exception))
                self.assertIn("unsupported MP3", str(context.exception))
            finally:
                narrator.close()


if __name__ == "__main__":
    unittest.main()
