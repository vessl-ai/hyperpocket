import base64


def get_encoded_str(target: str) -> str:
    encoded = base64.b64encode(target.encode("utf-8")).decode("utf-8")
    return encoded.rstrip("=")
