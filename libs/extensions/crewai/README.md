## CrewAI extensions

### Use Pocket Tools

```python
from crewai import Agent
from crewai.project import CrewBase, agent
from hyperpocket_crewai import PocketCrewAI


@CrewBase
class YourCrew:
    """Your Crew"""

    def __init__(self):
        self.pocket = PocketCrewAI(
            tools=[
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages",
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-calendar-events",
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-calendar-list",
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/github/list-pull-requests",
            ]
        )

        # (optional) if you use tools that require authentication.
        self.pocket.init()

    @agent
    def your_agent(self) -> Agent:
        return Agent(
            role=ROLE,
            llm=LLM,
            goal=GOAL,
            backstroy=BACKSTORY,
            tools=self.pocket.get_tools()
        )
```

if you want to use tools that require authentication,
you should call `PocketCrewAI.init()` during the init phase.

since CrewAI basically works as a batch system, it doesn't allow to interact during execution.

therefore, all necessary authentication processes must be completed before it starts.

And then, you can see all the required authentication urls during the init phase.

```text
[SLACK]
        User needs to authenticate using the following URL: https://slack.com/oauth/v2/authorize?...
[GOOGLE]
        User needs to authenticate using the following URL: https://accounts.google.com/o/oauth2/v2/auth?...
[GITHUB]
        User needs to authenticate using the following URL: https://github.com/login/oauth/authorize?...
```

after completing all authentication urls, it will proceed to the next step and start the tasks.
