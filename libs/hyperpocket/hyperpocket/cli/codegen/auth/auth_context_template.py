from jinja2 import Template


def get_auth_context_template() -> Template:
    return Template("""
from hyperpocket.auth.context import AuthContext
class {{ capitalized_service_name }}AuthContext(AuthContext):
    _ACCESS_TOKEN_KEY: str = "{{ upper_service_name }}_TOKEN"
    def to_dict(self) -> dict[str, str]:
        return {
            self._ACCESS_TOKEN_KEY: self.access_token,
        }
    def to_profiled_dict(self, profile: str) -> dict[str, str]:
        return {
            f"{profile.upper()}_{self._ACCESS_TOKEN_KEY}": self.access_token,
        }
""")
