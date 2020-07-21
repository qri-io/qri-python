import re
import shlex
from subprocess import Popen, PIPE


def shell_exec(command, cwd=None):
  """execute commands and return stdout"""
  proc = Popen(shlex.split(command),
               stdin=PIPE,
               stdout=PIPE,
               stderr=PIPE,
               cwd=cwd)
  stdout, err = proc.communicate()
  return stdout, err

class QriClientError(RuntimeError):
    def __init__(self, err_string):
        clean_err_string = strip_color(err_string.decode('utf-8'))
        super(QriClientError, self).__init__(clean_err_string)

def strip_color(colored_text):
  """ strips color characters to return plaintext for when the
      global color flag cannot be overriden"""
  ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
  return ansi_escape.sub('', colored_text)
