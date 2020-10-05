import base64
import io
import json
import pandas

from . import cmd_util, error, util
import requests
from subprocess import Popen, PIPE


_inst = None


def instance():
    global _inst
    if _inst is None:
        print
        proc = Popen(['which', 'qri'], stdout=PIPE)
        stdout, err = proc.communicate()
        if proc.returncode == 0:
            # Have a local qri binary
            _inst = LocalQriBinaryRepo()
        else:
            # Send http requests to api.qri.cloud
            _inst = CloudAPIRepo()
    return _inst


def set_instance(obj):
    global _inst
    _inst = obj


class LocalQriBinaryRepo(object):
    def get_dataset_object(self, ref):
        cmd = 'qri get --format json %s' % ref.human()
        result, err = cmd_util.shell_exec(cmd)
        if err:
            raise error.QriClientError(err)
        # NOTE: Work-around for auto-pull outputting an info message to stdout
        if result.startswith('pulling '):
            # There is a sentence about pulling, then the json data starting
            # with the opening brace. Trim everything before that first brace
            pos = result.find('{')
            result = result[pos:]
        return json.loads(result)

    def list_dataset_objects(self, username=None):
        if username is not None:
            raise error.QriClientError('listing with username not supported')
        cmd = 'qri list --format json'
        result, err = cmd_util.shell_exec(cmd)
        if err:
            raise error.QriClientError(err)
        return json.loads(result)

    def pull_dataset(self, ref):
        cmd = 'qri pull %s' % ref.human()
        result, err = cmd_util.shell_exec(cmd)
        if err:
            raise error.QriClientError(err)
        return result

    def load_body(self, ref, structure):
        if structure.format != 'csv':
            raise RuntimeError('Format "%s" not supported' % structure.format)
        cmd = 'qri get body %s' % ref.human()
        result, err = cmd_util.shell_exec(cmd)
        if err:
            raise error.QriClientError(err)
        result = util.ensure_string(result)
        stream = io.StringIO(result)
        columns = [e for e in structure.schema['items']['items']]
        col_names = [c['title'] for c in columns]
        types = {c['title']: pd_type(c['type']) for c in columns}
        header = 0 if structure.format_config.get('headerRow') else None
        df = None
        try:
            # Try to parse the csv using the schema
            df = pandas.read_csv(stream, header=header, names=col_names,
                                 dtype=types)
        except (TypeError, ValueError):
            # If pandas encountered parse errors, reparse without datatypes
            stream = io.StringIO(util.ensure_string(result))
            df = pandas.read_csv(stream, header=header, names=col_names)
        return df


class CloudAPIRepo(object):
    def get_dataset_object(self, ref):
        r = requests.get('https://api.qri.cloud/get/%s' % ref.human())
        return json.loads(r.text)['data']['dataset']

    def list_dataset_objects(self, username=None):
        raise error.CloudMissingAPIError('CloudAPIRepo.list_dataset_objects')

    def load_body(self, ref, structure):
        if structure.format != 'csv':
            raise RuntimeError('Format "%s" not supported' % structure.format)
        qparams = ['component=body', 'format=csv', 'download=true', 'all=true']
        r = requests.get('https://api.qri.cloud/get/%s?%s' %
                         (ref.human(), '&'.join(qparams)))
        stream = io.StringIO(r.text)
        columns = [e for e in structure.schema['items']['items']]
        col_names = [c['title'] for c in columns]
        types = {c['title']: pd_type(c['type']) for c in columns}
        header = 0 if structure.format_config.get('headerRow') else None
        df = None
        try:
            # Try to parse the csv using the schema
            df = pandas.read_csv(stream, header=header, names=col_names,
                                 dtype=types)
        except (TypeError, ValueError):
            # If pandas encountered parse errors, reparse without datatypes
            stream = io.StringIO(r.text)
            df = pandas.read_csv(stream, header=header, names=col_names)
        return df


def from_json(json_text):
    return pandas.read_json(json_text)


def base64_decode(bdata):
    return base64.b64decode(bdata)


def pd_type(t):
    if t == 'integer':
        return 'int64'
    elif t == 'number':
        return 'float64'
    elif t == 'string':
        return 'string'
    elif t == 'bool':
        return 'bool'
    elif t == 'array':
        return 'array'
    raise RuntimeError('Unknown type: "%s"' % t)
