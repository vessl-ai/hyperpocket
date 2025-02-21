# CrewAI

**CrewAI** CrewAI is an opensource-framework for orchestrating autonomous AI agents. Hyperpocket tools can be seamlessly integrated for dynamic actions.

Just use the following example to get started.

## Installation

To incorporate this tool into your project, follow the installation steps below:

```shell
pip install hyperpocket
pip install hyperpocket_crewai
pip install 'crewai[tools]'
```

if you like `uv` instead of `pip`, you can use the following command:

```shell
uv add hyperpocket hyperpocket_crewai crewai
```

## Step-by-step guide

1. Initialize HyperPocket

```python
pocket = PocketCrewAI(
  tools=[
    "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/list-gmail",
  ]
)
```

2. Define crewai agent

```python
crewai_agent = Agent(
  role="Gmail Agent",
  goal="You take action on Gmail using Gmail APIs",
  backstory=(
    "You are AI agent that is responsible for taking actions on Gmail"
  ),
  tools=pocket.get_tools()
)
```

3. (Optional) Trigger authentication in initialization of your agent

```python
pocket.init()
```

This will trigger the authentication process when the agent fires up.

If you skip this, authentication process will be triggered when the tool is called.

4. Execute task

```python
task = Task(
    description="List all emails in Gmail inbox",
    agent=crewai_agent,
    expected_output="A list of emails from Gmail inbox with their details",
)

task.execute()
```

## More details

- More detailed list of tools can be found [here](https://github.com/vessl-ai/hyperpocket/tree/main/tools)

## Example: Using google calendar, slack, github with CrewAI

```python
from crewai import Agent
from crewai.project import CrewBase, agent
from hyperpocket_crewai import PocketCrewAI

@CrewBase
class YourCrew:
    """Your Crew"""

    def __init__(self):
        # Initialize PocketCrewAI with the desired tools.
        self.pocket = PocketCrewAI(
            tools=[
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-message",
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-calendar-events",
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-calendar-list",
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/github/list-pull-requests",
            ]
        )

        # (Optional) If you use tools that require authentication,
        # call init() during the initialization phase.
        self.pocket.init()

    @agent
    def your_agent(self) -> Agent:
        return Agent(
            role=ROLE,
            llm=LLM,
            goal=GOAL,
            backstory=BACKSTORY,
            tools=self.pocket.get_tools()
        )
```
