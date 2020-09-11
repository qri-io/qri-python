import markdown

from . import dsref
from . import loader
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

    def _repr_html_(self):
        # TODO - look at the fuller schema of schema and format config in golang

        def render_schema_node(node):
            if node['type'] == 'array' and isinstance(node['items'], list):
                return """<table>
                <tr>
                    <th>Field Name</th>
                    <th>Type</th>
                </tr>
                """ + "".join(render_schema_node(item) for item in node['items']) + "</table>" # TODO header?
            elif node['type'] == 'array' and isinstance(node['items'], dict):
                return "<table>" + render_schema_node(node['items']) + "</table>" # TODO header? Call this a nullop? Or what?
            else:
                return f"""<tr>
                    <td><code>{node['title']}</code></td>
                    <td><em>{node['type']}</em></td>
                </tr>"""

        return f"""<table>
            <tr>
                <td><b>Checksum</b></td>
                <td><code>{self.checksum}</code></td>
            </tr>
            <tr>
                <td><b>Depth</b></td>
                <td>{self.depth}</td>
            </tr>
            <tr>
                <td><b>Entries</b></td>
                <td>{self.entries}</td>
            </tr>
            <tr>
                <td><b>Format</b></td>
                <td>{self.format}</td>
            </tr>
            <tr>
                <td><b>Format Config</b></td>
                <td><table>
                    <tr>
                        <td><b>Header Row:</b></td>
                        <td>{self.format_config['headerRow']}</td>
                    </tr>
                    <tr>
                        <td><b>Lazy Quotes:</b></td>
                        <td>{self.format_config['lazyQuotes']}</td>
                    </tr>
                </table></td>
            </tr>
            <tr>
                <td><b>Length</b></td>
                <td>{self.length}</td>
            </tr>
            <tr>
                <td><b>Schema</b></td>
                <td>{render_schema_node(self.schema)}</td>
            </tr>
        </table> """


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
