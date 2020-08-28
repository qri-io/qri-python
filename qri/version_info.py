from .util import set_fields


class VersionInfo(object):
    def __init__(self, obj):
        set_fields(self, obj, ['bodySize', 'bodyRows', 'bodyFormat', 'numErrors', 'commitTime'])
        # TODO(dustmop): Remove me after this typo is fixed in qri core
        if 'bodyFromat' in obj:
            self.body_format = obj.get('bodyFromat')

    def __repr__(self):
        return 'VersionInfo()'
