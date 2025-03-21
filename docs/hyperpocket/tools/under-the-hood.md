# Under the hood - how HyperPocket runs tool securely and universally

Hyperpocket utilizes wasm to run tools in a secure environment. This allows Hyperpocket to run tools in a sandboxed environment, ensuring that the tools do not have access to the host system and have flexibility to run tools in any language.

## WASM based tools

### How it executes - Pyodide and Playwright for WASM tools

Hyperpocket uses pyodide to run tools in a secure environment. Pyodide is a Python environment that runs entirely in the browser. It is a full Python environment that includes the Python standard library and many popular packages.

When you run a tool in Hyperpocket, the tool is loaded onto WebAssembly (wasm) version of python interpreter using Pyodide. The wasm code is then executed in a sandboxed environment, ensuring that the tool does not have access to the host system.

Hyperpocket uses Playwright, a Node.js library that provides a high-level API to control headless browsers. Playwright allows us to run the wasm code in a headless browser, ensuring that the tool is executed in a secure environment.

So by the time the tool execution is requested, Hyperpocket launches a headless browser, loads the wasm code, and executes the tool on the browser.

### How does it communicate with the tool

Tools are basically packages that get input by stdin and prints out their output to stdout. Hyperpocket uses this standard input-output mechanism to communicate with the tool.

For the wasm tools, the tools are provided with input data in JSON format. Our wasm interface script reads the input data, passes it to the tool, and reads the output from the tool. And the interface script pings the Hyperpocket core with the output data. (calling `/done` endpoint - what you see in the logs)

### Caching the loaded tool

As it is quite an overhead to launch a headless browser and load the wasm code every time a tool is executed, Hyperpocket caches the loaded tool after the first execution with the browser running.
