node_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyScript Offline</title>
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
    import { WebContainer } from 'https://esm.run/@webcontainer/api@1.5.1';
    function decodeContent(content) {
        return Uint8Array.from(atob(content), c => c.charCodeAt(0));
    }
    function decodeFileTree(filetree) {
        const decoded = {};
        for (const [key, value] of Object.entries(filetree)) {
            if (value.file) {
                decoded[key] = {
                    file: {
                        contents: decodeContent(value.file.contents)
                    }
                }
            } else if (value.directory) {
                decoded[key] = {
                    directory: decodeFileTree(value.directory)
                }
            } else if (value.symlink) {
                decoded[key] = {
                    symlink: value.symlink
                }
            }
        }
        return decoded;
    }
    async function main() {
        loadConfig();
        const b64FilesResp = await fetch(`/tools/wasm/scripts/${globalThis.toolConfigs.scriptID}/file_tree`);
        const b64Files = await b64FilesResp.json();
        const files = decodeFileTree(b64Files.tree);
        const webcontainer = await WebContainer.boot();
        
        await webcontainer.mount(files)
        const envs = JSON.parse(globalThis.toolConfigs.envs)
        envs['DEPLOYED'] = 'true'
        const runProcess = await webcontainer.spawn('node', ['dist/index.js'], {
            output: true,
            env: envs,
        });
        const stdin = runProcess.input.getWriter();
        const decodedBytes = atob(globalThis.toolConfigs.body);
        await (async () => {
            await stdin.ready
            await stdin.write(decodedBytes);
        })()
        let stdout = '';
        runProcess.output.pipeTo(
            new WritableStream({
                write(chunk) {
                    stdout += chunk;
                }
            })
        )
        await runProcess.exit;
        if (stdout.startsWith(decodedBytes)) {
            stdout = stdout.slice(decodedBytes);
        }
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
"""
