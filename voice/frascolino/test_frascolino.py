import os
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch
import frascolino

class PrivacyChecks(unittest.TestCase):
    def test_missing_password_blocks_archive(self):
        for password in ["", "short"]:
            with self.assertRaises(ValueError):
                frascolino.check_password(password)

    @patch("socket.getaddrinfo", return_value=[(2, 1, 6, "", ("8.8.8.8", 443))])
    def test_https_url_without_credentials_allowed(self, dns):
        self.assertEqual(frascolino.validate_url("https://example.com/file?signature=private"),
                         "https://example.com/file?signature=private")

    def test_credentials_plain_http_and_custom_port_blocked(self):
        for url in ["", "http://example.com/a", "https://user:pass@example.com/a",
                    "https://example.com:444/a"]:
            with self.assertRaises(ValueError):
                frascolino.validate_url(url)

    @patch("socket.getaddrinfo", return_value=[(2, 1, 6, "", ("127.0.0.1", 443))])
    def test_private_networks_blocked(self, dns):
        with self.assertRaises(ValueError):
            frascolino.validate_url("https://localhost/file")

    def test_transport_failure_redacts_source_url(self):
        private_url = "https://example.com/private?token=do-not-log"
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "reference"
            with patch.dict(os.environ, {"FRASCOLINO_REFERENCE_URL": private_url}), \
                 patch.object(frascolino, "validate_url", return_value=private_url), \
                 patch("urllib.request.OpenerDirector.open", side_effect=RuntimeError(private_url)):
                with self.assertRaises(ValueError) as caught:
                    frascolino.download_reference(target)
                self.assertNotIn(private_url, str(caught.exception))
                self.assertNotIn("do-not-log", str(caught.exception))
                self.assertFalse(target.exists())

    def test_encrypted_bundle_requires_correct_password_and_preserves_files(self):
        import pyzipper
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "private"
            root.mkdir()
            content = b"private-reference-bytes-for-test"
            (root / "reference.wav").write_bytes(content)
            archive = Path(tmp) / "out.zip"
            password = "a-separate-long-test-password"
            frascolino.archive_profile(root, archive, password)
            self.assertEqual((root / "reference.wav").read_bytes(), content)
            with pyzipper.AESZipFile(archive) as bundle:
                with self.assertRaises(RuntimeError):
                    bundle.read(bundle.namelist()[0])
                bundle.setpassword(b"incorrect-password")
                with self.assertRaises(RuntimeError):
                    bundle.read(bundle.namelist()[0])
                bundle.setpassword(password.encode())
                self.assertEqual(bundle.read(bundle.namelist()[0]), content)

    def test_bundle_does_not_overwrite_existing_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "private"
            root.mkdir()
            (root / "reference.wav").write_bytes(b"reference")
            archive = Path(tmp) / "existing.zip"
            archive.write_bytes(b"existing")
            with self.assertRaises(ValueError):
                frascolino.archive_profile(root, archive, "separate-long-test-password")
            self.assertEqual(archive.read_bytes(), b"existing")

if __name__ == "__main__":
    unittest.main()
