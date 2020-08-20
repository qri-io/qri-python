from .cmd_util import shell_exec, QriCLIError

def save(username, dsname, title=None):
    ref = '%s/%s' % (username, dsname)
    cmd = ['qri', 'save', ref]
    if title != None:
        cmd = cmd + ['--title', title]
    result, err = shell_exec(cmd)
    if err:
        raise QriCLIError(err)
