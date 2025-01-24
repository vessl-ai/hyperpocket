const fs = require('fs')
const util = require('util')
const { LinearClient } = require('@linear/sdk');

function readStdin() {
    if (process.env.DEPLOYED) {
        process.stdin.setRawMode(true);
        return new Promise((resolve) => {
            process.stdin.on('data', function (chunk) {
                resolve(chunk.toString());
            });
        });
    } else {
        return util.promisify(fs.readFile)(0, 'utf-8')
    }
}

async function main() {
    const client = new LinearClient({
        apiKey: process.env.LINEAR_API_KEY
    })
    const data = await readStdin();
    const req = JSON.parse(data.toString())
    const issues = await client.issues({
        filter: {
            title: req.title ? {
                containsIgnoreCase: req.title
            } : undefined,
            team: req.team ? {
                or: [
                    {
                        key: {
                            eqIgnoreCase: req.team
                        }
                    },
                    {
                        name: {
                            eqIgnoreCase: req.team
                        }
                    }
                ]
            } : undefined,
            assignee: req.assignee ? {
                or: [
                    {
                        name: {
                            containsIgnoreCase: req.assignee
                        },
                    },
                    {
                        email: {
                            containsIgnoreCase: req.assignee
                        }
                    }
                ]
            } : undefined,
            state: req.state ? {
                name: {
                    eqIgnoreCase: req.state
                }
            } : undefined
        }
    })
    const descriptions = await Promise.all(issues.nodes.map(async issue => {
        const team = await issue.team;
        const state = await issue.state;
        return `- [${team.key}-${issue.number}] ${issue.title} (priority: ${issue.priority} / ${state.name})`
    }));
    console.log(descriptions.join('\n'))
}

main().catch(console.error).finally(() => process.exit());
