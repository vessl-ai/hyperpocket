python_template = """
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
    async function _main() {
        // load the script configs
        loadConfig();
        
        // get entrypoint wheel
        const entrypointResp = await fetch(`/scripts/${globalThis.toolConfigs.scriptID}/entrypoint`);
        const { package_name: packageName, entrypoint } = await entrypointResp.json();
        
        // initialize pyodide
        const pyodide = await loadPyodide({
            env: JSON.parse(globalThis.toolConfigs.envs),
        });
        await pyodide.loadPackage("micropip");
        await pyodide.loadPackage("ssl");
        const micropip = pyodide.pyimport("micropip");
        await micropip.install(entrypoint);
        await micropip.install("pyodide-http")
        
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
        let stderr = "";
        pyodide.setStdout({
            batched: (x) => { stdout += x; },
        })
        pyodide.setStderr({
            batched: (x) => { stderr += x; },
        })
        await pyodide.runPythonAsync(`
import pyodide_http
pyodide_http.patch_all()

import ${packageName}
${packageName}.main()
`);
        console.log(stdout)
        await fetch(`/scripts/${globalThis.toolConfigs.scriptID}/done`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ stdout, stderr })
        });
    }
    
    async function main() {
        try {
            await _main();
        } catch (e) {
            console.error(e);
            await fetch(`/scripts/${globalThis.toolConfigs.scriptID}/done`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ error: e.message })
            });
        }
    }
    
    main();
</script>
</body>
</html>
"""
