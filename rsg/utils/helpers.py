from typing import Any, Mapping


def make_attrs(obj: Any, kwargs: Mapping[str, Any] = {}, private: bool = False):
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
        private (bool, optional): True to prepend "_" as a private qualifier to
            argument name. Defaults to False
    """

    def _traverse(data):
        for k, v in data.items():
            if k == "kwargs":
                _traverse(v)
            elif k != "self":
                if private and not k.startswith("_"):
                    k = f"_{k}"
                setattr(obj, k, v)

    _traverse(kwargs)
