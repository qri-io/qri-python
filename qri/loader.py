import base64
import io
import pandas
from .cmd_util import shell_exec


def load_body(username, dsname, structure):
    ref = '%s/%s' % (username, dsname)
    cmd = 'qri get body %s' % ref
    result, err = shell_exec(cmd)
    if err:
        raise RuntimeError(err)
    if structure.format != 'csv':
        raise RuntimeError('Format "%s" not supported' % structure.format)
    stream = io.StringIO(str(result, 'utf8'))
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
        stream = io.StringIO(str(result, 'utf8'))
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
    raise RuntimeError('Unknown type: "%s"' % t)
