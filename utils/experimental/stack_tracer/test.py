from __future__ import annotations
from contextlib import suppress
from utils.experimental.stack_tracer.stack_tracer import CodeStackEntries, StackTracer


# set up test functions to call
def a():
    b()
    b()
    c()


def b():
    d()
    return 4


def c():
    ...


def d():
    ...


def f():
    g()


def g():
    h()


def h():
    raise Exception


def _get_simple_stack(stack: CodeStackEntries) -> str:
    """return pipe delimited stack of function names in a single str"""
    return '|'.join(s[0][1] for s in stack)


# test methods
def _test_no_exception():
    with StackTracer() as st:
        a()
    st.display()
    assert 'a|b|d a|b|d a|c' == ' '.join(map(_get_simple_stack, st._stacks))


def _test_exception():
    with StackTracer(
        trace_pred=lambda frame: 'sweettuse/utils/utils' in frame.f_code.co_filename
    ) as st:
        with suppress(Exception):
            f()
        d()
        d()
    st.display()
    assert 'f|g|h d d' == ' '.join(map(_get_simple_stack, st._stacks))


def _test_within():
    with StackTracer() as st:
        a()
        st.display()


# test
_test_no_exception()
_test_exception()
_test_within()
