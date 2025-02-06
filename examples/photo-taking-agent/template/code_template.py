def python_code_template():
    return \
        '''
def get_user_email() -> str:
    """
    return your email to get your sticker photo.
    """
    # return your email 
'''


def javascript_code_template():
    return \
        """
/**
* return your email to get your sticker photo.
*/
function get_user_email(){
    // return your email
}
"""


def get_template(language: str):
    if language == "python":
        return python_code_template()
    elif language == "javascript":
        return javascript_code_template()
    else:
        raise AttributeError()
