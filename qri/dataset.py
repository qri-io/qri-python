from . import loader
from . import version_info


def set_fields(inst, obj, fields):
  for f in fields:
    if obj is None:
      setattr(inst, f, None)
    else:
      setattr(inst, f, obj.get(f))


class Meta(object):
  def __init__(self, obj):
    set_fields(self, obj, ['accessURL', 'accrualPeriodicity', 'citations',
                           'contributors', 'description', 'downloadURL',
                           'homeURL', 'identifier', 'keywords', 'language',
                           'license', 'path' 'readmeURL', 'title', 'theme',
                           'version'])

  def __repr__(self):
    return 'Meta()'


class Structure(object):
  def __init__(self, obj):
    set_fields(self, obj, ['checksum', 'depth', 'entries', 'format',
                           'formatConfig', 'length', 'schema'])

  def __repr__(self):
    return 'Structure()'


class Commit(object):
  def __init__(self, obj):
    set_fields(self, obj, ['author', 'message', 'path', 'signature',
                           'timestamp', 'title'])

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
    self.versionInfo = self._build_version_info(obj)
    # Subcomponents
    self.commit_component = Commit(obj.get('commit'))
    self.meta_component = Meta(obj.get('meta'))
    self.structure_component = Structure(obj.get('structure'))
    self.body_component = None

  def _build_version_info(self, obj):
    info = version_info.VersionInfo(obj)
    # TODO(dustmop): Remove me after this typo is fixed in qri core
    if 'bodyFromat' in obj:
      info.bodyFormat = obj.get('bodyFromat')
    return info

  @property
  def meta(self):
    return self.meta_component

  @property
  def commit(self):
    return self.commit_component

  @property
  def structure(self):
    return self.structure_component

  @property
  def body(self):
    if self.structure_component is None:
      raise RuntimeError('Cannot read body without structure')
    if self.structure.format != 'csv':
      raise RuntimeError('Only csv body format is supported')
    if self.body_component is None:
      df = loader.load_body(self.username, self.name, self.structure)
      self.body_component = df
    return self.body_component

  def human_ref(self):
    return '%s/%s' % (self.username, self.name)

  def __repr__(self):
    return 'Dataset("%s")' % self.human_ref()

  def _repr_html_(self):
    return '<code>Dataset("%s")</code>' % self.human_ref()


class DatasetList(list):
  def __repr__(self):
    content = ', '.join(['%s' % d for d in self])
    return '[%s]' % (content,)

  def _repr_html_(self):
    content = ', '.join(['%s' % d for d in self])
    return '<code>[%s]</code>' % (content,)
