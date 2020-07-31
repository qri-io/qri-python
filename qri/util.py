import re


def to_snake_case(text):
    return re.sub(r'([^A-Z])([A-Z])', r'\1_\2', text).lower()


def set_fields(inst, obj, fields):
    field_list = []
    for f in fields:
        name = to_snake_case(f)
        field_list.append(name)
        if obj is None:
            setattr(inst, name, None)
        else:
            setattr(inst, name, obj.get(f))
    setattr(inst, '_fields', field_list)


def build_repr(inst):
    accum = []
    for f in inst._fields:
        val = getattr(inst, f)
        if val:
            accum.append('%r: %r' % (f, val))
    return '{' + ', '.join(accum) + '}'
