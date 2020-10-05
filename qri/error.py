import re
from . import util


ANSI_ESCAPE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')


def strip_color(colored_text):
    """strips color characters to return plaintext for when the
       global color flag cannot be overriden"""
    return ANSI_ESCAPE.sub('', colored_text)


class QriClientError(RuntimeError):
    def __init__(self, err_string):
        err_string = util.ensure_string(err_string)
        super(QriClientError, self).__init__(strip_color(err_string))
