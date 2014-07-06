
"""Module that monkey-patches json module when it's imported so
JSONEncoder.default() automatically checks for a special "to_json()"
method and uses it to encode the object if found.
"""
# From: http://stackoverflow.com/questions/18478287/making-object-json-serializable-with-regular-encoder

from json import JSONEncoder


def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default  # save unmodified default
JSONEncoder.default = _default  # replacement

