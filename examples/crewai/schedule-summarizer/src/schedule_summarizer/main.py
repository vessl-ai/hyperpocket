#!/usr/bin/env python
import warnings
from datetime import datetime

import pytz
from schedule_summarizer.crew import ScheduleSummarizer

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        "slack_channel": "proj-hyperpocket",
        "github_org": "vessl-ai",
        "github_repo": "hyperpocket",
        "current_date": datetime.today().astimezone(tz=pytz.timezone('Asia/Seoul')).strftime('%m-%d-%Y')
    }
    crew = ScheduleSummarizer()
    try:
        crew.crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
    finally:
        crew.pocket._teardown_server()
