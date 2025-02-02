def python_code_template():
    return \
        '''
def roll_the_dice() -> int:
    """
    roll dice by your own way.
    return only integer number.
    """
    # write your own code

'''


def javascript_code_template():
    return \
        """
function roll_the_dice(){
    # write your own code
}
"""


def get_template(language: str):
    if language == "python":
        return python_code_template()
    elif language == "javascript":
        return javascript_code_template()
    else:
        raise AttributeError()
