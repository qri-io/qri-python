import re

from . import error


class Ref(object):
    def __init__(self, username, name):
        self.username = username
        self.name = name

    def human(self):
        return '{}/{}'.format(self.username, self.name)

    def clone(self):
        return Ref(self.username, self.name)

    def __str__(self):
        return self.human()


def parse_ref(s):
    m = re.match(r'^([a-z][a-z0-9_-]*)/([a-z][a-z0-9_-]*)$', s)
    if m:
        username = m.group(1)
        name = m.group(2)
        return Ref(username, name)
    raise error.QriClientError('Could not parse reference "{}"'.format(s))
