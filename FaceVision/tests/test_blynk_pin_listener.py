import unittest
from unittest.mock import patch

from core.blynk import BlynkPinListener


class BlynkPinListenerTests(unittest.TestCase):
    def test_only_low_to_high_transitions_trigger(self):
        triggered = []
        listener = BlynkPinListener(
            "device-token",
            "V10",
            lambda: triggered.append(True),
        )
        values = iter([False, True, True, False, True])
        listener._read_pin = lambda: next(values)

        for _ in range(5):
            listener.poll_once()

        self.assertEqual(triggered, [True, True])

    def test_read_uses_blynk_external_api_get(self):
        listener = BlynkPinListener(
            "device-token",
            "V10",
            lambda: None,
            server="https://blynk.example",
        )

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return b"1"

        with patch("core.blynk.urlopen", return_value=Response()) as open_url:
            self.assertTrue(listener._read_pin())
        self.assertIn("/external/api/get?token=device-token&v10", open_url.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
