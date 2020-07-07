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


def strip_color(colored_text):
  """ strips color characters to return plaintext for when the
      global color flag cannot be overriden"""
  ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
  return ansi_escape.sub('', colored_text)
