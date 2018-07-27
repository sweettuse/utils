import ast
import inspect
import textwrap

from contextlib import suppress
from collections import defaultdict
from typing import Union, Dict, Callable, Type, Any, Tuple, List


def is_union(t) -> bool:
    """`True` if type hint/annotation is `Union`"""
    return type(t) is type(Union)


def is_optional(t) -> bool:
    """`True` if type hint/annotation is `Optional`"""
    return is_union(t) and type(None) in t.__args__


def inspect_inline_annotations(func) -> Dict[str, Any]:
    """
    read into a function and determine what its inline variable annotations are

    an inline annotation looks something like:
    def f(param: float):  # function annotation
        var: int = 4      # inline variable annotation

    unlike function annotations, which you can grab by doing `f.__annotations__`,
    inline ones are not easy to get at; this function does that for you

    example:
    In [1]: from Utilities.typing_utils import inspect_inline_annotations

    In [2]: def f():
          :     x: int
          :     y: int = 7
          :     x = 16
          :     return x, y
          :

    In [3]: inspect_inline_annotations(f)
    Out[3]: {'x': int, 'y': int}
    """
    func_ast_by_type = _get_ast_by_type(func)
    ctx = _get_context(func, func_ast_by_type)
    lines = _get_source(func).splitlines()
    return dict(_extract_annotation(lines[e.lineno - 1], ctx) for e in func_ast_by_type[ast.AnnAssign])


def _get_ast_by_type(func: Callable) -> Dict[Type, List[Any]]:
    """parse a function's body and return abstract syntax tree objects by their types"""
    source = _get_source(func)
    tree = ast.parse(source)
    f_def = tree.body[0]
    res = defaultdict(list)
    for e in f_def.body:
        res[type(e)].append(e)
    return res


def _get_context(func: Callable, func_ast_by_type) -> Dict:
    """
    exec a func's module to fill in dictionaries with local vars so we can actually eval the type hints correctly

    additionally, crawl through the function to exec any local imports that the func might have used
    """
    d = {}
    with suppress(TypeError):
        # this will not work with objects in the main module, or with contexts created in, say, a jupyter console
        module_source = inspect.getsource(inspect.getmodule(func))
        exec(module_source, d, d)

    func_lines = _get_source(func).splitlines()
    import_stmts = '\n'.join(func_lines[e.lineno - 1].lstrip()
                             for ast_type in (ast.Import, ast.ImportFrom)
                             for e in func_ast_by_type.get(ast_type, []))
    exec(import_stmts, d, d)

    return d


def _get_source(func: Callable) -> str:
    return textwrap.dedent(inspect.getsource(func))


def _extract_annotation(line: str, ctx: Dict) -> Tuple[str, Any]:
    """
    based on a source line of code and an environmental context for that code,
    return a (var_name, annotation) tuple
    """
    for char in '=#':  # could cause problems if the type hint itself contains a `#` or a `=`
        if char in line:
            line = line[:line.rindex(char)]

    var, annot = line.split(':')
    return var.strip(), eval(annot.strip(), ctx, ctx)


def __main():
    def f():
        x: int
        y: int = 7
        x = 16
        return x, y

    def g():
        pass

    print(inspect_inline_annotations(f))
    print(inspect_inline_annotations(g))


if __name__ == '__main__':
    __main()
