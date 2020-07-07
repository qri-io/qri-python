def set_fields(inst, obj, fields):
  for f in fields:
    if obj is None:
      setattr(inst, f, None)
    else:
      setattr(inst, f, obj.get(f))


class VersionInfo(object):
  def __init__(self, obj):
    set_fields(self, obj, ['bodySize', 'bodyRows', 'bodyFormat', 'numErrors', 'commitTime'])

  def __repr__(self):
    return 'VersionInfo()'
