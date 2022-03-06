import inspect
from typing import Any, Mapping, Callable


def inspect_signature(fn: Callable) -> tuple[list[str], dict[str, Any]]:
    """Inspects the signature of a function, finding all args and kwargs using
    the `inspect` module.

    Args:
        fn (Callable): The function to inspect.

    Returns:
        tuple[list[str], dict[str, Any]]: (list of args, dictionary of kwargs).
    """
    params = inspect.signature(fn).parameters
    args = []
    kwargs = {}
    for k, v in params.items():
        if v.default == inspect._empty:
            args.append(k)
        else:
            kwargs[k] = v.default
    return args, kwargs


def make_attrs(
    obj: Any,
    kwargs: Mapping[str, Any] = {},
    private: bool = False,
    recur_on: tuple[str] = ("kwargs"),
    ignore: tuple[str] = ("self"),
    private_prefix: str = "_",
):
    """Generate attributes for obj.
    Example:
        .. code-block:: python
            class Foo:
                def __init__(self, a, b, c, *args, **kwargs):
                    make_members(self, locals())

        >>> f = Foo(1, 'fake', 42.0, 7, 8, 9, r=15, e=30)
        `f` now contains the following attributes:
        {'a': 1, 'b': 'fake', 'c': 42.0, 'args': (7, 8, 9), 'r': 15, 'e': 30}
    Args:
        obj (Any): attributes will be added to obj
        kwargs (Mapping[str, Any], optional): a map of attribute names and values.
            Defaults to {}.
        private (bool, optional): True to prepend the private prefix to all
            arguments. Defaults to False
        recur_on (tuple[str], optional): Also traverse inner arguments with names
            appearing in this tuple. Defaults to ("kwargs",).
        ignore (tuple[str], optional): Ignore arguments with names
            appearing in this tuple. Defaults to ("self",).
        private_prefix (str, optional): Prefix to prepend to private arguments. Defaults
            to "_".
    """

    def _traverse(data):
        for k, v in data.items():
            if k in recur_on:
                _traverse(v)
            elif k not in ignore:
                if private:
                    k = f"{private_prefix}{k}"
                setattr(obj, k, v)

    _traverse(kwargs)
