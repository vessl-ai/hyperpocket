import json
import os
import sys

from pydantic import BaseModel


class EchoRequest(BaseModel):
    text: str


def echo_request(req: EchoRequest):
    env_list = [f"{key}:{value}" for key, value in os.environ.items()]
    env_list_str = "\n\t".join(env_list)
    return f"""echo message : {req.text}\n\t{env_list_str}"""


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = EchoRequest.model_validate(req)
    print(echo_request(req_typed))


if __name__ == '__main__':
    main()
