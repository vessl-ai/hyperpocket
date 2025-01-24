# Applying Local Tools

## **What is a WASM Local Tool?**

A **WASM Local Tool** in Hyperpocket is a tool stored locally on your system and executed within a secure, isolated *
*WebAssembly (WASM)** environment. This ensures that even local tools run in a sandboxed environment, providing both
flexibility and security.

### **Key Characteristics of WASM Local Tools**

- **Local Execution:** Runs tools directly from your system’s file directory.
- **Sandboxed Environment:** Uses WASM to isolate the execution, preventing interference with the host system.
- **Customizable:** Allows developers to define their own logic, input/output schemas, and configurations.
- **WASM Compatibility:** Supports tools written in multiple languages like Python or Node.js, as long as they are
  WASM-compatible.

## **Benefits of WASM Local Tools**

- **Security:** Sandboxed execution prevents unauthorized access or system interference.
- **Performance:** Local execution reduces dependency on network latency.
- **Customization:** Developers can tailor tools to their specific needs using their preferred programming language.
- **Ease of Integration:** Simple API to load and execute tools seamlessly within Hyperpocket workflows.

### **How to Use Local Tools**

**1️⃣ Define a Local Tool**

A local tool can be any WASM-compatible tool stored in a specified directory. Ensure the tool is structured with the
required configuration files (e.g., schema.json, config.toml).

**2️⃣ Load the Local Tool**

Use the from_local function to load a tool from a specified path.

Example Code: Loading a Local Tool

```python
from hyperpocket import Pocket
from hyperpocket.tool.wasm.tool import from_local

# Load a local WASM tool
tool_request = from_local("/path/to/local/tool")

pocket = Pocket(
    tools=[tool_request]
)

# And more ...
```

or you can just write your local path

```python
from hyperpocket import Pocket

pocket = Pocket(
    tools=[
        "/path/to/local/tool"
    ]
)

# And more ...
```

**3️⃣ Execute the Local Tool**

Once the local tool is loaded, you can execute it using the invoke method.

**Example Code: Executing a Local Tool**

```python
from hyperpocket import Pocket

# Using the Function Tool
if __name__ == "__main__":
    pocket = Pocket(tools=["/path/to/local/tool"])
    tool_result = pocket.invoke(tool_name="get_weather", body={"location": "Seoul"})
    print(tool_result)  # Output: The weather in Seoul is sunny with a high of 25°C.
```

**Structure of a Local Tool Directory**

Your local tool directory should include the following files:

1. config.toml

- Defines the tool’s name, description, and runtime environment.
- Example:

```toml
name = "Example Local Tool"
description = "A local tool example"
language = "python"  # Supported: python, node
```

2. schema.json

- Specifies the tool’s input and output schema.

Example:

```json
{
  "type": "object",
  "properties": {
    "key": {
      "type": "string"
    }
  },
  "required": [
    "key"
  ]
}
```

3. **Tool Script**

- The script or executable logic for the tool, e.g., a Python script or a Node.js file.

Example(Python):

in `my_tool/__main__.py`

```python
import json
import sys
from pydantic import BaseModel


class MyToolRequest(BaseModel):
    arg1: str


def do_something(req: MyToolRequest):
    pass


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = MyToolRequest.model_validate(req)
    print(do_something(req_typed))


if __name__ == '__main__':
    main()
```

- Add your tool code in `__main__.py`
- You can get the input via `stdin`
- You should return your output via `stdout`

in `my_tool/__init__.py`

```python
from my_tool.__main__ import main

__all__ = ["main"]
```

- You should specify your `main` method in `__main__.py` in `__all__`

And Build your code to `dist` and locate this in `my_tool/dist/`


## **When to Use Local Tools?**

WASM Local Tools are ideal for scenarios where:

1. **Custom Logic is Required:** You have specific business logic that cannot be fetched from a remote repository.

2. **Secure Execution is Crucial:** You don't need to upload your code to any other remote spaces.

3. **Offline Availability:** Tools can be accessed and executed without an internet connection.

4. **Flexibility in Testing:** Easy to test and debug local tools before sharing or deploying them remotely.
