import re
import shlex
from subprocess import Popen, PIPE
import sys


def shell_exec(command, cwd=None):
    """execute commands and return stdout"""
    try:
        proc = Popen(shlex.split(command),
                     stdin=PIPE,
                     stdout=PIPE,
                     stderr=PIPE,
                     cwd=cwd)
        stdout, err = proc.communicate()
        return stdout, err
    except FileNotFoundError as e:
        sys.stderr.write("""qri command-line binary not found. It is either not installed, or PATH needs to be assigned. Please get the latest release from https://github.com/qri-io/qri, then run this command again.\n""")
        sys.exit(1)
    except:
        raise e


def strip_color(colored_text):
    """strips color characters to return plaintext for when the
       global color flag cannot be overriden"""
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', colored_text)


class QriClientError(RuntimeError):
    def __init__(self, err_string):
        clean_err_string = strip_color(err_string.decode('utf-8'))
        super(QriClientError, self).__init__(clean_err_string)
