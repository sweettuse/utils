__author__ = 'acushner'

from typing import NamedTuple, Tuple, Dict

from misty_py.utils import json_obj
from more_itertools import first


class SlackInfo(NamedTuple):
    """parse request information from slack"""
    cmd: str
    argstr: str
    kwargs: Dict[str, str]
    data: json_obj

    def __getattr__(self, item):
        return self.data[item]

    @classmethod
    def from_form_data(cls, form):
        data = _flatten_form(form)
        if 'text' in data:
            cmd, *argstr = data.text.strip().split(maxsplit=1)
        else:
            cmd, argstr = '', ['']
        argstr, kwargs = _parse_args(first(argstr, ''))
        return cls(cmd, argstr, kwargs, data)


def _flatten_form(form) -> json_obj:
    """transform {k: [v]} -> {k: v}"""
    return json_obj((k, first(v) if isinstance(v, list) and len(v) == 1 else v) for k, v in form.items())


def _parse_args(s: str) -> Tuple[str, json_obj]:
    str_res = []
    arg_res = json_obj()
    for w in s.split():
        if w.startswith('--'):
            split = w.index('=')
            arg_res[w[2:split]] = w[split + 1:]
        else:
            str_res.append(w)

    return ' '.join(str_res), arg_res


def __main():
    pass


if __name__ == '__main__':
    __main()
