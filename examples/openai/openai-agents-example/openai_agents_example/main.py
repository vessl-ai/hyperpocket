from agents import Agent, Runner
import asyncio

from hyperpocket_openai import PocketOpenAI

# Define the hyperpocket tools to use
pocket = PocketOpenAI(
    tools=[
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/list-gmail",
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
    ]
)


gmail_fetch_agent = Agent(
    name="Gmail Fetch Agent",
    tools=pocket.get_openai_agent_tools(),
    handoff_description="Specialist agent for fetching emails from Gmail",
    instructions="You fetch emails from Gmail and return the results.",
)

slack_agent = Agent(
    name="Slack Agent",
    tools=pocket.get_openai_agent_tools(),
    handoff_description="Specialist agent for posting messages to Slack",
    instructions="You post messages to Slack channels when requested.",
)

summarize_agent = Agent(
    name="Summarize Agent",
    tools=pocket.get_openai_agent_tools(),
    handoff_description="Specialist agent for summarizing emails",
    instructions="You summarize emails and return the results.",
)

orchestrator_agent = Agent(
    name="Orchestrator Agent",
    instructions="You orchestrate getting emails from Gmail, summarizing them, and posting the results to Slack.",
    tools=[
        gmail_fetch_agent.as_tool(
            tool_name="gmail_fetch_agent",
            tool_description="Fetch emails from Gmail",
        ),
        slack_agent.as_tool(
            tool_name="slack_agent",
            tool_description="Post messages to Slack",
        ),
        summarize_agent.as_tool(
            tool_name="summarize_agent",
            tool_description="Summarize emails",
        ),
    ],
)


async def main():
    # init tool auth
    await pocket.init_auth_async()

    result = await Runner.run(
        orchestrator_agent, "Fetch emails from Gmail and post the results to Slack"
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
