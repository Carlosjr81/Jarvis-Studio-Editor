import math
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import wave
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
from narrate import chunks, download_reference, inspect_wav, prepare_reference

class VoiceChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "voice.wav"

    def wav(self, seconds=1, channels=1, silence=False):
        rate = 16000
        samples = [0 if silence else int(4000 * math.sin(2 * math.pi * 220 * i / rate))
                   for i in range(int(seconds * rate))]
        raw = b"".join(struct.pack("<h", v) * channels for v in samples)
        with wave.open(str(self.path), "wb") as out:
            out.setnchannels(channels)
            out.setsampwidth(2)
            out.setframerate(rate)
            out.writeframes(raw)

    def test_valid_audio_has_expected_duration(self):
        self.wav()
        info = inspect_wav(self.path)
        self.assertEqual(info["duration_seconds"], 1)
        self.assertGreater(info["rms"], .01)

    def test_silence_rejected(self):
        self.wav(silence=True)
        with self.assertRaises(ValueError):
            inspect_wav(self.path)

    def test_stereo_rejected(self):
        self.wav(channels=2)
        with self.assertRaises(ValueError):
            inspect_wav(self.path)

    def test_truncated_pcm_rejected(self):
        self.wav()
        self.path.write_bytes(self.path.read_bytes()[:-100])
        with self.assertRaisesRegex(ValueError, "truncado"):
            inspect_wav(self.path)

    def test_short_reference_rejected(self):
        self.wav(seconds=1)
        with self.assertRaises(ValueError):
            inspect_wav(self.path, min_seconds=3, max_seconds=30)

    def test_split_does_not_drop_words(self):
        text = "Quer manter o Treino Livre gratuito? " + "Compartilha com quem treina. " * 20
        pieces = chunks(text, limit=80)
        self.assertEqual(" ".join(pieces), " ".join(text.split()))
        self.assertTrue(all(len(p) <= 80 for p in pieces))

    def test_empty_script_rejected(self):
        with self.assertRaises(ValueError):
            chunks("  ")

    def test_missing_reference_cannot_fall_back(self):
        with self.assertRaises(ValueError):
            prepare_reference(Path(self.tmp.name) / "missing.mp3", self.path)

    def test_private_reference_origin_is_restricted(self):
        for url in ["", "http://resource2.heygen.ai/x", "https://example.com/x",
                    "https://resource2.heygen.ai.evil.example/x"]:
            with self.subTest(url=url), patch.dict("os.environ", {"VOICE_TEST_URL": url}):
                with self.assertRaises(ValueError):
                    download_reference("VOICE_TEST_URL", self.path)

    def test_download_error_does_not_expose_url(self):
        private_url = "https://resource2.heygen.ai/private.mp3?token=do-not-log"
        with patch.dict("os.environ", {"VOICE_TEST_URL": private_url}), \
             patch("urllib.request.OpenerDirector.open", side_effect=RuntimeError(private_url)):
            with self.assertRaises(ValueError) as caught:
                download_reference("VOICE_TEST_URL", self.path)
        self.assertNotIn("do-not-log", str(caught.exception))
        self.assertNotIn(private_url, str(caught.exception))

if __name__ == "__main__":
    unittest.main()
