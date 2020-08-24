import markdown
from . import loader
from . import repository
from . import version_info
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
        if not obj or 'scriptBytes' not in obj:
            self.script = None
            return
        self.script = loader.base64_decode(obj['scriptBytes']).decode('utf-8')

    def render(self):
        if self.script is None:
            return ''
        return markdown.markdown(self.script)

    def __repr__(self):
        return self.script

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
        self.readme_component = Readme(obj.get('readme'))
        self.structure_component = Structure(obj.get('structure'))
        self.body_component = None

    def _build_version_info(self, obj):
        info = version_info.VersionInfo(obj)
        # TODO(dustmop): Remove me after this typo is fixed in qri core
        if 'bodyFromat' in obj:
            info.body_format = obj.get('bodyFromat')
        return info

    @property
    def meta(self):
        return self.meta_component

    @property
    def commit(self):
        return self.commit_component

    @property
    def readme(self):
        return self.readme_component

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

    # NOTE (remove before commit): "Save" in the context of a Python
    # library sounds like it should imply that we're saving any
    # changes done within Python. `qri save` on the command line by
    # default saves changes to `body.csv`. If the user wants that, it
    # would be less awkward to just use the command line tool.

    # TODO - As such: only allow save if we have a clean `qri status`,
    # to avoid overwriting work done by other clients. Not foolproof,
    # but it might avoid some surprises.
    def save(
            self,
            title=None,
            message=None,
            force=False
        ):
        # TODO - confirm body_path exists
        # * It was gotten by get(), not list()
        # * I actually own this dataset

        # TODO - loader.write_readme(self.readme)
        # TODO - loader.write_structure(self.structure)
        loader.write_body(self.body, self.body_path, self.structure)
        return repository.save(
            self.username,
            self.name,
            title=title,
            message=message,
            force=force
        )

    def commit(self, *args, **kwargs):
        return self.save(*args, **kwargs)


class DatasetList(list):
    def __repr__(self):
        content = ', '.join(['%s' % d for d in self])
        return '[%s]' % (content,)

    def _repr_html_(self):
        content = ', '.join(['%s' % d for d in self])
        return '<code>[%s]</code>' % (content,)
