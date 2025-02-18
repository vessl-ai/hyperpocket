from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from hyperpocket_crewai import PocketCrewAI


# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class ScheduleSummarizer:
    """Scheduler Summarizer crew"""

    def __init__(self):
        self.pocket = PocketCrewAI(
            tools=[
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-message",
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-calendar-events",
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-calendar-list",
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/github/list-pull-requests",
            ]
        )
        self.pocket.init()

    @agent
    def slack_agent(self) -> Agent:
        return Agent(
            role="slack agent",
            llm="gpt-4o",
            goal="process slack related job",
            backstory="slack agent",
            tools=self.pocket.get_tools(),
            verbose=True
        )

    @agent
    def github_agent(self) -> Agent:
        return Agent(
            role="github agent",
            llm="gpt-4o",
            goal="process github related job",
            backstory="github agent",
            tools=self.pocket.get_tools(),
            verbose=True
        )

    @agent
    def google_calendar_agent(self) -> Agent:
        return Agent(
            role="google calendar agent",
            llm="gpt-4o",
            goal="process google calendar related job",
            backstory="google calendar agent",
            tools=self.pocket.get_tools(),
            verbose=True
        )

    @agent
    def summarizer(self) -> Agent:
        return Agent(
            role="work summarizer",
            llm="gpt-4",
            goal="summarize all of the work sources, manage works, and list today's works",
            backstory="work summarizer",
            verbose=True
        )

    @task
    def slack_summarize(self) -> Task:
        return Task(
            description="summarize slack message and extract some works to do in today. read recently 5 slack message from `{slack_channel}` channel. current date: {current_date}",
            expected_output="A comprehensive summary of the slack messages and work list",
            agent=self.slack_agent(),
            output_file="output/slack_summary.txt"
        )

    @task
    def github_summarize(self) -> Task:
        return Task(
            description="get user's ongoing github pr from {github_org}/{github_repo} and get detailed information of the prs",
            expected_output="github pr list and detail information",
            agent=self.github_agent(),
            output_file="output/github_pr.txt"
        )

    @task
    def google_meeting_summarize(self) -> Task:
        return Task(
            description="get user's today google calendar meeting schedule. current date: {current_date}",
            expected_output="google calendar meeting schedule list",
            agent=self.google_calendar_agent(),
            output_file="output/google_calendar_summary.txt"
        )

    @task
    def total_summarize(self) -> Task:
        return Task(
            description=f"list all of the works and summarize, schedule",
            expected_output="today's todo list and schedule.",
            agent=self.summarizer(),
            input=["google_meeting_summarize", "github_summarize", "slack_summarize"],
            output_file="output/summary.txt"
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # Automatically collected from @agent methods
            tasks=self.tasks,  # Automatically collected from @task methods
            process=Process.sequential,
            verbose=True
        )
