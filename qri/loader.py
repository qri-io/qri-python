import base64
import io
import pandas
from .cmd_util import shell_exec, QriCLIError


def load_body(username, dsname, structure):
    ref = '%s/%s' % (username, dsname)
    cmd = ['qri', 'get', 'body', ref]
    result, err = shell_exec(cmd)
    if err:
        raise QriCLIError(err)
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
                # TODO - Something weird is happening. -122.83466340000001 gets resaved as -122.8346634,
                # and -122.8346634 gets resaved back as -122.83466340000001. float_precision='round_trip'
                # Sounds like it would fix it but it doesn't. We may want it regardless, though.
                # TODO - big test suite of round-trip csvs to make sure it doesn't screw it up here or in other ways?
        df = pandas.read_csv(stream, header=header, names=col_names)
    return df

def write_body(df, body_path, structure):

    # TODO - From basic testing it doesn't seem like I need these; column orders stay in place
    # However, maybe I shouldn't assume this.
    # columns = [e for e in structure.schema['items']['items']]
    # col_names = [c['title'] for c in columns]
    # types = {c['title']: pd_type(c['type']) for c in columns}

    # header = 0 if structure.format_config.get('headerRow') else None
    df.to_csv(body_path,
            # header=header, TODO - do I care about this value? It means something different than in csv_read
            #colums=col_names, TODO - ?
            index=False,
            )
    # TODO - return?


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
