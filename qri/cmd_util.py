"""
"""
import re
import shlex
from subprocess import Popen, PIPE
import time

_MAX_ATTEMPTS = 10
_DELAY = .1


#---------------------------------------------------------------------
def _shell_exec_once(command, cwd=None):
  """ helper function to execute bash commands and return output"""
  if cwd:
    proc = Popen(shlex.split(command),
                 stdin=PIPE,
                 stdout=PIPE,
                 stderr=PIPE,
                 cwd=cwd)
    stdoutdata, err = proc.communicate()
    return stdoutdata, err
  # else
  proc = Popen(shlex.split(command), stdin=PIPE, stdout=PIPE, stderr=PIPE)
  stdoutdata, err = proc.communicate()
  return stdoutdata.decode(), err

def shell_exec(command):
  """ helper function to deal with unreliable commands that may
      temporarily fail but succeed on a repeated attempt"""
  stdoutdata, _ = _shell_exec_once(command)
  for _ in range(_MAX_ATTEMPTS - 1):
    if "error" not in stdoutdata[:15]:
      break
    time.sleep(_DELAY)
    stdoutdata, _ = _shell_exec_once(command)
  return stdoutdata

#---------------------------------------------------------------------
def clean_up_files(paths):
  """ deletes the files listed in paths """
  for path in paths:
    cmd = "rm -rf {}".format(path)
    shell_exec(cmd)

def strip_color(colored_text):
  """ strips color characters to return plaintext for when the
      global color flag cannot be overriden"""
  ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
  return ansi_escape.sub('', colored_text)
