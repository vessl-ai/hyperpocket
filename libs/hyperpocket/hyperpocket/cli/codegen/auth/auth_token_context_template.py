from jinja2 import Template


def get_auth_token_context_template() -> Template:
    return Template("""\
from hyperpocket.auth.{{ service_name }}.context import {{ capitalized_service_name }}AuthContext
from hyperpocket.auth.{{ service_name }}.token_schema import {{ capitalized_service_name }}TokenResponse
class {{ capitalized_service_name }}TokenAuthContext({{ capitalized_service_name }}AuthContext):
    @classmethod
    def from_{{ service_name }}_token_response(cls, response: {{ capitalized_service_name }}TokenResponse):
        description = f'{{ capitalized_service_name }} Token Context logged in'
        return cls(
            access_token=response.access_token,
            description=description,
            expires_at=None
        )
""")
