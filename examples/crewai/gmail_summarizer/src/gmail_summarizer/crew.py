from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from hyperpocket_crewai import PocketCrewAI


@CrewBase
class GmailSummarizer:
    """Gmail Summarization Crew"""

    # YAML Configuration Files
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    gmail_agent_pocket: PocketCrewAI
    sheets_agent_pocket: PocketCrewAI
    slack_agent_pocket: PocketCrewAI

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.gmail_agent_pocket is not None:
            self.gmail_agent_pocket.teardown()
        if self.sheets_agent_pocket is not None:
            self.sheets_agent_pocket.teardown()
        if self.slack_agent_pocket is not None:
            self.slack_agent_pocket.teardown()

    # Agents
    @agent
    def gmail_agent(self) -> Agent:
        self.gmail_agent_pocket = PocketCrewAI(
            tools=[
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/list-gmail"
            ]
        )
        self.gmail_agent_pocket.init()

        return Agent(
            config=self.agents_config["gmail_agent"],
            tools=self.gmail_agent_pocket.get_tools(),
            verbose=True,
        )

    @agent
    def sheets_agent(self) -> Agent:
        self.sheets_agent_pocket = PocketCrewAI(
            tools=[
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/create-spreadsheet",
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/update-spreadsheet-cells",
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-spreadsheet",
            ]
        )
        self.sheets_agent_pocket.init()

        return Agent(
            config=self.agents_config["sheets_agent"],
            tools=self.sheets_agent_pocket.get_tools(),
            verbose=True,
        )

    @agent
    def slack_agent(self) -> Agent:
        self.slack_agent_pocket = PocketCrewAI(
            tools=[
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
            ]
        )
        self.slack_agent_pocket.init()

        return Agent(
            config=self.agents_config["slack_agent"],
            tools=self.slack_agent_pocket.get_tools(),
            verbose=True,
        )

    # Tasks
    @task
    def fetch_and_summarize_emails(self) -> Task:
        return Task(
            config=self.tasks_config["fetch_and_summarize_emails"],
        )

    @task
    def create_spreadsheet(self) -> Task:
        return Task(
            config=self.tasks_config["create_spreadsheet"],
        )

    @task
    def send_slack_notification(self) -> Task:
        return Task(
            config=self.tasks_config["send_slack_notification"],
        )

    # Crew Definition
    @crew
    def crew(self) -> Crew:
        """Creates the GmailSummarizer crew"""
        return Crew(
            agents=self.agents,  # Automatically created by @agent decorator
            tasks=self.tasks,  # Automatically created by @task decorator
            process=Process.sequential,  # Run tasks in order
            verbose=True,
        )
