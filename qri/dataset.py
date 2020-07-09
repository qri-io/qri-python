from . import version_info


def set_fields(inst, obj, fields):
  for f in fields:
    if obj is None:
      setattr(inst, f, None)
    else:
      setattr(inst, f, obj.get(f))


class Meta(object):
  def __init__(self, obj):
    set_fields(self, obj, ['accessURL', 'accrualPeriodicity', 'citations', 'contributors',
                           'description', 'downloadURL', 'homeURL', 'identifier', 'keywords',
                           'language', 'license', 'path' 'readmeURL', 'title', 'theme', 'version'])

  def __repr__(self):
    return 'Meta()'


class Structure(object):
  def __init__(self, obj):
    set_fields(self, obj, ['checksum', 'depth', 'entries', 'format', 'formatConfig', 'length',
                           'schema'])

  def __repr__(self):
    return 'Structure()'


class Commit(object):
  def __init__(self, obj):
    set_fields(self, obj, ['author', 'message', 'path', 'signature', 'timestamp', 'title'])

  def __repr__(self):
    return 'Commit()'


class Dataset(object):
  def __init__(self, obj):
    # Fields that are always present
    set_fields(self, obj, ['username', 'name', 'profileID', 'path'])
    if self.username is None and 'peername' in obj:
      self.username = obj.get('peername')
    # Fields returned by `get` commands
    set_fields(self, obj, ['bodyPath', 'previousPath'])
    # Version info
    self.versionInfo = self._buildVersionInfo(obj)
    # Subcomponents
    self.commitComponent = Commit(obj.get('commit'))
    self.metaComponent = Meta(obj.get('meta'))
    self.structureComponent = Structure(obj.get('structure'))

  def _buildVersionInfo(self, obj):
    info = version_info.VersionInfo(obj)
    # TODO(dustmop): Remove me after this typo is fixed in qri core
    if 'bodyFromat' in obj:
      info.bodyFormat = obj.get('bodyFromat')
    return info

  @property
  def meta(self):
    return self.metaComponent

  @property
  def commit(self):
    return self.commitComponent

  @property
  def structure(self):
    return self.structureComponent

  def humanRef(self):
    return '%s/%s' % (self.username, self.name)

  def __repr__(self):
    return 'Dataset("%s")' % self.humanRef()

  def _repr_html_(self):
    return '<code>Dataset("%s")</code>' % self.humanRef()


class DatasetList(list):
  def __repr__(self):
    content = ', '.join(['%s' % d for d in self])
    return '[%s]' % (content,)

  def _repr_html_(self):
    content = ', '.join(['%s' % d for d in self])
    return '<code>[%s]</code>' % (content,)
