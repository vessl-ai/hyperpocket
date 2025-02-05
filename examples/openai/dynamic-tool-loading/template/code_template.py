def python_code_template():
    return \
        '''
def guess_bulls_and_cows() -> int:
    """
    Guess 4 digits "Bulls and Cows" number.
    
    What's the Bulls and Cows games?
      It's a number guessing game where players try to guess a secret number by receiving feedback(Bulls and Cows)
      - Bulls: A digit is correct and in the correct position.
      - Cows: A digit is correct but in the wrong position.
    """
    # write your guessing number here.

'''


def javascript_code_template():
    return \
        """
/**
Guess 4 digits "Bulls and Cows" number.
    
What's the Bulls and Cows games?
  It's a number guessing game where players try to guess a secret number by receiving feedback(Bulls and Cows)
  - Bulls: A digit is correct and in the correct position.
  - Cows: A digit is correct but in the wrong position.
*/
function guess_bulls_and_cows(){
    // write your guessing number here.
}
"""


def get_template(language: str):
    if language == "python":
        return python_code_template()
    elif language == "javascript":
        return javascript_code_template()
    else:
        raise AttributeError()
