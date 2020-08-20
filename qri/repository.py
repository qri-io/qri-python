from .cmd_util import shell_exec, QriCLIError

def save(username, dsname, title=None, force=False):
    ref = '%s/%s' % (username, dsname)
    cmd = ['qri', 'save', ref]
    if title != None:
        cmd = cmd + ['--title', title]
    if force == True:
        cmd = cmd + ['--force']
    result, err = shell_exec(cmd)
    if err:
        raise QriCLIError(err)
