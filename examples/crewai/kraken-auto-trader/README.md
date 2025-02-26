# KrakenAutoTrader Crew

Welcome to the KrakenAutoTrader Crew project, powered by [crewAI](https://crewai.com). This project targets automating cryptocurrency leveraging Kraken service.

> Notes: USE AT YOUR OWN RISK. LLM might generate hallucinations. To put simply, they can make a big mistake with your assets. Hyperpocket maintainers are not responsible for any possible financial loses.

## Requirements

- Docker Desktop
- Python >=3.10, <3.13

## Installation

Ensure you have Python >=3.10 <3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/kraken_auto_trader/config/agents.yaml` to define your agents
- Modify `src/kraken_auto_trader/config/tasks.yaml` to define your tasks
- Modify `src/kraken_auto_trader/crew.py` to add your own logic, tools and specific args
- Modify `src/kraken_auto_trader/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the kraken-auto-trader Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The kraken-auto-trader Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

