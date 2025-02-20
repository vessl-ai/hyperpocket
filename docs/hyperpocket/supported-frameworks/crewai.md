# CrewAI

**CrewAI** CrewAI is an opensource-framework for orchestrating autonomous AI agents. Hyperpocket tools can be seamlessly integrated for dynamic actions.

**Example: Using Hyperpocket with CrewAI**

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
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages",
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
