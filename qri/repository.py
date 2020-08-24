from .cmd_util import shell_exec, QriCLIError

# TODO - does this belong in loader at this point? Since loader did the pull from `qri`
def save(
        username,
        dsname,
        body,
        title=None,
        message=None,
        force=False
    ):
    ref = '%s/%s' % (username, dsname)
    cmd = ['qri', 'save', ref, '--body', body]
    if title != None:
        cmd = cmd + ['--title', title]
    if message != None:
        cmd = cmd + ['--message', message]
    if force == True:
        cmd = cmd + ['--force']
    result, err = shell_exec(cmd)
    if err:
        raise QriCLIError(err)
