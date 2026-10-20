import hashlib
import json
import os
from pathlib import Path
import urllib.parse
import urllib.request
import wave
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def main():
    token = os.environ.get("CARLOS_VOICE_REFERENCE_URL", "").strip()
    if not token:
        raise ValueError("Private transfer key unavailable.")
    envelope = json.loads(Path("voice-transfer/payload.json").read_text())
    key = hashlib.sha256(("jarvis-descript-upload-v1\n" + token).encode()).digest()
    raw = AESGCM(key).decrypt(bytes.fromhex(envelope["nonce"]), bytes.fromhex(envelope["ciphertext"]), None)
    payload = json.loads(raw)
    parsed = urllib.parse.urlsplit(payload["upload_url"])
    if parsed.scheme != "https" or parsed.hostname != "production-273614-assets-us-east4.storage.googleapis.com":
        raise ValueError("Upload destination does not match the existing private Descript project.")
    audio = Path("approved/Treino_Livre_Carlos_Jr.wav")
    data = audio.read_bytes()
    manifest = json.loads(Path("approved/Treino_Livre_Carlos_Jr.json").read_text())
    if hashlib.sha256(data).hexdigest() != manifest["audio_sha256"]:
        raise ValueError("Approved audio checksum mismatch.")
    if len(data) != payload["file_size"]:
        raise ValueError(f"Approved WAV size {len(data)} does not match the declared upload size.")
    with wave.open(str(audio), "rb") as wav:
        if wav.getnchannels() != 1 or wav.getsampwidth() != 2 or wav.getframerate() != 48000:
            raise ValueError("Unexpected approved WAV format.")
        duration = wav.getnframes() / wav.getframerate()
    request = urllib.request.Request(payload["upload_url"], data=data, method="PUT",
                                     headers={"Content-Type": "application/octet-stream"})
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None
    opener = urllib.request.build_opener(NoRedirect())
    with opener.open(request, timeout=120) as response:
        if response.status not in (200, 201):
            raise ValueError("Upload was not accepted.")
    print(json.dumps({"uploaded": True, "bytes": len(data), "duration_seconds": duration}))

try:
    main()
except Exception as exc:
    # Do not log signed URLs, credentials or transport tracebacks.
    print("Approved audio transfer failed: " + type(exc).__name__)
    raise SystemExit(1) from None
