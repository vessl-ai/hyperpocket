python_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyScript Offline</title>
    <script src="https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js"></script>
</head>
<body>
<script type="module">
    function loadConfig() {
        globalThis.toolConfigs = {
            envs: `{{ ENV_JSON }}`,
            body: `{{ BODY_JSON_B64 }}`,
            scriptID: `{{ SCRIPT_ID }}`
        }
    }
    async function main() {
        loadConfig();
        const b64FilesResp = await fetch(`/tools/wasm/scripts/${globalThis.toolConfigs.scriptID}/file_tree`);
        const b64Files = await b64FilesResp.json();
        const code = atob(b64Files.tree["main.py"].file.contents);
        const requirements = atob(b64Files.tree["requirements.txt"].file.contents);
        
        const pyodide = await loadPyodide({
            env: JSON.parse(globalThis.toolConfigs.envs),
        });
        await pyodide.loadPackage("micropip");
        await pyodide.loadPackage("ssl");
        const micropip = pyodide.pyimport("micropip");
        await micropip.install("pyodide-http")
        const installation = requirements.split("\\n").map(async (req) => {
            if (req) {
                const pkg = req.split("==")[0];
                await micropip.install(pkg);
            }
        });
        await Promise.all(installation);
        let emitted = false;
        const decodedBytes = atob(globalThis.toolConfigs.body);
        pyodide.setStdin({
            stdin: () => {
                if (emitted) {
                    return null;
                }
                emitted = true;
                return decodedBytes;
            },
            autoEOF: true,
        })
        let stdout = "";
        pyodide.setStdout({
            batched: (x) => { stdout += x; },
        })
        await pyodide.runPythonAsync(`
import pyodide_http
pyodide_http.patch_all()

${code}
`);
        console.log(stdout)
        await fetch(`/tools/wasm/scripts/${globalThis.toolConfigs.scriptID}/done`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ stdout })
        });
    }
    main();
</script>
</body>
</html>
'''