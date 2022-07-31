"""
allow properties to be used at the module level

to use, in the module, do something like:

NOTE: pretty broken
# >>> _b = 14
# >>>
# >>> @property
# >>> def b():
# >>>     return _b
# >>>
# >>> @b.setter
# >>> def b(val)
# >>>     global _b
# >>>     _b = val
# >>>
# >>> if __name__ != '__main__':
# >>>     enable_module_properties()
"""

from functools import wraps
import sys


def _wrap_property(prop):
    """make it so module property functions do not need `self` if defined at module level"""
    new_props = {}

    def _create_func(func):
        return wraps(func)(lambda _, *args, **kwargs: func(*args, **kwargs))

    for name in 'fget fset fdel'.split():
        f = getattr(prop, name)
        if f:
            new_props[name] = _create_func(f)

    return property(**new_props)


def enable_module_properties():
    globs = sys._getframe(1).f_globals
    name = globs['__name__']
    print(f'{name=}')
    module = sys.modules[name]
    props, body = {}, {}
    for n, v in vars(module).items():
        if isinstance(v, property):
            props[n] = _wrap_property(v)
        else:
            body[n] = v

    new = sys.modules[name] = type(name, (type(module),), props)(name)
    for k, v in body.items():
        setattr(new, k, v)
    print(props)
    # print(body)
