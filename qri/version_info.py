from .util import set_fields


class VersionInfo(object):
    def __init__(self, obj):
        set_fields(self, obj, ['bodySize', 'bodyRows', 'bodyFormat', 'numErrors', 'commitTime'])

    def __repr__(self):
        return 'VersionInfo()'
