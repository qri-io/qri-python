import shlex
from subprocess import Popen, PIPE
import sys
from . import util


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
        return util.ensure_string(stdout), err
    except FileNotFoundError:
        write_missing_binary_error()
        sys.exit(1)
    except BaseException as e:
        raise e


def write_missing_binary_error():
    sys.stderr.write("""qri command-line binary not found. It is either not installed, or PATH needs to be assigned. Please get the latest release from https://github.com/qri-io/qri, then run this command again.\n""")


def write_missing_cloud_api():
    sys.stderr.write("""Cloud API cannot list, and qri command-line binary not found. You can either `get` using cloud, or install the qri command-line binary. To do that, please get the latest release from https://github.com/qri-io/qri, assign your PATH, then run this command again.\n""")
