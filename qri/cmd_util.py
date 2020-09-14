import re
import shlex
from subprocess import Popen, PIPE
import sys


def shell_exec(command, cwd=None):
    """execute commands and return stdout"""
    if isinstance(command, list):
        command_list = command
    else:
        command_list = shlex.split(command)
    try:
        proc = Popen(command_list,
                     stdin=PIPE,
                     stdout=PIPE,
                     stderr=PIPE,
                     cwd=cwd)
        stdout, err = proc.communicate()
        if proc.returncode == 0:
            # If command exit code is 0, assume stderr is informational only.
            # This probably won't work forever, but fits most of our current
            # use cases.
            err = None
        return stdout, err
    except FileNotFoundError:
        sys.stderr.write("""qri command-line binary not found. It is either not installed, or PATH needs to be assigned. Please get the latest release from https://github.com/qri-io/qri, then run this command again.\n""")
        sys.exit(1)
    except BaseException as e:
        raise e


def strip_color(colored_text):
    """strips color characters to return plaintext for when the
       global color flag cannot be overriden"""
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', colored_text)


class QriClientError(RuntimeError):
    def __init__(self, err_string):
        if isinstance(err_string, bytes):
            err_string = strip_color(err_string.decode('utf-8'))
        super(QriClientError, self).__init__(err_string)
