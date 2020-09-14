import re


ANSI_ESCAPE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')


def strip_color(colored_text):
    """strips color characters to return plaintext for when the
       global color flag cannot be overriden"""
    return ANSI_ESCAPE.sub('', colored_text)


class QriClientError(RuntimeError):
    def __init__(self, err_string):
        # Ensure the error text is a string, not simply bytes
        if isinstance(err_string, bytes):
            err_string = err_string.decode('utf-8')
        super(QriClientError, self).__init__(strip_color(err_string))
