import re


def to_snake_case(text):
  return re.sub(r'([^A-Z])([A-Z])', r'\1_\2', text).lower()


def set_fields(inst, obj, fields):
  for f in fields:
    name = to_snake_case(f)
    if obj is None:
      setattr(inst, name, None)
    else:
      setattr(inst, name, obj.get(f))
  setattr(inst, '_fields', fields)
