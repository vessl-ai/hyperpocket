#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from kraken_auto_trader.crew import KrakenAutoTrader

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
        'pair': 'XXDGXXBT',
        'current_time': str(datetime.now()),
    }
    
    with KrakenAutoTrader() as crew:
        while True:
            try:
                result = crew.crew().kickoff(inputs=inputs)
                print(result)
            except Exception as e:
                raise Exception(f"An error occurred while running the crew: {e}")

