from typing import Callable, Tuple

from hyperdock_langchain import converter

_default_dict = None

Converter = Callable[[str, str], Tuple[str, str]]


class EnvDict(object):
    _rules: dict[str, Converter]

    def __init__(self) -> None:
        # K(pocket auth key) -> V(tool env key)
        self._rules = {
            "SLACK_BOT_TOKEN": converter.slack_bot_token,
            "GOOGLE_TOKEN": converter.google_application_credentials,
        }

    @property
    def rules(self) -> dict[str, Converter]:
        return self._rules.copy()

    @classmethod
    def default(cls) -> "EnvDict":
        global _default_dict
        if _default_dict is None:
            _default_dict = EnvDict()
        return _default_dict
