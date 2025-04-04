#!/usr/bin/env python
import warnings
from datetime import datetime

from gmail_summarizer.crew import GmailSummarizer

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
        'num_emails': 20,
        'date': datetime.now().strftime("%Y%m%d"),
        'slack_channel': 'engr-test'
    }

    try:
        with GmailSummarizer() as summarizer:
            summarizer.crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


if __name__ == '__main__':
    run()
