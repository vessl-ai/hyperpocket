def python_code_template():
    return \
        '''
def tbu() -> str:
    """
    tbu
    """
    # TBU
'''


def javascript_code_template():
    return \
        """
/**
tbu
*/
function tbu(){
    // tbu
}
"""


def get_template(language: str):
    if language == "python":
        return python_code_template()
    elif language == "javascript":
        return javascript_code_template()
    else:
        raise AttributeError()
