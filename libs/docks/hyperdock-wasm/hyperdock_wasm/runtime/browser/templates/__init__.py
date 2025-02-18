import base64
import json

from jinja2 import DictLoader, Environment

from hyperdock_wasm.runtime.browser.templates.node import node_template
from hyperdock_wasm.runtime.browser.templates.python import python_template

TemplateEnvironments = Environment(
    loader=DictLoader(
        {
            "python.html": python_template,
            "node.html": node_template,
        }
    ),
    autoescape=False,
)


def render(
    language: str, script_id: str,  env: dict[str, str], body: str, **kwargs
) -> str:
    env_json = json.dumps(env)
    template = TemplateEnvironments.get_template(f"{language.lower()}.html")
    body_bytes = body.encode("utf-8")
    body_b64_bytes = base64.b64encode(body_bytes)
    body_b64 = body_b64_bytes.decode("ascii")
    return template.render(
        **{
            "SCRIPT_ID": script_id,
            "ENV_JSON": env_json,
            "BODY_JSON_B64": body_b64,
        }
        | kwargs
    )
