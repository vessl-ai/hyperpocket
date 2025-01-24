import json

import httpx


def client_example():
    URL = "http://localhost:8008/chat"
    client = httpx.Client()

    thread_id = None
    while True:
        print("user(q to quit) : ", end="")
        user_input = input()

        if user_input == "q":
            break

        with client.stream(
                "POST", URL, json={"message": user_input, 'thread_id': thread_id}, timeout=180
        ) as response:
            if tid := response.headers.get('x-pocket-langgraph-thread-id'):
                thread_id = tid
            for line in response.iter_lines():
                message = json.loads(line)
                print(f"[{message['type']}] message : {message['content']}" "\n")


if __name__ == "__main__":
    client_example()
