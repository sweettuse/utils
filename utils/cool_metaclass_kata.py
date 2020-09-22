# https://www.codewars.com/kata/5f24315eff32c4002efcfc6a/train/python
# ======================================================================================================================
# MUCH BETTER SOLUTION, NOT MINE
from collections import defaultdict
from contextlib import suppress


class Prep(dict):
    def __init__(self):
        self.d = defaultdict(dict)

    def __setitem__(self, k, v):
        self.setter(k, v, super().__setitem__)

    def setter(self, k, v, parent_setattr):
        if callable(v):
            def wrap(*args):
                with suppress(KeyError):
                    return self.d[k][len(args)](*args)
                raise AttributeError()

            self.d[k][v.__code__.co_argcount] = v
            v = wrap
        parent_setattr(k, v)


class Meta(type):
    @classmethod
    def __prepare__(mcs, *_, **__):
        return Prep()

    def __new__(mcs, name, bases, prep, **kwargs):
        prep['_Meta__DCT'] = prep
        return super().__new__(mcs, name, bases, prep, **kwargs)

    def __setattr__(self, k, v):
        self.__DCT.setter(k, v, super().__setattr__)


# ======================================================================================================================
# my solution

# def _valid_func(name, f):
#     return callable(f) and not name.startswith('__')
#
#
# class Multistore(dict):
#     def __init__(self):
#         super().__init__()
#         self.data = {}
#         self.overloads = defaultdict(dict)  # funcname -> num_args -> func
#
#     def __setitem__(self, key, val):
#         if _valid_func(key, val):
#             self.overloads[key][val.__code__.co_argcount] = val
#         else:
#             self.data[key] = val
#
#
# class OverloadProp:
#     def __init__(self, num_args_to_funcs=None):
#         self.num_args_to_funcs = num_args_to_funcs or {}
#
#     def __get__(self, instance, cls):
#         def foo_wrapper(*args):
#             try:
#                 return self.num_args_to_funcs[len(args) + 1](instance, *args)
#             except KeyError:
#                 raise AttributeError('no overload found')
#
#         return foo_wrapper
#
#     def update(self, f):
#         self.num_args_to_funcs[f.__code__.co_argcount] = f
#
#
# class Meta(type):
#     @classmethod
#     def __prepare__(mcs, name, bases):
#         return Multistore()
#
#     def __new__(mcs, name, bases, body):
#         overloads = defaultdict(OverloadProp,
#                                 {name: OverloadProp(args_to_funcs) for name, args_to_funcs in body.overloads.items()})
#         new_body = {**body.data, **overloads}
#         res = super().__new__(mcs, name, bases, new_body)
#         res._overloads = overloads
#         print(res._overloads)
#         return res
#
#     def __setattr__(cls, key, value):
#         if _valid_func(key, value):
#             cls._overloads[key].update(value)
#             setattr(cls, key, cls._overloads[key])
#         else:
#             super().__setattr__(key, value)


# ======================================================================================================================

class Overload(metaclass=Meta):
    CLS_VAR = 42

    def __init__(self):
        self.a = 1
        self.no = 'This is "No parameter" function.'
        self.single = 'This is "Single parameter" function'
        self.two = 'This is "Two parameter" function'
        self.three = 'This is "Three parameter" function'

    def foo(self):
        return self.no

    def foo(self, x):
        return self.single + ':' + str(x)

    def foo(self, x, y):
        return self.two + ':' + str(x) + ',' + str(y)

    def foo(self, x, y, z):
        return self.three + ':' + str(x) + ',' + str(y) + ',' + str(z)

    def extra(self):
        return 'This is extra method.'


obj = Overload()

Overload.foo = lambda self, a, b, c, d: 'from outside!'

print(obj.foo())  # 'This is "No parameter" function.'
print(obj.foo(1, 2))  # 'This is "Two parameter" function:1,2'
print(obj.foo(1, 2, 3))  # 'This is "Three parameter" function:1,2,3'
print(obj.foo(1, 2, 3, 4))  # 'from outside!'

Overload.boo = lambda s: 'wow with 0'
Overload.boo = lambda s, a: 'wow with 1'

print(obj.boo())
print(obj.boo(2))

(obj.foo(*[4] * 8))
