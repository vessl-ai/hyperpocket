from collections import Counter
from typing import Union

from hyperpocket.tool import function_tool


@function_tool
def bulls_and_cows(predict: str, target: str):
    """
    Play the "Bulls and Cows" number guessing game.

    - Bulls: A digit is correct and in the correct position.
    - Cows: A digit is correct but in the wrong position.

    Given two integer inputs, this function calculates the number of Bulls(correct digits in the correct positions)
    and Cows (correct digits in the wrong positions).

    Args:
        predict (Union[str, int]): The player's guessed number (assumed to be a four-digit number).
        target (Union[str, int]): The actual target number (assumed to be a four-digit number).

    Returns:
        tuple[int, int]: A tuple containing (number of Bulls, number of Cows).
    """

    if isinstance(predict, int):
        predict = str(predict).zfill(4)
    if isinstance(target, int):
        target = str(target).zfill(4)

    assert len(predict) == len(target), "Predict and target must have the same length"

    # calc bulls
    bulls = sum(a == b for a, b in zip(predict, target))

    # calc cows
    predict_counter = Counter(predict)
    target_counter = Counter(target)
    total_overlapped_count = sum([min(predict_counter[digit], target_counter[digit]) for digit in predict_counter])
    cows = total_overlapped_count - bulls

    return bulls, cows
