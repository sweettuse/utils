from pydantic import BaseModel
from typing import Any


class PosBaseModel(BaseModel):
    """pydantic BaseModel that allows positional args

    typically, you can't pass positional args to models. this fixes that
    """

    def __init_subclass__(cls, **kwargs):
        PosBaseModel._make_positional_init(cls)

    @staticmethod
    def _make_positional_init(cls):
        kwargs = {}
        for c in reversed(cls.__mro__):
            kwargs.update(getattr(c, '__annotations__', {}))

        # __slots__ is in annotations at this point. the below removes any dunders with annotations
        kwargs = {
            k: v
            for k, v in kwargs.items()
            if not (k.startswith('__') and k.endswith('__'))
        }
        sentinel = object()  # noqa
        argstr = ','.join(f'{k}=sentinel' for k in kwargs)
        body = (
            f'def __init__(self, {argstr}, **from_subclasses):\n'
            '    l = locals()\n'
            '    new_args = ((k, l[k]) for k in kwargs)\n'
            '    super(cls, self).__init__(**from_subclasses, **dict(na for na in new_args if na[1] is not sentinel))\n'
        )
        exec(body, locals())
        cls.__init__ = locals()['__init__']
        return cls

    def __init__(self, *_for_pycharm_only, **kwargs):
        """fake __init__ to keep pycharm from bitching about positional args.

        gets overridden dynamically, so no need to call `super().__init__`
        only calling so pycharm doesn't complain"""
        super().__init__(**kwargs)


def __main():
    class Model(PosBaseModel):
        a: int
        b: float

    class Under(Model):
        c: str
        d: Any

    m = Model(a=1, b=2)
    print(m)
    m = Model(1, b=2)
    print(m)
    u = Under(1, 2, c=3, d=4)
    print(u)
    return


if __name__ == '__main__':
    __main()
