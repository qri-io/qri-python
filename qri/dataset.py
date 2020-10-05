import collections
import markdown

from . import dsref
from . import loader
from . import version_info
from .util import set_fields, build_repr, ensure_string, max_len


NO_META_TITLE = '(untitled dataset)'


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
        text = loader.base64_decode(obj['scriptBytes'])
        self.script = ensure_string(text)

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

    def _repr_html_(self):
        text = """<table>
    <thead>
        <th></th><td>title</td><td>type</td><td>description</td>
    </thead>
    <tbody>"""
        for n, it in enumerate(self.schema['items']['items']):
            type = it.get('type', '')
            title = it.get('title', '')
            desc = it.get('description', '')
            tmpl = '<tr><th>{n}</th><td>{title}</td><td>{type}</td><td>{desc}</td></tr>'
            text += tmpl.format(n=n, title=title, type=type, desc=desc)
        text += '</tbody></table>'
        return text


class Commit(object):
    def __init__(self, obj):
        set_fields(self, obj, ['author', 'message', 'path', 'signature',
                               'timestamp', 'title'])

    def __repr__(self):
        r = build_repr(self)
        return 'Commit(%s)' % r


def is_short_info(obj):
    """Return whether the object is a short representation of a dataset"""
    fields = ['bodySize', 'bodyRows', 'bodyFormat', 'numErrors', 'metaTitle',
              'commitTime']
    return bool(set(obj) & set(fields))


class Dataset(object):
    def __init__(self, obj):
        # Fields that are always present
        set_fields(self, obj, ['username', 'name', 'profileID', 'path'])
        if self.username is None and 'peername' in obj:
            self.username = obj.get('peername')

        self._info = None
        self._is_populated = False

        if is_short_info(obj):
            self._info = version_info.VersionInfo(obj)
        else:
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
    def meta_title(self):
        if self._info:
            return self._info.meta_title
        return self.meta.title

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
        title = self.meta_title or NO_META_TITLE
        desc = self.meta.description or ''
        tmpl = """<h2>{title}</h2>
    <p>{desc}</p>
    <br />
    <table>
        <thead>
           <tr><td>records</td><td>last update</td><td>path</td><tr>
        </thead>
        <tbody>
           <tr><th>{structure.entries}</th><th>{commit.timestamp}</th><th>{path}</th><tr>
        </tbody>
    </table>"""
        text = tmpl.format(path=self.path, title=title, desc=desc,
                           commit=self.commit_component,
                           structure=self.structure_component)
        return text


class DatasetList(list):
    def __repr__(self):
        content = ', '.join(['%s' % d for d in self])
        return '[%s]' % (content,)

    def _repr_html_(self):
        curr_username = ''
        rows = ''
        # Assume datasets are sorted by human-friendly reference, which
        # will group by username, then by dataset name.
        for ds in self:
            if ds.username != curr_username:
                curr_username = ds.username
                disp_username = ds.username
            meta_title = max_len(ds.meta_title or NO_META_TITLE, 50)
            rows += f"""<tr>
                    <td><b>{disp_username}</b></td>
                    <td>{meta_title}</td>
                    <td style='text-align:left'>
                        <code>{ds.human_ref()}</code>
                    </td>
                </tr>"""
            # Only display the username once
            disp_username = ''

        return f"""<table>
            <thead>
                <td>Username</td>
                <td>Title</td>
                <td style='text-align:left'>Dataset Ref</td>
            </thead>
            <tbody>{rows}</tbody>
        </table>"""
