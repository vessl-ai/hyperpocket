def python_code_template():
    return \
        '''
def roll_the_dice() -> int:
    """
    roll dice by your own way.
    return only integer number.
    """
    # write your code here

'''


def javascript_code_template():
    return \
        """
/**
* roll dice by your own way.
* return only integer number.
*/
function roll_the_dice(){
    // write your code here
}
"""


def get_template(language: str):
    if language == "python":
        return python_code_template()
    elif language == "javascript":
        return javascript_code_template()
    else:
        raise AttributeError()
