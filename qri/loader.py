from .cmd_util import shell_exec


def loadBody(username, dsname, format):
  ref = '%s/%s' % (username, dsname)
  cmd = 'qri get body %s' % ref
  result, err = shell_exec(cmd)
  if err:
    raise RuntimeError(err)
  if format != 'csv':
    raise RuntimeError('Format "%s" not supported' % format)
  # Shell returns a bytearray, convert to utf8 encoded string
  result = str(result, 'utf8')
  # TODO(dustmop): Handle quotes, and other csv specific details
  return [line.split(',') for line in result.split('\n') if line]
