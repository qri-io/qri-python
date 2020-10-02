import markdown

from . import dsref
from . import loader
from .util import set_fields, build_repr


class Meta(object):
    def __init__(self, obj):
        set_fields(self, obj, ['accessURL', 'accrualPeriodicity', 'citations',
                               'contributors', 'description', 'downloadURL',
                               'homeURL', 'identifier', 'keywords', 'language',
                               'license', 'path' 'readmeURL', 'title', 'theme',
                               'version'])

    def __repr__(self):
        r = build_repr(self)
        return 'Meta(%s)' % r


class Readme(object):
    def __init__(self, obj):
        # TODO(dustmop): Handle scriptPath
        if not obj or 'scriptBytes' not in obj:
            self.script = None
            return
        self.script = loader.base64_decode(obj['scriptBytes']).decode('utf-8')

    def render(self):
        if self.script is None:
            return ''
        return markdown.markdown(self.script)

    def __str__(self):
        if self.script is None:
            return 'None'
        return self.script

    def __repr__(self):
        if self.script is None:
            return 'None'
        return 'Readme("%s")' % self

    def _repr_html_(self):
        return self.render()


class Structure(object):
    def __init__(self, obj):
        set_fields(self, obj, ['checksum', 'depth', 'entries', 'format',
                               'formatConfig', 'length', 'schema'])

    def __repr__(self):
        r = build_repr(self)
        return 'Structure(%s)' % r


class Commit(object):
    def __init__(self, obj):
        set_fields(self, obj, ['author', 'message', 'path', 'signature',
                               'timestamp', 'title'])

    def __repr__(self):
        r = build_repr(self)
        return 'Commit(%s)' % r


def is_from_list(obj):
    version_info_fields = ['bodySize', 'bodyRows', 'bodyFormat', 'numErrors', 'commitTime']
    return bool(set(obj) & set(version_info_fields))


class Dataset(object):
    def __init__(self, obj):
        # Fields that are always present
        set_fields(self, obj, ['username', 'name', 'profileID', 'path'])
        if self.username is None and 'peername' in obj:
            self.username = obj.get('peername')

        self._is_populated = False
        if not is_from_list(obj):
            self._populate(obj)

    def _ensure_populated(self):
        if self._is_populated:
            return
        ref = dsref.Ref(self.username, self.name)
        self._populate(loader.instance().get_dataset_object(ref))

    def _populate(self, obj):
        self.body_path_value = obj.get('bodyPath')
        self.previous_path_value = obj.get('previousPath')

        # Subcomponents
        self.commit_component = Commit(obj.get('commit'))
        self.meta_component = Meta(obj.get('meta'))
        self.readme_component = Readme(obj.get('readme'))
        self.structure_component = Structure(obj.get('structure'))
        self.body_component = None

        self._is_populated = True

    @property
    def body_path(self):
        self._ensure_populated()
        return self.body_path_value

    @property
    def previous_path(self):
        self._ensure_populated()
        return self.previous_path_value

    @property
    def meta(self):
        self._ensure_populated()
        return self.meta_component

    @property
    def commit(self):
        self._ensure_populated()
        return self.commit_component

    @property
    def readme(self):
        self._ensure_populated()
        return self.readme_component

    @property
    def structure(self):
        self._ensure_populated()
        return self.structure_component

    @property
    def body(self):
        self._ensure_populated()
        if self.structure.format != 'csv':
            raise RuntimeError('Only csv body format is supported')
        if self.body_component is None:
            ref = dsref.Ref(self.username, self.name)
            df = loader.instance().load_body(ref, self.structure)
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
