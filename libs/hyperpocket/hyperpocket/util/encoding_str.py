import base64
import hashlib


def encoding_str(target: str) -> str:
    encoded = base64.b64encode(target.encode("utf-8")).decode("utf-8")
    return encoded.rstrip("=")


def short_hashing_str(text, length=10):
    return hashlib.sha256(text.encode()).hexdigest()[:length]
