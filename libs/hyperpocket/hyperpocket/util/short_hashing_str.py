import hashlib


def short_hashing_str(text, length=10):
    return hashlib.sha256(text.encode()).hexdigest()[:length]
